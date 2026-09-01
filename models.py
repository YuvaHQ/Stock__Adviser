"""
Pydantic models for the AI Financial Agent (Gemini) module.

These models define:
  * Inputs the caller supplies: MarketData, UserProfile, SourceDocument /
    DocumentChunk.
  * The structured output produced by Gemini: AnalysisResult and its
    nested signal-dimension objects.
  * Supporting metadata: AnalysisMetadata.

Design notes:
  - Optional market-data fields are genuinely optional (default None) so
    partial/real-time data does not fail validation.
  - `sources_used` on the output is populated by application code from the
    caller-supplied source metadata, not trusted from the LLM directly.
    See analyzer.py for how this is enforced.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SignalClassification(str, Enum):
    """Classification value used for the overall signal and for each
    individual signal dimension."""

    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    UNKNOWN = "UNKNOWN"


class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class InvestmentHorizon(str, Enum):
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ---------------------------------------------------------------------------
# Input models: market data
# ---------------------------------------------------------------------------


class TechnicalIndicators(BaseModel):
    """Technical indicators for a symbol. All fields optional since not
    every data feed supplies every indicator."""

    model_config = ConfigDict(extra="forbid")

    rsi: Optional[float] = Field(
        default=None, description="Relative Strength Index, typically 0-100."
    )
    macd: Optional[float] = Field(
        default=None, description="MACD line value."
    )
    moving_average_20: Optional[float] = Field(
        default=None, description="20-period moving average of price."
    )
    moving_average_50: Optional[float] = Field(
        default=None, description="50-period moving average of price."
    )


class SentimentInfo(BaseModel):
    """Aggregated news/social sentiment for a symbol."""

    model_config = ConfigDict(extra="forbid")

    label: Optional[SentimentLabel] = Field(
        default=None, description="Overall sentiment label."
    )
    score: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Sentiment score from -1.0 (very negative) to 1.0 (very positive).",
    )
    source_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of distinct sources/articles the sentiment was derived from.",
    )


class FundamentalContext(BaseModel):
    """Optional fundamental data supporting a fourth (bonus) signal
    dimension."""

    model_config = ConfigDict(extra="forbid")

    revenue_growth: Optional[float] = Field(
        default=None, description="Year-over-year revenue growth, percent."
    )
    profit_growth: Optional[float] = Field(
        default=None, description="Year-over-year profit growth, percent."
    )
    pe_ratio: Optional[float] = Field(
        default=None, description="Price-to-earnings ratio, if available."
    )
    debt_to_equity: Optional[float] = Field(
        default=None, description="Debt-to-equity ratio, if available."
    )


class SourceDocument(BaseModel):
    """Metadata + text for a single supplied source document.

    This is supplied by the caller (application/RAG layer), never invented
    by the LLM. The `url` field, if present, must be an actual URL the
    application retrieved the document from.
    """

    model_config = ConfigDict(extra="forbid")

    document_id: str
    title: str
    source: str
    url: Optional[str] = None
    retrieved_at: Optional[datetime] = None
    text: str = Field(
        default="",
        description=(
            "Raw retrieved text. Treated strictly as reference material by "
            "the model - never as instructions to follow."
        ),
    )


class DocumentChunk(BaseModel):
    """A RAG-style retrieved chunk. Structurally compatible with
    SourceDocument but without a mandatory retrieval timestamp, to make it
    easy for a future retrieval pipeline to feed chunks directly into this
    module without extra bookkeeping."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    title: str
    source: str
    url: Optional[str] = None
    text: str = ""

    def to_source_document(self) -> "SourceDocument":
        return SourceDocument(
            document_id=self.document_id,
            title=self.title,
            source=self.source,
            url=self.url,
            retrieved_at=None,
            text=self.text,
        )


class MarketData(BaseModel):
    """Structured market data for a single symbol.

    Only `symbol` is strictly required. Every other field is optional so
    that partial real-time feeds do not fail validation - missing fields
    simply result in UNKNOWN classifications for the affected signal
    dimensions (see analyzer.py / prompts.py).
    """

    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(..., min_length=1)
    company_name: Optional[str] = None
    timestamp: Optional[datetime] = None

    current_price: Optional[float] = Field(default=None, ge=0)
    price_change_percent: Optional[float] = None

    volume: Optional[int] = Field(default=None, ge=0)
    average_volume: Optional[int] = Field(default=None, ge=0)

    technical_indicators: Optional[TechnicalIndicators] = None
    sentiment: Optional[SentimentInfo] = None
    fundamental_context: Optional[FundamentalContext] = None

    news_summary: Optional[str] = None

    source_documents: List[SourceDocument] = Field(default_factory=list)
    document_chunks: List[DocumentChunk] = Field(default_factory=list)

    @field_validator("symbol")
    @classmethod
    def _symbol_upper(cls, v: str) -> str:
        return v.strip().upper()

    def all_sources(self) -> List[SourceDocument]:
        """Combine source_documents and document_chunks (RAG-compatible)
        into a single, de-duplicated list of SourceDocument objects."""

        combined: List[SourceDocument] = list(self.source_documents)
        seen_ids = {doc.document_id for doc in combined}
        for chunk in self.document_chunks:
            if chunk.document_id not in seen_ids:
                combined.append(chunk.to_source_document())
                seen_ids.add(chunk.document_id)
        return combined


# ---------------------------------------------------------------------------
# Input models: user profile
# ---------------------------------------------------------------------------


class PortfolioContext(BaseModel):
    """Optional context about the user's existing portfolio exposure."""

    model_config = ConfigDict(extra="forbid")

    existing_exposure_percent: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Percent of portfolio already allocated to this symbol.",
    )
    sector_exposure_percent: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Percent of portfolio already allocated to this symbol's sector.",
    )


class UserProfile(BaseModel):
    """Investor profile used to personalize interpretation of market
    facts. Must never influence the underlying factual classification of
    market data - only the interpretation/framing."""

    model_config = ConfigDict(extra="forbid")

    risk_profile: RiskProfile
    investment_horizon: InvestmentHorizon
    portfolio_context: Optional[PortfolioContext] = None


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------


class SignalDimensionResult(BaseModel):
    """Classification + reasoning for a single signal dimension (price
    momentum, volume, sentiment, or fundamentals)."""

    model_config = ConfigDict(extra="forbid")

    classification: SignalClassification
    reason: str = Field(..., min_length=1)


class SignalDimensions(BaseModel):
    """The required independent signal dimensions. `fundamentals` is
    optional/bonus; the other three are always present (using UNKNOWN when
    data is insufficient)."""

    model_config = ConfigDict(extra="forbid")

    price_momentum: SignalDimensionResult
    volume: SignalDimensionResult
    sentiment: SignalDimensionResult
    fundamentals: Optional[SignalDimensionResult] = None


class SourceAttribution(BaseModel):
    """A trimmed-down, safe-to-display reference to a supplied source
    document. Constructed by application code from the caller-supplied
    SourceDocument/DocumentChunk metadata - never trusted directly from
    the LLM's output."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    title: str
    source: str
    url: Optional[str] = None


class AnalysisResult(BaseModel):
    """The structured financial analysis produced by this module.

    This is the schema handed to Gemini as `response_schema` for the raw
    LLM call (see gemini_client.py), and it is also the schema
    FinancialAnalyzer.analyze() returns to callers - with `sources_used`
    overwritten by application code after the LLM call to guarantee no
    fabricated URLs ever reach the caller.
    """

    model_config = ConfigDict(extra="forbid")

    symbol: str
    classification: SignalClassification
    confidence: float = Field(..., ge=0.0, le=1.0)

    signal_dimensions: SignalDimensions

    key_factors: List[str] = Field(default_factory=list)
    reasoning: str = Field(..., min_length=1)
    personalized_interpretation: str = Field(..., min_length=1)

    sources_used: List[SourceAttribution] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)

    conflicting_signals: bool = Field(
        default=False,
        description="True if the signal dimensions materially disagree with each other.",
    )


class AnalysisMetadata(BaseModel):
    """Performance / observability metadata for one analysis request, kept
    separate from the analysis content itself."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    symbol: str
    model: str
    latency_ms: int
    success: bool
    output_validation_success: bool
    error_type: Optional[str] = None
    retry_count: int = 0
    prompt_tokens: Optional[int] = None
    response_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    confidence: Optional[float] = None
    simulated: bool = Field(
        default=False,
        description="True when this result was produced without calling the live Gemini API.",
    )


class AnalysisResponse(BaseModel):
    """Convenience wrapper bundling the analysis result with its
    metadata, in case a caller prefers a single return value."""

    model_config = ConfigDict(extra="forbid")

    result: AnalysisResult
    metadata: AnalysisMetadata
