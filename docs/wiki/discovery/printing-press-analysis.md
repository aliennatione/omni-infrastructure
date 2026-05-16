---
tags: [discovery, external-tools]
related: [../decision/shared-mcp-config.md]
---

# Printing Press — MCP Server Generator

## What It Is

CLI Printing Press (~2K GitHub stars) is a Go-based CLI generator that produces Cobra CLIs + MCP servers from any API spec, URL, or HAR file.

## Key Features

- 82+ pre-built MCP servers in its library (Stripe, Linear, Slack, GitHub, Notion, Jira, Twilio, etc.)
- Each MCP server has a local SQLite data layer with FTS5 full-text search
- Incremental sync with compound query support
- Generated CLIs can be used standalone or as MCP servers

## Our Integration

Added 3 Printing Press MCP servers to `config/mcp_servers.json`:
- `linear` — Issue tracking and project management
- `slack` — Channel messages and workspace data
- `stripe` — Payment and subscription data

## Installation

Requires Go 1.26+:
```bash
make install-pp
```

## Key Insight

Printing Press turns any API into an MCP server with local data sync. This is valuable for agents that need persistent, queryable access to external services.

## Date

2026-05-16
