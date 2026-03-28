#!/usr/bin/env python3
"""
Entrypoint script for nanobot Docker deployment.

Resolves environment variables into config.json at runtime,
then launches 'nanobot gateway'.
"""

import json
import os
import sys
from pathlib import Path


def resolve_config():
    """Read config.json, inject env vars, write config.resolved.json."""
    # Paths
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.json"
    resolved_path = script_dir / "config.resolved.json"
    workspace_path = script_dir / "workspace"

    # Read original config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Inject LLM provider env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_base_url = os.environ.get("LLM_API_BASE_URL")
    llm_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_base_url:
        config["providers"]["custom"]["apiBase"] = llm_base_url
    if llm_model:
        config["agents"]["defaults"]["model"] = llm_model

    # Inject gateway config
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)

    # Inject webchat channel config
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")
    access_key = os.environ.get("NANOBOT_ACCESS_KEY")

    if "webchat" not in config.get("channels", {}):
        config["channels"]["webchat"] = {}

    if webchat_host:
        config["channels"]["webchat"]["host"] = webchat_host
    if webchat_port:
        config["channels"]["webchat"]["port"] = int(webchat_port)
    if access_key:
        config["channels"]["webchat"]["access_key"] = access_key

    # Inject MCP server env vars (LMS backend)
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")

    if "mcpServers" in config.get("tools", {}):
        if "lms" in config["tools"]["mcpServers"]:
            if lms_backend_url:
                config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
            if lms_api_key:
                config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    return str(resolved_path), str(workspace_path)


def main():
    """Resolve config and launch nanobot gateway."""
    resolved_config, workspace = resolve_config()

    print(f"[entrypoint] Using resolved config: {resolved_config}")
    print(f"[entrypoint] Using workspace: {workspace}")
    sys.stdout.flush()

    # Launch nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_config, "--workspace", workspace])


if __name__ == "__main__":
    main()
