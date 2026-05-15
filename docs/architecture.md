# Architettura

## Principio di Isolamento

Il sistema si basa sulla separazione dei compiti a livello di filesystem.
Tre repository Git distinti prevengono loop di auto-modifica, isolano dati
sensibili e garantiscono un audit trail lineare.

```
┌─────────────────────────────────────────────────────┐
│                    GitHub Actions                    │
│  ┌──────────────────────────────────────────────┐   │
│  │              omni-infrastructure             │   │
│  │  Control Plane: bridge, config, CI/CD        │   │
│  │                                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ bridge   │  │ inference│  │ config   │  │   │
│  │  │ .py      │  │ .py      │  │ .json    │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  │   │
│  └──────────────────┬───────────────────────────┘   │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐   │
│  │               agent-state                    │   │
│  │  Memory Plane: CONTEXT.md, journal/          │   │
│  │  (append-only logs)                          │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              project-source                  │   │
│  │  Data Plane: codice applicativo              │   │
│  │  (modificato solo via Pull Request)          │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Flusso di Esecuzione

```
┌──────────┐     ┌──────────────┐     ┌────────────┐
│  Trigger │────►│   Bridge     │────►│   LLM      │
│ (cron /  │     │  (bridge.py) │     │ (Gemini /  │
│  manual) │     │              │     │  locale)   │
└──────────┘     └──────┬───────┘     └────────────┘
                        │
               ┌────────▼────────┐
               │   Risultato     │
               ├─────────────────┤
               │ 1. Journal      │
               │ 2. PR su        │
               │    project-     │
               │    source       │
               │ 3. Sync memory  │
               └─────────────────┘
```

## Tre Repository in Dettaglio

### 1. omni-infrastructure (Control Plane)
Contiene la logica di orchestrazione:
- `core/bridge.py` — dispatcher degli eventi
- `core/inference.py` — router verso i provider LLM
- `config/providers.json` — definizione dei provider
- `config/matrix.json` — routing rules (evento → provider)
- `.github/workflows/omni-engine.yml` — pipeline CI/CD

### 2. agent-state (Memory Plane)
Memoria persistente dell'agente:
- `CONTEXT.md` — direttive di sistema e contesto globale
- `journal/YYYY-MM-DD.log` — log operativi append-only

### 3. project-source (Data Plane)
Codice applicativo su cui l'agente opera.
Tutte le modifiche sono sottoposte via Pull Request — mai su main diretto.

## Modelli di Esecuzione

| Modalità | Bridge | LLM | Attivazione |
|---|---|---|---|
| Cloud | GitHub Actions | Google Gemini API | `--mode cloud` (default) |
| Locale | Macchina locale | llama.cpp/Ollama/etc. | `--mode local` |
| Ibrido | GitHub Actions | LLM locale via tunnel | `--mode local` + tunnel |
