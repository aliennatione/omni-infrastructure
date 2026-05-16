---
tags: [decision, architecture]
related: [../../decision/three-repo-isolation.md]
---

# PR-Based Workflow for Agent Code Changes

## Decision

The agent never pushes directly to `main` in `project-source`. All code modifications go through Pull Requests.

## Rationale

- Human review gate: every agent change is visible before merging
- Audit trail: PRs provide discussion, diff, and approval history
- Safety: broken changes can be rejected without affecting production
- Consistency: matches standard GitOps practices

## Implementation

In CI/CD (`.github/workflows/omni-engine.yml`):
1. Agent creates a branch `agent/run-{RUN_ID}`
2. Agent commits changes to the branch
3. Agent opens a PR against `main`
4. Human reviews and merges (or auto-merges with safeguards)

## Date

2026-05-16
