#!/usr/bin/env sh
# tunnel.sh — Espone llama.cpp via tunnel per modalità ibrida (GitHub Actions → LLM locale)
#
# Prerequisiti:
#   - llama-server in esecuzione su localhost:8080
#   - ngrok o tailscale installati
#
# Uso:
#   ./scripts/tunnel.sh ngrok        # Espone via ngrok
#   ./scripts/tunnel.sh tailscale    # Espone via tailscale funnel
#

set -e

LLAMA_PORT="${LLAMA_PORT:-8080}"

case "${1:-ngrok}" in
  ngrok)
    echo "[*] Avvio tunnel ngrok verso localhost:${LLAMA_PORT}..."
    if ! command -v ngrok >/dev/null 2>&1; then
      echo "[-] ngrok non trovato. Installa da https://ngrok.com/download"
      exit 1
    fi
    ngrok http "${LLAMA_PORT}" --log=stdout
    ;;

  tailscale)
    echo "[*] Abilitazione Tailscale Funnel verso localhost:${LLAMA_PORT}..."
    if ! command -v tailscale >/dev/null 2>&1; then
      echo "[-] tailscale non trovato. Installa da https://tailscale.com/download"
      exit 1
    fi
    tailscale funnel --bg "${LLAMA_PORT}"
    echo "[*] Funnel attivo. Ottieni l'URL con: tailscale status --json | grep funnel"
    ;;

  *)
    echo "Uso: $0 {ngrok|tailscale}"
    exit 1
    ;;
esac
