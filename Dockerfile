# Optimized DeepSeek API Server for Render.com
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Create directory for Ollama models
RUN mkdir -p /root/.ollama

# Pre-pull the model during build (optional - comment out if build times out)
# RUN ollama serve & sleep 5 && ollama pull deepseek-r1:1.5b && pkill ollama

# Expose port
EXPOSE 8080

# Health check - longer grace period for model loading
HEALTHCHECK --interval=60s --timeout=30s --start-period=300s --retries=5 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["./start.sh"]
