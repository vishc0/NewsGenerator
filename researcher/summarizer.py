import os
import logging
from dotenv import load_dotenv
from . import token_tracker

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')


def summarize(text, model='hf-small', max_words=160):
    """Simple adapter: prefer Hugging Face Inference API when available, then OpenAI, else fallback.
    
    Args:
        text: The text to summarize
        model: The model to use (for HF)
        max_words: Target maximum words for the summary (for podcast segments)
    
    This function is intentionally minimal so callers can extend prompt/args.
    """
    # Truncate very long input text to avoid API limits (keep first 3000 words)
    words = text.split()
    if len(words) > 3000:
        text = ' '.join(words[:3000])
    
    if HUGGINGFACE_API_KEY:
        try:
            summary = _hf_summarize(text, model, max_words)
            token_tracker.get_tracker().record_call(text, summary, 'huggingface', success=True)
            return summary
        except Exception as e:
            logging.warning(f"HF summarizer failed: {e}")
            token_tracker.get_tracker().record_call(text, '', 'huggingface', success=False)

    if OPENAI_API_KEY:
        try:
            summary = _openai_summarize(text, max_words)
            token_tracker.get_tracker().record_call(text, summary, 'openai', success=True)
            return summary
        except Exception as e:
            logging.warning(f"OpenAI summarizer failed: {e}")
            token_tracker.get_tracker().record_call(text, '', 'openai', success=False)

    # fallback: return the first 3 sentences
    summary = _naive_summary(text)
    token_tracker.get_tracker().record_call(text, summary, 'fallback', success=True)
    return summary


def _naive_summary(text, sentences=3):
    parts = text.split('.')
    return '.'.join(parts[:sentences]).strip() + ('.' if len(parts) >= sentences else '')


def _hf_summarize(text, model='google/flan-t5-small', max_words=160):
    import requests
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    # Better prompt for news summarization
    prompt = f"Summarize this news article in approximately {max_words} words, focusing on the key points: {text}"
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and 'generated_text' in data[0]:
        return data[0]['generated_text']
    # some HF endpoints return a string
    if isinstance(data, dict) and data.get('summary_text'):
        return data['summary_text']
    return str(data)


def _openai_summarize(text, max_words=160):
    import openai
    openai.api_key = OPENAI_API_KEY
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'system', 'content': 'You are a concise news summarizer for podcast segments.'},
                  {'role': 'user', 'content': f'Summarize the following article in approximately {max_words} words, focusing on the key facts and takeaways:\n\n{text}'}],
        max_tokens=300,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
