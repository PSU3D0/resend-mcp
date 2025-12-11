# resend-mcp

![Banner](assets/banner.jpeg)

[![Crates.io](https://img.shields.io/crates/v/resend-mcp.svg)](https://crates.io/crates/resend-mcp)
[![Documentation](https://docs.rs/resend-mcp/badge.svg)](https://docs.rs/resend-mcp)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

MCP server for the [Resend](https://resend.com) email API. Exposes 49 tools for sending emails, managing domains, contacts, templates, broadcasts, webhooks, and more.

## Installation

### From Source

```bash
cargo install --path .
```

### Docker

```bash
docker pull ghcr.io/psu3d0/resend-mcp:latest
docker run -p 8080:8080 -e RESEND_API_KEY=re_xxx ghcr.io/psu3d0/resend-mcp:latest
```

### Pre-built Binaries

Download from [GitHub Releases](https://github.com/psu3d0/resend-mcp/releases).

## Usage

```bash
# Start server with stdio transport (default)
RESEND_API_KEY=re_xxx resend-mcp

# Or via CLI flag
resend-mcp --api-key re_xxx

# Use HTTP transport
resend-mcp --api-key re_xxx --transport http

# Custom bind address (HTTP mode)
resend-mcp --api-key re_xxx --transport http --bind-address 0.0.0.0 --port 3000

# Custom base URL (for proxies or testing)
resend-mcp --api-key re_xxx --base-url https://custom.api.com

# Disable startup health check
resend-mcp --api-key re_xxx --no-health-check

# Debug logging
RESEND_MCP_LOG=debug resend-mcp --api-key re_xxx
```

### MCP Client Configuration

#### Claude Desktop

```json
{
  "mcpServers": {
    "resend": {
      "command": "resend-mcp",
      "env": {
        "RESEND_API_KEY": "re_xxx"
      }
    }
  }
}
```

#### Docker

```json
{
  "mcpServers": {
    "resend": {
      "command": "docker",
      "args": ["run", "--rm", "-p", "8080:8080", "-e", "RESEND_API_KEY=re_xxx", "ghcr.io/psu3d0/resend-mcp:latest"]
    }
  }
}
```

## Available Tools

### Emails
- `sendEmail` - Send an email
- `sendBatchEmails` - Send up to 100 emails at once
- `getEmail` - Retrieve a single email
- `updateEmail` - Update a scheduled email
- `cancelScheduledEmail` - Cancel a scheduled email
- `listEmailAttachments` - List attachments for a sent email
- `getEmailAttachment` - Get a single attachment

### Received Emails
- `listReceivedEmails` - List received emails
- `getReceivedEmail` - Get a single received email
- `listReceivedEmailAttachments` - List attachments for a received email
- `getReceivedEmailAttachment` - Get a received email attachment

### Domains
- `createDomain` - Create a new domain
- `listDomains` - List all domains
- `getDomain` - Get a single domain
- `updateDomain` - Update a domain
- `deleteDomain` - Delete a domain
- `verifyDomain` - Verify a domain

### API Keys
- `createApiKey` - Create a new API key
- `listApiKeys` - List all API keys
- `deleteApiKey` - Delete an API key

### Audiences
- `createAudience` - Create an audience
- `listAudiences` - List all audiences
- `getAudience` - Get a single audience
- `deleteAudience` - Delete an audience

### Contacts
- `createContact` - Create a contact
- `listContacts` - List contacts in an audience
- `getContactByEmail` / `getContactById` - Get a contact
- `updateContactByEmail` / `updateContactById` - Update a contact
- `deleteContactByEmail` / `deleteContactById` - Delete a contact

### Broadcasts
- `createBroadcast` - Create a broadcast
- `listBroadcasts` - List all broadcasts
- `getBroadcast` - Get a single broadcast
- `deleteBroadcast` - Delete a draft broadcast
- `sendBroadcast` - Send or schedule a broadcast

### Templates
- `createTemplate` - Create a template
- `listTemplates` - List all templates
- `getTemplate` - Get a single template
- `updateTemplate` - Update a template
- `deleteTemplate` - Delete a template
- `duplicateTemplate` - Duplicate a template
- `publishTemplate` - Publish a template

### Webhooks
- `createWebhook` - Create a webhook
- `listWebhooks` - List all webhooks
- `getWebhook` - Get a single webhook
- `updateWebhook` - Update a webhook
- `deleteWebhook` - Delete a webhook

## Configuration

All options can be set via CLI flags or environment variables.

| CLI Flag | Env Variable | Default | Description |
|----------|--------------|---------|-------------|
| `--api-key` | `RESEND_API_KEY` | *required* | Resend API key |
| `--transport` | `TRANSPORT` | `stdio` | Transport mode (`stdio` or `http`) |
| `--base-url` | `RESEND_BASE_URL` | `https://api.resend.com` | Resend API base URL |
| `--bind-address` | `BIND_ADDRESS` | `127.0.0.1` | Server bind address (HTTP mode) |
| `--port` | `PORT` | `8080` | Server port (HTTP mode) |
| `--no-health-check` | - | `false` | Disable startup health check |
| - | `RESEND_MCP_LOG` | `info` | Log level (`error`, `warn`, `info`, `debug`, `trace`) |

## Health Check

On startup, the server calls `listDomains` to verify API key validity. This can be disabled with `--no-health-check`. A failed health check logs a warning but does not prevent startup.

## Development

```bash
# Build
cargo build

# Run with debug logging
RESEND_MCP_LOG=debug cargo run -- --api-key re_xxx

# Format and lint
cargo fmt && cargo clippy

# Update OpenAPI spec from upstream
python scripts/transform_spec.py /path/to/upstream/resend.yaml src/specs/resend.yaml
```

## OpenAPI Spec Updates

The spec is automatically synced from [resend/resend-openapi](https://github.com/resend/resend-openapi) daily via GitHub Actions. The transform script adds `operationId` fields and fixes YAML parsing issues.

## License

Apache-2.0
