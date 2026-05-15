# Modalità Ibrida

Bridge eseguito su GitHub Actions + LLM in esecuzione sulla tua macchina locale,
esposto via tunnel.

## Architettura

```
┌─────────────────────┐        Tunnel        ┌──────────────────┐
│   GitHub Actions    │ ◄──────────────────► │   Tua Macchina   │
│                     │   (ngrok / tailscale) │                  │
│  ┌──────────────┐   │                      │  ┌────────────┐  │
│  │   bridge.py  │   │                      │  │ llama.cpp  │  │
│  │              │   │                      │  │ :8080      │  │
│  └──────────────┘   │                      │  └────────────┘  │
└─────────────────────┘                      └──────────────────┘
```

## Passo 1: Avvia il LLM locale

```bash
llama-server --model models/llama-2-7b.Q4_K_M.gguf --host 0.0.0.0 --port 8080
```

## Passo 2: Esponi con tunnel

### Opzione A: ngrok

```bash
./scripts/tunnel.sh ngrok
```

Copia l'URL `https://xxxx.ngrok-free.app` generato da ngrok.

### Opzione B: Tailscale Funnel

```bash
./scripts/tunnel.sh tailscale
```

Ottieni l'URL con:
```bash
tailscale status --json | grep funnel
```

## Passo 3: Configura GitHub Secrets

Nel repository `omni-infrastructure`, imposta:

| Secret | Valore |
|---|---|
| `LLM_ENDPOINT_URL` | `https://xxxx.ngrok-free.app` (URL del tunnel) |
| `LLM_PROVIDER` | `local_llamacpp` |

## Passo 4: Esegui il workflow

1. Vai su **Actions → Omni-Agent Distributed Engine → Run workflow**
2. Imposta `mode` su **local**
3. Inserisci event_type e payload
4. Esegui

Il bridge su GitHub Actions si connetterà al tuo LLM locale via tunnel.

## Sicurezza

- ngrok genera URL casuali difficili da indovinare
- Tailscale Funnel richiede autenticazione Tailscale
- Il tunnel espone solo l'API del LLM, non la tua macchina
- I PAT di GitHub sono comunque necessari per clonare/pushare i repo

## Troubleshooting

**Il workflow fallisce con "Connection refused"**
Il tunnel non è attivo. Riavvia ngrok/tailscale.

**Timeout sulla richiesta**
Il LLM locale potrebbe essere troppo lento. Aumenta `generationConfig.maxOutputTokens`
in `inference.py` o usa un modello più piccolo.

**ngrok richiede signup**
Crea un account gratuito su ngrok.com. La parte `--log=stdout` non serve,
usa solo `ngrok http 8080`.
