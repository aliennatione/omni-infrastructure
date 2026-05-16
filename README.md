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
| [docs/STATUS.md](docs/STATUS.md) | Quadro completo della situazione — stato, componenti, provider, roadmap |
| [docs/architecture.md](docs/architecture.md) | Architettura a 3 repository, isolamento, flusso asincrono |
| [docs/setup.md](docs/setup.md) | Configurazione token GitHub, secrets, chiavi API |
| [docs/local-mode.md](docs/local-mode.md) | Esecuzione locale con Docker Compose e LLM locali |
| [docs/hybrid-mode.md](docs/hybrid-mode.md) | Bridge su GitHub Actions + LLM locale via tunnel |
| [docs/providers.md](docs/providers.md) | Provider LLM supportati e configurazione |
| [docs/ingestion.md](docs/ingestion.md) | Crawling documentazione → knowledge base agent |
| [docs/wiki/index.md](docs/wiki/index.md) | Wiki di conoscenza — decisioni, scoperte, provider |
| [docs/plan/README.md](docs/plan/README.md) | Piano di lavoro — fasi di sviluppo |
| [AGENTS.md](AGENTS.md) | Linee guida per AI agent che operano sul codice |
| [CLAUDE.md](CLAUDE.md) | Panoramica progetto per Claude Code e agenti LLM |
| [DeepWiki](https://deepwiki.com/aliennatione/omni-infrastructure) | Documentazione automatizzata generata da Devin |

Per una panoramica completa — provider, comandi, architettura e stato dello sviluppo —
vedi [docs/STATUS.md](docs/STATUS.md).
