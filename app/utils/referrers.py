"""Recognise a visitor sent by an AI assistant.

Only a label from a fixed list is ever stored, never the referrer URL, so there
is nothing personal in it. Two signals: the Referer host, and the ``utm_source``
value that assistants such as ChatGPT append to the links they show (many
browsers send no Referer for those clicks).
"""

from urllib.parse import urlparse

# Referer host (or one of its subdomains) -> label. Keep in step with the
# channel regex in docs/runbooks/search-discovery.md.
_AI_DOMAINS = {
    "chatgpt.com": "chatgpt",
    "chat.openai.com": "chatgpt",
    "claude.ai": "claude",
    "perplexity.ai": "perplexity",
    "gemini.google.com": "gemini",
    "copilot.microsoft.com": "copilot",
    "grok.com": "grok",
    "chat.deepseek.com": "deepseek",
    "chat.mistral.ai": "mistral",
}
# utm_source values -> label ("chatgpt.com" is what ChatGPT itself adds).
_AI_UTM = {
    **{domain: label for domain, label in _AI_DOMAINS.items()},
    **{label: label for label in set(_AI_DOMAINS.values())},
}


def ai_source(referer: str | None, utm_source: str | None = None) -> str | None:
    """The assistant label for this visit, or ``None`` when it is not from one."""
    host = (urlparse(referer).hostname or "").lower() if referer else ""
    for domain, label in _AI_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return label
    if utm_source:
        return _AI_UTM.get(utm_source.strip().lower())
    return None
