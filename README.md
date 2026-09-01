# 📈 Stock Adviser

### AI-Powered Multi-Agent Stock Analysis & Investment Research Platform

Stock Adviser is an AI-powered financial research platform designed to analyze a stock from multiple perspectives and produce a single, evidence-backed investment view.

The project combines:

* 📊 Market and financial analysis
* 🤖 Multi-agent AI reasoning
* 🧠 Gemini-powered financial intelligence
* 📚 RAG-based document and research retrieval
* 🔎 Evidence-based analysis
* 🏗️ Agent orchestration
* 🖥️ Interactive frontend
* 📋 Structured investment recommendations

The goal is to provide users with a single interface where they can enter a stock symbol and receive a comprehensive analysis instead of manually running several independent modules.

> **Project status:** Integration in progress
> **Primary objective:** Convert the existing independent modules into one production-ready application.

---

## 🎯 Project Vision

The current repository contains several independent components that solve different parts of the stock-analysis problem.

The final application should connect these components into one pipeline:

```text
                    ┌──────────────────────┐
                    │       Frontend       │
                    │  Stock Symbol/Input  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    API / App Layer   │
                    │  Request Validation  │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌────────────────────────────┐
                 │     Agent Orchestrator     │
                 │                            │
                 │ Coordinates all analysis   │
                 └─────────────┬──────────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
      │ Market      │  │ Fundamental  │  │ RAG /        │
      │ Analysis    │  │ / Financial  │  │ Documents    │
      │             │  │ Analysis     │  │              │
      └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Gemini / AI      │
                    │ Synthesis & Reasoning│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Unified Recommendation│
                    │                      │
                    │ BUY / HOLD / SELL    │
                    │ Confidence           │
                    │ Evidence             │
                    │ Risks                │
                    │ Explanation          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Frontend       │
                    │ Results / Charts /   │
                    │ Evidence / Reports   │
                    └──────────────────────┘
```

---

# 🚀 Core Objective

The final application should allow a user to do something as simple as:

```text
Enter: RELIANCE.NS
        ↓
Analyze
        ↓
Collect market data
        ↓
Run financial analysis
        ↓
Retrieve relevant documents
        ↓
Run specialized AI agents
        ↓
Combine agent results
        ↓
Generate final recommendation
        ↓
Display:
    • BUY / HOLD / SELL
    • Confidence
    • Financial analysis
    • Market analysis
    • Risks
    • Supporting evidence
    • AI explanation
```

The user should **not need to know which module is being executed**.

---

# 🧩 Current Repository Architecture

The repository currently contains the following major components:

```text
Stock__Adviser/
│
├── RAG and Document engine/
│   └── engine.py
│
├── Smoke and Mirror Architect/
│   └── demo_logic.py
│
├── agent_orchestrator/
│   ├── agents.py
│   ├── config.py
│   ├── orchestrator.py
│   ├── schemas.py
│   └── main.py
│
├── digital market engineer/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── config.py
│   ├── exceptions.py
│   ├── gemini_client.py
│   ├── models.py
│   ├── prompts.py
│   ├── requirements.txt
│   └── validators.py
│
└── frontend/
    └── page1.py
```

These directories are already present in the repository.

---

# 🔬 Module Responsibilities

## 1. Digital Market Engineer

Location:

```text
digital market engineer/
```

This module acts as the financial/AI analysis engine.

It contains:

```text
analyzer.py
models.py
gemini_client.py
prompts.py
validators.py
exceptions.py
config.py
```

The analyzer exposes a higher-level financial-analysis API, while `gemini_client.py` is intended to isolate communication with Google's Gemini SDK.

### Responsibility

The module should answer questions such as:

* What is the financial condition of the company?
* What are the important financial metrics?
* What are the major strengths?
* What are the weaknesses?
* What risks exist?
* What is the market outlook?
* What should an investor investigate further?

### Integration interface

The rest of the application should communicate with this module through a single service:

```python
FinancialAnalysisService.analyze(stock_data)
```

The frontend should never directly call Gemini.

---

# 2. Agent Orchestrator

Location:

```text
agent_orchestrator/
```

Files:

```text
agents.py
config.py
orchestrator.py
schemas.py
main.py
```

The orchestrator should become the **central brain of the application**.

Its responsibility is not to collect every piece of data itself.

Instead, it should coordinate specialized agents.

Example:

```text
                    Orchestrator
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   Market Agent     Financial Agent    Research Agent
        │                │                │
        ▼                ▼                ▼
   Market Data       Financial Data      RAG
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                   Risk Agent
                         │
                         ▼
                  Final Synthesis
```

The existing schemas already define structured concepts such as:

```text
Bullish
Bearish
Neutral

STRONG BUY
BUY
HOLD / CAUTION
SELL
STRONG SELL
```

and an `Evidence` model containing a source and claim.

These structured outputs should become the contract between agents.

---

# 3. RAG & Document Engine

Location:

```text
RAG and Document engine/
```

Current implementation:

```text
engine.py
```

The existing RAG engine:

1. Reads PDF documents.
2. Extracts text.
3. Splits documents into chunks.
4. Generates embeddings using `all-MiniLM-L6-v2`.
5. Stores vectors in ChromaDB.
6. Performs semantic retrieval.
7. Returns retrieved evidence.

The current implementation uses:

```text
PyPDF
Sentence Transformers
ChromaDB
```

and stores its vector database locally.

### Example

A user searches:

```text
"Is this company exposed to regulatory risk?"
```

The RAG engine should return:

```json
{
  "query": "Is this company exposed to regulatory risk?",
  "retrieved_facts": [
    {
      "content": "...",
      "metadata": {
        "source": "annual_report.pdf",
        "chunk_index": 17
      }
    }
  ]
}
```

The orchestrator then passes this evidence to the relevant AI agent.

---

# 4. Smoke & Mirror Architect

Location:

```text
Smoke and Mirror Architect/
```

Current file:

```text
demo_logic.py
```

This component should be treated as an architectural/prototype layer rather than being directly coupled to the frontend.

Its logic should eventually be converted into reusable services or agent capabilities.

The final application should avoid importing demo code directly into production routes.

Instead:

```text
demo_logic.py
       ↓
extract reusable logic
       ↓
services/
       ↓
orchestrator
```

---

# 5. Frontend

Location:

```text
frontend/
```

Current entry point:

```text
page1.py
```

The frontend should become a **thin client**.

It should be responsible for:

* Stock symbol input
* User profile/preferences
* Analysis request
* Loading state
* Results
* Charts
* Recommendation
* Evidence
* Risks
* Explanation

It should **not** contain business logic.

---

# 🏗️ Target Architecture

The current repository should eventually be reorganized into the following structure:

```text
Stock__Adviser/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── stock_service.py
│   │   ├── market_service.py
│   │   ├── financial_service.py
│   │   ├── research_service.py
│   │   └── recommendation_service.py
│   │
│   ├── agents/
│   │   ├── market_agent.py
│   │   ├── financial_agent.py
│   │   ├── research_agent.py
│   │   ├── risk_agent.py
│   │   └── synthesis_agent.py
│   │
│   ├── orchestrator/
│   │   └── orchestrator.py
│   │
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   └── vector_store.py
│   │
│   ├── ai/
│   │   ├── gemini_client.py
│   │   ├── prompts.py
│   │   └── models.py
│   │
│   ├── data/
│   │   ├── market_data.py
│   │   └── financial_data.py
│   │
│   └── config/
│       └── settings.py
│
├── frontend/
│   └── page1.py
│
├── documents/
│
├── tests/
│
├── .env.example
├── requirements.txt
├── README.md
└── run.py
```

The important change is that the modules become **services behind one application layer**, instead of each module behaving like an independent application.

---

# 🔄 Unified Analysis Pipeline

Every stock-analysis request should follow the same pipeline.

## Step 1 — User Request

```json
{
  "symbol": "RELIANCE.NS",
  "user_profile": {
    "risk_tolerance": "moderate",
    "investment_horizon": "long_term"
  }
}
```

---

## Step 2 — Validate Request

Validate:

* Stock symbol
* Market
* User profile
* Required configuration
* API credentials

Invalid requests should fail before expensive AI calls.

---

## Step 3 — Collect Market Data

Retrieve:

```text
Current price
Historical prices
Volume
Market trend
Volatility
Technical indicators
```

Normalize the result into one internal structure.

Example:

```python
MarketData(
    symbol="RELIANCE.NS",
    current_price=...,
    historical_prices=...,
    volume=...,
    volatility=...,
)
```

---

# Step 4 — Financial Analysis

Run the financial analysis engine.

Output:

```json
{
  "financial_health": "...",
  "growth": "...",
  "profitability": "...",
  "valuation": "...",
  "financial_risks": []
}
```

---

# Step 5 — RAG Retrieval

Search relevant documents.

Potential sources:

```text
Annual reports
Quarterly reports
Investor presentations
Regulatory documents
Company filings
Research documents
```

Return:

```json
{
  "evidence": [
    {
      "source": "annual_report.pdf",
      "claim": "..."
    }
  ]
}
```

The existing RAG engine already provides the core PDF → chunk → embedding → ChromaDB → semantic retrieval workflow.

---

# Step 6 — Specialized Agents

The orchestrator runs specialized agents.

### Market Agent

Analyzes:

```text
Trend
Momentum
Volatility
Market conditions
Technical signals
```

### Financial Agent

Analyzes:

```text
Revenue
Profit
Margins
Debt
Cash flow
ROE
Valuation
Growth
```

### Research Agent

Uses RAG:

```text
Company documents
Regulatory information
Business risks
Management commentary
```

### Risk Agent

Combines:

```text
Market risk
Financial risk
Business risk
Regulatory risk
Valuation risk
```

---

# Step 7 — Agent Aggregation

Each agent should return structured output.

Example:

```json
{
  "agent": "financial",
  "stance": "Bullish",
  "confidence": 0.82,
  "findings": [
    "...",
    "..."
  ],
  "evidence": [
    {
      "source": "annual_report.pdf",
      "claim": "..."
    }
  ]
}
```

The orchestrator collects all agent results.

---

# Step 8 — Final Synthesis

The synthesis agent receives:

```text
Market Analysis
+
Financial Analysis
+
RAG Evidence
+
Risk Analysis
+
User Profile
```

It produces one final result.

Example:

```json
{
  "symbol": "RELIANCE.NS",
  "recommendation": "BUY",
  "confidence": 0.78,
  "stance": "Bullish",

  "summary": "...",

  "bull_case": [
    "...",
    "..."
  ],

  "bear_case": [
    "...",
    "..."
  ],

  "risks": [
    "...",
    "..."
  ],

  "evidence": [
    {
      "source": "...",
      "claim": "..."
    }
  ]
}
```

---

# 🖥️ Frontend Result

The frontend should display:

```text
┌───────────────────────────────────────────┐
│ RELIANCE.NS                               │
│                                           │
│              BUY                          │
│          Confidence: 78%                  │
│                                           │
├───────────────────────────────────────────┤
│ Market View       Bullish                 │
│ Financial View    Bullish                 │
│ Risk Level        Moderate                │
├───────────────────────────────────────────┤
│ Financial Analysis                       │
│                                           │
│ Revenue       ████████████████             │
│ Profitability ███████████████              │
│ Valuation    ███████████                   │
├───────────────────────────────────────────┤
│ Why BUY?                                  │
│                                           │
│ • ...                                     │
│ • ...                                     │
│ • ...                                     │
├───────────────────────────────────────────┤
│ ⚠ Risks                                   │
│                                           │
│ • ...                                     │
│ • ...                                     │
├───────────────────────────────────────────┤
│ 📚 Evidence                               │
│                                           │
│ Annual Report                             │
│ Regulatory Filing                         │
└───────────────────────────────────────────┘
```

---

# 🔌 Integration Contract

The most important architectural rule is:

> **Modules communicate through typed interfaces, not through direct cross-module imports everywhere.**

For example:

```python
class StockAnalysisRequest:
    symbol: str
    user_profile: UserProfile
```

```python
class StockAnalysisResult:
    symbol: str
    recommendation: str
    confidence: float
    stance: str
    summary: str
    risks: list
    evidence: list
```

The orchestrator becomes:

```python
result = orchestrator.analyze(request)
```

Everything else happens internally.

---

# 🤖 Recommended Orchestrator API

The application should expose one primary function:

```python
def analyze_stock(request: StockAnalysisRequest) -> StockAnalysisResult:
    ...
```

Internally:

```python
def analyze_stock(request):

    validated_request = validate(request)

    market_data = market_service.get_market_data(
        request.symbol
    )

    financial_data = financial_service.get_financial_data(
        request.symbol
    )

    research = rag_service.retrieve(
        request.symbol
    )

    market_result = market_agent.analyze(
        market_data
    )

    financial_result = financial_agent.analyze(
        financial_data
    )

    research_result = research_agent.analyze(
        research
    )

    risk_result = risk_agent.analyze(
        market_result,
        financial_result,
        research_result
    )

    final_result = synthesis_agent.synthesize(
        market_result,
        financial_result,
        research_result,
        risk_result,
        request.user_profile
    )

    return final_result
```

This becomes the heart of the application.

---

# 🔐 Environment Variables

Create:

```text
.env
```

Example:

```env
GEMINI_API_KEY=your_gemini_api_key

APP_ENV=development

CHROMA_DB_PATH=./data/chroma_db
DOCUMENTS_PATH=./documents

LOG_LEVEL=INFO
```

Never commit:

```text
.env
```

to Git.

Instead commit:

```text
.env.example
```

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone https://github.com/YuvaHQ/Stock__Adviser.git
cd Stock__Adviser
```

---

## 2. Create virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install dependencies

After consolidating the individual module dependencies into the root project:

```bash
pip install -r requirements.txt
```

The existing market-engine module currently has its own `requirements.txt`; this should eventually be merged into the root dependency file so the application has a single installation process.

The RAG module also introduces dependencies such as:

```text
pypdf
sentence-transformers
chromadb
```

---

# ▶️ Running the Application

The final target should be:

```bash
python run.py
```

or:

```bash
python -m app.main
```

The developer should **not** need to run:

```bash
python agent_orchestrator/main.py
```

then separately run:

```bash
python RAG_and_Document_engine/engine.py
```

and then separately start the frontend.

Those are internal components.

The application should have **one entry point**.

---

# 📚 Document Ingestion

Place documents inside:

```text
documents/
```

Example:

```text
documents/
├── reliance_annual_report.pdf
├── reliance_investor_presentation.pdf
├── sebi_regulations.pdf
└── industry_report.pdf
```

Run:

```bash
python -m app.rag.ingestion
```

The ingestion pipeline should:

```text
PDF
 ↓
Text extraction
 ↓
Chunking
 ↓
Embedding
 ↓
ChromaDB
```

After ingestion, the application can perform semantic retrieval during stock analysis.

---

# 🧪 Testing

Every module should be testable independently.

Recommended structure:

```text
tests/
├── test_market_service.py
├── test_financial_service.py
├── test_rag.py
├── test_agents.py
├── test_orchestrator.py
└── test_api.py
```

Run:

```bash
pytest
```

---

# 🔍 Integration Testing

The most important test is an end-to-end test.

Example:

```python
def test_full_stock_analysis():

    request = StockAnalysisRequest(
        symbol="RELIANCE.NS"
    )

    result = orchestrator.analyze_stock(request)

    assert result.symbol == "RELIANCE.NS"
    assert result.recommendation in [
        "STRONG BUY",
        "BUY",
        "HOLD / CAUTION",
        "SELL",
        "STRONG SELL"
    ]

    assert 0 <= result.confidence <= 1
```

---

# 🧱 Integration Roadmap

## Phase 1 — Clean Existing Modules

* [ ] Rename directories to Python-friendly names
* [ ] Remove spaces from package directories
* [ ] Add `__init__.py`
* [ ] Standardize imports
* [ ] Remove duplicate configuration
* [ ] Consolidate requirements files
* [ ] Create common models
* [ ] Create root `.env.example`

---

## Phase 2 — Create Common Data Models

Create shared models for:

```text
Stock
MarketData
FinancialData
UserProfile
AgentResult
Evidence
RiskAssessment
Recommendation
StockAnalysisResult
```

All modules should use these models.

---

## Phase 3 — Convert Existing Modules into Services

Create:

```text
MarketService
FinancialService
RAGService
AIService
RecommendationService
```

The existing code should be moved behind these interfaces.

---

## Phase 4 — Integrate Agent Orchestrator

Connect:

```text
MarketService
       ↓
FinancialService
       ↓
RAGService
       ↓
Agents
       ↓
Risk Agent
       ↓
Synthesis Agent
```

The orchestrator becomes the single coordinator.

---

## Phase 5 — Create Backend API

Recommended endpoints:

```text
POST /api/analyze
GET  /api/stock/{symbol}
POST /api/documents/index
GET  /api/health
```

Example:

```http
POST /api/analyze
```

Request:

```json
{
  "symbol": "RELIANCE.NS",
  "risk_tolerance": "moderate",
  "investment_horizon": "long_term"
}
```

Response:

```json
{
  "symbol": "RELIANCE.NS",
  "recommendation": "BUY",
  "confidence": 0.78,
  "stance": "Bullish",
  "summary": "...",
  "risks": [],
  "evidence": []
}
```

---

# Phase 6 — Connect Frontend

The frontend should only call:

```text
/api/analyze
```

It should not directly import:

```text
Gemini
ChromaDB
SentenceTransformer
Agent classes
Market scraping logic
```

This keeps the UI independent from the backend architecture.

---

# Phase 7 — End-to-End Validation

A successful integration should support:

```text
User enters stock
       ↓
Frontend
       ↓
API
       ↓
Orchestrator
       ↓
Market Data
       ↓
Financial Analysis
       ↓
RAG Retrieval
       ↓
Specialized Agents
       ↓
Risk Analysis
       ↓
Gemini Synthesis
       ↓
Structured Result
       ↓
Frontend
```

Only when this complete path works should the project be considered integrated.

---

# ⚠️ Important Architectural Rules

## 1. One Entry Point

The project must eventually have:

```text
run.py
```

as the primary entry point.

---

## 2. One Configuration System

Do not maintain independent API/configuration systems in every module.

Use:

```text
app/config/settings.py
```

---

## 3. One Shared Schema

Agents should not return arbitrary dictionaries.

Use Pydantic models.

The existing orchestrator already moves in this direction through structured schemas and recommendation/stance types.

---

## 4. Evidence Is Mandatory

AI recommendations should not be based solely on an LLM response.

Every important claim should contain:

```text
Source
Claim
```

The existing `Evidence` schema already models this pattern.

---

## 5. Gemini Must Be Isolated

Only one component should communicate with Gemini:

```text
GeminiClient
```

The rest of the application communicates with:

```python
AIService
```

The existing Gemini client is already designed around isolating SDK/API communication.

---

## 6. RAG Must Be a Service

Do not call:

```python
SentenceTransformer(...)
```

or:

```python
chromadb.PersistentClient(...)
```

from the frontend or individual agents.

Use:

```python
rag_service.search(query)
```

instead.

---

## 7. Agents Should Be Independent

Each agent should have one responsibility.

Bad:

```text
FinancialAgent
    ├── downloads PDFs
    ├── calls Gemini
    ├── calculates technical indicators
    ├── queries ChromaDB
    └── generates UI
```

Good:

```text
FinancialAgent
    └── analyzes financial information
```

The orchestrator coordinates everything else.

---

# 🛡️ Reliability & Safety

This application is a research and decision-support system.

It should **not automatically execute trades**.

Recommendations should be presented as:

```text
STRONG BUY
BUY
HOLD / CAUTION
SELL
STRONG SELL
```

along with:

```text
Confidence
Supporting evidence
Risks
Bull case
Bear case
Reasoning
Data timestamp
```

AI-generated recommendations should never be represented as guaranteed financial outcomes.

---

# 📊 Recommendation Model

The final recommendation should combine multiple signals.

Example:

```text
Financial Analysis       35%
Market Analysis          25%
Research/RAG             20%
Risk Assessment          20%
```

These weights should be configurable rather than hard-coded.

Example:

```python
weights = {
    "financial": 0.35,
    "market": 0.25,
    "research": 0.20,
    "risk": 0.20
}
```

The final decision engine should preserve the underlying agent outputs so the user can understand **why** the recommendation was generated.

---

# 📈 Example User Journey

### User

```text
Analyze TCS
```

### System

```text
1. Validate TCS
2. Fetch market data
3. Fetch financial information
4. Retrieve relevant documents
5. Run market agent
6. Run financial agent
7. Run research agent
8. Run risk agent
9. Ask synthesis agent
10. Generate final recommendation
```

### Result

```text
TCS

Recommendation
BUY

Confidence
81%

Market
Bullish

Financial Health
Strong

Risk
Moderate

Why?

• Strong profitability
• Healthy balance sheet
• Positive long-term growth characteristics

Risks

• Valuation
• IT-sector slowdown
• Currency exposure

Evidence

• Annual Report
• Investor Presentation
• Regulatory Documents
```

---

# 🧭 Definition of Done

The integration is complete when:

* [ ] One command starts the application
* [ ] Frontend communicates with backend
* [ ] Backend communicates with orchestrator
* [ ] Orchestrator communicates with all required agents
* [ ] Market data flows into analysis
* [ ] Financial data flows into analysis
* [ ] RAG retrieval works
* [ ] Gemini synthesis works
* [ ] All agents return structured schemas
* [ ] Evidence is attached to important claims
* [ ] Final recommendation is generated
* [ ] Frontend displays the recommendation
* [ ] Errors are handled gracefully
* [ ] API keys are never exposed to frontend
* [ ] Unit tests pass
* [ ] End-to-end analysis test passes
* [ ] Documentation is updated

---

# 🗺️ Final Architecture

The completed system should look like this:

```text
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │  FRONTEND   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ API / APP   │
                    └──────┬──────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │    ORCHESTRATOR   │
                 └─────────┬─────────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
    ┌───────────┐   ┌────────────┐   ┌────────────┐
    │   MARKET  │   │ FINANCIAL  │   │    RAG     │
    │  SERVICE  │   │  SERVICE   │   │  SERVICE   │
    └─────┬─────┘   └──────┬─────┘   └──────┬─────┘
          │                │                 │
          └────────────────┼─────────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ SPECIALIZED AGENTS│
                 ├───────────────────┤
                 │ Market Agent      │
                 │ Financial Agent   │
                 │ Research Agent    │
                 │ Risk Agent        │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ GEMINI SYNTHESIS  │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ FINAL RESULT      │
                 │                   │
                 │ BUY / HOLD / SELL │
                 │ Confidence        │
                 │ Evidence          │
                 │ Risks             │
                 │ Explanation       │
                 └─────────┬─────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  FRONTEND   │
                    └─────────────┘
```

---

# 🤝 Development Principle

The repository should evolve from:

```text
Several independent prototypes
```

into:

```text
One application
    +
Shared schemas
    +
Shared services
    +
Central orchestrator
    +
Single frontend
```

The objective is **not to rewrite every module from scratch**.

Instead:

> **Preserve the useful logic from each existing module, standardize its interface, and connect everything through the orchestrator.**

---

# ⚖️ Disclaimer

Stock Adviser is intended for educational and research purposes.

The application provides AI-generated analysis and should not be considered professional financial advice. Investment decisions involve risk, and users should independently verify information and consult qualified financial professionals where appropriate.

---

# 📄 License

Add the project's chosen license here before public production release.

---

## 🔗 Repository

[YuvaHQ/Stock__Adviser on GitHub](https://github.com/YuvaHQ/Stock__Adviser?utm_source=chatgpt.com)
