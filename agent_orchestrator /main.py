import asyncio
import json

from config import (
    MOCK_SIGNALS,
    MOCK_DOCS,
    MOCK_USER_PROFILE,
    DEMO_MODE,
    MODEL_NAME,
)

from orchestrator import (
    run_agent_pipeline
)


async def main():

    # ========================================================
    # STOCK
    # ========================================================

    stock_symbol = "RELIANCE"


    # ========================================================
    # HEADER
    # ========================================================

    print("=" * 60)

    print(
        f"RUNNING MULTI-AGENT PIPELINE: "
        f"{stock_symbol}"
    )

    print("=" * 60)


    print(
        f"\nMode: "
        f"{'DEMO' if DEMO_MODE else 'LIVE GEMINI'}"
    )


    if not DEMO_MODE:

        print(
            f"Model: {MODEL_NAME}"
        )


    # ========================================================
    # RUN PIPELINE
    # ========================================================

    try:

        result = await run_agent_pipeline(

            symbol=stock_symbol,

            signals=MOCK_SIGNALS,

            docs=MOCK_DOCS,

            user_profile=MOCK_USER_PROFILE
        )


    except Exception as exc:

        print("\n")
        print("=" * 60)
        print("PIPELINE FAILED")
        print("=" * 60)

        print(
            f"\nError: {exc}"
        )

        return


    # ========================================================
    # SPECIALIST RESULTS
    # ========================================================

    print("\n")
    print("=" * 60)
    print("SPECIALIST AGENT RESULTS")
    print("=" * 60)


    for trace in result.sub_agent_traces:

        print(
            f"\nAgent: "
            f"{trace.agent_name}"
        )


        print(
            f"Stance: "
            f"{trace.stance}"
        )


        print(
            f"Confidence: "
            f"{trace.confidence * 100:.1f}%"
        )


        print(
            f"Rationale:\n"
            f"{trace.rationale}"
        )


        if trace.evidence:

            print(
                "\nEvidence:"
            )


            for evidence in trace.evidence:

                print(
                    f"  - "
                    f"{evidence.source}: "
                    f"{evidence.claim}"
                )


        if trace.key_risks:

            print(
                "\nRisks:"
            )


            for risk in trace.key_risks:

                print(
                    f"  - {risk}"
                )


    # ========================================================
    # FAILED AGENTS
    # ========================================================

    if result.failed_agents:

        print("\n")
        print("=" * 60)
        print("FAILED AGENTS")
        print("=" * 60)


        for error in result.failed_agents:

            print(
                f"\n{error.agent_name}"
            )

            print(
                f"Type: "
                f"{error.error_type}"
            )

            print(
                f"Message: "
                f"{error.message}"
            )


    # ========================================================
    # FINAL SYNTHESIS
    # ========================================================

    print("\n")
    print("=" * 60)
    print("MASTER SYNTHESIS")
    print("=" * 60)


    print(
        f"\nStock: "
        f"{result.symbol}"
    )


    print(
        f"Final Recommendation: "
        f"{result.final_recommendation}"
    )


    print(
        f"Risk Profile: "
        f"{result.user_risk_profile}"
    )


    print(
        f"\nSynthesis Summary:\n"
        f"{result.synthesis_summary}"
    )


    print(
        f"\nRisk Adjustment:\n"
        f"{result.risk_adjustment_note}"
    )


    # ========================================================
    # DOMINANT FACTORS
    # ========================================================

    if result.dominant_factors:

        print(
            "\nDominant Factors:"
        )


        for factor in result.dominant_factors:

            print(
                f"  - {factor}"
            )


    # ========================================================
    # CONFLICTS
    # ========================================================

    if result.conflicts:

        print(
            "\nConflicts:"
        )


        for conflict in result.conflicts:

            print(
                f"  - {conflict}"
            )


    # ========================================================
    # MEMBER 4 JSON
    # ========================================================

    print("\n")
    print("=" * 60)
    print("JSON OUTPUT FOR MEMBER 4")
    print("=" * 60)


    print(
        json.dumps(
            result.model_dump(),
            indent=2
        )
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())
