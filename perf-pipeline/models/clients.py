import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
import anthropic
from google import genai

# Initialize clients if keys exist
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if os.getenv("ANTHROPIC_API_KEY") else None
genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_openai(model, prompt):
    response = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    usage = response.usage
    return json.loads(content), content, usage.prompt_tokens, usage.completion_tokens

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_anthropic(model, prompt):
    response = anthropic_client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt + "\n\nOutput JSON only."}]
    )
    content = response.content[0].text
    # Basic JSON extraction if wrapped
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    return json.loads(content), content, response.usage.input_tokens, response.usage.output_tokens

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_gemini(model, prompt):
    response = genai_client.models.generate_content(
        model=model,
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    content = response.text
    usage = response.usage_metadata
    return json.loads(content), content, usage.prompt_token_count, usage.candidates_token_count

def get_model_label(provider, model_name, prompt):
    """
    Returns {label, confidence, raw_response, tokens_in, tokens_out}
    """
    try:
        if provider == "openai":
            parsed, raw, t_in, t_out = call_openai(model_name, prompt)
        elif provider == "anthropic":
            parsed, raw, t_in, t_out = call_anthropic(model_name, prompt)
        elif provider == "google":
            parsed, raw, t_in, t_out = call_gemini(model_name, prompt)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
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
