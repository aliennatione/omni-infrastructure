#!/usr/bin/env sh
# crawl-docs.sh — Crawler documentazione per knowledge base agent
#
# Uso:
#   ./scripts/crawl-docs.sh [source-name]     # Crawla una fonte specifica
#   ./scripts/crawl-docs.sh --all              # Crawla tutte le fonti
#   ./scripts/crawl-docs.sh --list             # Elenca documenti crawlati
#   ./scripts/crawl-docs.sh --rebuild-context  # Ricostruisce CONTEXT.md
#
# Richiede:
#   - pip install -r requirements.txt (trafilatura)
#   - directory state/ con agent-state

set -e

STATE_DIR="${STATE_DIR:-./state}"
CONFIG_DIR="${CONFIG_DIR:-./config}"
ACTION="${1:---all}"

cd "$(dirname "$0")/.."

PYTHONPATH=./core python core/doclingest.py \
  --state "$STATE_DIR" \
  --config "$CONFIG_DIR" \
  --action "${ACTION#--}"

# Se non è --list o --rebuild-context, ricostruisci anche CONTEXT.md
case "$ACTION" in
  --list|--rebuild-context)
    ;;
  *)
    echo "[*] Ricostruzione CONTEXT.md..."
    PYTHONPATH=./core python core/doclingest.py \
      --state "$STATE_DIR" \
      --config "$CONFIG_DIR" \
      --action rebuild-context
    ;;
esac
