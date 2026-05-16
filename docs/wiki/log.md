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
