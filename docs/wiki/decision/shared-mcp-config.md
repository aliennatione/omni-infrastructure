---
tags: [decision, architecture]
related: [../discovery/printing-press-analysis.md]
---

# Shared MCP Server Configuration

## Decision

Centralize all MCP server configurations in a single `config/mcp_servers.json` file rather than scattering them across provider configs or environment variables.

## Rationale

MCP (Model Context Protocol) servers are tool providers that LLM agents can call. As the project grows, we'll accumulate MCP servers for:
- Filesystem access (built-in)
- GitHub operations
- Nanobot (custom git/fs/db tools)
- Printing Press servers (Linear, Slack, Stripe, etc.)

A single JSON config file provides:
- One source of truth for all MCP server endpoints and credentials
- Easy to add/remove servers without code changes
- Provider-agnostic (works with any LLM provider that supports MCP)
- Version-controlled and auditable

## Format

```json
{
  "servers": {
    "server_name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
      "env": {"API_KEY": "${ENV_VAR}"},
      "description": "What this server does"
    }
  }
}
```

## Date

2026-05-16
