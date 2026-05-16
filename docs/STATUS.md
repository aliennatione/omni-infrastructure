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
│  Orchestr.   │     │  Router      │     │  LLM (6)     │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ├──▶ doclingest.py   (crawling documentazione → CONTEXT.md)
       ├──▶ matrix.json      (event → provider routing)
       ├──▶ docker-compose   (LLM server profiles)
       └──▶ Makefile         (comandi frequenti)
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
| `openhands_api` | `openhands_api` | ❌ Non implementato | 8000 | API sessioni OpenHands |

## Struttura file

```
omni-infrastructure/
├── core/                     # Codice Python principale
│   ├── bridge.py             # Orchestratore CLI (entrypoint)
│   ├── inference.py          # Router LLM (6 tipi provider)
│   ├── doclingest.py         # Crawler documentazione con trafilatura
│   └── __init__.py
├── config/                   # Configurazioni JSON
│   ├── providers.json        # 6 provider dichiarati
│   ├── matrix.json           # 6 regole di routing evento → provider
│   └── docs.json             # 3 fonti per DocIngester
├── docs/                     # Documentazione
│   ├── STATUS.md             # QUESTO FILE
│   ├── architecture.md       # Architettura 3-repo
│   ├── setup.md              # Setup token/secrets
│   ├── local-mode.md         # Esecuzione locale
│   ├── hybrid-mode.md        # Cloud + tunnel
│   ├── providers.md          # Provider LLM
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
│   └── crawl-docs.sh         # Wrapper DocIngester
├── .github/workflows/
│   └── omni-engine.yml       # CI/CD cron 4h + dispatch
├── docker-compose.yml        # 3 profiles LLM + bridge
├── Dockerfile                # python:3.11-slim
├── Makefile                  # 14 target
├── requirements.txt          # requests, trafilatura
├── .env.example              # 16 variabili d'ambiente
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

## Bug fixati (commit 7c8d4d2)

Dalla review del codice sono stati corretti:
- 8 bug (mancata validazione path, errori connessione Opencode,
  mancata gestione sessione, doclingest errori di stato, etc.)
- 4 inefficienze (variabile endpoint duplicata, try/except generici,
  journal senza mkdir, logica doclingest ridondante)
- 8 migliorie (hint di connessione, --list-providers, docop stringhe,
  variabili d'ambiente, nomi descrittivi, segnaposto models)

## Cosa funziona oggi

- Bridge CLI con `--state`, `--workspace`, `--config`, `--event`, `--payload`, `--mode`, `--provider`, `--list-providers`
- 6 provider LLM (4 locali con openai_compat, 1 opencode_api, 2 cloud)
- Routing eventi via `matrix.json` o override diretto `--provider`
- Docker Compose profiles per avviare solo il LLM desiderato
- Makefile con target frequenti
- DocIngester: crawling documentazione con trafilatura, ricostruzione CONTEXT.md
- `.env.example` completo

## Cosa manca (da fare)

Priorità alta:
1. Provider `openhands_api` — non implementato in inference.py
2. Config MCP condivisa — `mcp_servers.json` non esiste

Priorità media:
3. Nanobot MCP server — non implementato
4. Trigger locali (cron/systemd) — script non esistono

Priorità bassa:
5. Integrazione NanoClaw (gateway chat mobile)

## Differenze chiave tra provider API

| Aspetto | `openai_compat` | `opencode_api` | `openhands_api` (TODO) |
|---------|----------------|----------------|----------------------|
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

## Comandi rapidi

```bash
# Setup iniziale
make setup                         # mkdir state workspace
pip install -r requirements.txt    # dipendenze Python

# Esecuzione locale (senza Docker)
make run PROVIDER=local_llamacpp EVENT=git_automation PAYLOAD="Refactor"
# Equivalente senza Makefile:
PYTHONPATH=./core python core/bridge.py \
  --state ../agent-state \
  --workspace ../project-source \
  --config ./config \
  --event git_automation \
  --payload "Refactor" \
  --mode local \
  --provider local_llamacpp

# Esecuzione cloud (con Gemini)
GEMINI_API_KEY=... make run PROVIDER=google_gemini_flash

# Con Docker Compose
make up-llamacpp     # avvia llama.cpp + bridge
make logs            # tail -f
make down            # ferma

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
| Pipeline ingestion documentazione | `docs/ingestion.md` |
| Piano di sviluppo completo | `docs/plan/README.md` |
