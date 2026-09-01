from typing import List, Literal

from pydantic import BaseModel, Field


# ============================================================
# TYPES
# ============================================================

Stance = Literal[
    "Bullish",
    "Bearish",
    "Neutral"
]


Recommendation = Literal[
    "STRONG BUY",
    "BUY",
    "HOLD / CAUTION",
    "SELL",
    "STRONG SELL"
]


# ============================================================
# EVIDENCE
# ============================================================

class Evidence(BaseModel):

    source: str = Field(
        description="Source supporting the claim."
    )

    claim: str = Field(
        description="Factual claim supported by the source."
    )


# ============================================================
# SUB-AGENT OUTPUT
# ============================================================

class SubAgentOutput(BaseModel):

    agent_name: str

    stance: Stance

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence between 0 and 1."
    )

    rationale: str

    evidence: List[Evidence] = Field(
        default_factory=list
    )

    key_risks: List[str] = Field(
        default_factory=list
    )


# ============================================================
# AGENT ERROR
# ============================================================

class AgentError(BaseModel):

    agent_name: str

    error_type: str

    message: str


# ============================================================
# FINAL SYNTHESIS
# ============================================================

class FinalSynthesisOutput(BaseModel):

    symbol: str

    user_risk_profile: str

    final_recommendation: Recommendation

    synthesis_summary: str

    risk_adjustment_note: str

    dominant_factors: List[str] = Field(
        default_factory=list
    )

    conflicts: List[str] = Field(
        default_factory=list
    )

    sub_agent_traces: List[SubAgentOutput] = Field(
        default_factory=list
    )

    failed_agents: List[AgentError] = Field(
        default_factory=list
    )