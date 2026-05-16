---
tags: [provider, local]
related: [../discovery/external-tools-landscape.md]
---

# Local Providers (llama.cpp / LocalAI / Ollama)

## Overview

Three local inference provider variants are available, all using the `openai_compat` type:

| Provider | Server | Docker Profile |
|---|---|---|
| `local_llamacpp` | llama.cpp server | `llamacpp` |
| `local_localai` | LocalAI server | `localai` |
| `local_ollama` | Ollama server | `ollama` |

## Configuration

Provider type: `openai_compat`
Authentication: `LLM_API_KEY` environment variable (optional)
Endpoint: Configurable per provider in `providers.json`

## Behavior

- HTTP POST to `/v1/chat/completions` (OpenAI-compatible endpoint)
- JSON request with `model`, `messages` array
- Response parsed from `choices[0].message.content`
- Error handling: returns `{"error": ...}` dict on failure (does not raise)

## Matrix Routing

- `local_inference` → `local_llamacpp`
- `local_cron` → `local_llamacpp`

## Docker Compose

Three profiles available:
```bash
make up-llamacpp   # llama.cpp
make up-localai    # LocalAI
make up-ollama     # Ollama
```

## Date

2026-05-16
