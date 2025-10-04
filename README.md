# DeepSeek API Server on Fly.io

OpenAI-compatible API server running DeepSeek via Ollama on Fly.io's free tier.

## Features

- ✅ OpenAI-compatible API endpoints
- ✅ Streaming support
- ✅ Auto-scaling (scales to zero when idle)
- ✅ Free tier optimized (512MB RAM)
- ✅ Global deployment
- ✅ Built-in SSL/HTTPS
- ✅ Health checks & monitoring

## API Endpoints

### Chat Completions (OpenAI compatible)
```bash
curl -X POST https://your-app.fly.dev/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1:1.5b",
    "messages": [
      {"role": "user", "content": "What is the meaning of life?"}
    ],
    "stream": false
  }'
```

### Text Completions
```bash
curl -X POST https://your-app.fly.dev/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1:1.5b",
    "prompt": "Write a poem about AI",
    "max_tokens": 100
  }'
```

### Health Check
```bash
curl https://your-app.fly.dev/health
```

### List Models
```bash
curl https://your-app.fly.dev/v1/models
```

## Deployment

Already configured! Your API will be available at:
**https://deepseek-api.fly.dev**

## Environment Variables

- `MODEL_NAME`: DeepSeek model to use (default: `deepseek-r1:1.5b`)
- `PORT`: Server port (default: `8080`)
- `MAX_TOKENS`: Maximum tokens per request (default: `2048`)

## Scaling

```bash
# Scale to 2 machines
flyctl scale count 2

# Increase memory
flyctl scale memory 1024

# Change to performance CPU
flyctl scale vm shared-cpu-2x
```

## Monitoring

```bash
# View logs
flyctl logs

# SSH into machine
flyctl ssh console

# Check status
flyctl status
```

## Cost Optimization

This setup uses:
- **Free tier:** 3 x 256MB VMs (we use 512MB = 2 units)
- **Auto-stop:** Scales to 0 when idle
- **Auto-start:** Wakes up on requests (~2s cold start)

## Custom Domain

```bash
# Add your domain
flyctl certs add api.yourdomain.com

# Update DNS with provided values
flyctl certs show api.yourdomain.com
```

## Troubleshooting

### Model not loading
Check logs: `flyctl logs`

### Out of memory
Increase VM size: `flyctl scale memory 1024`

### Slow responses
Use smaller model or increase CPU: `flyctl scale vm shared-cpu-2x`

## Development

Run locally:
```bash
docker build -t deepseek-api .
docker run -p 8080:8080 deepseek-api
```

## License

MIT
