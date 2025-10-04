#!/usr/bin/env python3
"""
Quick test script for DeepSeek API
"""

import requests
import json
import time

API_URL = "https://deepseek-api-tbp3.onrender.com"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_chat_completion():
    """Test chat completion"""
    print("💬 Testing chat completion (may take 30s on first request)...")

    payload = {
        "model": "deepseek-r1:1.5b",
        "messages": [
            {"role": "user", "content": "Say hello in exactly 5 words"}
        ],
        "max_tokens": 50
    }

    start = time.time()
    response = requests.post(
        f"{API_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=120
    )
    elapsed = time.time() - start

    print(f"Status: {response.status_code}")
    print(f"Time: {elapsed:.2f}s")

    if response.status_code == 200:
        data = response.json()
        content = data['choices'][0]['message']['content']
        print(f"Response: {content}\n")
    else:
        print(f"Error: {response.text}\n")

def test_streaming():
    """Test streaming response"""
    print("📡 Testing streaming response...")

    payload = {
        "model": "deepseek-r1:1.5b",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5"}
        ],
        "stream": True,
        "max_tokens": 100
    }

    response = requests.post(
        f"{API_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload,
        stream=True,
        timeout=120
    )

    print(f"Status: {response.status_code}")
    print("Stream output: ", end="", flush=True)

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str != '[DONE]':
                    try:
                        data = json.loads(data_str)
                        content = data['choices'][0]['delta'].get('content', '')
                        print(content, end="", flush=True)
                    except:
                        pass

    print("\n")

if __name__ == "__main__":
    print("=" * 60)
    print("DeepSeek API Test Suite")
    print("=" * 60 + "\n")

    try:
        test_health()
        test_chat_completion()
        test_streaming()

        print("✅ All tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
