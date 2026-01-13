# RFC 0001: Initial API Surface

**Status:** Accepted
**Created:** 2025-12-11
**Upstream Spec:** [resend/resend-openapi](https://github.com/resend/resend-openapi)

## Summary

This RFC establishes the canonical API surface for resend-mcp, documenting the 49 curated MCP tools derived from the Resend OpenAPI specification.

## Motivation

The upstream Resend OpenAPI spec lacks `operationId` fields, which are required for generating readable MCP tool names. Raw path-to-name conversion produces unusable names like `POST__emails__batch`. This RFC documents the hand-curated mappings that produce clean, intuitive tool names like `sendBatchEmails`.

## Transform Pipeline

```
upstream spec (resend.yaml)
    │
    ▼
scripts/transform_spec.py
    ├── Add operationId to all endpoints
    ├── Inline parameter references
    └── Fix YAML quoting issues
    │
    ▼
src/specs/resend.yaml (transformed)
    │
    ▼
rmcp-openapi (runtime)
    │
    ▼
49 MCP tools
```

## Canonical Tool Surface

### Emails (7 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/emails` | POST | `sendEmail` |
| `/emails/batch` | POST | `sendBatchEmails` |
| `/emails/{email_id}` | GET | `getEmail` |
| `/emails/{email_id}` | PATCH | `updateEmail` |
| `/emails/{email_id}/cancel` | POST | `cancelScheduledEmail` |
| `/emails/{email_id}/attachments` | GET | `listEmailAttachments` |
| `/emails/{email_id}/attachments/{attachment_id}` | GET | `getEmailAttachment` |

### Received Emails (4 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/emails/receiving` | GET | `listReceivedEmails` |
| `/emails/receiving/{email_id}` | GET | `getReceivedEmail` |
| `/emails/receiving/{email_id}/attachments` | GET | `listReceivedEmailAttachments` |
| `/emails/receiving/{email_id}/attachments/{attachment_id}` | GET | `getReceivedEmailAttachment` |

### Domains (6 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/domains` | POST | `createDomain` |
| `/domains` | GET | `listDomains` |
| `/domains/{domain_id}` | GET | `getDomain` |
| `/domains/{domain_id}` | PATCH | `updateDomain` |
| `/domains/{domain_id}` | DELETE | `deleteDomain` |
| `/domains/{domain_id}/verify` | POST | `verifyDomain` |

### API Keys (3 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/api-keys` | POST | `createApiKey` |
| `/api-keys` | GET | `listApiKeys` |
| `/api-keys/{api_key_id}` | DELETE | `deleteApiKey` |

### Audiences (4 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/audiences` | POST | `createAudience` |
| `/audiences` | GET | `listAudiences` |
| `/audiences/{id}` | GET | `getAudience` |
| `/audiences/{id}` | DELETE | `deleteAudience` |

### Contacts (7 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/audiences/{audience_id}/contacts` | POST | `createContact` |
| `/audiences/{audience_id}/contacts` | GET | `listContacts` |
| `/audiences/{audience_id}/contacts/{email}` | GET | `getContactByEmail` |
| `/audiences/{audience_id}/contacts/{email}` | PATCH | `updateContactByEmail` |
| `/audiences/{audience_id}/contacts/{email}` | DELETE | `deleteContactByEmail` |
| `/audiences/{audience_id}/contacts/{id}` | GET | `getContactById` |
| `/audiences/{audience_id}/contacts/{id}` | PATCH | `updateContactById` |
| `/audiences/{audience_id}/contacts/{id}` | DELETE | `deleteContactById` |

### Broadcasts (5 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/broadcasts` | POST | `createBroadcast` |
| `/broadcasts` | GET | `listBroadcasts` |
| `/broadcasts/{id}` | GET | `getBroadcast` |
| `/broadcasts/{id}` | DELETE | `deleteBroadcast` |
| `/broadcasts/{id}/send` | POST | `sendBroadcast` |

### Templates (7 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/templates` | POST | `createTemplate` |
| `/templates` | GET | `listTemplates` |
| `/templates/{id}` | GET | `getTemplate` |
| `/templates/{id}` | PATCH | `updateTemplate` |
| `/templates/{id}` | DELETE | `deleteTemplate` |
| `/templates/{id}/publish` | POST | `publishTemplate` |
| `/templates/{id}/duplicate` | POST | `duplicateTemplate` |

### Webhooks (5 tools)

| Endpoint | Method | operationId |
|----------|--------|-------------|
| `/webhooks` | POST | `createWebhook` |
| `/webhooks` | GET | `listWebhooks` |
| `/webhooks/{webhook_id}` | GET | `getWebhook` |
| `/webhooks/{webhook_id}` | PATCH | `updateWebhook` |
| `/webhooks/{webhook_id}` | DELETE | `deleteWebhook` |

## Naming Conventions

1. **CRUD operations**: `create`, `get`, `list`, `update`, `delete` prefixes
2. **Actions**: Verb prefixes like `send`, `cancel`, `verify`, `publish`, `duplicate`
3. **Disambiguation**: Suffix with `ByEmail`/`ById` when multiple lookup methods exist
4. **Pluralization**: `list*` returns arrays, singular verbs return single items

## Future Changes

When the upstream spec changes:
1. New endpoints require adding `operationId` mappings to `transform_spec.py`
2. Removed endpoints should be flagged as breaking changes
3. Parameter changes should be analyzed for backwards compatibility

## References

- Upstream spec: https://github.com/resend/resend-openapi/blob/main/resend.yaml
- Transform script: `scripts/transform_spec.py`
- Generated spec: `src/specs/resend.yaml`
