"""
AI Financial Agent (Gemini) - reusable Gemini-powered financial analysis
module for the VIT Chennai Hackverse PS-01 multi-agent financial
intelligence system.

Typical usage:

    from src.analyzer import FinancialAnalyzer
    from src.models import MarketData, UserProfile

    analyzer = FinancialAnalyzer()
    result = analyzer.analyze(market_data=market_data, user_profile=user_profile)
"""

from .analyzer import FinancialAnalyzer
from .models import (
    AnalysisMetadata,
    AnalysisResponse,
    AnalysisResult,
    DocumentChunk,
    FundamentalContext,
    InvestmentHorizon,
    MarketData,
    PortfolioContext,
    RiskProfile,
    SentimentInfo,
    SentimentLabel,
    SignalClassification,
    SignalDimensionResult,
    SignalDimensions,
    SourceAttribution,
    SourceDocument,
    TechnicalIndicators,
    UserProfile,
)

__all__ = [
    "FinancialAnalyzer",
    "AnalysisMetadata",
    "AnalysisResponse",
    "AnalysisResult",
    "DocumentChunk",
    "FundamentalContext",
    "InvestmentHorizon",
    "MarketData",
    "PortfolioContext",
    "RiskProfile",
    "SentimentInfo",
    "SentimentLabel",
    "SignalClassification",
    "SignalDimensionResult",
    "SignalDimensions",
    "SourceAttribution",
    "SourceDocument",
    "TechnicalIndicators",
    "UserProfile",
]

__version__ = "0.1.0"
