# Fase 1 — Provider OpenHands API

**Obiettivo:** Aggiungere OpenHands come tipo provider in `inference.py`,
replicando il pattern già consolidato per `opencode_api`.

## Contesto

OpenHands espone un Software Agent SDK Python con REST API server
(`agent_server`) su `http://localhost:8000`. Supporta MCP nativamente come client.
Non è ancora integrato nel bridge.

## Cosa modificare

### 1. `core/inference.py`

Aggiungere branch `openhands_api` in `InferenceRouter.infer()`:

- **Endpoint:** `http://localhost:8000`
- **Creazione sessione:** `POST /api/sessions` → ottiene `session_id`
- **Invio prompt:** `POST /api/sessions/{id}/messages` con body `{"message": "...", "reset": true/false}`
- **Autenticazione:** API key via header `Authorization: Bearer <token>` (da env `OPENHANDS_API_KEY`)
- **Stessa interfaccia:** riceve `prompt` e `context`, restituisce `{"response": "...", "session_id": "..."}` o `{"error": "..."}`

Schema della risposta di `/api/sessions/{id}/messages` (da verificare):
```json
{
  "id": "...",
  "session_id": "...",
  "role": "assistant",
  "content": "...",
  "timestamp": "..."
}
```

### 2. `config/providers.json`

Aggiungere entry:

```json
"openhands_api": {
  "type": "openhands_api",
  "endpoint": "http://localhost:8000",
  "models": ["openhands-default"]
}
```

### 3. `docs/providers.md`

Aggiungere riga nella tabella Provider Supportati:

| OpenHands agent_server | openhands_api | locale |

E sezione dedicata con endpoint, autenticazione, note su MCP host.

### 4. Variabili d'ambiente (aggiornare `AGENTS.md` e `.env.example`)

| `OPENHANDS_API_KEY` | `openhands_api` | OpenHands auth |

## Verifica

```bash
python3 -m py_compile core/inference.py
PYTHONPATH=./core python core/bridge.py \
  --state /tmp/test-state \
  --workspace /tmp/test-ws \
  --config ./config \
  --event test \
  --payload "Hello" \
  --mode local \
  --provider openhands_api
```

## Commit

```
feat: add openhands_api provider type to InferenceRouter
```
