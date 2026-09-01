"""
Custom exception hierarchy for the AI Financial Agent (Gemini) module.

All exceptions raised by this package derive from ``FinancialAgentError`` so
callers (teammates integrating this module) can catch broadly with a single
``except FinancialAgentError`` or narrowly with a specific subclass.

None of these exceptions must ever include the raw API key or authorization
headers in their message. See ``gemini_client.py`` for how errors from the
Gemini SDK are translated into these types without leaking secrets.
"""

from __future__ import annotations


class FinancialAgentError(Exception):
    """Base class for all errors raised by this module."""


class ConfigurationError(FinancialAgentError):
    """Raised when required configuration (e.g. GEMINI_API_KEY) is missing
    or invalid. Never includes the value of any secret in its message."""


class GeminiError(FinancialAgentError):
    """Base class for all errors originating from the Gemini API layer."""


class GeminiAuthenticationError(GeminiError):
    """Raised when the Gemini API rejects the request due to an invalid or
    missing API key (HTTP 401/403 style errors)."""


class GeminiQuotaError(GeminiError):
    """Raised when the Gemini API reports that the account/project has
    exhausted its quota (as opposed to a transient rate limit)."""


class GeminiRateLimitError(GeminiError):
    """Raised when the Gemini API reports a transient rate limit (HTTP 429)."""


class GeminiRequestError(GeminiError):
    """Raised when the request sent to Gemini was malformed (bad schema,
    bad arguments, invalid model name, etc.) - a client-side (4xx) problem
    that is not an auth, quota, or rate-limit issue."""


class GeminiServiceError(GeminiError):
    """Raised for network failures, timeouts, or Gemini-side (5xx) service
    errors that are not the caller's fault."""


class OutputValidationError(FinancialAgentError):
    """Raised when the Gemini response could not be parsed into / validated
    against the expected structured output schema."""
