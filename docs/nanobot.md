# Nanobot MCP Server

## Panoramica

Nanobot è un server MCP leggero che espone tool per operazioni di base
(git, filesystem, db SQLite) agli agent AI nel cluster.

## Tool Disponibili

### Git

| Tool | Descrizione | Parametri |
|---|---|---|
| `git_status` | Mostra lo stato del working tree | `repo_path` (default: ".") |
| `git_diff` | Mostra le modifiche | `repo_path`, `target` (opzionale) |
| `git_log` | Mostra i commit recenti | `repo_path`, `n` (default: 10) |
| `git_commit` | Registra le modifiche | `repo_path`, `message` |
| `git_branch_create` | Crea un nuovo branch | `repo_path`, `branch_name` |
| `git_push` | Pusha al remote | `repo_path`, `remote` (default: "origin"), `branch` |

### Filesystem

| Tool | Descrizione | Parametri |
|---|---|---|
| `fs_read` | Legge un file | `file_path` |
| `fs_write` | Scrive un file | `file_path`, `content` |
| `fs_list_dir` | Lista una directory | `dir_path` (default: ".") |
| `fs_glob` | Cerca file con pattern glob | `pattern`, `root` (default: ".") |

### Database

| Tool | Descrizione | Parametri |
|---|---|---|
| `db_query` | Esegue query SQL su SQLite | `db_path`, `query` |

## Configurazione

### Docker Compose

```bash
make up-nanobot   # avvia il profilo nanobot
make logs         # vedi i log
```

### Esecuzione Locale

```bash
pip install -r requirements.nanobot.txt

# Via stdio (per subprocess)
python core/nanobot_mcp.py

# Via HTTP
python core/nanobot_mcp.py --transport streamable-http --port 4097
```

### Integrazione con MCP Config

Nanobot è già incluso in `config/mcp_servers.json`:

```json
{
  "name": "nanobot",
  "transport": "tcp",
  "endpoint": "http://localhost:4097"
}
```

## Esempi d'Uso

### Controllare lo stato git

```
Tool: git_status
Args: {"repo_path": "/workspace"}
```

### Leggere un file

```
Tool: fs_read
Args: {"file_path": "/workspace/src/main.py"}
```

### Query sul journal

```
Tool: db_query
Args: {"db_path": "/state/journal.db", "query": "SELECT * FROM entries LIMIT 10"}
```
