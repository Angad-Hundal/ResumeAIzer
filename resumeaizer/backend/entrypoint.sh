#!/bin/sh

if [ -f "/app/.env" ]; then
    export $(grep -v '^#' /app/.env | xargs)
fi

echo "=== Starting Application with ==="
echo "DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-not_set}"
echo "PYTHONPATH=${PYTHONPATH}"
echo "==============================="

RELOAD="--reload" exec uvicorn main:app --host 0.0.0.0 --port 8000 ${RELOAD:-}