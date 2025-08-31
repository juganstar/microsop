from typing import Dict, Any, Tuple

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

SCHEMAS: Dict[str, Tuple[str, Dict[str, Any]]] = {
    "email": ("EmailAsset", EMAIL_SCHEMA),
    "checklist": ("ChecklistAsset", CHECKLIST_SCHEMA),
    "sms": ("SmsAsset", SMS_SCHEMA),
}
