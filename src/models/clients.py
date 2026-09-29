import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

# Global Client Caching
_openai_client = None
_anthropic_client = None
_genai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        key = os.getenv("OPENAI_API_KEY")
        if key:
            from openai import OpenAI
            _openai_client = OpenAI(api_key=key)
    return _openai_client

def get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            import anthropic
            _anthropic_client = anthropic.Anthropic(api_key=key)
    return _anthropic_client

def get_genai_client():
    global _genai_client
    if _genai_client is None:
        key = os.getenv("GEMINI_API_KEY")
        if key:
            from google import genai
            _genai_client = genai.Client(api_key=key)
    return _genai_client

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_openai(model, prompt):
    client = get_openai_client()
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured.")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    usage = response.usage
    return json.loads(content), content, usage.prompt_tokens, usage.completion_tokens

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_anthropic(model, prompt):
    client = get_anthropic_client()
    if not client:
        raise ValueError("ANTHROPIC_API_KEY is not configured.")
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt + "\n\nOutput JSON only."}]
    )
    content = response.content[0].text
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    return json.loads(content), content, response.usage.input_tokens, response.usage.output_tokens

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_gemini(model, prompt):
    client = get_genai_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is not configured.")
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    content = response.text
    usage = response.usage_metadata
    return json.loads(content), content, usage.prompt_token_count, usage.candidates_token_count

def get_model_label(provider, model_name, prompt):
    """
    Query specified LLM provider and return standardized JSON result:
    {label, confidence, raw_response, tokens_in, tokens_out, error}
    """
    try:
        if provider == "openai":
            parsed, raw, t_in, t_out = call_openai(model_name, prompt)
        elif provider == "anthropic":
            parsed, raw, t_in, t_out = call_anthropic(model_name, prompt)
        elif provider == "google":
            parsed, raw, t_in, t_out = call_gemini(model_name, prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        return {
            "label": str(parsed.get("label", "")),
            "confidence": float(parsed.get("confidence", 50)),
            "raw_response": raw,
            "tokens_in": t_in,
            "tokens_out": t_out,
            "error": None
        }
    except Exception as e:
        return {
            "label": None,
            "confidence": 0,
            "raw_response": str(e),
            "tokens_in": 0,
            "tokens_out": 0,
            "error": str(e)
        }
