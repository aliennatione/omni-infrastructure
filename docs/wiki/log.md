# Log

Storico cronologico delle modifiche al wiki.

Formato: `## [YYYY-MM-DD] tipo | Titolo`

```
grep "^## \[" log.md | tail -10
```

## [2026-05-16] init | Creazione struttura wiki

- Creata directory `docs/wiki/` con index.md e log.md
- Aggiunte sottodirectory: `provider/`, `decision/`, `discovery/`
- Aggiunto schema wiki ad AGENTS.md

## [2026-05-16] ingest | Sviluppo completo fasi 1-5

- **Fase 1:** Provider `openhands_api` implementato in `inference.py`
- **Fase 2:** Config MCP condivisa `config/mcp_servers.json` + `docs/mcp.md`
- **Fase 3:** Nanobot MCP server `core/nanobot_mcp.py` + Dockerfile + docs
- **Fase 4:** Trigger locali (cron/systemd) + evento `local_cron` in matrix.json
- **Fase 5:** NanoClaw gateway Telegram `core/nanoclaw_gateway.py` + `docs/mobile.md`
- Aggiornati: STATUS.md, README.md, providers.md, AGENTS.md, .env.example, docker-compose.yml, Makefile

## [2026-05-16] ingest | Integrazioni esterne: Caveman + Printing Press

- **Caveman:** Modalità `--compact` nel bridge, compressione CONTEXT.md, `CAVEMAN_MODE` env var
- **Printing Press:** 82+ MCP server in `mcp_servers.json`, `docs/printing-press.md`, `make install-pp`

## [2026-05-16] ingest | Wiki population — decision records, discovery, provider pages

- **Decisioni:** 5 ADR creati in `docs/wiki/decision/`:
  - `three-repo-isolation.md` — Modello a 3 repository
  - `reject-bmad-adopt-event-prompts.md` — Rifiuto BMAD, pattern prompt per evento
  - `caveman-native-implementation.md` — Caveman implementato nativamente
  - `shared-mcp-config.md` — Config MCP centralizzata
  - `pr-based-workflow.md` — Workflow PR per agent
- **Scoperte:** 4 pagine in `docs/wiki/discovery/`:
  - `caveman-analysis.md` — Analisi compressione token
  - `printing-press-analysis.md` — Analisi generatore MCP
  - `bmad-analysis.md` — Perché BMAD è stato rifiutato
  - `external-tools-landscape.md` — Panorama tool esterni
- **Provider:** 4 pagine in `docs/wiki/provider/`:
  - `google-gemini.md`, `local-providers.md`, `opencode.md`, `openhands.md`
- Aggiornati `index.md` e `log.md`

## [2026-05-16] ingest | Per-event-type system prompts

- Creata directory `config/prompts/` con 7 prompt JSON specializzati:
  - `small_fix.json`, `git_automation.json`, `software_refactor.json`
  - `local_inference.json`, `opencode_inference.json`, `local_cron.json`, `chat_message.json`
- Ogni prompt definisce: `system_directive`, `behavior` (regole), `output_format`
- Aggiornato `core/bridge.py`: nuovi metodi `load_event_prompt()` e `build_system_prompt()`
- Il bridge carica automaticamente il prompt specifico per l'evento
- CAVEMAN_MODE si compone con i prompt evento (aggiunge direttiva caveman)
- Fallback al prompt generico se nessun file prompt esiste per l'evento

## [2026-05-16] ingest | Fase 6 — Tests, Gateway Matrix, Streaming

- **6A — Automated Tests:** 71 test totali, tutti passanti
  - `test_bridge.py`: 22 test (resolve_event, load_event_prompt, build_system_prompt, _compress_context)
  - `test_inference.py`: 21 test (google_api, openai_compat, opencode_api, openhands_api, streaming)
  - `test_nanobot_mcp.py`: 14 test (git, fs, db tools)
  - `test_doclingest.py`: 9 test (config, context, crawl)
  - `test_nanoclaw_gateway.py`: 5 test (handle_message, TelegramBackend)
  - `conftest.py`: fixtures condivise (temp dirs, mock providers, bridge, router)
- **6B — Multi-platform Gateway:**
  - `gateway_base.py`: `MessagingBackend` ABC + `GatewayRunner` (loop polling/dispatch)
  - `gateway_matrix.py`: `MatrixBackend` con matrix-nio (login, sync, send)
  - `nanoclaw_gateway.py`: refactored a `TelegramBackend` che usa `GatewayRunner`
  - Architettura estensibile: aggiungere nuovi backend è implementare 3 metodi
- **6C — Streaming:**
  - `inference.py`: `stream()` method + `_stream_google_api()` + `_stream_openai_compat()`
  - `bridge.py`: flag `--stream`, stampa tokens in real-time
  - Google: streamGenerateContent endpoint, SSE chunk parsing
  - OpenAI compat: stream=True payload, data: SSE line parsing
  - Opencode/OpenHands: wrapper generator (yield full result)
- **Piano aggiornato:** `docs/plan/README.md`, `resume.md`, `phase-6-automation.md`, `pi-integration-note.md`
- **Wiki:** index.md aggiornato con nuove pagine decision/discovery/provider
- **requirements.txt:** pytest, pytest-mock, responses, matrix-nio
- **Makefile:** target `test` e `test-%`
