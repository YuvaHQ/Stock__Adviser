"""
Validation and sanitization helpers.

Two responsibilities live here:

1. `validate_analysis_payload` - validate a raw dict/JSON payload (e.g. from
   Gemini, or from a test fixture) against the strict `AnalysisResult`
   schema, raising `OutputValidationError` with a clear message on failure.
   This is used both by the analyzer's own safety net and directly by
   tests, independent of any Gemini call.

2. `build_verified_sources_used` - construct the final `sources_used` list
   for an AnalysisResult from the *caller-supplied* MarketData sources,
   ignoring whatever (if anything) the LLM produced for that field. This
   guarantees the module never surfaces a fabricated URL or document to
   the end user, per requirement #14 in the project spec.
"""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import ValidationError

from .exceptions import OutputValidationError
from .models import AnalysisResult, MarketData, SourceAttribution


def validate_analysis_payload(payload: Dict[str, Any]) -> AnalysisResult:
    """Validate a raw dict against the AnalysisResult schema.

    Args:
        payload: A plain dict, e.g. `json.loads(raw_text)` or a
            hand-constructed test fixture.

    Returns:
        A validated AnalysisResult.

    Raises:
        OutputValidationError: if the payload does not conform to the
            schema (missing required fields, out-of-range confidence,
            invalid classification enum value, etc.).
    """

    try:
        return AnalysisResult.model_validate(payload)
    except ValidationError as exc:
        raise OutputValidationError(
            f"Analysis output failed validation: {exc}"
        ) from exc


def build_verified_sources_used(market_data: MarketData) -> List[SourceAttribution]:
    """Build the trustworthy `sources_used` list directly from the
    application-supplied MarketData, never from LLM output.

    If the caller supplied no source_documents/document_chunks, this
    correctly returns an empty list rather than allowing any
    model-invented source to pass through.
    """

    return [
        SourceAttribution(
            document_id=doc.document_id,
            title=doc.title,
            source=doc.source,
            url=doc.url,
        )
        for doc in market_data.all_sources()
    ]
