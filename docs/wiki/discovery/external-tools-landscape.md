---
tags: [discovery, external-tools]
related: [caveman-analysis.md, printing-press-analysis.md, bmad-analysis.md]
---

# External Tools Landscape

## Overview

Survey of external tools evaluated for integration with Omni-Agent Infrastructure.

## Evaluated Tools

### Caveman (61K stars) — INTEGRATED
- **Type**: Prompt skill for token compression
- **Status**: Native implementation in bridge.py
- **Value**: 65% fewer output tokens
- **Cost**: ~20 lines of code, zero dependencies

### Printing Press (2K stars) — INTEGRATED
- **Type**: MCP server generator from API specs
- **Status**: 3 servers configured (Linear, Slack, Stripe), 82+ available
- **Value**: Persistent, queryable access to external services via MCP
- **Cost**: Requires Go 1.26+ for installation

### BMAD-METHOD (47K stars) — REJECTED
- **Type**: Dev-time AI IDE prompt management
- **Status**: Not integrated; pattern extracted as event prompts
- **Value**: Specialized agent behavior (extracted)
- **Cost**: 15K token overhead, wrong layer

### Superpowers (186K stars) — NOT INTEGRATED
- **Type**: Composable AI IDE skills
- **Status**: Evaluated, dev-time focused
- **Reason**: Same layer mismatch as BMAD

### GSD (60K stars) — NOT INTEGRATED
- **Type**: Minimalist AI IDE framework
- **Status**: Evaluated, dev-time focused
- **Reason**: Same layer mismatch as BMAD

### CrewAI / LangGraph — NOT INTEGRATED
- **Type**: Runtime multi-agent orchestration
- **Status**: Evaluated, different category
- **Reason**: Heavy frameworks; our bridge is lightweight and purpose-built

## Decision Criteria

1. **Layer match**: Must operate at runtime orchestration, not dev-time IDE
2. **Token efficiency**: Should not add unnecessary token overhead
3. **Dependency weight**: Prefer patterns over libraries
4. **Integration cost**: Should work with existing architecture without major changes

## Date

2026-05-16
