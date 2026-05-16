---
tags: [decision, architecture]
related: [../discovery/external-tools-landscape.md, ../discovery/bmad-analysis.md]
---

# Three-Repository Isolation Model

## Decision

The project uses three isolated Git repositories as the foundational architecture:

| Repository | Role | Visibility |
|---|---|---|
| `omni-infrastructure` | Control plane — bridge code, config, CI/CD | Public/Private |
| `agent-state` | Memory plane — CONTEXT.md, append-only journal | Private |
| `project-source` | Data plane — application code modified via PRs | Private |

## Rationale

Separation of concerns at the repository level prevents:
- Agent state (context, logs) from polluting the application codebase
- Infrastructure code from mixing with business logic
- Accidental exposure of agent memory in public repos

The PR-based workflow on `project-source` ensures human review before any code change lands on main.

## Alternatives Considered

- **Single repo with branches**: Too much coupling, harder to manage permissions
- **Two repos (infra + app)**: No dedicated memory plane, context would be lost between runs

## Date

2026-05-16
