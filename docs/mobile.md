# NanoClaw Gateway

## Panoramica

NanoClaw è il componente gateway mobile che permette di interagire con
l'infrastruttura Omni-Agent tramite chat (Telegram).

## Architettura

```
Utente → Telegram Bot → NanoClaw Gateway → Bridge → LLM → Risposta → Telegram
```

1. L'utente invia un messaggio al bot Telegram
2. NanoClaw riceve il messaggio via polling Telegram Bot API
3. NanoClaw chiama il bridge con evento `chat_message`
4. Il bridge instrada al provider LLM (default: `local_openhands`)
5. La risposta viene inviata all'utente su Telegram

## Setup

### 1. Creare il Bot Telegram

1. Apri Telegram e cerca `@BotFather`
2. Invia `/newbot` e segui le istruzioni
3. Copia il token fornito

### 2. Configurare

```bash
cp .env.example .env
# Modifica .env:
TELEGRAM_TOKEN=il-tuo-token-qui
NANOCLAW_PROVIDER=local_openhands
NANOCLAW_MODE=local
```

### 3. Avviare

```bash
# Installa dipendenze
pip install -r requirements.txt

# Avvia il gateway
PYTHONPATH=./core python core/nanoclaw_gateway.py

# Oppure in test mode
PYTHONPATH=./core python core/nanoclaw_gateway.py --test "Cosa sai fare?"
```

## Variabili d'Ambiente

| Variabile | Descrizione | Default |
|---|---|---|
| `TELEGRAM_TOKEN` | Token del bot Telegram | (richiesto) |
| `NANOCLAW_PROVIDER` | Provider LLM predefinito | `local_openhands` |
| `NANOCLAW_MODE` | Modalità di esecuzione | `local` |

## Routing

I messaggi da chat vengono instradati tramite l'evento `chat_message` in `matrix.json`:

```json
{
  "chat_message": {
    "provider": "local_openhands",
    "description": "Messaggio da chat mobile (Telegram/Signal)"
  }
}
```

## Note

- NanoClaw usa il polling Telegram Bot API (non webhook)
- I messaggi sono limitati a 4096 caratteri nella risposta
- Il timeout per le chiamate al bridge è di 600 secondi
- In futuro potrebbe diventare un repository indipendente
