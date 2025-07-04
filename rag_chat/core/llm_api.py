import requests
import json
import os
from rag_chat.config.settings import LLM_API_URL, LLM_MODEL_NAME, OPENAI_API_KEY

# Helper to detect OpenAI usage
USE_OPENAI = 'openai' in LLM_API_URL or LLM_API_URL.startswith('https://api.openai.com')

try:
    from openai import OpenAI  # modern SDK client
except ImportError:
    OpenAI = None

def query_llm_stream_with_callback(prompt: str, on_token, model=None, url=None):
    model = model or LLM_MODEL_NAME
    url = url or LLM_API_URL
    api_key = OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')

    if USE_OPENAI:
        if OpenAI is None:
            on_token("[Error] openai package not installed")
            return

        # print(f"[DEBUG] Using OpenAI model: '{model}' with API key: '{api_key[:8]}...'")  # DEBUG: commented out
        # print(f"[DEBUG] Requesting model: '{model}'")  # DEBUG: commented out
        print(f"[DEBUG] Requesting model: '{model}'")

        client = OpenAI(api_key=api_key)  # You can add `organization="org_id"` if needed

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    on_token(chunk.choices[0].delta.content)
        except Exception as e:
            on_token(f"\n[Error] {e}")
    else:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        try:
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "response" in chunk:
                            on_token(chunk["response"])
        except Exception as e:
            on_token(f"\n[Error] {e}")

def query_llm_response(prompt: str, model=None, url=None) -> str:
    model = model or LLM_MODEL_NAME
    url = url or LLM_API_URL
    api_key = OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')

    if USE_OPENAI:
        if OpenAI is None:
            return "[Error] openai package not installed"

        # print(f"[DEBUG] Using OpenAI model: '{model}' with API key: '{api_key[:8]}...'")  # DEBUG: commented out
        # print(f"[DEBUG] Requesting model: '{model}'")  # DEBUG: commented out


        client = OpenAI(api_key=api_key)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Error] {e}"
    else:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            return f"[Error] {e}"
