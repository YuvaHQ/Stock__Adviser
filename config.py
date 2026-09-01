"""
Configuration loading for the AI Financial Agent (Gemini) module.

Reads settings from environment variables (optionally populated from a
local .env file via python-dotenv). Never hard-codes, prints, or logs the
API key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .exceptions import ConfigurationError

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# Load a local .env file if present. This is a no-op if the file does not
# exist, and it never overrides variables that are already set in the real
# environment (override=False is the dotenv default).
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable runtime configuration for the Gemini-powered analyzer.

    Attributes:
        gemini_api_key: Secret API key used to authenticate with Gemini.
            Never logged, printed, or included in error messages.
        gemini_model: Model name to use for generation, e.g.
            "gemini-2.5-flash".
        run_gemini_integration_test: Whether the optional live-API
            integration test is allowed to run.
    """

    gemini_api_key: str
    gemini_model: str
    run_gemini_integration_test: bool

    def __repr__(self) -> str:  # pragma: no cover - defensive redaction
        # Guard against accidental logging of the Settings object exposing
        # the API key, even though dataclass __repr__ would normally include
        # every field.
        return (
            "Settings(gemini_api_key='***REDACTED***', "
            f"gemini_model={self.gemini_model!r}, "
            f"run_gemini_integration_test={self.run_gemini_integration_test!r})"
        )

    __str__ = __repr__


def _get_bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_settings(require_api_key: bool = True) -> Settings:
    """Load settings from the environment.

    Args:
        require_api_key: If True (default), raise ConfigurationError when
            GEMINI_API_KEY is missing or empty. Callers that only need
            offline/demo behavior (e.g. building prompts without calling
            the API) may pass False.

    Returns:
        A populated, immutable Settings instance.

    Raises:
        ConfigurationError: If require_api_key is True and GEMINI_API_KEY
            is not set.
    """

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("GEMINI_MODEL", "").strip() or DEFAULT_GEMINI_MODEL
    run_integration_test = _get_bool_env("RUN_GEMINI_INTEGRATION_TEST", False)

    if require_api_key and not api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is not set. Create a .env file (see "
            ".env.example) or export GEMINI_API_KEY in your shell before "
            "running live analyses."
        )

    return Settings(
        gemini_api_key=api_key,
        gemini_model=model,
        run_gemini_integration_test=run_integration_test,
    )
