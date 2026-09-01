# AI Financial Agent (Gemini) module

**PS-01 — Multi-Agent Autonomous Financial Intelligence System for Retail Investors**
VIT Chennai Hackverse: Into the Web — Sprint 1

This repository contains **one team member's module**: a reusable,
Gemini-powered financial analysis engine. It is **not** the full
hackathon application — it has no frontend, no database, no
authentication, and no multi-agent orchestration. It is designed to be
imported and called by teammates building those other pieces.

## Project purpose

Given structured market data for a symbol and an investor's profile, this
module calls the Gemini API to produce a validated, structured, explainable
financial analysis: independent classifications across three signal
dimensions (price momentum, volume, sentiment — plus optional
fundamentals), an overall classification and confidence score, cited
reasoning, and a personalized interpretation for the specific investor.

It is explicitly a **research/analysis tool**, not a licensed financial
advisor and not a trading system. It never executes trades, connects to
brokerages, or places orders.

## Architecture

```text
Market Data (+ User Profile, + optional Source Documents)
        │
        ▼
  FinancialAnalyzer   (src/analyzer.py)
   - builds prompt, tracks request id / latency / retries
        │
        ▼
   GeminiClient        (src/gemini_client.py)
   - only module that talks to google-genai
   - structured JSON output via response_schema
        │
        ▼
  Gemini API (gemini-2.5-flash by default)
        │
        ▼
  Structured Analysis  (validated AnalysisResult + AnalysisMetadata)
   - sources_used is rebuilt from caller-supplied metadata, never
     trusted from the LLM
        │
        ▼
  Your team's synthesis / other agents
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your key, or export environment
variables directly:

```text
GEMINI_API_KEY   - your Gemini API key (required for live calls; never commit this)
GEMINI_MODEL     - model name, defaults to "gemini-2.5-flash"
RUN_GEMINI_INTEGRATION_TEST - "true" to allow the optional live integration test to run
```

`.env` is loaded automatically via `python-dotenv`. The key is never
hard-coded, printed, or written into any source file, and it is scrubbed
from all error messages and logs.

## Run the simulated demo (no API key required)

```bash
python examples/example_analysis.py
```

This builds clearly-labeled **simulated** market data, runs a small
offline rule-based classifier (not Gemini) for a conservative and an
aggressive investor against the identical data, and prints both results so
you can see how `personalized_interpretation` differs while the
underlying facts and per-dimension classifications stay the same.

## Run the live Gemini demo

```bash
export GEMINI_API_KEY="YOUR_KEY"
export GEMINI_MODEL="gemini-2.5-flash"

python examples/example_analysis.py --live
```

This calls the real Gemini API twice (once per investor profile) using the
`FinancialAnalyzer` public API and prints the structured result plus
request metadata for each call.

## Run tests

```bash
pytest -q
```

All unit tests (models, analyzer, gemini client, validators) run fully
offline using mocked Gemini responses — no API key is required.

## Run the integration test

An additional test actually calls the live Gemini API. It is **skipped by
default**. To enable it:

```bash
export GEMINI_API_KEY="YOUR_KEY"
export RUN_GEMINI_INTEGRATION_TEST=true
pytest -q tests/test_live_integration.py
```

## Team integration

The smallest possible example for a teammate:

```python
from src.analyzer import FinancialAnalyzer
from src.models import MarketData, UserProfile

analyzer = FinancialAnalyzer()

market_data = MarketData(
    symbol="RELIANCE",
    current_price=1450.50,
    price_change_percent=-2.4,
    volume=12_500_000,
    average_volume=7_000_000,
)

user_profile = UserProfile(
    risk_profile="moderate",
    investment_horizon="long_term",
)

result = analyzer.analyze(market_data=market_data, user_profile=user_profile)
print(result.classification, result.confidence)
print(result.personalized_interpretation)
```

For request metadata (latency, token usage, retry count) alongside the
result, call `analyzer.analyze_with_metadata(...)` instead, which returns
an `AnalysisResponse` with `.result` and `.metadata`.

### Output schema

`analyzer.analyze(...)` returns an `AnalysisResult` (see `src/models.py`)
shaped like:

```json
{
  "symbol": "RELIANCE",
  "classification": "BEARISH",
  "confidence": 0.82,
  "signal_dimensions": {
    "price_momentum": {"classification": "BEARISH", "reason": "..."},
    "volume": {"classification": "BEARISH", "reason": "..."},
    "sentiment": {"classification": "BEARISH", "reason": "..."}
  },
  "key_factors": ["Negative price momentum", "Elevated trading volume", "Negative sentiment"],
  "reasoning": "The supplied signals are predominantly bearish.",
  "personalized_interpretation": "For a moderate-risk investor, ...",
  "sources_used": [],
  "limitations": ["Analysis is based only on the supplied data."],
  "conflicting_signals": false
}
```

`sources_used` is always rebuilt by application code (`src/validators.py`)
from the `source_documents` / `document_chunks` you supplied in
`MarketData` — it can never contain a URL or document the model invented.

## Error handling

All failures raise a subclass of `FinancialAgentError`
(`src/exceptions.py`): `ConfigurationError`, `GeminiAuthenticationError`,
`GeminiQuotaError`, `GeminiRateLimitError`, `GeminiRequestError`,
`GeminiServiceError`, or `OutputValidationError`. `FinancialAnalyzer`
performs at most one bounded retry (configurable via `max_retries`) for
transient rate-limit/service errors only — it never retries auth, quota,
malformed-request, or validation failures.

## Financial safety notice

This is a 24-hour hackathon prototype. Output is analysis/research, not
financial advice, and the system does not execute trades or connect to
any brokerage or payment system.
