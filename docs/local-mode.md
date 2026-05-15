# Modalità Locale

Esecuzione completa su macchina locale con Docker Compose.

## Prerequisiti

- Docker + Docker Compose
- Un modello LLM in formato GGUF

## 1. Modello LLM

Scarica un modello GGUF nella directory `models/`:

```bash
mkdir -p models
make pull-model MODEL_URL=https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf MODEL_FILE=llama-2-7b.Q4_K_M.gguf
```

## 2. Avvio

```bash
# Crea le directory per i volumi
make setup

# Avvia llama-server + omni-bridge
make up

# Log in tempo reale
make logs
```

Il bridge eseguirà il task configurato in `EVENT_TYPE` (default: `git_automation`)
e scriverà il risultato in `state/journal/`.

## 3. Personalizzazione

Imposta variabili d'ambiente o crea un file `.env`:

```bash
# .env
LLM_MODE=local
LLM_PROVIDER=local_llamacpp
LLM_ENDPOINT_URL=http://llama-server:8080
MODEL_FILE=llama-2-7b.Q4_K_M.gguf
EVENT_TYPE=git_automation
TASK_PAYLOAD="Refactor the main function"
```

Poi avvia con:
```bash
docker compose --env-file .env up -d
```

## 4. Esecuzione senza Docker

Puoi eseguire il bridge direttamente in Python se hai già
un LLM server in esecuzione su localhost:

```bash
# llama.cpp server
llama-server --model models/llama-2-7b.Q4_K_M.gguf --host 0.0.0.0 --port 8080

# In un altro terminale:
PYTHONPATH=./core python core/bridge.py \
  --state ./state \
  --workspace ./workspace \
  --config ./config \
  --event local_inference \
  --payload "Hello world" \
  --mode local
```

## 5. Provider Locali Disponibili

| Provider | Porta | Tipo |
|---|---|---|
| `local_llamacpp` | 8080 | OpenAI-compat |
| `local_ollama` | 11434 | OpenAI-compat |
| `local_localai` | 8081 | OpenAI-compat |
| `local_opencode` | 4096 | API nativa opencode serve |

Per cambiare provider, imposta `LLM_PROVIDER` o modifica `config/matrix.json`.

## Troubleshooting

**Errore: "Connection refused"**
Il LLM server non è in esecuzione. Avvia prima llama-server.

**Errore: "No such file or directory"**
Hai dimenticato `make setup`. Le directory `state/` e `workspace/` devono esistere.

**Il container esce subito**
Il bridge esegue un singolo task e termina. È normale.
Per tenerlo in vita, usa `make logs` e verifica il risultato.
