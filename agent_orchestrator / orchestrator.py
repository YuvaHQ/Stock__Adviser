import json

from google import genai

from config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    DEMO_MODE,
)

from schemas import (
    SubAgentOutput,
    FinalSynthesisOutput,
    AgentError,
)

from agents import (
    run_technical_agent,
    run_fundamental_agent,
    run_sentiment_agent,
    generate_structured,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# SAFE AGENT EXECUTION
# ============================================================

async def safe_agent_call(
    agent_name,
    agent_function,
    data
):

    try:

        result = await agent_function(data)

        return result, None


    except Exception as exc:

        print(
            f"[WARNING] {agent_name} failed: {exc}"
        )

        error = AgentError(

            agent_name=agent_name,

            error_type=type(exc).__name__,

            message=str(exc)[:500]
        )

        return None, error


# ============================================================
# SYNTHESIS
# ============================================================

async def synthesize_master_recommendation(
    symbol: str,
    sub_agent_results: list[SubAgentOutput],
    failed_agents: list[AgentError],
    user_profile: dict,
) -> FinalSynthesisOutput:


    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if DEMO_MODE:

        return create_demo_synthesis(
            symbol,
            sub_agent_results,
            failed_agents,
            user_profile
        )


    # --------------------------------------------------------
    # PREPARE AGENT DATA
    # --------------------------------------------------------

    agent_data = [

        result.model_dump()

        for result in sub_agent_results
    ]


    failed_data = [

        error.model_dump()

        for error in failed_agents
    ]


    risk_tolerance = user_profile.get(
        "risk_tolerance",
        "Moderate"
    )


    # --------------------------------------------------------
    # SYNTHESIS PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are the Lead Portfolio Synthesis Agent.

Your job is to combine independent specialist analyses.

You are NOT the Technical Agent.

You are NOT the Fundamental Agent.

You are NOT the Sentiment Agent.

You are the final reasoning layer.

============================================================
STOCK
============================================================

{symbol}


============================================================
USER RISK PROFILE
============================================================

{json.dumps(user_profile, indent=2)}


============================================================
SPECIALIST ANALYSES
============================================================

{json.dumps(agent_data, indent=2)}


============================================================
FAILED AGENTS
============================================================

{json.dumps(failed_data, indent=2)}


============================================================
SYNTHESIS RULES
============================================================

1. Consider each specialist independently.

2. Do NOT blindly use majority voting.

3. Consider evidence quality and confidence.

4. Identify conflicts explicitly.

5. Never invent missing information.

6. If an important agent failed, increase caution.

7. Conservative users:
   - prioritize downside protection
   - be cautious when signals conflict
   - avoid strong recommendations from weak evidence

8. Aggressive users:
   - give more consideration to momentum
   - still account for fundamental and sentiment risks

9. High portfolio concentration:
   - treat additional sector exposure as a risk

10. The recommendation MUST be one of:

STRONG BUY
BUY
HOLD / CAUTION
SELL
STRONG SELL

11. Explain why the recommendation was selected.

12. Explain how the user's risk profile changed the result.

13. List the most important factors.

14. List important conflicts.

Do not provide hidden chain-of-thought.

Return only structured output.
"""


    result = await generate_structured(
        prompt,
        FinalSynthesisOutput
    )


    result.symbol = symbol

    result.user_risk_profile = risk_tolerance

    result.sub_agent_traces = sub_agent_results

    result.failed_agents = failed_agents


    return result


# ============================================================
# DEMO SYNTHESIS
# ============================================================

def create_demo_synthesis(
    symbol,
    sub_agent_results,
    failed_agents,
    user_profile
):

    return FinalSynthesisOutput(

        symbol=symbol,

        user_risk_profile=
            user_profile.get(
                "risk_tolerance",
                "Moderate"
            ),

        final_recommendation=
            "HOLD / CAUTION",

        synthesis_summary=(
            "Fundamental and sentiment signals are positive, "
            "but the technical agent identifies short-term "
            "overbought conditions and elevated volume. "
            "Because the user has a conservative risk profile "
            "and high sector concentration, the system favors "
            "caution instead of issuing a BUY recommendation."
        ),

        risk_adjustment_note=(
            "The conservative risk profile increases the "
            "weight given to downside protection. High energy "
            "sector concentration further reduces the "
            "attractiveness of taking additional exposure."
        ),

        dominant_factors=[

            "Strong profit growth",

            "Reduced debt-to-equity ratio",

            "Positive market sentiment",

            "RSI in overbought territory",

            "Elevated trading volume",

            "High portfolio concentration"
        ],

        conflicts=[

            "Fundamental analysis is Bullish "
            "while technical analysis is Bearish.",

            "Positive sentiment conflicts with "
            "short-term technical risk."
        ],

        sub_agent_traces=
            sub_agent_results,

        failed_agents=
            failed_agents
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

async def run_agent_pipeline(
    symbol: str,
    signals: dict,
    docs: list,
    user_profile: dict,
) -> FinalSynthesisOutput:


    print(
        "\n[ORCHESTRATOR] "
        "Starting specialist agents..."
    )


    # ========================================================
    # RUN SPECIALISTS
    # ========================================================

    # Sequential execution is intentional.
    #
    # It reduces the chance of immediately consuming the
    # Gemini free-tier RPM quota.
    #
    # Later, when you have higher API limits, these can be
    # changed back to asyncio.gather().
    # ========================================================


    technical_result, technical_error = (
        await safe_agent_call(
            "Technical Analysis Agent",
            run_technical_agent,
            signals
        )
    )


    fundamental_result, fundamental_error = (
        await safe_agent_call(
            "Fundamental & Regulatory Agent",
            run_fundamental_agent,
            docs
        )
    )


    sentiment_result, sentiment_error = (
        await safe_agent_call(
            "Sentiment & Context Agent",
            run_sentiment_agent,
            signals
        )
    )


    # ========================================================
    # COLLECT RESULTS
    # ========================================================

    sub_agent_results = []

    failed_agents = []


    results = [

        technical_result,
        fundamental_result,
        sentiment_result
    ]


    errors = [

        technical_error,
        fundamental_error,
        sentiment_error
    ]


    for result in results:

        if result is not None:

            sub_agent_results.append(result)


    for error in errors:

        if error is not None:

            failed_agents.append(error)


    print(
        f"[ORCHESTRATOR] "
        f"{len(sub_agent_results)} specialist agents succeeded."
    )


    if failed_agents:

        print(
            f"[ORCHESTRATOR] "
            f"{len(failed_agents)} specialist agents failed."
        )


    # ========================================================
    # TOTAL FAILURE
    # ========================================================

    if not sub_agent_results:

        raise RuntimeError(
            "All specialist agents failed. "
            "Cannot produce a synthesis."
        )


    # ========================================================
    # SYNTHESIS
    # ========================================================

    print(
        "[ORCHESTRATOR] "
        "Starting synthesis..."
    )


    final_output = (
        await synthesize_master_recommendation(

            symbol=symbol,

            sub_agent_results=
                sub_agent_results,

            failed_agents=
                failed_agents,

            user_profile=
                user_profile
        )
    )


    print(
        "[ORCHESTRATOR] "
        "Synthesis complete."
    )


    return final_output
