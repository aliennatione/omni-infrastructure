# Piano di Lavoro — Omni-Agent Infrastructure

Questo documento traccia le fasi di sviluppo pianificate per l'infrastruttura,
in modo da poter interrompere e riprendere la sessione in qualsiasi momento.

## Workflow consigliato

```
Leggi docs/wiki/index.md → Leggi questo file → Scegli una fase → Leggi il file dettaglio → Implementa → Aggiorna wiki → Commit
```

Dopo ogni implementazione, aggiorna il wiki:
- Aggiungi pagine per decisioni o scoperte (vedi [AGENTS.md](../../AGENTS.md#wiki-maintenance-llm-wiki-pattern))
- Aggiorna `docs/wiki/index.md` se necessario
- Scrivi in `docs/wiki/log.md`

## Fasi

| # | Nome | File | Priorità | Dipende da |
|---|------|------|----------|------------|
| 1 | Provider OpenHands API | [phase-1-openhands.md](phase-1-openhands.md) | Alta | — |
| 2 | Config MCP condivisa | [phase-2-mcp-config.md](phase-2-mcp-config.md) | Alta | — |
| 3 | Nanobot MCP server | [phase-3-nanobot.md](phase-3-nanobot.md) | Media | Fase 2 |
| 4 | Trigger locali (cron/systemd) | [phase-4-local-triggers.md](phase-4-local-triggers.md) | Media | — |
| 5 | Integrazione NanoClaw | [phase-5-nanoclaw.md](phase-5-nanoclaw.md) | Bassa | Fase 1 |

## Come riprendere

0. Leggi **[resume.md](resume.md)** — contesto immediato, stato git, prossimo passo
1. `git log --oneline -3` — vedi ultimi commit
2. `git status` — vedi working tree
3. Leggi `docs/plan/README.md` — scegli prossima fase
4. Leggi il file dettaglio della fase scelta
5. Implementa e committa

## Legenda priorità

- **Alta** — Bloccante per altre fasi o per funzionalità core
- **Media** — Funzionalità importante ma non blocca nulla
- **Bassa** — Nice-to-have, può aspettare
