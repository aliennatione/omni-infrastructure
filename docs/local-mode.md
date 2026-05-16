# Modalità Locale

Esecuzione su macchina locale con server LLM Dockerizzati e bridge nativo.

## Prerequisiti

- Docker + Docker Compose
- Un modello LLM in formato GGUF (per llama.cpp)

## Server LLM con Docker Compose Profiles

I server LLM sono organizzati con **profili Docker Compose**. Ogni profilo
corrisponde a un provider e si avvia separatamente:

```bash
# Profili disponibili
make profiles

# Avvia solo llama.cpp (default)
make up-llamacpp

# Oppure LocalAI o Ollama
make up-localai
make up-ollama

# Verifica che sia su
make ps
```

| Servizio | Profile | Porta | Provider |
|---|---|---|---|
| `llama-server` | `llamacpp` | `:8080` | `local_llamacpp` |
| `localai` | `localai` | `:8081` | `local_localai` |
| `ollama` | `ollama` | `:11434` | `local_ollama` |

Puoi anche tenerne su più di uno contemporaneamente (se hai RAM):

```bash
docker compose --profile llamacpp --profile ollama up -d
```

## Esecuzione bridge con `--provider`

Una volta che il server LLM è in ascolto, esegui il bridge specificando il provider:

```bash
PYTHONPATH=./core python core/bridge.py \
  --state ./state \
  --workspace ./workspace \
  --config ./config \
  --event git_automation \
  --payload "Refactor the main function" \
  --mode local \
  --provider local_llamacpp
```

### Tutti in un comando con Make

```bash
make run PROVIDER=local_llamacpp PAYLOAD="Refactor"
make run PROVIDER=local_ollama PAYLOAD="Audit code"
make run PROVIDER=local_localai PAYLOAD="Add tests"
```

Oppure containerizzato (server + bridge, poi ferma tutto):

```bash
make run-container PROVIDER=llamacpp
```

## Esempi per scenario

### Locale (utente umano)
```bash
# 1. Avvia il server una volta
make up-llamacpp

# 2. Chiama il bridge quante volte vuoi — risposta immediata
make run PROVIDER=local_llamacpp PAYLOAD="Fix bug in main.py"
make run PROVIDER=google_gemini_flash PAYLOAD="Review my code"

# 3. Fine sessione: libera RAM
docker compose --profile llamacpp down
```

### Locale (agente autonomo)
```bash
# L'agente chiama il bridge con --provider esplicito
# Il server LLM deve già essere in ascolto (gestito esternamente)
python core/bridge.py \
  --state /data/state --workspace /data/workspace --config ./config \
  --event git_automation --payload "Refactor" \
  --mode local --provider local_llamacpp
```

### GitHub Actions (trigger manuale, LLM locale via tunnel)
```yaml
# Nel workflow, se mode=local, passa --provider dal secret
python3 infrastructure/core/bridge.py \
  ... --mode local --provider "${{ secrets.LLM_PROVIDER }}"
```

### GitHub Actions (cron automatico)
Senza `--provider`, usa matrix.json → `google_gemini_flash`. Nessun server locale.

## 1. Modello LLM (solo per llama.cpp)

Scarica un modello GGUF nella directory `models/`:

```bash
mkdir -p models
make pull-model MODEL_URL=https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf MODEL_FILE=llama-2-7b.Q4_K_M.gguf
```

## 2. Esecuzione senza Docker

Bridge direttamente in Python se hai già un LLM server su localhost:

```bash
# llama.cpp server
llama-server --model models/llama-2-7b.Q4_K_M.gguf --host 0.0.0.0 --port 8080

# In un altro terminale:
PYTHONPATH=./core python core/bridge.py \
  --state ./state \
  --workspace ./workspace \
  --config ./config \
  --event git_automation \
  --payload "Hello world" \
  --mode local \
  --provider local_llamacpp
```

## Troubleshooting

**Errore: "impossibile connettersi"**
Il server LLM non è in esecuzione. Il bridge ora mostra un suggerimento:
```
Provider 'local_llamacpp': impossibile connettersi.
    Suggerimento: make up-llamacpp
```

**Errore: "No such file or directory"**
Hai dimenticato `make setup`. Le directory `state/` e `workspace/` devono esistere.

## Trigger Automatici

Per eseguire il bridge periodicamente senza intervento manuale:

### Cron

```bash
# Installa lo script
make install-cron

# Aggiungi a crontab (ogni 4 ore)
crontab -e
# Aggiungi: 0 */4 * * * /usr/local/bin/omni-agent-cron --event local_cron

# Test manuale
/usr/local/bin/omni-agent-cron --event local_cron --provider local_llamacpp
```

### Systemd

```bash
# Installa e avvia il servizio
make install-service

# Verifica stato
sudo systemctl status omni-agent

# Vedi log in tempo reale
sudo journalctl -u omni-agent -f
```

### Configurazione

Prima di usare i trigger automatici, assicurati che `.env` sia configurato:

```bash
cp .env.example .env
# Modifica .env con i tuoi valori
```

Il servizio systemd carica automaticamente le variabili da `.env`.
