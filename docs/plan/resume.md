# Resume — Sessione di sviluppo Omni-Agent Infrastructure

## Contesto

Stiamo sviluppando **omni-infrastructure**, un orchestratore GitOps multi-agent.
Tutto il codice è in `/data/workspace/omni-infrastructure/`.

## Stato attuale

Esegui `git log --oneline -3` e `git status` per vedere lo stato corrente.

## Cosa è stato fatto finora

- Bridge CLI funzionante (`core/bridge.py`) con `--provider`, `--list-providers`, `--mode local/cloud`
- 6 provider LLM in `config/providers.json` e `core/inference.py`:
  - `google_api` (Gemini Flash + Pro)
  - `openai_compat` (llama.cpp, LocalAI, Ollama)
  - `opencode_api` (OpenCode via API nativa sessioni)
- Routing eventi in `config/matrix.json` (6 regole)
- DocIngester (`core/doclingest.py`) — crawling documentazione con trafilatura
- Docker Compose con 3 profiles (llamacpp, localai, ollama)
- Makefile con 14 target
- Documentazione completa in `docs/` (architecture, setup, local-mode, hybrid-mode, providers, ingestion)
- Piano di lavoro dettagliato in `docs/plan/` (5 fasi)
- `docs/STATUS.md` — quadro completo della situazione
- `docs/wiki/` — wiki di conoscenza condiviso (index.md + log.md), schema in AGENTS.md

## Cosa fare dopo

Prossimo passo: **Fase 1 — Provider OpenHands API**

Vedi `docs/plan/phase-1-openhands.md` per i dettagli. In sintesi:
- Aggiungere `openhands_api` come branch in `InferenceRouter.infer()` in `core/inference.py`
- Endpoint `http://localhost:8000` con sessioni stile OpenHands agent_server
- Aggiungere entry in `config/providers.json`
- Documentare in `docs/providers.md`

## Per orientarsi

- [docs/STATUS.md](../STATUS.md) — quadro completo
- [docs/plan/README.md](README.md) — scegli fase
- [docs/plan/phase-1-openhands.md](phase-1-openhands.md) — dettagli prossima fase

```bash
# Syntax check veloce
python3 -m py_compile core/inference.py
python3 -m py_compile core/bridge.py

# Validare JSON
python3 -c "import json; json.load(open('config/providers.json')); json.load(open('config/matrix.json')); print('OK')"

# Elencare provider
make list-providers
```
