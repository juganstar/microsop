# backend/generator/ai/coercers.py
from typing import Any, Dict, List, Optional
import re

def first_string(*vals) -> Optional[str]:
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def truncate(s: str, max_len: int) -> str:
    return s if len(s) <= max_len else (s[: max_len - 1] + "…")

def _sanitize_line(ln: str) -> str:
    ln = ln.strip()
    ln = ln.lstrip("-*• ").strip()
    ln = ln.strip(" ,.;:—–-").strip()
    ln = re.sub(r"\s+", " ", ln)
    return ln

def _is_generic_label(s: str) -> bool:
    s = s.lower().strip()
    return s in {
        "", "checklist", "check list", "lista", "lista de tarefas",
        "tarefas", "to-do", "todo", "steps", "passos"
    }

# -----------------------
# Coercers (auto-repair)
# -----------------------
def _coerce_email(data: Any, fallback_prompt: str) -> Dict[str, Any]:
    if not isinstance(data, dict):
        if isinstance(data, str):
            body = data.strip()
            return {"subject": "Follow-up / Update", "body_markdown": body, "summary": body[:160]}
        return {
            "subject": "Follow-up / Update",
            "body_markdown": fallback_prompt.strip(),
            "summary": fallback_prompt[:160],
        }

    subject = first_string(
        data.get("subject"), data.get("title"), data.get("headline"), "Follow-up / Update"
    )
    body = first_string(
        data.get("body_markdown"), data.get("body"), data.get("content"), data.get("message")
    )
    if not body:
        if isinstance(data.get("items"), list):
            bullets = [
                f"- {_sanitize_line(str(i.get('text')))}"
                for i in data["items"]
                if isinstance(i, dict) and i.get("text")
            ]
            body = "\n".join([b for b in bullets if not _is_generic_label(b[2:].strip())]) or fallback_prompt
        else:
            body = fallback_prompt

    summary = first_string(data.get("summary"), body[:160])
    return {"subject": subject, "body_markdown": body, "summary": summary}

def _coerce_checklist(data: Any, fallback_prompt: str, *, language: str = "en") -> Dict[str, Any]:
    title = "Checklist" if language == "en" else "Checklist"
    items: List[Dict[str, str]] = []

    if isinstance(data, dict):
        title = first_string(data.get("title"), data.get("subject"), title) or title
        raw_items = data.get("items") if isinstance(data.get("items"), list) else data.get("steps")
        if isinstance(raw_items, list):
            for it in raw_items:
                if isinstance(it, dict) and it.get("text"):
                    pr = it.get("priority") if it.get("priority") in ("low", "medium", "high") else "medium"
                    txt = _sanitize_line(str(it["text"]))
                    if not _is_generic_label(txt):
                        items.append({"text": txt, "priority": pr})
                elif isinstance(it, str):
                    txt = _sanitize_line(it)
                    if txt and not _is_generic_label(txt):
                        items.append({"text": txt, "priority": "medium"})
    elif isinstance(data, list):
        for it in data:
            if isinstance(it, str):
                txt = _sanitize_line(it)
                if txt and not _is_generic_label(txt):
                    items.append({"text": txt, "priority": "medium"})

    if not items:
        raw_lines: List[str] = []
        for ln in fallback_prompt.splitlines():
            parts = re.split(r"[•\-\u2022]|[.;,\n]", ln)
            raw_lines.extend([p for p in parts if p is not None])

        lines: List[str] = []
        for ln in raw_lines:
            s = _sanitize_line(ln)
            if s and not _is_generic_label(s):
                lines.append(s)

        for s in lines[:7]:
            items.append({"text": s, "priority": "medium"})

    # Meaningful fillers in both languages
    FILLERS_EN = [
        {"text": "Clarify objective & success criteria", "priority": "high"},
        {"text": "List tasks with owners and deadlines", "priority": "medium"},
        {"text": "Prepare required resources/materials", "priority": "medium"},
        {"text": "Review quality and finalize delivery", "priority": "medium"},
        {"text": "Confirm next steps & follow-up", "priority": "low"},
    ]
    FILLERS_PT = [
        {"text": "Clarificar objetivo e critérios de sucesso", "priority": "high"},
        {"text": "Listar tarefas com responsáveis e prazos", "priority": "medium"},
        {"text": "Preparar recursos/materiais necessários", "priority": "medium"},
        {"text": "Rever qualidade e finalizar entrega", "priority": "medium"},
        {"text": "Confirmar próximos passos e follow-up", "priority": "low"},
    ]
    fillers = FILLERS_PT if language == "pt" else FILLERS_EN

    i = 0
    while len(items) < 3 and i < len(fillers):
        items.append(fillers[i])
        i += 1

    items = items[:12]
    title = _sanitize_line(title) or ("Checklist" if language == "en" else "Checklist")
    return {"title": title, "items": items}

def _coerce_sms(data: Any, fallback_prompt: str, *, language: str = "en") -> Dict[str, Any]:
    message = None
    cta = None
    if isinstance(data, dict):
        message = first_string(data.get("message"), data.get("text"), data.get("body"))
        cta = first_string(data.get("cta"), data.get("action"))
    elif isinstance(data, str):
        message = data.strip()

    if not message:
        base = re.sub(r"\s+", " ", fallback_prompt.strip())
        if language == "pt":
            message = (base[:180].strip()) or "Olá! Preciso da sua confirmação. Pode responder a este SMS?"
        else:
            message = (base[:180].strip()) or "Hi! Quick confirmation needed. Please reply to this SMS."

    payload: Dict[str, str] = {"message": truncate(message, 320)}
    if cta:
        payload["cta"] = truncate(cta, 120)
    return payload

def coerce_to_schema(asset_type: str, raw: Any, fallback_prompt: str, *, language: str = "en") -> Dict[str, Any]:
    if asset_type == "email":
        return _coerce_email(raw, fallback_prompt)
    if asset_type == "checklist":
        return _coerce_checklist(raw, fallback_prompt, language=language)
    if asset_type == "sms":
        return _coerce_sms(raw, fallback_prompt, language=language)
    return _coerce_email(raw, fallback_prompt)
