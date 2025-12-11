use clap::Parser;
use hyper_util::{
    rt::{TokioExecutor, TokioIo},
    server::conn::auto::Builder,
    service::TowerToHyperService,
};
use reqwest::header::{AUTHORIZATION, CONTENT_TYPE, HeaderMap, HeaderValue};
use rmcp::ServiceExt;
use rmcp::transport::stdio;
use rmcp::transport::streamable_http_server::{
    StreamableHttpService, session::local::LocalSessionManager,
};
use rmcp_openapi::Server;
use tracing::{debug, info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

const OPENAPI_SPEC: &str = include_str!("specs/resend.yaml");
const DEFAULT_BASE_URL: &str = "https://api.resend.com";

#[derive(clap::ValueEnum, Clone, Debug)]
enum Transport {
    Http,
    Stdio,
}

#[derive(Parser, Debug)]
#[command(name = "resend-mcp")]
#[command(about = "MCP server for the Resend email API")]
#[command(version)]
struct Args {
    #[arg(long, env = "RESEND_API_KEY", hide_env_values = true)]
    api_key: String,

    #[arg(long, env = "RESEND_BASE_URL", default_value = DEFAULT_BASE_URL)]
    base_url: String,

    #[arg(long, env = "BIND_ADDRESS", default_value = "127.0.0.1")]
    bind_address: String,

    #[arg(long, env = "PORT", default_value = "8080")]
    port: u16,

    #[arg(long, env = "TRANSPORT", default_value = "stdio")]
    transport: Transport,

    #[arg(long, help = "Disable startup health check")]
    no_health_check: bool,
}

async fn run_health_check(base_url: &str, api_key: &str) -> Result<(), String> {
    let client = reqwest::Client::new();
    let url = format!("{}/domains", base_url.trim_end_matches('/'));

    let response = client
        .get(&url)
        .header(AUTHORIZATION, format!("Bearer {}", api_key))
        .header(CONTENT_TYPE, "application/json")
        .send()
        .await
        .map_err(|e| format!("Health check request failed: {}", e))?;

    if response.status().is_success() {
        Ok(())
    } else {
        let status = response.status();
        let body = response.text().await.unwrap_or_default();
        Err(format!(
            "Health check failed: {} - {}",
            status,
            body.chars().take(200).collect::<String>()
        ))
    }
}

fn build_server(args: &Args) -> Result<Server, Box<dyn std::error::Error>> {
    let openapi_json: serde_json::Value = serde_yaml::from_str(OPENAPI_SPEC)?;
    let base_url = url::Url::parse(&args.base_url)?;

    let mut headers = HeaderMap::new();
    headers.insert(
        AUTHORIZATION,
        HeaderValue::from_str(&format!("Bearer {}", args.api_key))?,
    );

    let mut server = Server::builder()
        .openapi_spec(openapi_json)
        .base_url(base_url)
        .default_headers(headers)
        .build();

    server.load_openapi_spec()?;

    info!(tool_count = server.tool_count(), "Loaded Resend API tools");

    debug!(
        tools = %server.get_tool_names().join(", "),
        "Available tools"
    );

    server.validate_registry()?;

    Ok(server)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_env("RESEND_MCP_LOG")
                .unwrap_or_else(|_| "info".into()),
        )
        .with(tracing_subscriber::fmt::layer().with_writer(std::io::stderr))
        .init();

    let args = Args::parse();

    if args.api_key.is_empty() {
        eprintln!("Error: --api-key or RESEND_API_KEY cannot be empty");
        std::process::exit(1);
    }

    let server = build_server(&args)?;

    if !args.no_health_check {
        info!("Running startup health check...");
        match run_health_check(&args.base_url, &args.api_key).await {
            Ok(()) => info!("Health check passed"),
            Err(e) => {
                warn!(%e, "Health check failed - API key may be invalid or Resend API unreachable");
            }
        }
    }

    match args.transport {
        Transport::Http => {
            let bind_addr = format!("{}:{}", args.bind_address, args.port);
            info!(%bind_addr, "Starting HTTP transport");

            let service = TowerToHyperService::new(StreamableHttpService::new(
                move || Ok(server.clone()),
                LocalSessionManager::default().into(),
                Default::default(),
            ));

            let listener = tokio::net::TcpListener::bind(&bind_addr).await?;

            info!(
                connection_url = %format!("http://{}/mcp", bind_addr),
                "Server ready for MCP client connections"
            );

            loop {
                let io = tokio::select! {
                    _ = tokio::signal::ctrl_c() => break,
                    accept = listener.accept() => {
                        TokioIo::new(accept?.0)
                    }
                };
                let service = service.clone();
                tokio::spawn(async move {
                    let _ = Builder::new(TokioExecutor::default())
                        .serve_connection(io, service)
                        .await;
                });
            }
        }
        Transport::Stdio => {
            info!("Starting stdio transport");
            let service = server.serve(stdio()).await.inspect_err(|e| {
                tracing::error!("serving error: {:?}", e);
            })?;
            service.waiting().await?;
        }
    }

    Ok(())
}
