.PHONY: up down ps logs pull-model shell

# Avvia tutta la pila locale (llama.cpp + omni-bridge)
up:
	docker compose up -d
	@echo "[*] omni-bridge avviato. Log con: make logs"

# Ferma i container
down:
	docker compose down

# Elenca i container attivi
ps:
	docker compose ps

# Mostra i log in tempo reale
logs:
	docker compose logs -f

# Avvia solo llama-server (per sviluppo bridge)
up-llama:
	docker compose up -d llama-server

# Scarica un modello GGUF in ./models/
pull-model:
	@echo "[*] Scarico modello $(MODEL_URL) in ./models/..."
	mkdir -p models
	curl -L -o models/$(MODEL_FILE) $(MODEL_URL)

# Shell interattiva dentro il container bridge
shell:
	docker compose run --rm omni-bridge /bin/bash

# Esegui bridge in locale (senza Docker)
run-local:
	pip install -r requirements.txt
	PYTHONPATH=./core python core/bridge.py \
		--state ../agent-state \
		--workspace ../project-source \
		--config ./config \
		--event $(EVENT) \
		--payload "$(PAYLOAD)" \
		--mode local
