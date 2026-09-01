"""
Low-level Gemini API client wrapper.

This is the ONLY module that talks to the `google-genai` SDK. It is
responsible for:
  - initializing the client
  - sending the structured-output request
  - parsing the response into the requested Pydantic model
  - translating SDK exceptions into this package's custom exception
    hierarchy (src/exceptions.py) without leaking the API key
  - reporting basic usage/token metadata back to the caller

`analyzer.py` depends only on this module's public interface and never
imports `google.genai` directly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from pydantic import BaseModel, ValidationError

from .config import Settings
from .exceptions import (
    GeminiAuthenticationError,
    GeminiQuotaError,
    GeminiRateLimitError,
    GeminiRequestError,
    GeminiServiceError,
    OutputValidationError,
)

logger = logging.getLogger("ai_financial_agent_gemini.gemini_client")

TModel = TypeVar("TModel", bound=BaseModel)

# HTTP status codes that indicate the API key itself was rejected.
_AUTH_STATUS_CODES = {401, 403}
# HTTP status code Gemini uses for rate limiting AND quota exhaustion; we
# disambiguate using the message/status text since both map to 429.
_RATE_LIMIT_STATUS_CODE = 429


@dataclass(frozen=True)
class GeminiCallResult:
    """Result of a single successful Gemini structured-output call."""

    parsed: BaseModel
    raw_text: Optional[str]
    prompt_tokens: Optional[int]
    response_tokens: Optional[int]
    total_tokens: Optional[int]


class GeminiClient:
    """Thin, defensive wrapper around the google-genai SDK.

    Example:
        client = GeminiClient(settings)
        result = client.generate_structured(
            system_instruction=SYSTEM_INSTRUCTION,
            user_prompt=prompt_text,
            response_schema=AnalysisResult,
        )
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # genai.Client reads the key from the argument, never from a
        # module-level global, so there is nothing to leak via logging here.
        self._client = genai.Client(api_key=settings.gemini_api_key)

    @property
    def model_name(self) -> str:
        return self._settings.gemini_model

    def generate_structured(
        self,
        *,
        system_instruction: str,
        user_prompt: str,
        response_schema: Type[TModel],
        temperature: float = 0.2,
    ) -> GeminiCallResult:
        """Call Gemini and parse the response into `response_schema`.

        Raises:
            GeminiAuthenticationError, GeminiQuotaError,
            GeminiRateLimitError, GeminiRequestError, GeminiServiceError:
                on various failure modes from the SDK/API.
            OutputValidationError: if the API call succeeded but the
                response could not be parsed/validated into the requested
                schema.
        """

        config = genai_types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=temperature,
        )

        try:
            response = self._client.models.generate_content(
                model=self._settings.gemini_model,
                contents=user_prompt,
                config=config,
            )
        except genai_errors.ClientError as exc:
            raise self._translate_client_error(exc) from exc
        except genai_errors.ServerError as exc:
            raise GeminiServiceError(
                f"Gemini service error (code={getattr(exc, 'code', 'unknown')}): "
                f"{getattr(exc, 'message', str(exc))}"
            ) from exc
        except genai_errors.APIError as exc:
            # Fallback for any APIError subclass not explicitly handled
            # above.
            raise self._translate_client_error(exc) from exc
        except Exception as exc:  # noqa: BLE001 - network/timeout/etc.
            raise GeminiServiceError(
                f"Unexpected error calling Gemini API: {exc.__class__.__name__}: {exc}"
            ) from exc

        return self._parse_response(response, response_schema)

    # -- internal helpers ---------------------------------------------

    def _translate_client_error(self, exc: genai_errors.APIError) -> Exception:
        code = getattr(exc, "code", None)
        status = (getattr(exc, "status", None) or "").upper()
        message = getattr(exc, "message", None) or str(exc)

        safe_message = f"Gemini API error (code={code}, status={status}): {message}"

        if code in _AUTH_STATUS_CODES or "UNAUTHENTICATED" in status or "PERMISSION_DENIED" in status:
            return GeminiAuthenticationError(safe_message)

        if code == _RATE_LIMIT_STATUS_CODE or status == "RESOURCE_EXHAUSTED":
            # Gemini uses 429 / RESOURCE_EXHAUSTED for both hard quota
            # exhaustion and transient rate limiting. Use the message text
            # to disambiguate; default to the more conservative "quota"
            # classification (no automatic retry) when uncertain.
            lowered = message.lower()
            if "quota" in lowered or "exceeded your current quota" in lowered:
                return GeminiQuotaError(safe_message)
            return GeminiRateLimitError(safe_message)

        if code is not None and 400 <= code < 500:
            return GeminiRequestError(safe_message)

        return GeminiServiceError(safe_message)

    def _parse_response(
        self, response: genai_types.GenerateContentResponse, response_schema: Type[TModel]
    ) -> GeminiCallResult:
        usage = response.usage_metadata
        prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        response_tokens = getattr(usage, "response_token_count", None) if usage else None
        total_tokens = getattr(usage, "total_token_count", None) if usage else None

        # The SDK will already attempt to populate `.parsed` when a Pydantic
        # response_schema was supplied and the response was valid JSON
        # matching it. Prefer that; fall back to manually validating
        # `.text` for SDK versions/edge cases where `.parsed` is absent.
        parsed_obj = getattr(response, "parsed", None)

        if isinstance(parsed_obj, response_schema):
            return GeminiCallResult(
                parsed=parsed_obj,
                raw_text=getattr(response, "text", None),
                prompt_tokens=prompt_tokens,
                response_tokens=response_tokens,
                total_tokens=total_tokens,
            )

        raw_text = getattr(response, "text", None)
        if not raw_text:
            raise OutputValidationError(
                "Gemini response contained no parsed object and no text "
                "payload to validate."
            )

        try:
            validated = response_schema.model_validate_json(raw_text)
        except ValidationError as exc:
            raise OutputValidationError(
                f"Gemini response failed schema validation: {exc}"
            ) from exc

        return GeminiCallResult(
            parsed=validated,
            raw_text=raw_text,
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            total_tokens=total_tokens,
        )
