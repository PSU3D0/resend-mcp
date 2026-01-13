# OpenAPI Spec Review Instructions

You are reviewing changes to the Resend OpenAPI specification for resend-mcp.

## Context

resend-mcp transforms the upstream Resend OpenAPI spec into MCP tools. The key file is `scripts/transform_spec.py` which contains hand-curated `operationId` mappings in `path_overrides` (around line 43-93).

## Your Task

Analyze the spec diff provided and create an RFC document.

## Analysis Steps

1. **Identify New Endpoints**
   - Any new paths in the spec need `operationId` mappings
   - Suggest names following conventions: `create*`, `get*`, `list*`, `update*`, `delete*`, or action verbs like `send*`, `verify*`, `cancel*`

2. **Identify Removed Endpoints**
   - Flag as breaking changes
   - Note which tools will be removed

3. **Identify Modified Endpoints**
   - Parameter additions (non-breaking if optional)
   - Parameter removals (breaking)
   - Parameter type changes (potentially breaking)
   - Response schema changes

4. **Check Schema Changes**
   - New required fields (breaking for request bodies)
   - Removed fields (breaking for responses)
   - Type changes

## Output

Create a new RFC file at `docs/rfcs/YYYYMMDD-spec-update.md` using the template at `docs/rfcs/TEMPLATE.md`.

Fill in:
- RFC number (increment from last RFC in docs/rfcs/)
- Today's date
- All detected changes
- Suggested operationId mappings for new endpoints
- Breaking change analysis
- Required updates to transform_spec.py (just the new path_overrides entries)

## Naming Conventions

Follow existing patterns:
- `sendEmail` not `createEmail` (POST /emails sends, doesn't just create)
- `listDomains` not `getDomains` (GET on collection = list)
- `getContactByEmail` / `getContactById` when multiple lookup methods exist
- camelCase, verb prefix, singular noun for single item, plural for lists

## Do NOT

- Modify any code files (only create the RFC markdown)
- Make assumptions about changes not visible in the diff
- Skip the RFC even if changes seem minor
