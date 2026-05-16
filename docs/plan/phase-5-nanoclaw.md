# Fase 5 — Integrazione NanoClaw

**Obiettivo:** Creare un gateway chat (Telegram/Signal) che chiama il bridge
via API, permettendo interazione da mobile con l'infrastruttura agent.

**Dipende da:** Fase 1 (provider OpenHands per interaction loop)

## Contesto

NanoClaw è il componente gateway mobile nello schema architetturale.
Deve ricevere messaggi da chat (Telegram o Signal), chiamare il bridge
per elaborarli, e restituire la risposta all'utente.

## Cosa creare

### 1. `core/nanoclaw_gateway.py`

Gateway leggero che:
- Ascolta webhook Telegram (`python-telegram-bot` o equivalente)
- Riceve messaggio utente
- Chiama bridge via subprocess o API (se bridge esposto)
- Restituisce risposta all'utente

Schema:

```python
class NanoClawGateway:
    def handle_message(self, user_message: str, chat_id: str):
        # Inoltra a bridge
        result = self.call_bridge(user_message, chat_id)
        # Restituisce risposta
        return result

    def call_bridge(self, message: str, session_id: str):
        # Chiama bridge.py via subprocess o REST
        pass
```

### 2. `config/matrix.json` — evento `chat_message`

```json
{
  "event": "chat_message",
  "provider": "openhands_api",
  "mode": "local",
  "description": "Messaggio da chat mobile (Telegram/Signal)"
}
```

### 3. `docs/mobile.md`

Documentare:
- Architettura del gateway
- Setup bot Telegram
- Variabili d'ambiente (`TELEGRAM_TOKEN`, `SIGNAL_NUMBER`)
- Esempi d'uso

### 4. Variabili d'ambiente

| `TELEGRAM_TOKEN` | `nanoclaw_gateway.py` | Telegram bot token |

## Note

NanoClaw è un componente separato ma può coesistere nel repo
`omni-infrastructure` nella fase iniziale. In futuro potrebbe
diventare un repository indipendente.

## Commit

```
feat: add NanoClaw chat gateway for Telegram/Signal mobile interaction
```
