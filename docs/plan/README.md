# Piano di Lavoro — Omni-Agent Infrastructure

Questo documento traccia le fasi di sviluppo pianificate per l'infrastruttura,
in modo da poter interrompere e riprendere la sessione in qualsiasi momento.

## Workflow consigliato

```
Leggi docs/wiki/index.md → Leggi questo file → Scegli una fase → Leggi il file dettaglio → Implementa → Aggiorna wiki → Commit
```

Dopo ogni implementazione:
- Aggiungi pagine per decisioni o scoperte in `docs/wiki/`
- Aggiorna `docs/wiki/index.md` se necessario
- Scrivi in `docs/wiki/log.md`
- Commit con messaggio descrittivo

## Fasi completate

| # | Nome | File | Priorità | Dipende da | Stato |
|---|------|------|----------|------------|-------|
| 1 | Provider OpenHands API | [phase-1-openhands.md](phase-1-openhands.md) | Alta | — | ✅ Completato |
| 2 | Config MCP condivisa | [phase-2-mcp-config.md](phase-2-mcp-config.md) | Alta | — | ✅ Completato |
| 3 | Nanobot MCP server | [phase-3-nanobot.md](phase-3-nanobot.md) | Media | Fase 2 | ✅ Completato |
| 4 | Trigger locali (cron/systemd) | [phase-4-local-triggers.md](phase-4-local-triggers.md) | Media | — | ✅ Completato |
| 5 | Integrazione NanoClaw | [phase-5-nanoclaw.md](phase-5-nanoclaw.md) | Bassa | Fase 1 | ✅ Completato |
| — | Integrazione Caveman | — | Alta | — | ✅ Completato |
| — | Integrazione Printing Press | — | Media | Fase 2 | ✅ Completato |
| — | Analisi BMAD (rifiutato) | [wiki/discovery/bmad-analysis.md](../wiki/discovery/bmad-analysis.md) | — | — | ✅ Completato |
| — | Per-event system prompts | — | Alta | — | ✅ Completato |
| — | Wiki population | — | Media | — | ✅ Completato |

## Fasi in corso

| # | Nome | File | Priorità | Dipende da | Stato |
|---|------|------|----------|------------|-------|
| 6A | Automated tests | [phase-6-automation.md](phase-6-automation.md) | Alta | — | 🔄 In corso |
| 6B | Multi-platform gateway (Matrix) | [phase-6-automation.md](phase-6-automation.md) | Alta | 6A (parziale) | 🔄 In corso |
| 6C | Streaming support | [phase-6-automation.md](phase-6-automation.md) | Media | 6A | 🔄 In corso |

## Possibili fasi future

| # | Nome | File | Priorità | Dipende da | Stato |
|---|------|------|----------|------------|-------|
| 7 | Pi integration note | [pi-integration-note.md](pi-integration-note.md) | Bassa | — | 📋 Pianificato |
| 8 | Signal gateway | — | Bassa | 6B | ⏳ Da fare |
| 9 | Automated test CI | — | Media | 6A | ⏳ Da fare |

## Come riprendere

0. Leggi **[resume.md](resume.md)** — contesto immediato, stato git, prossimo passo
1. `git log --oneline -5` — vedi ultimi commit
2. `git status` — vedi working tree
3. Leggi `docs/plan/README.md` — scegli prossima fase
4. Leggi il file dettaglio della fase scelta
5. Implementa, aggiorna wiki, committa

## Legenda priorità

- **Alta** — Bloccante per altre fasi o per funzionalità core
- **Media** — Funzionalità importante ma non blocca nulla
- **Bassa** — Nice-to-have, può aspettare
