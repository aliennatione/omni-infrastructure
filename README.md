# Omni-Agent Infrastructure

Orchestratore GitOps multi-agent asincrono con inferenza distribuita.
Supporta Google Gemini, LLM locali (llama.cpp, Ollama, LocalAI) e OpenCode.

## Quick Start

### 1. Prerequisiti
- Python 3.11+, Docker + Docker Compose (opzionale)
- Un account GitHub e tre repository: `omni-infrastructure`, `agent-state`, `project-source`

### 2. Setup rapido
```bash
git clone <your-repo-url>
cd omni-infrastructure
pip install -r requirements.txt

# Crea le directory per i volumi Docker (se usi Docker)
make setup
```

### 3. Avvia con Docker (locale)
```bash
# In ./models/ metti un modello GGUF (es. llama-2-7b.Q4_K_M.gguf)
make pull-model   # oppure scaricalo manualmente
make up           # docker compose up -d
make logs         # per vedere i log
```

### 4. Avvia senza Docker (locale)
```bash
PYTHONPATH=./core python core/bridge.py \
  --state ../agent-state \
  --workspace ../project-source \
  --config ./config \
  --event git_automation \
  --payload "Routine check" \
  --mode local
```

### 5. Configura su GitHub Actions
Vedi [docs/setup.md](docs/setup.md) per token, secrets e deploy CI/CD.

## Documentazione

| Documento | Contenuto |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Architettura a 3 repository, isolamento, flusso asincrono |
| [docs/setup.md](docs/setup.md) | Configurazione token GitHub, secrets, chiavi API |
| [docs/local-mode.md](docs/local-mode.md) | Esecuzione locale con Docker Compose e LLM locali |
| [docs/hybrid-mode.md](docs/hybrid-mode.md) | Bridge su GitHub Actions + LLM locale via tunnel |
| [docs/providers.md](docs/providers.md) | Provider LLM supportati e configurazione |
| [docs/ingestion.md](docs/ingestion.md) | Crawling documentazione → knowledge base agent |
| [AGENTS.md](AGENTS.md) | Linee guida per AI agent che operano sul codice |
| [DeepWiki](https://deepwiki.com/aliennatione/omni-infrastructure) | Documentazione automatizzata generata da Devin |

## Provider Supportati

| Provider | Tipo | Modalità |
|---|---|---|
| Google Gemini Flash | cloud | default per task piccoli |
| Google Gemini Pro | cloud | default per refactor complessi |
| llama.cpp (locale) | locale | via `local_llamacpp` |
| Ollama (locale) | locale | via `local_ollama` |
| LocalAI (locale) | locale | via `local_localai` |
| OpenCode serve | locale | via `local_opencode` |

## Repository del sistema

| Repository | Ruolo | Visibilità |
|---|---|---|
| `omni-infrastructure` | Control plane — bridge, config, CI/CD | Pubblico/Privato |
| `agent-state` | Memory plane — contesto, journal | Privato |
| `project-source` | Data plane — codice applicativo | Privato |

## Comandi utili

```bash
make setup      # crea state/ e workspace/
make up         # avvia llama-server + omni-bridge
make down       # ferma tutto
make logs       # log in tempo reale
make shell      # shell interattiva nel container bridge
make pull-model # scarica un modello GGUF
```
