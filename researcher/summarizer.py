import os
import logging
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')


def summarize(text, model='hf-small'):
    """Simple adapter: prefer Hugging Face Inference API when available, then OpenAI, else fallback.

    This function is intentionally minimal so callers can extend prompt/args.
    """
    if HUGGINGFACE_API_KEY:
        try:
            return _hf_summarize(text, model)
        except Exception as e:
            logging.warning(f"HF summarizer failed: {e}")

    if OPENAI_API_KEY:
        try:
            return _openai_summarize(text)
        except Exception as e:
            logging.warning(f"OpenAI summarizer failed: {e}")

    # fallback: return the first 3 sentences
    return _naive_summary(text)


def _naive_summary(text, sentences=3):
    parts = text.split('.')
    return '.'.join(parts[:sentences]).strip() + ('.' if len(parts) >= sentences else '')


def _hf_summarize(text, model='google/flan-t5-small'):
    import requests
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": f"Summarize: {text}", "options": {"wait_for_model": True}}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and 'generated_text' in data[0]:
        return data[0]['generated_text']
    # some HF endpoints return a string
    if isinstance(data, dict) and data.get('summary_text'):
        return data['summary_text']
    return str(data)


def _openai_summarize(text):
    import openai
    openai.api_key = OPENAI_API_KEY
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'system', 'content': 'You are a concise summarizer.'},
                  {'role': 'user', 'content': f'Summarize the following article:\n\n{text}'}],
        max_tokens=300,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
