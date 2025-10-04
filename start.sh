#!/bin/bash
set -e

echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
max_attempts=30
attempt=0
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "Ollama failed to start"
        exit 1
    fi
    echo "Attempt $attempt/$max_attempts..."
    sleep 2
done

echo "Ollama is ready!"

# Pull the model if not exists
echo "Checking for model: ${MODEL_NAME:-deepseek-r1:1.5b}"
if ! ollama list | grep -q "${MODEL_NAME:-deepseek-r1:1.5b}"; then
    echo "Pulling model..."
    ollama pull "${MODEL_NAME:-deepseek-r1:1.5b}"
else
    echo "Model already exists"
fi

echo "Starting Flask API server..."
exec gunicorn --bind 0.0.0.0:${PORT:-8080} \
    --workers 1 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
