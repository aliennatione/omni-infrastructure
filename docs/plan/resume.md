# Resume — Sessione di sviluppo Omni-Agent Infrastructure

## Contesto

Stiamo sviluppando **omni-infrastructure**, un orchestratore GitOps multi-agent.
Tutto il codice è in `/data/workspace/omni-infrastructure/`.

## Stato attuale (commit recenti)

```bash
git log --oneline -5
git status
```

## Cosa è stato fatto (commit 048a10b e precedenti)

### Core
- Bridge CLI (`core/bridge.py`) con `--event`, `--payload`, `--mode`, `--provider`, `--list-providers`, `--compact`
- 7 provider LLM in `config/providers.json` e `core/inference.py`:
  - `google_api` (Gemini Flash + Pro)
  - `openai_compat` (llama.cpp, LocalAI, Ollama)
  - `opencode_api` (OpenCode via API nativa sessioni)
  - `openhands_api` (OpenHands via API sessioni)
- Routing eventi in `config/matrix.json` (8 eventi)
- Per-event system prompts in `config/prompts/` (7 file JSON specializzati)
- Caveman mode: `--compact` flag + `CAVEMAN_MODE` env var + `_compress_context()`

### MCP e integrazioni
- Config MCP condivisa (`config/mcp_servers.json`) — filesystem, github, nanobot
- Printing Press: 3 MCP server configurati (linear, slack, stripe), 82+ disponibili
- Nanobot MCP server (`core/nanobot_mcp.py`) — 12 tool git/fs/db
- NanoClaw Gateway (`core/nanoclaw_gateway.py`) — Telegram polling bot
- DocIngester (`core/doclingest.py`) — crawling documentazione con trafilatura

### Infrastruttura
- Docker Compose con 4 profiles (llamacpp, localai, ollama, nanobot)
- Makefile con 18+ target (install-cron, install-service, install-pp)
- Trigger locali: script cron + servizio systemd
- `.env.example` completo (20+ variabili)

### Documentazione
- Wiki popolata: `docs/wiki/` con 13 pagine (decision/, discovery/, provider/)
- Docs: architecture, setup, local-mode, hybrid-mode, providers, mcp, nanobot, mobile, printing-press, ingestion

## Cosa fare dopo (Fase 6)

Tre blocchi indipendenti, sviluppabili in parallelo:

### 6A — Automated tests (priorità: massima)
- `pip install pytest pytest-mock responses`
- `tests/conftest.py` — fixtures condivise
- `tests/test_bridge.py` — resolve_event, load_event_prompt, build_system_prompt, _compress_context
- `tests/test_inference.py` — mock HTTP per ogni provider
- `tests/test_nanobot_mcp.py` — test tool git/fs/db
- `tests/test_doclingest.py` — test parsing HTML locale
- `tests/test_nanoclaw_gateway.py` — test handle_message, call_bridge
- `Makefile` target `test` (pytest -v --tb=short)

### 6B — Multi-platform gateway (Matrix)
- `core/gateway_base.py` — `MessagingBackend` (ABC) + `GatewayRunner` (loop polling)
- `core/gateway_matrix.py` — `MatrixBackend` con matrix-nio
- `core/nanoclaw_gateway.py` — refactor: `TelegramBackend` usa `GatewayRunner`
- `requirements.txt` — aggiungere `matrix-nio>=0.25`
- `.env.example` — variabili Matrix (HOMESERVER, USER, PASSWORD, ROOM_ID)

### 6C — Streaming support
- `core/inference.py` — param `stream` su `run()` + metodi `*_stream()` (SSE)
- `core/bridge.py` — flag `--stream`, stampa tokens in real-time
- Test in `tests/test_inference.py` (mock SSE)

## Per orientarsi

- [docs/STATUS.md](../STATUS.md) — quadro completo
- [docs/plan/README.md](README.md) — piano di sviluppo
- [docs/wiki/index.md](../wiki/index.md) — wiki di conoscenza
- [docs/providers.md](../providers.md) — provider LLM
- [docs/mcp.md](../mcp.md) — configurazione MCP

## Comandi rapidi

```bash
# Syntax check
python3 -m py_compile core/inference.py
python3 -m py_compile core/bridge.py

# Validare JSON
python3 -c "import json; json.load(open('config/providers.json')); json.load(open('config/matrix.json')); json.load(open('config/mcp_servers.json')); print('OK')"

# Validare prompt JSON
for f in config/prompts/*.json; do python3 -c "import json; json.load(open('$f'))"; done

# Elencare provider
make list-providers

# Eseguire tests (dopo setup)
make test
```
