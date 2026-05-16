---
tags: [provider, local]
related: [../discovery/external-tools-landscape.md, ../../decision/pr-based-workflow.md]
---

# OpenHands Provider

## Overview

OpenHands is an autonomous software development agent with a session-based API.

## Configuration

Provider type: `openhands_api`
Authentication: `OPENHANDS_API_KEY` environment variable (optional)
Endpoint: Configurable in `providers.json`

## Behavior

- POST `/api/sessions` to create a new session with task
- POST `/api/sessions/{id}/messages` to send follow-up messages
- Bearer token auth (if key provided)
- Session-based: each task creates a new OpenHands session

## Matrix Routing

- `chat_message` → `local_openhands`

## Implementation

Added in Phase 1. The `openhands_api()` method in `core/inference.py` handles:
1. Session creation with the task as initial message
2. Polling for session completion
3. Returning the final agent response

## Date

2026-05-16
