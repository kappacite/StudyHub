#!/bin/bash
# Detecte l'architecture et compose la bonne commande docker compose.
# Usage : ./scripts/dev-up.sh [args docker compose additionnels...]
set -e

ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64)
    OVERLAY="docker-compose.amd64.yml"
    ;;
  aarch64|arm64)
    OVERLAY="docker-compose.arm64.yml"
    ;;
  *)
    echo "Architecture non reconnue : $ARCH — utilise le socle seul." >&2
    OVERLAY=""
    ;;
esac

cd "$(dirname "$0")/.."

if [ -n "$OVERLAY" ]; then
  echo "Architecture detectee : $ARCH -> $OVERLAY"
  exec docker compose -f docker-compose.yml -f "$OVERLAY" up "$@"
else
  exec docker compose -f docker-compose.yml up "$@"
fi
