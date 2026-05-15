# Documentation Ingestion Pipeline

Crawla documentazione tecnica e la converte in markdown per la knowledge base
dell'agente (agent-state/CONTEXT.md).

## Architettura

```
Sito web (docs, wiki, blog)
       │
       ▼
  trafilatura ──── estrazione contenuto, rimozione navbar/footer
       │
       ▼
  Markdown ────── salvato in state/docs/<fonte>/
       │
       ▼
  Indice JSON ─── state/docs-index.json (hash, date, pagine)
       │
       ▼
  CONTEXT.md ──── ricostruito con tutti i documenti
```

## Installazione

```bash
pip install -r requirements.txt  # include trafilatura
```

## Configurazione Fonti

Modifica `config/docs.json` per aggiungere siti da crawlare:

```json
{
  "sources": [
    {
      "name": "Mia Doc",
      "url": "https://docs.example.com",
      "crawl": true
    }
  ]
}
```

Opzioni:

| Campo | Tipo | Descrizione |
|---|---|---|
| `name` | string | Nome identificativo della fonte |
| `url` | string | URL principale |
| `crawl` | bool | Se `true`, trafilatura segue i link interni. Se `false`, usa solo `pages` |
| `pages` | array | Lista di URL specifici da crawlare (usato quando `crawl: false`) |

## Uso

### CLI diretta

```bash
# Crawla tutte le fonti
PYTHONPATH=./core python core/doclingest.py --state ./state --config ./config

# Crawla una fonte specifica per nome
PYTHONPATH=./core python core/doclingest.py --state ./state --config ./config \
  --source "OpenCode Docs"

# Elenca documenti crawlati
PYTHONPATH=./core python core/doclingest.py --state ./state --config ./config \
  --action list

# Ricostruisce CONTEXT.md
PYTHONPATH=./core python core/doclingest.py --state ./state --config ./config \
  --action rebuild-context
```

### Via shell script

```bash
./scripts/crawl-docs.sh --all            # Crawla tutto
./scripts/crawl-docs.sh "OpenCode Docs"  # Fonte specifica
./scripts/crawl-docs.sh --list           # Elenca
./scripts/crawl-docs.sh --rebuild-context  # Ricostruisce CONTEXT.md
```

### Via bridge (GitHub Actions)

```bash
python core/bridge.py \
  --state ./state \
  --workspace ./workspace \
  --config ./config \
  --event doc_ingestion \
  --payload "__all__"
```

## Output

Dopo il crawling, la struttura in `state/` sarà:

```
state/
├── CONTEXT.md              ← Knowledge base completa (auto-generata)
├── docs-index.json         ← Indice delle fonti crawlate
└── docs/
    ├── opencode_docs/
    │   ├── index.md
    │   └── opencode_ai_docs_config.md
    └── docker_docs/
        └── index.md
```

## Esempio: Aggiungere una Documentazione

```bash
# 1. Aggiungi la fonte in config/docs.json
# 2. Crawla
./scripts/crawl-docs.sh "Mia Doc"
# 3. Il contenuto finisce in CONTEXT.md automaticamente
# 4. L'agente avrà il contesto al prossimo ciclo
```

## Troubleshooting

**Errore: "trafilatura non installato"**
Esegui `pip install -r requirements.txt`.

**Nessun contenuto estratto**
Alcuni siti richiedono JavaScript. Usa `crawl: true` per abilitare il crawling
base, o considera strumenti aggiuntivi come crawl4ai per siti SPA.

**Rate limiting**
Aggiungi delay tra le richieste se crawli molti documenti.
