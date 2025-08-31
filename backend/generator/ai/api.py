import json
from typing import Dict, Any
from openai import OpenAI
try:
    # v1-style exceptions
    from openai import RateLimitError, APITimeoutError, APIError
except Exception:  # very old SDK fallback
    RateLimitError = Exception
    APITimeoutError = Exception
    APIError = Exception

from .parsing import extract_json_text
from .errors import ModelQuotaExceeded, ModelRateLimited, ModelTimeout, ModelAPIError

client = OpenAI()

def _is_insufficient_quota(err: Exception) -> bool:
    # Inspect the serialized body if present
    try:
        body = getattr(err, "response", None)
        if body is None:
            body = getattr(err, "body", None)
        if body and hasattr(body, "json"):
            data = body.json()
        else:
            data = body
        msg = ""
        code = ""
        if isinstance(data, dict):
            err_obj = data.get("error") or {}
            msg = (err_obj.get("message") or "").lower()
            code = (err_obj.get("code") or "").lower()
        else:
            msg = str(err).lower()
        return "insufficient_quota" in code or "insufficient quota" in msg
    except Exception:
        return False

def call_model_with_schema(
    *,
    user_prompt: str,
    schema_name: str,
    schema_def: Dict[str, Any],
    system_prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
) -> str:
    """
    Wide-compat call:
      1) Responses API with messages=
      2) Responses API with input=
      3) Chat Completions fallback

    Returns raw JSON text OR raises typed exceptions for the caller to handle.
    """
    schema_payload = {
        "type": "json_schema",
        "json_schema": {"name": schema_name, "schema": schema_def, "strict": True},
    }

    # Helper to normalize OpenAI exceptions -> typed
    def _map_error(e: Exception):
        if isinstance(e, RateLimitError):
            if _is_insufficient_quota(e):
                raise ModelQuotaExceeded(str(e))
            raise ModelRateLimited(str(e))
        if isinstance(e, APITimeoutError):
            raise ModelTimeout(str(e))
        if isinstance(e, APIError):
            raise ModelAPIError(str(e))
        raise ModelAPIError(str(e))

    # 1) responses.create(..., messages=[...])
    try:
        resp = client.responses.create(
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=schema_payload,
        )
        return extract_json_text(resp)
    except TypeError:
        pass
    except Exception as e:
        _map_error(e)

    # 2) responses.create(..., input=[...])
    try:
        resp = client.responses.create(
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            input=[
                {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "text", "text": user_prompt}]},
            ],
            response_format=schema_payload,
        )
        return extract_json_text(resp)
    except Exception as e:
        # continue to chat fallback
        pass

    # 3) chat.completions.create
    try:
        comp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt + "\nReturn ONLY minified JSON matching the schema."},
                {"role": "user", "content": user_prompt},
            ],
        )
        return comp.choices[0].message.content if comp.choices else ""
    except Exception as e:
        _map_error(e)
        raise  # not reached
