class ModelQuotaExceeded(Exception):
    """OpenAI account has no quota or was rate-limited with insufficient_quota."""
    pass

class ModelRateLimited(Exception):
    """Temporary 429 without insufficient_quota; backoff and retry later."""
    pass

class ModelTimeout(Exception):
    """Upstream timeout."""
    pass

class ModelAPIError(Exception):
    """Generic upstream failure."""
    pass
