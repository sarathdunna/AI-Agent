"""Modular LLM provider abstraction.

Core analytics/ML NEVER depend on this module for numeric computation — it is used
only for natural-language explanation, summarization and NL->SQL text generation,
always fed already-computed real values. When no API key is configured, every
method gracefully returns a clear "AI explanation unavailable" message instead of
raising, so the rest of the app keeps working without any LLM key.
"""
from __future__ import annotations

from app.core.config import get_settings

UNAVAILABLE_MSG = (
    "AI explanation unavailable (no ANTHROPIC_API_KEY configured). "
    "Showing deterministic, computation-based results only."
)


class LLMProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.enabled = bool(settings.ANTHROPIC_API_KEY) and settings.LLM_PROVIDER == "anthropic"
        self.model = settings.LLM_MODEL
        self._client = None
        if self.enabled:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except Exception:
                self.enabled = False
                self._client = None

    def is_available(self) -> bool:
        return self.enabled and self._client is not None

    def complete(self, system: str, prompt: str, max_tokens: int = 4000) -> str:
        """Return an LLM completion, or the unavailable message if no key is set."""
        if not self.is_available():
            return UNAVAILABLE_MSG
        try:
            resp = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,  # leaves room for the model's thinking before the short answer
                system=system,
                messages=[{"role": "user", "content": prompt}],
                # Short explanations and SQL need little reasoning. Sent via extra_body
                # because the pinned SDK version predates the output_config parameter.
                extra_body={"output_config": {"effort": "low"}},
            )
            parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
            return "\n".join(parts).strip() or UNAVAILABLE_MSG
        except Exception as exc:  # noqa: BLE001 - never let LLM errors break core features
            return f"AI explanation unavailable (LLM call failed: {exc.__class__.__name__})."

_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = LLMProvider()
    return _provider
