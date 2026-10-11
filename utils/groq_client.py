"""
groq_client.py
--------------
Thin wrapper around the Groq SDK.

All LLM calls are funnelled through call_llm() so that token limits,
model selection, and error handling live in one place.

Security note:
  - The API key is accepted as a runtime parameter and is NEVER stored,
    logged, written to disk, or added to any global state.
"""

from __future__ import annotations

from typing import List, Dict

from groq import Groq

# -- Constants -----------------------------------------------------------------
MODEL_ID   = "qwen/qwen3.8-27b"
MAX_TOKENS = 1000


def get_client(api_key: str) -> Groq:
    """Return a fresh Groq client bound to the caller-supplied key."""
    return Groq(api_key=api_key)


def call_llm(
    api_key: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = MAX_TOKENS,
) -> str:
    """
    Send *messages* to the LLM and return the assistant's reply as a string.

    Parameters
    ----------
    api_key    : Groq API key supplied by the user at runtime.
    messages   : OpenAI-style message list
                 [{"role": "system"|"user"|"assistant", "content": "..."}].
    temperature: Sampling temperature (0 = deterministic, 1 = creative).
    max_tokens : Hard ceiling on output tokens (default 1000).

    Returns
    -------
    The assistant message text, or an error string starting with "Warning Error".
    """
    try:
        client   = get_client(api_key)
        response = client.chat.completions.create(
            model       = MODEL_ID,
            messages    = messages,
            temperature = temperature,
            max_tokens  = max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:  # noqa: BLE001
        return f"Warning: Error communicating with Groq API: {exc}"
