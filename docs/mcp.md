# Configurazione MCP Condivisa

## Panoramica

Il file `config/mcp_servers.json` è la fonte unica di configurazione per i server MCP
(Model Context Protocol) utilizzabili da bridge, OpenCode e OpenHands.

## Formato del File

```json
{
  "mcp_servers": [
    {
      "name": "nome-server",
      "transport": "stdio|tcp",
      "command": "comando",
      "args": ["arg1", "arg2"],
      "env": {"VAR": "valore"},
      "endpoint": "http://localhost:PORT"
    }
  ]
}
```

### Campi

| Campo | Tipo | Obbligatorio | Descrizione |
|---|---|---|---|
| `name` | string | sì | Identificativo univoco del server |
| `transport` | string | sì | `stdio` per processi locali, `tcp` per server remoti |
| `command` | string | stdio | Comando da eseguire |
| `args` | array | stdio | Argomenti del comando |
| `env` | object | no | Variabili d'ambiente (supporta `${VAR}` per env var) |
| `endpoint` | string | tcp | URL del server TCP |

## Come Usarlo

### Con OpenCode

OpenCode può importare la configurazione MCP nel suo `opencode.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    }
  }
}
```

### Con OpenHands

OpenHands accetta configurazione MCP inline o tramite `microagents/`:

```yaml
mcp_servers:
  - name: filesystem
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
```

## Variabili d'Ambiente

Le variabili nel campo `env` possono usare il formato `${VAR_NAME}` per riferirsi
a variabili d'ambiente del sistema. Esempio:

```json
{
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}"
  }
}
```

## Aggiungere un Nuovo Server MCP

1. Aggiungi un entry in `config/mcp_servers.json`
2. Per server `stdio`: specifica `command`, `args`, e opzionalmente `env`
3. Per server `tcp`: specifica `endpoint` con URL completo
4. Verifica la sintassi: `python3 -c "import json; json.load(open('config/mcp_servers.json')); print('OK')"`

## Server Disponibili

| Server | Transport | Descrizione |
|---|---|---|
| `filesystem` | stdio | Accesso al filesystem locale |
| `github` | stdio | Interazione con GitHub API |
| `nanobot` | tcp | MCP server interno con tool git/fs/db |
