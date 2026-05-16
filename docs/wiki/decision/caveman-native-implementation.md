---
tags: [decision, architecture]
related: [../discovery/caveman-analysis.md]
---

# Implement Caveman Mode Natively

## Decision

Implement Caveman-style compression (~65% fewer output tokens) as a native feature rather than depending on the external Caveman project.

## Rationale

Caveman (61K stars) is a Claude Code skill — a prompt file, not a library. Its core technique is:
1. System prompt directive to respond tersely
2. Context compression (truncate long lines, skip HTML comments, deduplicate blanks)

We implemented this as:
- `--compact` CLI flag + `CAVEMAN_MODE` env var in `bridge.py`
- `_compress_context()` method: truncate lines >200 chars, skip `> ` and `<!--` blocks, deduplicate blank lines
- Composed with event-specific prompts (caveman directive appended to event system_directive)

## Impact

- No external dependency
- ~20 lines of logic in bridge.py
- Works with any provider and any event type
- Can be toggled per-run via flag or globally via env var

## Date

2026-05-16
