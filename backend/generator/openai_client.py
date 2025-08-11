# backend/generator/openai_client.py
from typing import Literal, Optional, Dict, Any
from openai import OpenAI
import json

AssetType = Literal["email", "checklist", "sms"]

client = OpenAI()

# --- JSON Schemas for strict output ---
EMAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "body_markdown": {"type": "string"},
        "summary": {"type": "string"},
    },
    "required": ["subject", "body_markdown"],
    "additionalProperties": False,
}

CHECKLIST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["text"],
                "additionalProperties": False,
            },
            "minItems": 3
        }
    },
    "required": ["title", "items"],
    "additionalProperties": False,
}

SMS_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string", "maxLength": 320},
        "cta": {"type": "string"},
    },
    "required": ["message"],
    "additionalProperties": False,
}

SCHEMAS = {
    "email": ("EmailAsset", EMAIL_SCHEMA),
    "checklist": ("ChecklistAsset", CHECKLIST_SCHEMA),
    "sms": ("SmsAsset", SMS_SCHEMA),
}

SYSTEM_PROMPT = """You are a senior ops copywriter.
- Output must follow the JSON schema exactly (no extra keys).
- Keep it concise, actionable, and free of fluff.
- Use the requested language and tone.
- Never include secrets, unsafe advice, or illegal guidance.
"""

def _build_user_prompt(
    asset_type: AssetType,
    prompt: str,
    *,
    language: Literal["en", "pt"] = "en",
    tone: Literal["professional", "friendly", "urgent", "casual"] = "professional",
    audience: Optional[str] = None,
    constraints: Optional[str] = None,
    brand_voice: Optional[str] = None,
    include_signature: bool = False,
) -> str:
    pieces = [
        f"Asset type: {asset_type}",
        f"Language: {'English' if language=='en' else 'Português (PT)'}",
        f"Tone: {tone}",
        f"Audience: {audience or 'general client'}",
        f"Constraints: {constraints or 'be clear, short, and specific'}",
        f"Brand voice: {brand_voice or 'neutral'}",
        f"Include signature: {include_signature}",
        "User brief:",
        prompt.strip()
    ]
    return "\n".join(pieces)

def generate_micro_sop(
    asset_type: AssetType,
    prompt: str,
    *,
    language: Literal["en", "pt"] = "en",
    tone: Literal["professional", "friendly", "urgent", "casual"] = "professional",
    audience: Optional[str] = None,
    constraints: Optional[str] = None,
    brand_voice: Optional[str] = None,
    include_signature: bool = False,
    model: str = "gpt-4o-mini",
    temperature: float = 0.4,
    max_output_tokens: int = 1200,
) -> Dict[str, Any]:
    """
    Returns a dict matching the JSON schema for the asset_type.
    Raises ValueError on schema mismatch.
    """
    if asset_type not in SCHEMAS:
        raise ValueError(f"Unsupported asset_type: {asset_type}")

    schema_name, schema_def = SCHEMAS[asset_type]
    user_prompt = _build_user_prompt(
        asset_type, prompt,
        language=language, tone=tone, audience=audience,
        constraints=constraints, brand_voice=brand_voice,
        include_signature=include_signature,
    )

    resp = client.responses.create(
        model=model,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "schema": schema_def,
                "strict": True,
            }
        },
    )

    # Extract JSON text safely (Responses API returns output in a content array)
    try:
        content_items = resp.output if hasattr(resp, "output") else resp  # SDK variance safety
        # Prefer the first text item
        if hasattr(resp, "output") and content_items and getattr(content_items[0], "content", None):
            text_chunks = [c.text for c in content_items[0].content if getattr(c, "type", "") == "output_text"]
            json_text = text_chunks[0] if text_chunks else ""
        else:
            # Fallback for older SDKs:
            json_text = resp.output_text  # may exist on some versions
    except Exception:
        # Last-resort parse path: some SDKs expose choices[0].message.content
        try:
            json_text = resp.choices[0].message["content"]
        except Exception as e:
            raise ValueError(f"Unexpected API response shape: {e}")

    try:
        data = json.loads(json_text)
    except Exception as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw: {json_text[:500]}")

    # Minimal schema sanity checks (the API enforces, we just double-check required keys)
    required = schema_def.get("required", [])
    for key in required:
        if key not in data:
            raise ValueError(f"Missing required key '{key}' in model output")

    return data
