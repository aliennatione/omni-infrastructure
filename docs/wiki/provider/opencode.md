---
tags: [provider, local]
related: [../discovery/external-tools-landscape.md]
---

# OpenCode Provider

## Overview

OpenCode is a local IDE agent that exposes an API for agent communication.

## Configuration

Provider type: `opencode_api`
Authentication: Basic auth via `OPENCODE_SERVER_USERNAME` / `OPENCODE_SERVER_PASSWORD`
Endpoint: Configurable in `providers.json`

## Behavior

- Communicates with OpenCode's serve API
- Basic auth for session management
- Response handling: returns `{"error": ...}` dict on failure (does not raise)

## Matrix Routing

- `opencode_inference` → `local_opencode`

## Date

2026-05-16
