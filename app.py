#!/usr/bin/env python3
"""
DeepSeek API Server - Optimized for Fly.io
OpenAI-compatible API endpoints using Ollama + DeepSeek
"""

import os
import time
import json
import logging
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import ollama

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
MODEL_NAME = os.getenv('MODEL_NAME', 'deepseek-r1:1.5b')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
PORT = int(os.getenv('PORT', '8080'))

# Model loading status
model_loaded = False

def ensure_model_loaded():
    """Ensure DeepSeek model is loaded"""
    global model_loaded
    if not model_loaded:
        try:
            logger.info(f"Pulling model: {MODEL_NAME}")
            ollama.pull(MODEL_NAME)
            model_loaded = True
            logger.info(f"Model {MODEL_NAME} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': MODEL_NAME,
        'model_loaded': model_loaded,
        'timestamp': time.time()
    })

@app.route('/v1/models', methods=['GET'])
def list_models():
    """List available models (OpenAI compatible)"""
    return jsonify({
        'object': 'list',
        'data': [{
            'id': MODEL_NAME,
            'object': 'model',
            'created': int(time.time()),
            'owned_by': 'deepseek'
        }]
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """Chat completions endpoint (OpenAI compatible)"""
    try:
        ensure_model_loaded()

        data = request.json
        messages = data.get('messages', [])
        stream = data.get('stream', False)
        max_tokens = data.get('max_tokens', MAX_TOKENS)
        temperature = data.get('temperature', 0.7)

        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        # Convert OpenAI format to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        if stream:
            return stream_response(ollama_messages, max_tokens, temperature)
        else:
            return non_stream_response(ollama_messages, max_tokens, temperature)

    except Exception as e:
        logger.error(f"Error in chat_completions: {e}")
        return jsonify({'error': str(e)}), 500

def non_stream_response(messages, max_tokens, temperature):
    """Non-streaming response"""
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            options={
                'num_predict': max_tokens,
                'temperature': temperature
            }
        )

        return jsonify({
            'id': f'chatcmpl-{int(time.time())}',
            'object': 'chat.completion',
            'created': int(time.time()),
            'model': MODEL_NAME,
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response['message']['content']
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': response.get('prompt_eval_count', 0),
                'completion_tokens': response.get('eval_count', 0),
                'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
            }
        })
    except Exception as e:
        logger.error(f"Error in non_stream_response: {e}")
        return jsonify({'error': str(e)}), 500

def stream_response(messages, max_tokens, temperature):
    """Streaming response"""
    def generate():
        try:
            stream = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                stream=True,
                options={
                    'num_predict': max_tokens,
                    'temperature': temperature
                }
            )

            for chunk in stream:
                if 'message' in chunk:
                    content = chunk['message'].get('content', '')
                    if content:
                        response_chunk = {
                            'id': f'chatcmpl-{int(time.time())}',
                            'object': 'chat.completion.chunk',
                            'created': int(time.time()),
                            'model': MODEL_NAME,
                            'choices': [{
                                'index': 0,
                                'delta': {'content': content},
                                'finish_reason': None
                            }]
                        }
                        yield f"data: {json.dumps(response_chunk)}\n\n"

            # Send final chunk
            final_chunk = {
                'id': f'chatcmpl-{int(time.time())}',
                'object': 'chat.completion.chunk',
                'created': int(time.time()),
                'model': MODEL_NAME,
                'choices': [{
                    'index': 0,
                    'delta': {},
                    'finish_reason': 'stop'
                }]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error in stream_response: {e}")
            error_chunk = {'error': str(e)}
            yield f"data: {json.dumps(error_chunk)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/v1/completions', methods=['POST'])
def completions():
    """Text completions endpoint (OpenAI compatible)"""
    try:
        ensure_model_loaded()

        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', MAX_TOKENS)
        temperature = data.get('temperature', 0.7)

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        response = ollama.generate(
            model=MODEL_NAME,
            prompt=prompt,
            options={
                'num_predict': max_tokens,
                'temperature': temperature
            }
        )

        return jsonify({
            'id': f'cmpl-{int(time.time())}',
            'object': 'text_completion',
            'created': int(time.time()),
            'model': MODEL_NAME,
            'choices': [{
                'text': response['response'],
                'index': 0,
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': response.get('prompt_eval_count', 0),
                'completion_tokens': response.get('eval_count', 0),
                'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
            }
        })
    except Exception as e:
        logger.error(f"Error in completions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'DeepSeek API Server',
        'version': '1.0.0',
        'model': MODEL_NAME,
        'endpoints': {
            'health': '/health',
            'models': '/v1/models',
            'chat': '/v1/chat/completions',
            'completions': '/v1/completions'
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting DeepSeek API server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
