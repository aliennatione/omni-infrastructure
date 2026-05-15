# Omni-Agent Infrastructure — AGENTS.md

This file is consumed by AI coding agents operating on the `omni-infrastructure` repository.
It describes the project structure, conventions, and available commands.

## Project Overview

Omni-Agent Infrastructure is a GitOps multi-agent orchestration system.
It runs an inference bridge (`core/bridge.py`) that routes tasks to LLM providers
(Google Gemini cloud or local models via llama.cpp/Ollama/LocalAI/OpenCode),
manages three isolated Git repositories, and operates on a 4-hour cron cycle via GitHub Actions.

## Architecture

Three-repository isolation model:

| Repository | Role | Visibility |
|---|---|---|
| `omni-infrastructure` | Control plane — bridge, config, CI/CD | Public/Private |
| `agent-state` | Memory plane — context, journal (append-only logs) | Private |
| `project-source` | Data plane — application code modified via PRs | Private |

## Build / Run / Lint / Test Commands

### Python environment
```bash
pip install -r requirements.txt
```

### Run locally (without Docker)
```bash
PYTHONPATH=./core python core/bridge.py \
  --state ../agent-state \
  --workspace ../project-source \
  --config ./config \
  --event git_automation \
  --payload "Routine check" \
  --mode local
```

### Run with Docker Compose (full stack)
```bash
make setup         # create state/ and workspace/ directories
make up            # docker compose up -d (llama-server + omni-bridge)
make logs          # tail -f logs
make down          # docker compose down
make pull-model    # download a GGUF model into ./models/
make shell         # interactive bash in omni-bridge container
```

### Syntax check (no test framework yet)
```bash
python3 -m py_compile core/inference.py
python3 -m py_compile core/bridge.py
```

### Validate JSON configs
```bash
python3 -c "import json; json.load(open('config/providers.json')); json.load(open('config/matrix.json')); print('OK')"
```

### Single test (manual integration)
```bash
# Requires opencode serve running on localhost:4096
mkdir -p /tmp/test-state /tmp/test-ws
python3 core/bridge.py \
  --state /tmp/test-state \
  --workspace /tmp/test-ws \
  --config ./config \
  --event opencode_inference \
  --payload "Hello, what is 2+2?" \
  --mode local
```

## Code Style Guidelines

### Imports
- Standard library first (`os`, `sys`, `json`, `argparse`, `datetime`, `base64`)
- Third-party libraries second (`requests`)
- Relative imports for sibling modules (`from inference import InferenceRouter`)
- One import per line; `import` blocks separated by blank line
- Never use `import` inside function/method bodies — always at module level

### Formatting & Types
- Python 3.11+ — no type annotations currently used, prefer descriptive names instead
- 4-space indentation, no tabs
- Max line length: 100 characters (informal)
- No trailing whitespace; final newline at EOF
- Double quotes for strings (`"`) except when single quotes are nested

### Naming conventions
- `PascalCase` for classes (`InferenceRouter`, `OmniBridge`)
- `snake_case` for functions, methods, variables (`google_api`, `resolve_event`)
- `UPPER_SNAKE_CASE` for env-var-derived constants
- JSON config keys in `snake_case`
- File names in `snake_case` (`.py`, `.json`, `.yml`, `.sh`)
- Git branch prefix: `agent/run-{RUN_ID}`

### Error handling
- Use `raise ValueError(...)` for invalid configuration/missing providers
- Use `raise NotImplementedError(...)` for unsupported provider types
- Use `try/except` in I/O and network code; wrap with `sys.exit(1)` in CLI entry points
- Network errors in `opencode_api` / `openai_compat` return `{"error": ...}` dict (do not raise)
- Prefixed log messages: `[*]` for info, `[-]` for errors, `[+]` for success
- Remote API calls must always check `response.raise_for_status()`

### Config conventions
- `providers.json` declares available LLM providers with `type`, `endpoint`, `model`
- `matrix.json` maps event types → provider + mode
- Provider types: `google_api`, `openai_compat`, `opencode_api`
- Environment variables override config at runtime (`LLM_PROVIDER`, `LLM_ENDPOINT_URL`)

### Environment variables
| Variable | Used by | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | `google_api` | Google Gemini auth |
| `LLM_MODE` | `bridge.py --mode` | `cloud` or `local` |
| `LLM_PROVIDER` | `bridge.py` | Override provider name |
| `LLM_ENDPOINT_URL` | `bridge.py` | Override provider endpoint |
| `LLM_API_KEY` | `openai_compat` | Local LLM API key |
| `OPENCODE_SERVER_PASSWORD` | `opencode_api` | Basic auth for opencode serve |
| `OPENCODE_SERVER_USERNAME` | `opencode_api` | Basic auth user (default: opencode) |
| `STATE_REPO_PAT` | GitHub Actions | Access agent-state repo |
| `SOURCE_REPO_PAT` | GitHub Actions | Access project-source repo |

### Docker conventions
- Base image: `python:3.11-slim`
- `ENV PYTHONPATH=/app/core` for module resolution
- `requirements.txt` installed before copying source for layer caching
- Entrypoint: `python core/bridge.py` with CLI args via `command` in compose

### Shell scripts
- `scripts/tunnel.sh` exposes llama.cpp via ngrok or tailscale
- Use `set -e`, `command -v` for dependency checks
- Prefixed messages matching Python style (`[*]`, `[-]`)
- `snake_case` for variable names

### CI/CD (GitHub Actions)
- Workflow: `.github/workflows/omni-engine.yml`
- Triggers: cron `0 */4 * * *` + `workflow_dispatch` with `event_type`, `payload`, `mode` inputs
- Three checkout steps (infra, state, workspace)
- Python 3.11, install deps, run bridge, create PR in project-source, sync agent-state
- Secrets: `GEMINI_API_KEY`, `STATE_REPO_PAT`, `SOURCE_REPO_PAT`, `LLM_ENDPOINT_URL`, `LLM_PROVIDER`

### Security rules
- Never hardcode API keys or PATs in source files
- Use env vars at runtime (os.environ.get) or GitHub secrets in CI
- Append-only journal (never overwrite log files)
- PR-based workflow: agent never pushes directly to main in project-source
