"""
Main public API for the AI Financial Agent (Gemini) module.

Teammates integrating this module should only need:

    from src.analyzer import FinancialAnalyzer
    from src.models import MarketData, UserProfile

    analyzer = FinancialAnalyzer()
    result = analyzer.analyze(market_data=market_data, user_profile=user_profile)

`FinancialAnalyzer` owns request orchestration (id generation, timing,
logging, metrics, retries) and delegates all Gemini-specific work to
`GeminiClient`. It never imports `google.genai` directly.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Optional

from .config import Settings, load_settings
from .exceptions import (
    FinancialAgentError,
    GeminiRateLimitError,
    GeminiServiceError,
    OutputValidationError,
)
from .gemini_client import GeminiClient
from .models import (
    AnalysisMetadata,
    AnalysisResponse,
    AnalysisResult,
    MarketData,
    UserProfile,
)
from .prompts import SYSTEM_INSTRUCTION, build_user_prompt
from .validators import build_verified_sources_used, validate_analysis_payload

logger = logging.getLogger("ai_financial_agent_gemini.analyzer")

# Errors worth a single bounded retry: transient rate limiting and
# ambiguous service/network failures. Auth, quota, request, and
# validation errors are never retried automatically.
_RETRYABLE_ERRORS = (GeminiRateLimitError, GeminiServiceError)


class FinancialAnalyzer:
    """High-level entry point for turning MarketData + UserProfile into a
    validated, source-attributed AnalysisResult via Gemini."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        gemini_client: Optional[GeminiClient] = None,
        max_retries: int = 1,
        retry_backoff_seconds: float = 1.5,
    ) -> None:
        """
        Args:
            settings: Pre-loaded Settings. If omitted, loaded from the
                environment on first use (requires GEMINI_API_KEY).
            gemini_client: Inject a pre-built GeminiClient (e.g. a mock in
                tests). If omitted, one is built lazily from `settings`.
            max_retries: Maximum number of *additional* attempts for
                transient errors (rate limit / service errors). 0 disables
                retries. Never applies to auth/quota/request/validation
                errors.
            retry_backoff_seconds: Base delay between retries; grows
                linearly with attempt number.
        """

        self._settings = settings
        self._client = gemini_client
        self._max_retries = max(0, max_retries)
        self._retry_backoff_seconds = retry_backoff_seconds

    # -- public API -------------------------------------------------

    def analyze(
        self, market_data: MarketData, user_profile: UserProfile
    ) -> AnalysisResult:
        """Run a full analysis and return only the AnalysisResult.

        Raises:
            FinancialAgentError (or a subclass) on any failure - see
            exceptions.py for the full hierarchy.
        """

        response = self.analyze_with_metadata(market_data, user_profile)
        return response.result

    def analyze_with_metadata(
        self, market_data: MarketData, user_profile: UserProfile
    ) -> AnalysisResponse:
        """Run a full analysis and return both the result and request
        metadata (latency, token usage, validation status, etc.).

        Raises:
            FinancialAgentError (or a subclass) on any failure.
        """

        request_id = str(uuid.uuid4())
        client = self._get_client()
        model_name = client.model_name
        start = time.perf_counter()
        retry_count = 0

        prompt = build_user_prompt(market_data, user_profile)

        last_error: Optional[Exception] = None
        while True:
            try:
                call_result = client.generate_structured(
                    system_instruction=SYSTEM_INSTRUCTION,
                    user_prompt=prompt,
                    response_schema=AnalysisResult,
                )
                break
            except _RETRYABLE_ERRORS as exc:
                last_error = exc
                if retry_count >= self._max_retries:
                    latency_ms = int((time.perf_counter() - start) * 1000)
                    self._log_failure(
                        request_id, market_data.symbol, model_name, latency_ms, exc, retry_count
                    )
                    raise
                retry_count += 1
                logger.warning(
                    "gemini_transient_error request_id=%s symbol=%s attempt=%d error_type=%s - retrying",
                    request_id,
                    market_data.symbol,
                    retry_count,
                    exc.__class__.__name__,
                )
                time.sleep(self._retry_backoff_seconds * retry_count)
                continue
            except FinancialAgentError as exc:
                latency_ms = int((time.perf_counter() - start) * 1000)
                self._log_failure(
                    request_id, market_data.symbol, model_name, latency_ms, exc, retry_count
                )
                raise

        latency_ms = int((time.perf_counter() - start) * 1000)

        output_validation_success = True
        try:
            # Defense in depth: even though GeminiClient already validated
            # the parsed object against AnalysisResult, re-validate the
            # dict form here so this safety net is exercised independent
            # of SDK internals, and so a bad `.parsed` object can never
            # silently slip through.
            validated_result = validate_analysis_payload(
                call_result.parsed.model_dump(mode="json")
            )
        except OutputValidationError as exc:
            output_validation_success = False
            self._log_failure(
                request_id, market_data.symbol, model_name, latency_ms, exc, retry_count
            )
            raise

        # Overwrite sources_used with application-verified data regardless
        # of what the model produced, so a fabricated source can never
        # reach the caller.
        verified_sources = build_verified_sources_used(market_data)
        final_result = validated_result.model_copy(
            update={"sources_used": verified_sources}
        )

        metadata = AnalysisMetadata(
            request_id=request_id,
            symbol=market_data.symbol,
            model=model_name,
            latency_ms=latency_ms,
            success=True,
            output_validation_success=output_validation_success,
            retry_count=retry_count,
            prompt_tokens=call_result.prompt_tokens,
            response_tokens=call_result.response_tokens,
            total_tokens=call_result.total_tokens,
            confidence=final_result.confidence,
            simulated=False,
        )

        logger.info(
            "gemini_analysis_success request_id=%s symbol=%s model=%s latency_ms=%d "
            "classification=%s confidence=%.2f retry_count=%d",
            request_id,
            market_data.symbol,
            model_name,
            latency_ms,
            final_result.classification.value,
            final_result.confidence,
            retry_count,
        )

        return AnalysisResponse(result=final_result, metadata=metadata)

    # -- internal helpers --------------------------------------------

    def _get_client(self) -> GeminiClient:
        if self._client is not None:
            return self._client
        settings = self._settings or load_settings(require_api_key=True)
        self._settings = settings
        self._client = GeminiClient(settings)
        return self._client

    def _log_failure(
        self,
        request_id: str,
        symbol: str,
        model_name: str,
        latency_ms: int,
        exc: Exception,
        retry_count: int,
    ) -> None:
        # Never log exc's raw args if they could theoretically contain
        # request headers; our custom exceptions' messages are already
        # scrubbed of secrets in gemini_client.py.
        logger.error(
            "gemini_analysis_failure request_id=%s symbol=%s model=%s latency_ms=%d "
            "error_type=%s retry_count=%d",
            request_id,
            symbol,
            model_name,
            latency_ms,
            exc.__class__.__name__,
            retry_count,
        )
