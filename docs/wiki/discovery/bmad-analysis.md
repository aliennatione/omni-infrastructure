---
tags: [discovery, external-tools]
related: [../decision/reject-bmad-adopt-event-prompts.md]
---

# BMAD-METHOD — Why We Rejected It

## What It Is

BMAD-METHOD (~47K GitHub stars) is a development-time framework for AI IDE prompt management. It installs 42+ SKILL.md files into `.claude/skills/` to control how AI coding assistants (Claude Code, Cursor) behave when a HUMAN developer codes.

## Why It Does Not Fit

| Aspect | BMAD | Omni-Agent |
|---|---|---|
| Layer | AI IDE (dev-time) | Runtime orchestration |
| User | Human developer | Autonomous agent |
| Overhead | ~15K tokens | Zero (we extract the pattern) |
| Benefit | Better AI IDE interactions | None at runtime |

## Alternatives Evaluated

- **Superpowers** (186K stars): Lighter composable skills, but still dev-time focused
- **GSD** (60K stars): Minimalist, but same layer mismatch
- **bmalph**: BMAD + Ralph loop hybrid, same issues
- **GitHub Spec Kit**: Spec-driven development, different category
- **CrewAI / LangGraph**: Runtime orchestration libraries, but heavy frameworks for a different use case

## What We Extracted

The valuable pattern: **per-task-type specialized system prompts**. We implemented this as `config/prompts/` with JSON files defining `system_directive`, `behavior`, and `output_format` for each event type.

## Date

2026-05-16
