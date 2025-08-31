def extract_json_text(resp: object) -> str:
    """
    Try multiple SDK response shapes to get the JSON output string.
    """
    try:
        if hasattr(resp, "output") and resp.output:
            content_items = resp.output[0].content
            text_chunks = [c.text for c in content_items if getattr(c, "type", "") == "output_text" and getattr(c, "text", None)]
            if text_chunks:
                return text_chunks[0]
    except Exception:
        pass

    try:
        return resp.output_text
    except Exception:
        pass

    try:
        return resp.choices[0].message["content"]
    except Exception:
        pass

    raise ValueError("Could not extract JSON text from model response")
