# Omni-Agent Infrastructure

Orchestratore GitOps multi-agent asincrono con inferenza distribuita.
Supporta Google Gemini, LLM locali (llama.cpp, Ollama, LocalAI), OpenCode e OpenHands.

## Quick Start

```bash
# Setup
pip install -r requirements.txt
make setup          # crea state/ e workspace/

# Esecuzione locale
make run PROVIDER=local_llamacpp EVENT=git_automation PAYLOAD="Refactor"

# Con Docker
make up-llamacpp    # avvia llama.cpp + bridge
make logs
make down
```

## Repository Structure

```
core/bridge.py       # Orchestratore CLI (entrypoint)
core/inference.py    # Router LLM (6 tipi provider)
core/doclingest.py   # Crawler documentazione
config/providers.json    # 6 provider dichiarati
config/matrix.json       # Regole routing evento → provider
docs/STATUS.md           # Quadro completo del progetto
docs/wiki/index.md       # Wiki di conoscenza (decisioni, scoperte, provider)
docs/wiki/log.md         # Log cronologico wiki
docs/plan/README.md      # Fasi di sviluppo
```

## Provider

| Nome | Tipo |
|------|------|
| `google_gemini_flash` | Google Gemini Flash cloud |
| `google_gemini_pro` | Google Gemini Pro cloud |
| `local_llamacpp` | llama.cpp su :8080 |
| `local_localai` | LocalAI su :8081 |
| `local_ollama` | Ollama su :11434 |
| `local_opencode` | OpenCode su :4096 |
| `openhands_api` | OpenHands su :8000 (TODO) |

## Comandi frequenti

```bash
make list-providers              # elenca provider
python3 -m py_compile core/*.py  # syntax check
python3 -m py_compile core/inference.py
python3 -c "import json; json.load(open('config/providers.json')); json.load(open('config/matrix.json')); print('OK')"
```

## Documentazione completa

Per convenzioni di codice, stile, CI/CD e regole di sicurezza,
vedi [AGENTS.md](AGENTS.md).

Per la manutenzione del wiki (LLM Wiki Pattern) — index, log, ingest, query, lint —
vedi sezione "Wiki Maintenance" in [AGENTS.md](AGENTS.md).

Per lo stato aggiornato del progetto, vedi [docs/STATUS.md](docs/STATUS.md).
