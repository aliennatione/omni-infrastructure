# Fase 4 — Trigger locali

**Obiettivo:** Permettere l'esecuzione automatica del bridge su macchina locale
tramite cron e systemd, e aggiungere l'evento `local_cron` in `matrix.json`.

## Contesto

Attualmente il bridge si avvia solo manualmente (`make run`) o via GitHub Actions.
Per supportare agenti autonomi futuri, serve un meccanismo di esecuzione periodica
anche in ambiente locale.

## Cosa creare

### 1. `scripts/omni-agent-cron`

Script eseguibile da crontab:

```bash
#!/bin/sh
# Usage: omni-agent-cron [--event <type>] [--provider <name>]
# Install: crontab -e → aggiungi riga:
#   0 */4 * * * /path/to/scripts/omni-agent-cron --event local_cron

EVENT="${1:-local_cron}"
cd /data/workspace/omni-infrastructure
PYTHONPATH=./core python core/bridge.py \
  --state ../agent-state \
  --workspace ../project-source \
  --config ./config \
  --event "$EVENT" \
  --payload "Scheduled local run" \
  --mode local \
  "$@"
```

### 2. `scripts/omni-agent.service`

Unit file systemd per esecuzione continua o a intervalli:

```ini
[Unit]
Description=Omni-Agent Bridge Service
After=network.target docker.target

[Service]
Type=simple
WorkingDirectory=/data/workspace/omni-infrastructure
EnvironmentFile=/data/workspace/omni-infrastructure/.env
ExecStart=/usr/bin/python3 core/bridge.py \
  --state ../agent-state \
  --workspace ../project-source \
  --config ./config \
  --event service \
  --payload "Systemd run" \
  --mode local
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

### 3. `config/matrix.json` — evento `local_cron`

Aggiungere regola di routing:

```json
{
  "event": "local_cron",
  "provider": "local_llamacpp",
  "mode": "local",
  "description": "Esecuzione automatica periodica su macchina locale"
}
```

### 4. `docs/local-mode.md`

Aggiungere sezione "Trigger automatici" che spiega:
- Installare lo script cron
- Installare il servizio systemd
- Configurare `.env`
- Verificare con `journalctl`

### 5. `Makefile`

Aggiungere target:

```makefile
install-cron:
	cp scripts/omni-agent-cron /usr/local/bin/
	chmod +x /usr/local/bin/omni-agent-cron

install-service:
	sudo cp scripts/omni-agent.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable omni-agent
	sudo systemctl start omni-agent
```

## Verifica

```bash
# Test manuale
scripts/omni-agent-cron --event test --provider local_llamacpp

# Test systemd (se installato)
sudo systemctl status omni-agent
sudo journalctl -u omni-agent -f
```

## Commit

```
feat: add local cron/systemd triggers for automated bridge execution
```
