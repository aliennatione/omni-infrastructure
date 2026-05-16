# Fase 6 — Automated Tests + Multi-Platform Gateway + Streaming

Tre blocchi indipendenti, sviluppabili in parallelo dopo setup iniziale.

## Setup iniziale (5 min)

```bash
pip install pytest pytest-mock responses matrix-nio
```

Aggiornare `requirements.txt`:
```
requests>=2.31.0
trafilatura>=2.0.0
pytest>=7.0.0
pytest-mock>=3.10.0
responses>=0.23.0
matrix-nio>=0.25.0
```

Aggiungere a `Makefile`:
```makefile
test:
	python3 -m pytest tests/ -v --tb=short
```

---

## Blocco 6A — Automated Tests

### Obiettivo

Copertura test per tutti i moduli core. Mock HTTP per evitare chiamate reali.

### Files da creare

#### `tests/conftest.py`
- Fixture `tmp_state_dir` — temp directory con CONTEXT.md finto
- Fixture `tmp_workspace_dir` — temp directory vuota
- Fixture `config_dir` — path a `./config`
- Fixture `bridge` — OmniBridge istanziata con temp dirs
- Fixture `mock_providers` — dict provider fittizi per InferenceRouter
- Fixture `router` — InferenceRouter con mock_providers

#### `tests/test_bridge.py`
- `test_resolve_event_valid` — evento esistente in matrix.json
- `test_resolve_event_invalid` — ValueError per evento sconosciuto
- `test_load_event_prompt_exists` — carica small_fix.json
- `test_load_event_prompt_missing` — ritorna None
- `test_build_system_prompt_with_event` — prompt con behavior rules
- `test_build_system_prompt_without_event` — fallback generico
- `test_build_system_prompt_compact` — caveman mode + event prompt
- `test_compress_context_truncate_long_lines` — linee >200 chars troncate
- `test_compress_context_skip_html_comments` — `<!-- -->` rimossi
- `test_compress_context_deduplicate_blanks` — blank lines consecutive ridotte

#### `tests/test_inference.py`
- `test_google_api_success` — mock 200 con risposta Gemini
- `test_google_api_missing_key` — errore GEMINI_API_KEY
- `test_google_api_error` — mock 500
- `test_openai_compat_success` — mock 200 con risposta OpenAI
- `test_openai_compat_error` — mock 500
- `test_opencode_api_success` — mock session create + message + delete
- `test_opencode_api_auth` — Basic auth headers
- `test_openhands_api_success` — mock session create + messages + delete
- `test_openhands_api_missing_key` — senza OPENHANDS_API_KEY (opzionale)
- `test_connection_refused_hint` — hint "make up-llamacpp" su connection refused
- `test_provider_not_found` — ValueError per provider sconosciuto
- `test_unsupported_provider_type` — NotImplementedError

#### `tests/test_nanobot_mcp.py`
- `test_git_status` — mock subprocess git status
- `test_git_diff` — mock subprocess git diff
- `test_fs_read` — lettura file finto
- `test_fs_write` — scrittura file finto
- `test_fs_list_dir` — listing directory finta
- `test_fs_glob` — glob pattern matching
- `test_db_query` — query SQLite finto

#### `tests/test_doclingest.py`
- `test_crawl_source` — mock HTTP con HTML finto
- `test_ingest_all` — mock config/docs.json sources
- `test_rebuild_context` — CONTEXT.md creato/aggiornato
- `test_crawl_no_crawl_flag` — source senza crawl=True ignorato

#### `tests/test_nanoclaw_gateway.py`
- `test_handle_message` — messaggio finto, risposta da bridge
- `test_call_bridge_success` — subprocess.run con returncode 0
- `test_call_bridge_error` — subprocess.run con returncode != 0
- `test_missing_telegram_token` — sys.exit(1) senza TELEGRAM_TOKEN

### Strategia mock

- `responses` library per intercettare `requests.post`/`requests.get`
- `pytest-mock` per `mocker.patch` su subprocess, os, etc.
- Zero chiamate di rete reali
- Temp directory per state/workspace (isolamento test)

---

## Blocco 6B — Multi-Platform Gateway (Matrix)

### Obiettivo

Refactor NanoClaw per supportare Matrix come backend di messaggistica.
Matrix funge da hub: bridge ufficiali per Telegram, Signal, WhatsApp, Discord, Slack.

### Architettura

```
MessagingBackend (ABC)
├── TelegramBackend (ex nanoclaw_gateway.py, refactored)
└── MatrixBackend (nuovo, matrix-nio)

GatewayRunner
├── __init__(backend, config_dir, state_dir, workspace_dir)
├── run() → backend.poll() in loop
├── handle_message(msg, chat_id) → call_bridge(msg) → backend.send(chat_id, reply)
└── call_bridge(message, provider, mode) → subprocess.run(bridge.py)
```

### Files da creare/modificare

#### `core/gateway_base.py` (nuovo, ~150 righe)
```python
class MessagingBackend(ABC):
    @abstractmethod
    def poll(self):
        """Return list of (chat_id, text) tuples."""
        pass

    @abstractmethod
    def send(self, chat_id, text):
        """Send text response to chat_id."""
        pass

    @abstractmethod
    def start(self):
        """Initialize connection."""
        pass

class GatewayRunner:
    def __init__(self, backend, config_dir, state_dir, workspace_dir):
        self.backend = backend
        self.config_dir = config_dir
        self.state_dir = state_dir
        self.workspace_dir = workspace_dir
        self.default_provider = os.environ.get("NANOCLAW_PROVIDER", "local_openhands")
        self.default_mode = os.environ.get("NANOCLAW_MODE", "local")

    def call_bridge(self, message, provider=None, mode=None):
        # subprocess.run([bridge.py, --event, chat_message, --payload, message, ...])
        ...

    def handle_message(self, text, chat_id):
        response = self.call_bridge(text)
        self.backend.send(chat_id, response[:4096])

    def run(self):
        self.backend.start()
        while True:
            events = self.backend.poll()
            for chat_id, text in events:
                self.handle_message(text, chat_id)
```

#### `core/gateway_matrix.py` (nuovo, ~150 righe)
```python
class MatrixBackend(MessagingBackend):
    def __init__(self):
        self.homeserver = os.environ.get("MATRIX_HOMESERVER", "https://matrix.org")
        self.user = os.environ.get("MATRIX_USER", "")
        self.password = os.environ.get("MATRIX_PASSWORD", "")
        self.room_id = os.environ.get("MATRIX_ROOM_ID", "")
        self.device_id = os.environ.get("MATRIX_DEVICE_ID", "omni-agent")

    def start(self):
        # matrix-nio AsyncClient login
        ...

    def poll(self):
        # sync_messages, return (room_id, text) tuples
        ...

    def send(self, room_id, text):
        # room_send(room_id, text)
        ...
```

#### `core/nanoclaw_gateway.py` (refactor, ~80 righe dopo)
```python
class TelegramBackend(MessagingBackend):
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0

    def start(self):
        pass

    def poll(self):
        # getUpdates, return (chat_id, text) tuples
        ...

    def send(self, chat_id, text):
        # sendMessage
        ...
```

#### `core/__init__.py` (modificare)
Aggiungere export per gateway_base, gateway_matrix.

#### `.env.example` (modificare)
Aggiungere:
```
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER=your-matrix-user
MATRIX_PASSWORD=your-matrix-password
MATRIX_ROOM_ID=!room:matrix.org
MATRIX_DEVICE_ID=omni-agent
```

#### `docs/mobile.md` (modificare)
Aggiungere sezione Matrix: setup, configurazione, bridge Matrix → altre piattaforme.

### Perché Matrix

- Protocollo aperto, self-hostable
- Client ufficiali: Element (mobile, desktop, web)
- Bridge ufficiali: Telegram, Signal, WhatsApp, Discord, Slack, IRC, XMPP
- Una implementazione → accesso a TUTTE le piattaforme via bridge
- E2EE opzionale
- matrix-nio: libreria Python matura, async-ready

---

## Blocco 6C — Streaming Support

### Obiettivo

Aggiungere supporto streaming per provider che lo supportano (google_api, openai_compat).
Stampa tokens in real-time durante l'esecuzione.

### Files da modificare

#### `core/inference.py` (~100 righe aggiunte)

Aggiungere metodo `stream(provider_name, prompt)` a `InferenceRouter`:
- Per `google_api`: endpoint `streamGenerateContent`, parse SSE chunks
- Per `openai_compat`: `"stream": True` nel payload, parse `data: {...}` lines
- Per `opencode_api`/`openhands_api`: wrapper generator (no streaming reale, interfaccia uniforme)

```python
def stream(self, provider_name, prompt):
    """Yield text chunks as they arrive from the LLM."""
    provider = self.providers.get(provider_name)
    if not provider:
        raise ValueError(...)
    ptype = provider["type"]
    if ptype == "google_api":
        yield from self._stream_google_api(provider["endpoint"], prompt)
    elif ptype == "openai_compat":
        yield from self._stream_openai_compat(...)
    # ...
```

#### `core/bridge.py` (~30 righe aggiunte)

Aggiungere flag `--stream`:
```python
parser.add_argument("--stream", action="store_true",
                    help="Stampa tokens in real-time durante l'inferenza")
```

Nel dispatch:
```python
if args.stream:
    full_response = ""
    for chunk in self.router.stream(provider, prompt):
        print(chunk, end="", flush=True)
        full_response += chunk
    print()
    # journal con full_response
else:
    result = self.router.run(provider, prompt)
```

### Test (in tests/test_inference.py)

- `test_stream_openai_compat` — mock SSE response con chunks
- `test_stream_google_api` — mock streamGenerateContent
- `test_stream_opencode_api` — wrapper generator (no streaming reale)

---

## Verifica finale

```bash
make test
python3 -m py_compile core/bridge.py
python3 -m py_compile core/inference.py
python3 -m py_compile core/gateway_base.py
python3 -m py_compile core/gateway_matrix.py
python3 -c "import json; json.load(open('config/providers.json')); json.load(open('config/matrix.json')); print('OK')"
```
