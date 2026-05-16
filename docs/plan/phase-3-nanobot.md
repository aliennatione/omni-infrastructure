# Fase 3 — Nanobot MCP Server

**Obiettivo:** Implementare un piccolo MCP server Python in
`core/nanobot_mcp.py` che espone tool git, filesystem, db,
utilizzabile da bridge, OpenCode e OpenHands.

**Dipende da:** Fase 2 (config MCP condivisa)

## Contesto

Nanobot è pensato come un server MCP leggero che fornisce operazioni
di base (git, filesystem, db SQLite) agli agent AI nel cluster.
Deve essere compatibile con il protocollo MCP (Model Context Protocol).

## Cosa creare

### 1. `core/nanobot_mcp.py`

Server MCP usando `mcp` Python SDK (`pip install mcp`):

```python
# Schema concettuale
class NanobotMCPServer:
    tools = {
        "git_status": git_status_handler,
        "git_diff": git_diff_handler,
        "git_commit": git_commit_handler,
        "fs_read": fs_read_handler,
        "fs_write": fs_write_handler,
        "db_query": db_query_handler,
    }

    def run(self):
        # Avvia server MCP su stdio o TCP
        pass
```

Tool previsti:
- **Git:** `status`, `diff`, `log`, `commit`, `branch_create`, `push`
- **Filesystem:** `read`, `write`, `list_dir`, `glob`
- **Database:** `query` (SQLite su `state/journal.db`)

### 2. Docker Compose profile

Aggiungere profile `nanobot` in `docker-compose.yml`:

```yaml
nanobot:
  profiles: ["nanobot"]
  build:
    context: .
    dockerfile: Dockerfile.nanobot
  ports:
    - "4097:4097"
  volumes:
    - ../agent-state:/state:ro
    - ../project-source:/workspace:rw
```

### 3. `Dockerfile.nanobot`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.nanobot.txt .
RUN pip install -r requirements.nanobot.txt
COPY core/nanobot_mcp.py .
CMD ["python", "nanobot_mcp.py"]
```

### 4. `requirements.nanobot.txt`

```
mcp>=1.0.0
```

### 5. `config/mcp_servers.json`

Aggiungere Nanobot alla lista (dopo Fase 2):

```json
{
  "name": "nanobot",
  "transport": "tcp",
  "endpoint": "http://localhost:4097"
}
```

### 6. `docs/nanobot.md`

Documentare tool disponibili, configurazione, esempi d'uso.

## Verifica

```bash
python3 core/nanobot_mcp.py --help
# o in container:
make up-nanobot
make logs nanobot
```

## Commit

```
feat: add Nanobot MCP server with git/fs/db tools
```
