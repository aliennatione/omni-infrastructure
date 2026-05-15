# Setup e Configurazione

## 1. Repository GitHub

Crea tre repository su GitHub:

```bash
# 1. Control Plane (questo repo)
gh repo create omni-infrastructure --public --clone

# 2. Agent State (privato)
gh repo create agent-state --private --clone

# 3. Project Source (privato)
gh repo create project-source --private --clone
```

Popola `agent-state` con un file `CONTEXT.md` iniziale:

```markdown
# Omni-Agent Core Directives
## Identity
You are the active control loop of the Omni-Agent infrastructure.
Your goal is to maintain, refactor, and improve the software stack
located in the `project-source` repository.
## Rules
1. Never hardcode secrets or credentials.
2. Provide clean, modular and commented code.
3. You DO NOT modify the infrastructure orchestration code.
4. Always document your architectural decisions in the journal.
```

## 2. Token GitHub (PAT)

Genera due Personal Access Token (classic) da
**Settings → Developer Settings → Personal Access Tokens → Tokens (classic)**.

Scopo richiesto: `repo` (full control of private repositories).

| Token | Usato per |
|---|---|
| `STATE_REPO_PAT` | Clonare e pushare in `agent-state` |
| `SOURCE_REPO_PAT` | Pushare branch e aprire PR in `project-source` |

## 3. Secrets in GitHub Actions

Nel repository `omni-infrastructure`, vai su
**Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Valore |
|---|---|
| `STATE_REPO_PAT` | PAT per agent-state |
| `SOURCE_REPO_PAT` | PAT per project-source |
| `GEMINI_API_KEY` | Chiave Google Gemini (da AI Studio) |
| `LLM_ENDPOINT_URL` | (opzionale) URL del LLM locale per modalità ibrida |
| `LLM_PROVIDER` | (opzionale) Nome provider per forzatura locale |

## 4. Chiave Google Gemini

1. Vai su [Google AI Studio](https://aistudio.google.com/)
2. Crea una chiave API gratuita
3. Aggiungila come `GEMINI_API_KEY` nei secrets di GitHub

## 5. Ambiente Locale (opzionale)

Copia `.env.example` in `.env` e modifica:

```bash
cp .env.example .env
# Modifica GEMINI_API_KEY, LLM_MODE, etc.
```

## 6. Verifica

```bash
# Sintassi Python
python3 -m py_compile core/inference.py
python3 -m py_compile core/bridge.py

# JSON config
python3 -c "import json; json.load(open('config/providers.json')); json.load(open('config/matrix.json'))"
```
