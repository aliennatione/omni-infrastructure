---
tags: [provider, google]
related: [../discovery/external-tools-landscape.md]
---

# Google Gemini Providers

## Overview

Two Google Gemini provider variants are configured in `config/providers.json`:

| Provider | Model | Use Case |
|---|---|---|
| `google_gemini_flash` | gemini-2.0-flash | Fast, cheap tasks: small_fix, git_automation |
| `google_gemini_pro` | gemini-2.0-pro | Complex tasks: software_refactor |

## Configuration

Provider type: `google_api`
Authentication: `GEMINI_API_KEY` environment variable
Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`

## Behavior

- HTTP POST to Google's generateContent API
- JSON request with `contents` array and `systemInstruction`
- Response parsed for `candidates[0].content.parts[0].text`
- Error handling: checks `response.raise_for_status()`

## Matrix Routing

- `small_fix` → `google_gemini_flash`
- `git_automation` → `google_gemini_flash`
- `software_refactor` → `google_gemini_pro`

## Date

2026-05-16
