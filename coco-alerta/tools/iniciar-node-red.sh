#!/bin/zsh
cd "$(dirname "$0")/.."
export COCO_ALERTA_DATA="$PWD/data/readings.csv"
export COCO_ALERTA_LIMITES="$PWD/shared/limites.json"
echo "CSV: $COCO_ALERTA_DATA"
echo "Limites: $COCO_ALERTA_LIMITES"
echo "Painel: http://127.0.0.1:${PORT:-1880}/ui/"
exec node-red --userDir "${COCO_ALERTA_USERDIR:-$HOME/.node-red}" --port "${PORT:-1880}"
