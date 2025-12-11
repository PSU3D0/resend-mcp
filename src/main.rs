use std::sync::Arc;

use actix_web::{App, HttpServer, web};
use rmcp::transport::streamable_http_server::session::local::LocalSessionManager;
use rmcp_actix_web::transport::StreamableHttpService;
use rmcp_openapi::Server;
use tracing::{debug, info};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

const OPENAPI_SPEC: &str = include_str!("specs/resend.yaml");

#[actix_web::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_env("RESEND_MCP_LOG")
                .unwrap_or_else(|_| "info".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let openapi_json: serde_json::Value = serde_yaml::from_str(OPENAPI_SPEC)?;
    let base_url = url::Url::parse("https://api.resend.com")?;

    let mut server = Server::builder()
        .openapi_spec(openapi_json)
        .base_url(base_url)
        .build();

    server.load_openapi_spec()?;

    info!(tool_count = server.tool_count(), "Loaded Resend API tools");

    debug!(
        tools = %server.get_tool_names().join(", "),
        "Available tools"
    );

    server.validate_registry()?;

    let bind_address = std::env::var("BIND_ADDRESS").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()?;
    let bind_addr = format!("{}:{}", bind_address, port);

    info!(%bind_addr, "Starting Resend MCP server");

    let service = StreamableHttpService::builder()
        .service_factory(Arc::new(move || Ok(server.clone())))
        .session_manager(LocalSessionManager::default().into())
        .stateful_mode(false)
        .build();

    let http_server = HttpServer::new(move || {
        App::new().service(web::scope("/mcp").service(service.clone().scope()))
    })
    .bind(&bind_addr)?
    .run();

    info!(
        connection_url = %format!("http://{}/mcp", bind_addr),
        "Server ready for MCP client connections"
    );

    http_server.await?;

    Ok(())
}
