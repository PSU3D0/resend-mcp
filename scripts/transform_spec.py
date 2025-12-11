#!/usr/bin/env python3
"""
Transform Resend OpenAPI spec:
1. Add operationId to all endpoints
2. Inline parameter references
3. Fix YAML quoting issues
"""

import sys
import yaml


def preprocess_yaml(text: str) -> str:
    """Fix YAML issues before parsing."""
    lines = text.split("\n")
    result = []

    for line in lines:
        if "description:" in line and ": " in line.split("description:", 1)[1]:
            indent = len(line) - len(line.lstrip())
            key_part = line.lstrip().split(":", 1)[0]
            value_part = line.split("description:", 1)[1].strip()
            if not value_part.startswith("'") and not value_part.startswith('"'):
                value_part = value_part.replace("'", "''")
                line = " " * indent + f"{key_part}: '{value_part}'"
        result.append(line)

    return "\n".join(result)


def path_to_operation_id(method: str, path: str) -> str:
    """Convert HTTP method + path to camelCase operationId."""
    method = method.lower()

    method_prefixes = {
        "get": "get",
        "post": "create",
        "put": "update",
        "patch": "update",
        "delete": "delete",
    }

    path_overrides = {
        ("post", "/emails"): "sendEmail",
        ("post", "/emails/batch"): "sendBatchEmails",
        ("post", "/emails/{email_id}/cancel"): "cancelScheduledEmail",
        ("get", "/emails/{email_id}"): "getEmail",
        ("patch", "/emails/{email_id}"): "updateEmail",
        ("get", "/emails/{email_id}/attachments"): "listEmailAttachments",
        ("get", "/emails/{email_id}/attachments/{attachment_id}"): "getEmailAttachment",
        ("get", "/emails/receiving"): "listReceivedEmails",
        ("get", "/emails/receiving/{email_id}"): "getReceivedEmail",
        ("get", "/emails/receiving/{email_id}/attachments"): "listReceivedEmailAttachments",
        ("get", "/emails/receiving/{email_id}/attachments/{attachment_id}"): "getReceivedEmailAttachment",
        ("post", "/domains"): "createDomain",
        ("get", "/domains"): "listDomains",
        ("get", "/domains/{domain_id}"): "getDomain",
        ("patch", "/domains/{domain_id}"): "updateDomain",
        ("delete", "/domains/{domain_id}"): "deleteDomain",
        ("post", "/domains/{domain_id}/verify"): "verifyDomain",
        ("post", "/api-keys"): "createApiKey",
        ("get", "/api-keys"): "listApiKeys",
        ("delete", "/api-keys/{api_key_id}"): "deleteApiKey",
        ("post", "/audiences"): "createAudience",
        ("get", "/audiences"): "listAudiences",
        ("get", "/audiences/{id}"): "getAudience",
        ("delete", "/audiences/{id}"): "deleteAudience",
        ("post", "/audiences/{audience_id}/contacts"): "createContact",
        ("get", "/audiences/{audience_id}/contacts"): "listContacts",
        ("get", "/audiences/{audience_id}/contacts/{email}"): "getContactByEmail",
        ("patch", "/audiences/{audience_id}/contacts/{email}"): "updateContactByEmail",
        ("delete", "/audiences/{audience_id}/contacts/{email}"): "deleteContactByEmail",
        ("get", "/audiences/{audience_id}/contacts/{id}"): "getContactById",
        ("patch", "/audiences/{audience_id}/contacts/{id}"): "updateContactById",
        ("delete", "/audiences/{audience_id}/contacts/{id}"): "deleteContactById",
        ("post", "/broadcasts"): "createBroadcast",
        ("get", "/broadcasts"): "listBroadcasts",
        ("get", "/broadcasts/{id}"): "getBroadcast",
        ("delete", "/broadcasts/{id}"): "deleteBroadcast",
        ("post", "/broadcasts/{id}/send"): "sendBroadcast",
        ("post", "/webhooks"): "createWebhook",
        ("get", "/webhooks"): "listWebhooks",
        ("get", "/webhooks/{webhook_id}"): "getWebhook",
        ("patch", "/webhooks/{webhook_id}"): "updateWebhook",
        ("delete", "/webhooks/{webhook_id}"): "deleteWebhook",
        ("post", "/templates"): "createTemplate",
        ("get", "/templates"): "listTemplates",
        ("get", "/templates/{id}"): "getTemplate",
        ("patch", "/templates/{id}"): "updateTemplate",
        ("delete", "/templates/{id}"): "deleteTemplate",
        ("post", "/templates/{id}/publish"): "publishTemplate",
        ("post", "/templates/{id}/duplicate"): "duplicateTemplate",
    }

    if (method, path) in path_overrides:
        return path_overrides[(method, path)]

    prefix = method_prefixes.get(method, method)

    parts = path.strip("/").split("/")
    name_parts = []

    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            continue
        part = part.replace("-", "_")
        words = part.split("_")
        name_parts.extend(words)

    if not name_parts:
        return f"{prefix}Root"

    result = prefix
    for i, part in enumerate(name_parts):
        if i == 0 and prefix in ("get", "create", "update", "delete"):
            result += part.capitalize()
        else:
            result += part.capitalize()

    return result


def inline_parameter_refs(spec: dict) -> dict:
    """Inline component parameter references."""
    if "components" not in spec or "parameters" not in spec.get("components", {}):
        return spec

    param_defs = spec["components"]["parameters"]

    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method.startswith("x-") or not isinstance(operation, dict):
                continue

            if "parameters" not in operation:
                continue

            new_params = []
            for param in operation["parameters"]:
                if "$ref" in param:
                    ref_path = param["$ref"]
                    if ref_path.startswith("#/components/parameters/"):
                        param_name = ref_path.split("/")[-1]
                        if param_name in param_defs:
                            new_params.append(param_defs[param_name].copy())
                        else:
                            new_params.append(param)
                    else:
                        new_params.append(param)
                else:
                    new_params.append(param)

            operation["parameters"] = new_params

    return spec


def fix_description_quoting(spec: dict) -> dict:
    """Fix descriptions that contain colons or special chars."""
    def fix_string(s):
        if not isinstance(s, str):
            return s
        if ": " in s and not s.startswith("'") and not s.startswith('"'):
            return s
        return s

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "description" and isinstance(v, str):
                    obj[k] = fix_string(v)
                else:
                    walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(spec)
    return spec


def add_operation_ids(spec: dict) -> dict:
    """Add operationId to all path operations."""
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method.startswith("x-") or not isinstance(operation, dict):
                continue

            if "operationId" not in operation:
                operation["operationId"] = path_to_operation_id(method, path)

    return spec


def transform_spec(spec: dict) -> dict:
    """Apply all transformations."""
    spec = inline_parameter_refs(spec)
    spec = add_operation_ids(spec)
    spec = fix_description_quoting(spec)
    return spec


class QuotedDumper(yaml.SafeDumper):
    """Custom dumper that quotes strings with colons."""
    pass


def quoted_str_representer(dumper, data):
    if ": " in data or data.startswith("Deprecated"):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


QuotedDumper.add_representer(str, quoted_str_representer)


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "-"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "-"

    if input_file == "-":
        raw_text = sys.stdin.read()
    else:
        with open(input_file) as f:
            raw_text = f.read()

    fixed_text = preprocess_yaml(raw_text)
    spec = yaml.safe_load(fixed_text)

    spec = transform_spec(spec)

    if output_file == "-":
        yaml.dump(spec, sys.stdout, QuotedDumper, default_flow_style=False, sort_keys=False, allow_unicode=True)
    else:
        with open(output_file, "w") as f:
            yaml.dump(spec, f, QuotedDumper, default_flow_style=False, sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    main()
