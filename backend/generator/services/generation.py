# backend/generator/services/generation.py
import os
import logging
from generator.openai_client import generate_micro_sop
logger = logging.getLogger(__name__)

def generate_asset(*, prompt: str, language: str, tone: str,
                   audience: str | None, brand_voice: str | None,
                   include_signature: bool, constraints: dict) -> dict:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing")

    # Call with auto_coerce to avoid hard failures
    return generate_micro_sop(
        asset_type="auto",
        prompt=prompt,
        language=language,
        tone=tone,
        audience=audience,
        constraints=constraints,
        brand_voice=brand_voice,
        include_signature=include_signature,
        auto_coerce=True,
    )
