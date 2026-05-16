# Fase 2 — Config MCP condivisa

**Obiettivo:** Creare `config/mcp_servers.json` come fonte unica di
configurazione per server MCP, referenziabile da bridge, OpenCode e OpenHands.

## Contesto

Attualmente ogni tool/configura i propri MCP server separatamente.
Una config centralizzata permette di:
- Aggiungere un server MCP una volta sola
- Bridge può leggere la lista per esporre tool agli agent
- OpenCode e OpenHands possono importare la stessa config

## Cosa creare

### 1. `config/mcp_servers.json`

Formato proposto:

```json
{
  "mcp_servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
      "env": {}
    },
    {
      "name": "github",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  ]
}
```

### 2. `docs/mcp.md`

Documentare:
- Formato del file
- Come usarlo con OpenCode (`opencode.json` o `mcpServers` in config)
- Come usarlo con OpenHands (config inline o `microagents/`)
- Variabili d'ambiente
- Procedura per aggiungere un nuovo server MCP

## Cosa modificare

### 3. `docs/providers.md`

Aggiungere sezione o reference a `docs/mcp.md`.

### 4. `README.md`

Aggiungere riga nella tabella documentazione:

| [docs/mcp.md](docs/mcp.md) | Configurazione MCP server condivisa |

## Verifica

```bash
python3 -c "import json; json.load(open('config/mcp_servers.json')); print('OK')"
```

## Commit

```
feat: add shared MCP server configuration
```
