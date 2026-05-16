# STATUS — Omni-Agent Infrastructure

Stato del progetto al 16 maggio 2026.

## Cos'è

Orchestratore GitOps multi-agent asincrono che:
- Riceve eventi (git_automation, software_refactor, chat_message...)
- Li instrada a un LLM provider (cloud Gemini o locale)
- Il LLM produce modifiche al codice in un repository workspace
- Il bridge crea PR e aggiorna journal su un repository state

Tre repository isolati: `omni-infrastructure` (control plane),
`agent-state` (memory plane), `project-source` (data plane).

## Componenti principali

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  bridge.py   │────▶│ inference.py │────▶│  Provider    │
│  Orchestr.   │     │  Router      │     │  LLM (7)     │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ├──▶ doclingest.py       (crawling documentazione → CONTEXT.md)
       ├──▶ nanobot_mcp.py      (MCP server: git/fs/db tools)
       ├──▶ nanoclaw_gateway.py (gateway Telegram mobile)
       ├──▶ matrix.json         (event → provider routing)
       ├──▶ mcp_servers.json    (config MCP condivisa + 82+ Printing Press)
       ├──▶ docker-compose      (LLM server profiles)
       ├──▶ caveman mode        (token compression: ~65% output, ~46% context)
       └──▶ Makefile            (comandi frequenti)
```

## Provider Landscape

| Provider | Tipo | Stato | Porta | Endpoint API |
|----------|------|-------|-------|-------------|
| `google_gemini_flash` | `google_api` | ✅ Funzionante | — | Gemini REST |
| `google_gemini_pro` | `google_api` | ✅ Funzionante | — | Gemini REST |
| `local_llamacpp` | `openai_compat` | ✅ Funzionante | 8080 | `/v1/chat/completions` |
| `local_localai` | `openai_compat` | ✅ Funzionante | 8081 | `/v1/chat/completions` |
| `local_ollama` | `openai_compat` | ✅ Funzionante | 11434 | `/v1/chat/completions` |
| `local_opencode` | `opencode_api` | ✅ Funzionante | 4096 | API nativa sessioni |
| `local_openhands` | `openhands_api` | ✅ Implementato | 8000 | API sessioni OpenHands |

## Struttura file

```
omni-infrastructure/
├── core/                     # Codice Python principale
│   ├── bridge.py             # Orchestratore CLI (entrypoint)
│   ├── inference.py          # Router LLM (7 tipi provider)
│   ├── doclingest.py         # Crawler documentazione con trafilatura
│   ├── nanobot_mcp.py        # MCP server: git/fs/db tools
│   ├── nanoclaw_gateway.py   # Gateway Telegram mobile
│   └── __init__.py
├── config/                   # Configurazioni JSON
│   ├── providers.json        # 7 provider dichiarati
│   ├── matrix.json           # 8 regole di routing evento → provider
│   ├── mcp_servers.json      # Config MCP condivisa
│   └── docs.json             # 3 fonti per DocIngester
├── docs/                     # Documentazione
│   ├── STATUS.md             # QUESTO FILE
│   ├── architecture.md       # Architettura 3-repo
│   ├── setup.md              # Setup token/secrets
│   ├── local-mode.md         # Esecuzione locale
│   ├── hybrid-mode.md        # Cloud + tunnel
│   ├── providers.md          # Provider LLM
│   ├── mcp.md                # Configurazione MCP condivisa
│   ├── nanobot.md            # Nanobot MCP server
│   ├── mobile.md             # NanoClaw gateway Telegram
│   ├── printing-press.md     # Printing Press — 82+ MCP server pre-built
│   ├── ingestion.md          # DocIngester pipeline
│   └── plan/                 # Piano di lavoro dettagliato
│       ├── README.md
│       ├── phase-1-openhands.md
│       ├── phase-2-mcp-config.md
│       ├── phase-3-nanobot.md
│       ├── phase-4-local-triggers.md
│       └── phase-5-nanoclaw.md
├── scripts/
│   ├── tunnel.sh             # ngrok/tailscale tunnel
│   ├── crawl-docs.sh         # Wrapper DocIngester
│   ├── omni-agent-cron       # Script per crontab
│   └── omni-agent.service    # Unit systemd
├── .github/workflows/
│   └── omni-engine.yml       # CI/CD cron 4h + dispatch
├── docker-compose.yml        # 4 profiles LLM + bridge + nanobot
├── Dockerfile                # python:3.11-slim
├── Dockerfile.nanobot        # Nanobot MCP server
├── Makefile                  # 18 target
├── requirements.txt          # requests, trafilatura
├── requirements.nanobot.txt  # mcp
├── .env.example              # 20 variabili d'ambiente
├── AGENTS.md                 # Istruzioni per AI agent
└── README.md                 # Entry point
```

## Config matrix.json — Routing eventi

| Evento | Provider | Modalità |
|--------|----------|----------|
| `small_fix` | `google_gemini_flash` | cloud |
| `git_automation` | `google_gemini_flash` | cloud |
| `software_refactor` | `google_gemini_pro` | cloud |
| `local_inference` | `local_llamacpp` | locale |
| `opencode_inference` | `local_opencode` | locale |
| `doc_ingestion` | `doclingest` | n/a |
| `local_cron` | `local_llamacpp` | locale |
| `chat_message` | `local_openhands` | locale |

## Bug fixati (commit 7c8d4d2)

Dalla review del codice sono stati corretti:
- 8 bug (mancata validazione path, errori connessione Opencode,
  mancata gestione sessione, doclingest errori di stato, etc.)
- 4 inefficienze (variabile endpoint duplicata, try/except generici,
  journal senza mkdir, logica doclingest ridondante)
- 8 migliorie (hint di connessione, --list-providers, docop stringhe,
  variabili d'ambiente, nomi descrittivi, segnaposto models)

## Cosa funziona oggi

- Bridge CLI con `--state`, `--workspace`, `--config`, `--event`, `--payload`, `--mode`, `--provider`, `--list-providers`, `--compact`
- 7 provider LLM (4 locali con openai_compat, 1 opencode_api, 1 openhands_api, 2 cloud)
- Caveman mode: risposte concise (~65% meno token output) + compressione contesto (~46% meno token input)
- Routing eventi via `matrix.json` o override diretto `--provider`
- Docker Compose profiles per avviare solo il LLM desiderato
- Makefile con target frequenti
- DocIngester: crawling documentazione con trafilatura, ricostruzione CONTEXT.md
- Nanobot MCP server: tool git, filesystem, SQLite
- NanoClaw Gateway: interazione mobile via Telegram
- Config MCP condivisa (`mcp_servers.json`) + 82+ MCP server Printing Press
- Trigger locali: script cron + servizio systemd
- `.env.example` completo

## Cosa manca (da fare)

Tutte le fasi del piano sono state implementate. Integrazioni esterne completate (Caveman, Printing Press). Possibili miglioramenti futuri:
1. Test automatizzati (unit/integration)
2. Signal oltre a Telegram per NanoClaw
3. Wiki population con decisioni e scoperte
4. Supporto per streaming nelle risposte LLM
5. Installazione automatica MCP server Printing Press (richiede Go)

## Differenze chiave tra provider API

| Aspetto | `openai_compat` | `opencode_api` | `openhands_api` |
|---------|----------------|----------------|-----------------|
| Endpoint | `/v1/chat/completions` | `/session` + `/session/{id}/message` | `/api/sessions` + `/api/sessions/{id}/messages` |
| Auth | Bearer token | Basic auth | Bearer token |
| Sessioni | Stateless | Create + Delete | Create + mantieni |
| Response | `choices[0].message.content` | `parts[].text` | `content` |
| MCP | No | Sì (come host) | Sì (come host) |

## Variabili d'ambiente critiche

| Variabile | Serve per | Obbligatoria? |
|-----------|-----------|---------------|
| `GEMINI_API_KEY` | Provider cloud Gemini | Sì, se mode=cloud |
| `OPENCODE_SERVER_PASSWORD` | Provider opencode_api | No (opzionale) |
| `OPENHANDS_API_KEY` | Provider openhands_api | No (opzionale) |
| `TELEGRAM_TOKEN` | NanoClaw gateway | Sì, se usi Telegram |
| `CAVEMAN_MODE` | Bridge: risposte concise (~65% meno token) | No (imposta a `1` per attivare) |
| `LINEAR_API_KEY` | Linear MCP server (Printing Press) | No |
| `SLACK_BOT_TOKEN` | Slack MCP server (Printing Press) | No |
| `STRIPE_SECRET_KEY` | Stripe MCP server (Printing Press) | No |

## Comandi rapidi

```bash
# Setup iniziale
make setup                         # mkdir state workspace
pip install -r requirements.txt    # dipendenze Python

# Esecuzione locale (senza Docker)
make run PROVIDER=local_llamacpp EVENT=git_automation PAYLOAD="Refactor"
# Con modalità compatta (caveman, ~65% meno token):
make run PROVIDER=local_llamacpp PAYLOAD="Refactor" CAVEMAN_MODE=1
# Equivalente senza Makefile:
PYTHONPATH=./core python core/bridge.py \
  --state ../agent-state \
  --workspace ../project-source \
  --config ./config \
  --event git_automation \
  --payload "Refactor" \
  --mode local \
  --provider local_llamacpp \
  --compact

# Esecuzione cloud (con Gemini)
GEMINI_API_KEY=... make run PROVIDER=google_gemini_flash

# Con Docker Compose
make up-llamacpp     # avvia llama.cpp + bridge
make up-nanobot      # avvia Nanobot MCP server
make logs            # tail -f
make down            # ferma

# Trigger locali
make install-cron    # installa script cron
make install-service # installa servizio systemd

# Printing Press (82+ MCP server)
make install-pp      # installa binary + MCP server linear/slack/stripe

# Utility
make profiles        # elenca profili Docker
make list-providers  # elenca provider disponibili
python3 -m py_compile core/inference.py   # syntax check
python3 -m py_compile core/bridge.py
```

## Dove approfondire

| Se vuoi... | Vedi... |
|------------|---------|
| Capire l'architettura 3-repo | `docs/architecture.md` |
| Setup token e GitHub Actions | `docs/setup.md` |
| Eseguire in locale con Docker | `docs/local-mode.md` |
| Tunnel cloud → LLM locale | `docs/hybrid-mode.md` |
| Lista provider e configurazione | `docs/providers.md` |
| Configurazione MCP condivisa | `docs/mcp.md` |
| Nanobot MCP server | `docs/nanobot.md` |
| Gateway mobile Telegram | `docs/mobile.md` |
| Printing Press — 82+ MCP server | `docs/printing-press.md` |
| Pipeline ingestion documentazione | `docs/ingestion.md` |
| Piano di sviluppo completo | `docs/plan/README.md` |
