"""Stdio MCP server exposing observability operations as typed tools."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("observability")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_VICTORIALOGS_URL: str = ""
_VICTORIATRACES_URL: str = ""


def _get_victorialogs_url() -> str:
    """Get VictoriaLogs base URL from environment."""
    return os.environ.get("VICTORIALOGS_URL", "http://localhost:42010")


def _get_victoriatraces_url() -> str:
    """Get VictoriaTraces base URL from environment."""
    return os.environ.get("VICTORIATRACES_URL", "http://localhost:42011")


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _LogsSearchArgs(BaseModel):
    """Arguments for logs_search tool."""

    query: str = Field(
        default="*",
        description="LogsQL query string. Use '*' for all logs. Examples: 'level:error', '_stream:{service.name=\"Learning Management Service\"}', 'db_query'",
    )
    limit: int = Field(
        default=30,
        ge=1,
        le=1000,
        description="Maximum number of log entries to return (default 30, max 1000)",
    )
    start: str = Field(
        default="1h",
        description="Start time for the search. Examples: '1h', '30m', '24h'. Default is 1 hour ago.",
    )


class _LogsErrorCountArgs(BaseModel):
    """Arguments for logs_error_count tool."""

    start: str = Field(
        default="1h",
        description="Time window for counting errors. Examples: '1h', '30m', '24h'. Default is 1 hour.",
    )


class _TracesListArgs(BaseModel):
    """Arguments for traces_list tool."""

    service: str = Field(
        default="Learning Management Service",
        description="Service name to filter traces. Default is 'Learning Management Service'.",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of traces to return (default 10, max 100)",
    )


class _TracesGetArgs(BaseModel):
    """Arguments for traces_get tool."""

    trace_id: str = Field(
        ..., description="The trace ID to fetch. Example: '2a511ed65bae55c9e95befa6cef949fb'"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(data: Any) -> list[TextContent]:
    """Serialize data to a JSON text block."""
    return [
        TextContent(
            type="text", text=json.dumps(data, ensure_ascii=False, indent=2)
        )
    ]


def _parse_time_window(start: str) -> tuple[int, int]:
    """Parse a time window string like '1h', '30m' into start/end timestamps.

    Returns (start_ms, end_ms) timestamps.
    """
    now = datetime.now(timezone.utc)
    end_ms = int(now.timestamp() * 1000)

    # Parse the start time
    if start.endswith("h"):
        hours = int(start[:-1])
        start_time = now - timedelta(hours=hours)
    elif start.endswith("m"):
        minutes = int(start[:-1])
        start_time = now - timedelta(minutes=minutes)
    elif start.endswith("d"):
        days = int(start[:-1])
        start_time = now - timedelta(days=days)
    else:
        # Default to 1 hour
        start_time = now - timedelta(hours=1)

    start_ms = int(start_time.timestamp() * 1000)
    return start_ms, end_ms


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def _logs_search(args: _LogsSearchArgs) -> list[TextContent]:
    """Search logs in VictoriaLogs using LogsQL."""
    url = f"{_VICTORIALOGS_URL}/select/logsql/query"
    params = {
        "query": args.query,
        "limit": args.limit,
    }

    # Add time range if specified
    if args.start:
        start_ms, end_ms = _parse_time_window(args.start)
        params["start"] = str(start_ms)
        params["end"] = str(end_ms)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            # VictoriaLogs returns newline-delimited JSON
            lines = response.text.strip().split("\n")
            logs = [json.loads(line) for line in lines if line.strip()]
            return _text(
                {
                    "query": args.query,
                    "time_window": args.start,
                    "count": len(logs),
                    "logs": logs,
                }
            )
        except httpx.HTTPError as e:
            return _text({"error": f"Failed to query VictoriaLogs: {e}"})
        except json.JSONDecodeError as e:
            return _text({"error": f"Failed to parse response: {e}", "raw": response.text[:500]})


async def _logs_error_count(args: _LogsErrorCountArgs) -> list[TextContent]:
    """Count errors per service over a time window."""
    # Query for error-level logs
    url = f"{_VICTORIALOGS_URL}/select/logsql/query"
    start_ms, end_ms = _parse_time_window(args.start)

    # Query for errors with severity ERROR or level:error
    query = 'severity:ERROR OR level:error'
    params = {
        "query": query,
        "start": str(start_ms),
        "end": str(end_ms),
        "limit": "10000",  # Get more to count accurately
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            lines = response.text.strip().split("\n")
            logs = [json.loads(line) for line in lines if line.strip()]

            # Count errors by service
            error_counts: dict[str, int] = {}
            error_details: list[dict] = []

            for log in logs:
                service = log.get("service.name", log.get("service", "unknown"))
                error_counts[service] = error_counts.get(service, 0) + 1
                error_details.append(
                    {
                        "time": log.get("_time", log.get("time", "unknown")),
                        "service": service,
                        "event": log.get("event", log.get("_msg", "unknown")),
                        "error": log.get("error", log.get("error.message", "unknown")),
                    }
                )

            return _text(
                {
                    "time_window": args.start,
                    "total_errors": len(logs),
                    "errors_by_service": error_counts,
                    "recent_errors": error_details[:20],  # Show first 20
                }
            )
        except httpx.HTTPError as e:
            return _text({"error": f"Failed to query VictoriaLogs: {e}"})
        except json.JSONDecodeError as e:
            return _text({"error": f"Failed to parse response: {e}"})


async def _traces_list(args: _TracesListArgs) -> list[TextContent]:
    """List recent traces for a service."""
    # VictoriaTraces uses a different API - try the native API first
    url = f"{_VICTORIATRACES_URL}/api/traces"
    params = {
        "service": args.service,
        "limit": args.limit,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            if response.status_code == 200:
                traces = response.json()
                return _text(
                    {
                        "service": args.service,
                        "count": len(traces) if isinstance(traces, list) else "unknown",
                        "traces": traces if isinstance(traces, list) else traces,
                    }
                )

            # Try Jaeger-compatible API
            jaeger_url = f"{_VICTORIATRACES_URL}/jaeger/api/traces"
            response = await client.get(jaeger_url, params=params, timeout=30.0)
            response.raise_for_status()
            traces = response.json()
            return _text(
                {
                    "service": args.service,
                    "count": len(traces) if isinstance(traces, list) else "unknown",
                    "traces": traces if isinstance(traces, list) else traces,
                }
            )
        except httpx.HTTPError as e:
            return _text(
                {
                    "error": f"Failed to query VictoriaTraces: {e}",
                    "hint": "Check if VictoriaTraces is running and the service name is correct. Try accessing http://localhost:42011/select/vmui directly.",
                }
            )


async def _traces_get(args: _TracesGetArgs) -> list[TextContent]:
    """Fetch a specific trace by ID."""
    # Try native API first
    url = f"{_VICTORIATRACES_URL}/api/traces/{args.trace_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            if response.status_code == 200:
                trace = response.json()
                return _text({"trace_id": args.trace_id, "trace": trace})

            # Try Jaeger-compatible API
            jaeger_url = f"{_VICTORIATRACES_URL}/jaeger/api/traces/{args.trace_id}"
            response = await client.get(jaeger_url, timeout=30.0)
            response.raise_for_status()
            trace = response.json()
            return _text({"trace_id": args.trace_id, "trace": trace})
        except httpx.HTTPError as e:
            return _text(
                {
                    "error": f"Failed to fetch trace {args.trace_id}: {e}",
                    "hint": "The trace ID might be invalid or the trace may have expired (retention is 7 days).",
                }
            )


# ---------------------------------------------------------------------------
# Registry: tool name -> (input model, handler, Tool definition)
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "logs_search",
    "Search logs in VictoriaLogs using LogsQL. Use for finding specific log entries, errors, or events.",
    _LogsSearchArgs,
    _logs_search,
)
_register(
    "logs_error_count",
    "Count errors per service over a time window. Use for answering 'any errors in the last hour?' type questions.",
    _LogsErrorCountArgs,
    _logs_error_count,
)
_register(
    "traces_list",
    "List recent traces for a service. Use for exploring trace data and finding trace IDs.",
    _TracesListArgs,
    _traces_list,
)
_register(
    "traces_get",
    "Fetch a specific trace by ID. Use for detailed investigation of a request flow.",
    _TracesGetArgs,
    _traces_get,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    global _VICTORIALOGS_URL, _VICTORIATRACES_URL
    _VICTORIALOGS_URL = _get_victorialogs_url()
    _VICTORIATRACES_URL = _get_victoriatraces_url()

    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
