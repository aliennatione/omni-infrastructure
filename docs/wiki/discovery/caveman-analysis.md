---
tags: [discovery, external-tools]
related: [../decision/caveman-native-implementation.md, ../decision/reject-bmad-adopt-event-prompts.md]
---

# Caveman — Token Compression Analysis

## What It Is

Caveman is a Claude Code skill (~61K GitHub stars) that compresses agent output by 65-75%. It is a prompt/skill file, not a library or binary.

## How It Works

1. **System prompt directive**: Tells the model to respond in "caveman mode" — drop filler words, use fragments, keep substance, no pleasantries
2. **Context compression**: Truncates long lines, skips HTML comments, deduplicates blank lines, preserves headings and list items

## Our Implementation

We implemented a native version in `core/bridge.py`:
- `--compact` flag and `CAVEMAN_MODE` env var
- `_compress_context()` method (~20 lines)
- Composes with event-specific prompts

## Token Savings

- Estimated 65% reduction in output tokens
- Context compression adds ~5-10% additional savings on large CONTEXT.md files
- No impact on technical accuracy

## Key Insight

Caveman is a pattern, not a dependency. Any project can implement it in a few lines of code.

## Date

2026-05-16
