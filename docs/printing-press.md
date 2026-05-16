# Printing Press Integration

## Panoramica

[CLI Printing Press](https://github.com/mvanhorn/cli-printing-press) è un generatore
Go che produce CLI + MCP server da qualsiasi API. La [Printing Press Library](https://github.com/mvanhorn/printing-press-library)
contiene 82+ MCP server già pronti per API reali (Stripe, Linear, GitHub, Slack, Notion, Jira, ecc.).

## Cosa Aggiunge al Progetto

| Capacità | Descrizione |
|---|---|
| 82+ MCP server pronti | MCP server per API comuni, installabili con `go install` |
| Generazione on-demand | Creare nuovi MCP server da qualsiasi API spec, URL o HAR |
| SQLite locale + FTS5 | Ogni CLI generata ha sync locale, ricerca full-text, query SQL |
| Agent-native output | Exit codes tipizzati, `--compact`, auto-JSON, ~60-80% meno token |

## Installazione

### 1. Binario Printing Press

```bash
go install github.com/mvanhorn/cli-printing-press/v4/cmd/printing-press@latest
printing-press --version
```

### 2. MCP Server dalla Library

I server MCP rilevanti per il nostro workflow sono già in `config/mcp_servers.json`:

| Server | API | Install |
|---|---|---|
| `linear-pp-mcp` | Linear (issue tracking) | `go install .../linear/cmd/linear-pp-mcp@latest` |
| `slack-pp-mcp` | Slack (messaging) | `go install .../slack/cmd/slack-pp-mcp@latest` |
| `stripe-pp-mcp` | Stripe (pagamenti) | `go install .../stripe/cmd/stripe-pp-mcp@latest` |

Per installare tutti e tre:

```bash
go install github.com/mvanhorn/printing-press-library/library/project-management/linear/cmd/linear-pp-mcp@latest
go install github.com/mvanhorn/printing-press-library/library/productivity/slack/cmd/slack-pp-mcp@latest
go install github.com/mvanhorn/printing-press-library/library/payments/stripe/cmd/stripe-pp-mcp@latest
```

### 3. Generare un Nuovo MCP Server

Se serve un'API non nella library:

```bash
# Da nome API (se ha OpenAPI spec pubblica)
printing-press Notion

# Da URL (browser-sniff se non c'è spec)
printing-press https://api.example.com

# Da file HAR (export da DevTools)
printing-press --har ./capture.har
```

Output: `<api>-pp-cli` + `<api>-pp-mcp` nella directory `~/printing-press/library/<api>/`.

## Integrazione con Nanobot

Nanobot può chiamare i CLI della Printing Press come subprocess per operazioni
compound che le API dirette non supportano:

```python
# Esempio: query compound su Linear che l'API non supporta direttamente
import subprocess

result = subprocess.run(
    ["linear-pp-cli", "sql", "--compact",
     "SELECT i.identifier, i.title FROM issues i WHERE i.state = 'blocked'"],
    capture_output=True, text=True
)
```

## Catalogo Completo

Vedi il [catalogo completo](https://github.com/mvanhorn/printing-press-library#catalog)
per tutti gli 82+ MCP server disponibili, organizzati per categoria:

- **Developer Tools**: Docker Hub, PyPI, NVD, SEC EDGAR, Postman Explore
- **Project Management**: Linear, Jira, GitHub
- **Productivity**: Slack, Notion, Figma, Cal.com
- **Payments**: Stripe, Mercury, Kalshi, CoinGecko
- **Commerce**: Shopify, Amazon Seller, eBay, TikTok Shop
- **Travel**: FlightGoat, Airbnb, Seats.aero
- **Media**: Hacker News, Steam, Wikipedia, Substack
- **Marketing**: Google Ads, Klaviyo, Ahrefs, Product Hunt
- **E molti altri...**

## Variabili d'Ambiente

| Variabile | Serve per |
|---|---|
| `LINEAR_API_KEY` | Linear MCP server |
| `SLACK_BOT_TOKEN` | Slack MCP server |
| `STRIPE_SECRET_KEY` | Stripe MCP server |

Aggiungere a `.env` le chiavi per i server MCP che si intendono usare.

## Risorse

- [Printing Press GitHub](https://github.com/mvanhorn/cli-printing-press)
- [Printing Press Library](https://github.com/mvanhorn/printing-press-library)
- [printingpress.dev](https://printingpress.dev)
