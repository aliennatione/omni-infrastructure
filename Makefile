.PHONY: up down ps logs pull-model shell setup run up-% run-%

PROVIDER ?= llamacpp

# Avvia il server LLM selezionato
up:
	docker compose --profile $(PROVIDER) up -d
	@echo "[*] Profilo '$(PROVIDER)' avviato."

# Avvia un server LLM specifico
up-%:
	docker compose --profile $(*) up -d
	@echo "[*] Profilo '$(*)' avviato."

# Ferma tutto
down:
	docker compose down

# Elenca i container attivi
ps:
	docker compose ps

# Mostra i log in tempo reale
logs:
	docker compose logs -f

# Mostra lo stato dei profili disponibili
profiles:
	@echo "Profili disponibili: llamacpp, localai, ollama"
	@echo ""
	@echo "Uso:  make up-llamacpp    # Avvia solo llama.cpp"
	@echo "      make up-localai     # Avvia solo LocalAI"
	@echo "      make up-ollama      # Avvia solo Ollama"
	@echo "      make up             # Avvia il profilo di default (llamacpp)"
	@echo ""
	@echo "Provider: local_llamacpp, local_localai, local_ollama,"
	@echo "          local_opencode, google_gemini_flash, google_gemini_pro"

# Scarica un modello GGUF in ./models/
# Uso: make pull-model MODEL_URL=https://... MODEL_FILE=model.gguf
pull-model:
	@echo "[*] Scarico modello $(MODEL_URL) in ./models/..."
	mkdir -p models
	curl -L -o models/$(MODEL_FILE) $(MODEL_URL)

# Shell interattiva dentro il container bridge (sovrascrive ENTRYPOINT)
shell:
	docker compose run --rm --entrypoint /bin/bash omni-bridge

# Crea le directory per i volumi Docker
setup:
	mkdir -p state workspace
	@echo "[*] Directory state/ e workspace/ create."

# Esegui bridge con provider specifico (locale, senza Docker)
# Uso: make run PROVIDER=local_llamacpp EVENT=git_automation PAYLOAD="..."
run:
	pip install -r requirements.txt
	PYTHONPATH=./core python core/bridge.py \
		--state ../agent-state \
		--workspace ../project-source \
		--config ./config \
		--event $(or $(EVENT),git_automation) \
		--payload "$(or $(PAYLOAD),Routine check)" \
		--mode local \
		$(if $(PROVIDER),--provider $(PROVIDER),)

# Esegui bridge con Docker Compose (server + bridge, poi ferma tutto)
run-container:
	@echo "[*] Avvio profilo '$(PROVIDER)', esecuzione bridge, poi fermo..."
	docker compose --profile $(PROVIDER) up --abort-on-container-exit --exit-code-from omni-bridge

# Elenca i provider disponibili
list-providers:
	PYTHONPATH=./core python core/bridge.py \
		--state ./state \
		--workspace ./workspace \
		--config ./config \
		--list-providers
