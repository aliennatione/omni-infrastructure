---
tags: [decision, architecture]
related: [../discovery/bmad-analysis.md, ../discovery/caveman-analysis.md]
---

# Reject BMAD-METHOD, Adopt Event Prompts Pattern

## Decision

Do NOT install BMAD-METHOD (~47K stars) as a dependency. Instead, implement per-event-type system prompts via `config/prompts/` directory.

## Rationale

BMAD operates at the AI IDE layer (dev-time) — it installs 42+ SKILL.md files into `.claude/skills/` to control how an AI coding assistant behaves when a HUMAN developer codes. Our Omni-Agent operates at the runtime orchestration layer. These are completely different layers.

Installing BMAD would add ~15K tokens overhead with zero runtime benefit.

The useful pattern from BMAD is **specialized agents per task type**. We extract this pattern as lightweight JSON prompt files in `config/prompts/`, one per event type. Each prompt defines:
- `system_directive`: Role-specific system prompt
- `behavior`: Array of behavioral rules
- `output_format`: Expected response format

## Impact

- Each event type (small_fix, git_automation, software_refactor, chat_message, etc.) gets a tailored system prompt
- Zero token overhead from external frameworks
- Prompts are version-controlled and editable without code changes
- CAVEMAN_MODE composes with event prompts (adds caveman directive on top)

## Date

2026-05-16
