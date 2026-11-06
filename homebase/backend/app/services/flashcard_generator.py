"""
Flashcard generator — converts raw notes into Q&A pairs.

Provider priority (first available wins):
  1. Ollama  — fully local, zero cost, zero keys.
               Install: https://ollama.com  then  `ollama pull granite3-moe:1b`
  2. Groq    — free cloud tier, no credit card needed.
               Sign up at https://console.groq.com → create a free API key.
               Set GROQ_API_KEY in .env
  3. watsonx — IBM cloud, set WATSONX_API_KEY + WATSONX_PROJECT_ID in .env

The active provider is selected at call time based on which keys / services
are available, so you can switch by simply setting / unsetting env vars.
"""
from __future__ import annotations
import json
from typing import List


_PROMPT_TEMPLATE = """\
You are a study assistant. Convert the notes below into flashcards.
Return ONLY a valid JSON array — no markdown fences, no explanation.
Each element must have exactly two string keys: "question" and "answer".
Aim for concise, exam-style questions. Produce between 5 and 20 cards.

Notes:
{notes}

Flashcards JSON:"""


def _extract_json(text: str) -> str:
    """Return the first [...] block found in the model output."""
    start = text.find("[")
    end   = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Model did not return a JSON array")
    return text[start : end + 1]


def _parse_cards(raw: str) -> List[dict]:
    json_str = _extract_json(raw)
    cards = json.loads(json_str)
    if not isinstance(cards, list):
        raise ValueError("Parsed JSON is not a list")
    validated = []
    for item in cards:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            validated.append({
                "question": str(item["question"]).strip(),
                "answer":   str(item["answer"]).strip(),
            })
    if not validated:
        raise ValueError("No valid flashcards found in model response")
    return validated


# ── Provider implementations ───────────────────────────────────────────────

def _via_ollama(notes: str, model: str) -> List[dict]:
    """
    Uses a locally running Ollama instance (http://localhost:11434).
    No API key required.  Install Ollama then: ollama pull <model>
    Recommended free models:
      granite3-moe:1b   (IBM Granite, ~800 MB)
      llama3.2:3b       (~2 GB)
      phi3:mini         (~2 GB)
    """
    import ollama as _ollama  # lazy import so missing install is a clear error
    response = _ollama.chat(
        model=model,
        messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(notes=notes)}],
        options={"temperature": 0.3},
    )
    return _parse_cards(response.message.content)


def _via_groq(notes: str, model: str, api_key: str) -> List[dict]:
    """
    Uses Groq's free cloud API — fastest zero-cost option.
    Sign up at https://console.groq.com → create API key → set GROQ_API_KEY.
    Free tier: 6 000 req/day, 500 000 tokens/day. No credit card needed.
    """
    from groq import Groq  # lazy import
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(notes=notes)}],
        temperature=0.3,
        max_tokens=1200,
    )
    return _parse_cards(resp.choices[0].message.content)


def _via_watsonx(notes: str, model: str, api_key: str, project_id: str, url: str) -> List[dict]:
    """IBM watsonx.ai — requires paid IBM Cloud account / credits."""
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    credentials = Credentials(url=url, api_key=api_key)
    client = APIClient(credentials=credentials, project_id=project_id)
    inference = ModelInference(
        model_id=model,
        api_client=client,
        params={"max_new_tokens": 1200, "temperature": 0.3},
    )
    raw = inference.generate_text(prompt=_PROMPT_TEMPLATE.format(notes=notes))
    return _parse_cards(raw if isinstance(raw, str) else str(raw))


# ── Public entry point ─────────────────────────────────────────────────────

def generate_flashcards(notes: str) -> List[dict]:
    """
    Generate flashcards from raw notes.
    Tries providers in order: Ollama → Groq → watsonx.
    Raises RuntimeError if no provider is available/configured.
    """
    from ..config import get_settings
    settings = get_settings()

    # 1. Ollama (local, always free, no key)
    try:
        import ollama as _ollama
        # Ping to confirm the daemon is running
        _ollama.list()
        model = settings.ollama_model
        return _via_ollama(notes, model)
    except Exception:
        pass   # Ollama not running / not installed — try next

    # 2. Groq (free cloud tier)
    if settings.groq_api_key:
        return _via_groq(notes, settings.groq_model, settings.groq_api_key)

    # 3. watsonx (paid IBM Cloud)
    if settings.watsonx_api_key and settings.watsonx_project_id:
        return _via_watsonx(
            notes,
            settings.watsonx_model,
            settings.watsonx_api_key,
            settings.watsonx_project_id,
            settings.watsonx_url,
        )

    raise RuntimeError(
        "No AI provider is available. Choose one:\n"
        "  • Ollama (free, local): install from https://ollama.com then "
        "`ollama pull granite3-moe:1b`\n"
        "  • Groq (free cloud): sign up at https://console.groq.com and set "
        "GROQ_API_KEY in .env\n"
        "  • watsonx: set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env"
    )
