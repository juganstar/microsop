# backend/generator/services/persist.py
from __future__ import annotations
from typing import Any, Dict
import json
import logging

from django.db import transaction
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import Field
from generator.models import GeneratedAsset
from generator.presenters import result_to_plain_text

logger = logging.getLogger(__name__)


def _get_field(model_cls, name: str) -> Field | None:
    try:
        return model_cls._meta.get_field(name)
    except FieldDoesNotExist:
        return None
    except Exception:
        return None


def _is_concrete_writable(field: Field) -> bool:
    # Skip reverse relations / auto fields
    return getattr(field, "concrete", True) and getattr(field, "editable", True) and not getattr(field, "auto_created", False)


def _internal_type(field: Field) -> str:
    try:
        return field.get_internal_type()
    except Exception:
        return ""


def _find_field_by_names(model_cls, candidates: list[str], type_names: tuple[str, ...]) -> str | None:
    for name in candidates:
        f = _get_field(model_cls, name)
        if f and _is_concrete_writable(f) and _internal_type(f) in type_names:
            return name
    return None


def _find_any_field_by_type(model_cls, type_names: tuple[str, ...]) -> str | None:
    for f in model_cls._meta.get_fields():
        if isinstance(f, Field) and _is_concrete_writable(f) and _internal_type(f) in type_names:
            return f.name
    return None


def _guess_title(asset_type: str, content: Dict[str, Any]) -> str:
    if isinstance(content, dict):
        if content.get("subject"):
            return str(content["subject"])[:140]
        if content.get("title"):
            return str(content["title"])[:140]
    return {"email": "Email", "checklist": "Checklist", "sms": "SMS"}.get(asset_type, "Generated Item")


def save_asset(*, user, prompt_used: str, content: Dict[str, Any], asset_type: str = "auto"):
    """
    Persist the generated asset regardless of your model's exact field names.

    Strategy:
    - Prefer a JSONField named one of: content, data, payload, json, result, output
    - Else, write to a TextField named one of: plain_text, text, body, body_markdown
    - Else, fall back to ANY JSONField, then ANY TextField
    - Optionally set a title/subject if such a field exists
    - Only set fields that actually exist on the model
    """
    Model = GeneratedAsset

    # Preferred field names (JSON then Text)
    json_candidates = ["content", "data", "payload", "json", "result", "output"]
    text_candidates = ["plain_text", "text", "body", "body_markdown", "markdown"]

    # Find suitable fields by type/name
    json_field_name = _find_field_by_names(Model, json_candidates, ("JSONField",))
    text_field_name = _find_field_by_names(Model, text_candidates, ("TextField",))
    # Titles commonly live in CharField/TextField
    title_field_name = _find_field_by_names(Model, ["title", "subject", "name", "headline"], ("CharField", "TextField"))

    # If nothing matched by name, try any JSON/Text field
    if not json_field_name:
        json_field_name = _find_any_field_by_type(Model, ("JSONField",))
    if not text_field_name:
        text_field_name = _find_any_field_by_type(Model, ("TextField",))

    # Build kwargs dynamically based on what exists
    kwargs: Dict[str, Any] = {"user": user}

    if _get_field(Model, "asset_type"):
        kwargs["asset_type"] = asset_type
    if _get_field(Model, "prompt_used"):
        kwargs["prompt_used"] = prompt_used

    # Title/subject if present
    if title_field_name:
        kwargs.setdefault(title_field_name, _guess_title(asset_type, content))

    # Prefer JSON storage; otherwise write pretty text
    if json_field_name:
        kwargs[json_field_name] = content
    elif text_field_name:
        kwargs[text_field_name] = result_to_plain_text(content)
    else:
        # Absolute last resort: dump JSON into the first writable Char/Text field we can find
        fallback_text_name = _find_any_field_by_type(Model, ("CharField", "TextField"))
        if fallback_text_name:
            kwargs[fallback_text_name] = json.dumps(content, ensure_ascii=False)

    with transaction.atomic():
        obj = Model.objects.create(**kwargs)

    logger.info(
        "GeneratedAsset saved. fields=%s",
        {k: ("<json>" if isinstance(v, (dict, list)) else str(v)[:60]) for k, v in kwargs.items()},
    )
    return obj
