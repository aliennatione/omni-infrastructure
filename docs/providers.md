# Provider LLM

## Configurazione

I provider sono definiti in `config/providers.json`.
Ogni provider ha:

```json
"nome_provider": {
  "type": "tipo_api",
  "endpoint": "http://...",
  "model": "nome-modello"
}
```

## Tipi di API Supportati

### `google_api`
API nativa di Google Generative Language (Gemini).
- Autenticazione: `GEMINI_API_KEY` (env var)
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/...:generateContent`
- Payload: formato proprietario Google

### `openai_compat`
API compatibile con OpenAI Chat Completions.
Usata da: llama.cpp, Ollama, LocalAI, e qualsiasi server OpenAI-compat.
- Autenticazione: `LLM_API_KEY` (env var, default: `sk-no-key-required`)
- Endpoint: `{base_url}/v1/chat/completions`
- Payload: `{ model, messages: [{role, content}], temperature, max_tokens }`

### `opencode_api`
API nativa del server `opencode serve`.
- Autenticazione: `OPENCODE_SERVER_PASSWORD` / `OPENCODE_SERVER_USERNAME`
- Flusso: crea sessione → invia messaggio → recupera risposta → cancella sessione
- Endpoint: `{base_url}/session`

## Provider Predefiniti

| Provider | Tipo | Endpoint | Modello |
|---|---|---|---|
| `google_gemini_flash` | `google_api` | Google Gemini API | `gemini-1.5-flash` |
| `google_gemini_pro` | `google_api` | Google Gemini API | `gemini-1.5-pro` |
| `local_llamacpp` | `openai_compat` | `http://localhost:8080` | `llama-2-7b` |
| `local_ollama` | `openai_compat` | `http://localhost:11434` | `llama3.2` |
| `local_localai` | `openai_compat` | `http://localhost:8081` | `gpt-4` |
| `local_opencode` | `opencode_api` | `http://localhost:4096` | — |

## Routing

Due modalità: **automatica** (via matrix.json) o **esplicita** (via `--provider`).

### Automatica: `config/matrix.json`

Usata quando NON passi `--provider`. Mappa eventi → provider:

```json
{
  "routing_rules": {
    "small_fix":        { "provider": "google_gemini_flash" },
    "git_automation":   { "provider": "google_gemini_flash" },
    "software_refactor":{ "provider": "google_gemini_pro" },
    "local_inference":  { "provider": "local_llamacpp" },
    "opencode_inference":{ "provider": "local_opencode" }
  }
}
```

Adatta per cron automatico e workflow prevedibili.

### Esplicita: `--provider <nome>`

Passando `--provider`, matrix.json viene saltato e il provider scelto viene usato direttamente. Funziona in TUTTI gli scenari:

```bash
# Umano o agente locale — sceglie il LLM al volo
python core/bridge.py \
  --state ../agent-state --workspace ../project-source --config ./config \
  --event git_automation --payload "Refactor" \
  --mode local \
  --provider local_llamacpp

# GitHub Actions (trigger manuale) — LLM locale via tunnel
python core/bridge.py ... --mode local --provider local_llamacpp

# GitHub Actions (cron) — senza --provider, usa matrix.json → Gemini
python core/bridge.py ... --event git_automation --payload "..."
```

### Elenco provider disponibili

```bash
PYTHONPATH=./core python core/bridge.py \
  --state ./state --workspace ./workspace --config ./config \
  --list-providers
```

### Sovrascritture via Ambiente

In modalità `--mode local`, puoi forzare provider ed endpoint:

| Variabile | Effetto |
|---|---|
| `LLM_PROVIDER=local_ollama` | Usa Ollama invece del provider di default |
| `LLM_ENDPOINT_URL=http://10.0.0.5:8080` | Punta a un LLM su un altro host |

## Aggiungere un Nuovo Provider

1. Aggiungi una voce in `providers.json`
2. Scegli il `type` appropriato (`google_api`, `openai_compat`, `opencode_api`)
3. Opzionale: aggiungi una routing rule in `matrix.json`
4. Opzionale: se il tipo non esiste, implementa un nuovo metodo in `inference.py`
