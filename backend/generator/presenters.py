# backend/generator/presenters.py
def result_to_plain_text(result: dict) -> str:
    if not isinstance(result, dict):
        return str(result).strip()

    # Email schema
    if "subject" in result or "body_markdown" in result:
        subject = (result.get("subject") or "").strip()
        body = (result.get("body_markdown") or "").strip()
        summary = (result.get("summary") or "").strip()
        parts = []
        if subject: parts += [subject, ""]
        if body: parts.append(body)
        if summary: parts += ["", f"Resumo / Summary: {summary}"]
        return "\n".join(parts).strip()

    # Checklist schema
    if isinstance(result.get("items"), list):
        title = (result.get("title") or "Checklist").strip()
        lines = [title, ""]
        for i, it in enumerate(result["items"], 1):
            if isinstance(it, dict) and it.get("text"):
                pr = it.get("priority")
                suffix = f" [{pr}]" if pr in ("low", "medium", "high") else ""
                lines.append(f"{i}. {it['text'].strip()}{suffix}")
            elif isinstance(it, str):
                lines.append(f"{i}. {it.strip()}")
        return "\n".join(lines).strip()

    # SMS schema
    if result.get("message"):
        msg = (result.get("message") or "").strip()
        cta = (result.get("cta") or "").strip()
        lines = ["SMS:", msg]
        if cta: lines += ["", f"CTA: {cta}"]
        return "\n".join(lines).strip()

    # Fallback
    return str(result)
