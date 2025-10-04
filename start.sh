#!/bin/bash
set -e

echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready with longer timeout
echo "⏳ Waiting for Ollama to be ready..."
max_attempts=60
attempt=0
while ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Ollama failed to start after ${max_attempts} attempts"
        exit 1
    fi
    echo "   Attempt $attempt/$max_attempts..."
    sleep 3
done

echo "✅ Ollama is ready!"

# Pull the model if not exists (this is the longest part)
echo "🔍 Checking for model: ${MODEL_NAME:-deepseek-r1:1.5b}"
if ! ollama list | grep -q "${MODEL_NAME:-deepseek-r1:1.5b}"; then
    echo "📥 Pulling model (this may take 5-10 minutes on first run)..."
    echo "   Model size: ~900MB"
    ollama pull "${MODEL_NAME:-deepseek-r1:1.5b}" || {
        echo "❌ Failed to pull model"
        exit 1
    }
    echo "✅ Model downloaded successfully!"
else
    echo "✅ Model already exists"
fi

echo "🌐 Starting Flask API server on port ${PORT:-8080}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8080} \
    --workers 1 \
    --threads 4 \
    --timeout 300 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
