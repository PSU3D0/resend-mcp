FROM rust:1.83-alpine AS builder

RUN apk add --no-cache musl-dev

WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release --locked

FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=builder /build/target/release/resend-mcp /usr/local/bin/resend-mcp

LABEL org.opencontainers.image.source="https://github.com/psu3d0/resend-mcp"
LABEL org.opencontainers.image.description="MCP server for the Resend email API"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL io.modelcontextprotocol.server.name="io.github.psu3d0/resend-mcp"

EXPOSE 8080

ENTRYPOINT ["resend-mcp"]
