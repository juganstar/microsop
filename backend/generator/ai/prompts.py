# backend/generator/ai/prompts.py
from typing import Optional, Literal
from .types import AssetType

SYSTEM_PROMPT = """You are a senior ops copywriter.
- Output must follow the JSON schema exactly (no extra keys).
- Keep it concise, actionable, and free of fluff.
- Use the requested language and tone.
- Never include secrets, unsafe advice, or illegal guidance.
"""

def build_user_prompt(
    asset_type: AssetType,
    prompt: str,
    *,
    language: Literal["en", "pt"] = "en",
    tone: Literal["professional", "friendly", "urgent", "casual"] = "professional",
    audience: Optional[str] = None,
    constraints: Optional[str] = None,
    brand_voice: Optional[str] = None,
    include_signature: bool = False,
    niche: Optional[str] = None,
    niche_guide: Optional[str] = None,
) -> str:
    pieces = [
        f"Asset type: {asset_type}",
        f"Language: {'English' if language=='en' else 'Português (PT)'}",
        f"Tone: {tone}",
        f"Audience: {audience or 'general client'}",
        f"Constraints: {constraints or 'be clear, short, and specific'}",
        f"Brand voice: {brand_voice or 'neutral'}",
        f"Include signature: {include_signature}",
    ]
    if niche:
        pieces.append(f"Niche: {niche}")
    if niche_guide:
        pieces += ["Niche guide:", niche_guide]
    pieces += ["User brief:", prompt.strip()]
    return "\n".join(pieces)

def detect_asset_type(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["sms", "text message", "texto curto", "mensagem curta", "send a text", "send an sms"]):
        return "sms"
    if any(k in p for k in ["checklist", "to-do", "tarefas", "passos", "steps", "task list"]):
        return "checklist"
    return "email"
