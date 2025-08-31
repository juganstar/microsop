# backend/generator/ai/public.py
from __future__ import annotations

import json
from typing import Optional, Dict, Any, Literal

from .types import AssetType
from .schemas import SCHEMAS
from .prompts import SYSTEM_PROMPT, build_user_prompt, detect_asset_type
from .niches import niche_guide as build_niche_guide
from .coercers import coerce_to_schema, truncate
from .api import call_model_with_schema, client
from .errors import ModelQuotaExceeded, ModelRateLimited, ModelTimeout, ModelAPIError


def generate_micro_sop(
    asset_type: AssetType,
    prompt: str,
    *,
    language: Literal["en", "pt"] = "en",   # <-- output language is user-selected
    tone: Literal["professional", "friendly", "urgent", "casual"] = "professional",
    audience: Optional[str] = None,
    constraints: Optional[Any] = None,  # may be a dict (we read constraints["niche"]) or a string
    brand_voice: Optional[str] = None,
    include_signature: bool = False,
    model: str = "gpt-4o-mini",
    temperature: float = 0.4,
    max_output_tokens: int = 1200,
    auto_coerce: bool = True,
) -> Dict[str, Any]:
    """
    - Select schema by asset_type (or auto-detect).
    - Build user prompt incl. niche guide and requested output language (EN/PT).
    - Call model with SDK-compatible wrapper.
    - On upstream failure, synthesize a valid object (respecting language).
    """
    if asset_type not in ("email", "checklist", "sms", "auto"):
        raise ValueError(f"Unsupported asset_type: {asset_type}")

    resolved_type = detect_asset_type(prompt) if asset_type == "auto" else asset_type
    schema_name, schema_def = SCHEMAS[resolved_type]

    # Niche (from constraints dict, if present)
    niche_slug: Optional[str] = None
    if isinstance(constraints, dict):
        niche_slug = constraints.get("niche")
    guide = build_niche_guide(niche_slug)

    user_prompt = build_user_prompt(
        resolved_type,
        prompt,
        language=language,
        tone=tone,
        audience=audience,
        constraints=constraints,   # dict OK; it will be stringified
        brand_voice=brand_voice,
        include_signature=include_signature,
        niche=niche_slug,
        niche_guide=guide,
    )

    # Call model, with graceful fallbacks
    try:
        json_text = call_model_with_schema(
            user_prompt=user_prompt,
            schema_name=schema_name,
            schema_def=schema_def,
            system_prompt=SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
    except (ModelQuotaExceeded, ModelRateLimited, ModelTimeout, ModelAPIError) as e:
        if auto_coerce:
            # Synthesize minimal valid asset from the prompt (respect language)
            data = coerce_to_schema(resolved_type, None, prompt, language=language)
            if resolved_type == "sms":
                data["message"] = truncate(str(data.get("message", "")), 320)
                if "cta" in data and data["cta"]:
                    data["cta"] = truncate(str(data["cta"]), 120)
            if resolved_type == "email":
                data.setdefault("summary", str(data.get("body_markdown", ""))[:160])
            return data
        # clean, user-facing error
        msg = "Upstream model unavailable"
        if isinstance(e, ModelQuotaExceeded):
            msg = "Model quota exceeded"
        elif isinstance(e, ModelRateLimited):
            msg = "Model temporarily rate-limited"
        elif isinstance(e, ModelTimeout):
            msg = "Upstream model timeout"
        raise ValueError(msg) from e

    # Parse or coerce to schema
    try:
        data = json.loads(json_text)
        for key in schema_def.get("required", []):
            if key not in data:
                raise KeyError(f"Missing required key '{key}'")
    except Exception:
        if not auto_coerce:
            snippet = (json_text or "")[:500]
            raise ValueError(f"Model did not return valid {resolved_type} JSON. Raw snippet:\n{snippet}")
        try:
            parsed_any = json.loads(json_text) if json_text else None
        except Exception:
            parsed_any = None
        data = coerce_to_schema(resolved_type, parsed_any, prompt, language=language)

    # Final polish per type
    if resolved_type == "sms":
        data["message"] = truncate(str(data.get("message", "")), 320)
        if "cta" in data and data["cta"]:
            data["cta"] = truncate(str(data["cta"]), 120)
    if resolved_type == "email":
        data.setdefault("summary", str(data.get("body_markdown", ""))[:160])

    return data


__all__ = ["generate_micro_sop", "client", "AssetType"]
