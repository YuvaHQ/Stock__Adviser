import asyncio
import random

from google import genai

from config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    MAX_RETRIES,
    INITIAL_RETRY_DELAY,
    DEMO_MODE,
)

from schemas import (
    SubAgentOutput
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# GEMINI STRUCTURED OUTPUT HELPER
# ============================================================

async def generate_structured(
    prompt: str,
    response_model
):

    for attempt in range(MAX_RETRIES + 1):

        try:

            response = await client.aio.models.generate_content(

                model=MODEL_NAME,

                contents=prompt,

                config={
                    "response_mime_type": "application/json",
                    "response_schema": response_model,
                },
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response_model.model_validate_json(
                response.text
            )


        except Exception as exc:

            error_text = str(exc)


            # ------------------------------------------------
            # 429 = QUOTA
            # ------------------------------------------------

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                raise RuntimeError(
                    "Gemini API quota exceeded. "
                    "Use DEMO_MODE=true while developing "
                    "or wait for the quota window to reset."
                )


            # ------------------------------------------------
            # 503 = TEMPORARY SERVER FAILURE
            # ------------------------------------------------

            temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            )


            if temporary_error:

                if attempt >= MAX_RETRIES:

                    raise


                delay = (
                    INITIAL_RETRY_DELAY
                    * (2 ** attempt)
                    + random.uniform(0, 2)
                )


                print(
                    f"[RETRY] Gemini temporarily unavailable. "
                    f"Waiting {delay:.1f}s..."
                )


                await asyncio.sleep(delay)

                continue


            # ------------------------------------------------
            # Other errors should NOT be retried
            # ------------------------------------------------

            raise


    raise RuntimeError(
        "Gemini request failed."
    )


# ============================================================
# MOCK TECHNICAL AGENT
# ============================================================

def mock_technical_agent():

    return SubAgentOutput(

        agent_name=
            "Technical Analysis Agent",

        stance=
            "Bearish",

        confidence=
            0.82,

        rationale=
            "Price momentum is bullish, but RSI is "
            "in the overbought region and trading volume "
            "is significantly elevated. This creates "
            "short-term correction risk.",

        evidence=[

            {
                "source":
                    "Market Signals",

                "claim":
                    "RSI is 72 and volume is "
                    "180% above the 10-day moving average."
            }

        ],

        key_risks=[

            "Overbought RSI may indicate "
            "short-term correction risk.",

            "Unusually high volume may indicate "
            "increased volatility."
        ]
    )


# ============================================================
# MOCK FUNDAMENTAL AGENT
# ============================================================

def mock_fundamental_agent():

    return SubAgentOutput(

        agent_name=
            "Fundamental & Regulatory Agent",

        stance=
            "Bullish",

        confidence=
            0.86,

        rationale=
            "The company shows improving profitability "
            "and lower leverage. However, management "
            "expects margin pressure from rising raw "
            "material costs.",

        evidence=[

            {
                "source":
                    "SEBI Corporate Disclosure Q3 - Page 14",

                "claim":
                    "Net profit grew 14% YoY and "
                    "debt-to-equity declined from "
                    "1.2 to 0.8."
            },

            {
                "source":
                    "Earnings Call Transcript Q3 - Page 4",

                "claim":
                    "Management projected lower margins "
                    "because of rising raw material costs."
            }

        ],

        key_risks=[

            "Rising raw material costs may reduce margins.",

            "Management guidance indicates "
            "near-term margin pressure."
        ]
    )


# ============================================================
# MOCK SENTIMENT AGENT
# ============================================================

def mock_sentiment_agent():

    return SubAgentOutput(

        agent_name=
            "Sentiment & Context Agent",

        stance=
            "Bullish",

        confidence=
            0.68,

        rationale=
            "The supplied sentiment score indicates "
            "moderately positive market perception.",

        evidence=[

            {
                "source":
                    "Market Sentiment Signal",

                "claim":
                    "Sentiment score is 0.68."
            }

        ],

        key_risks=[

            "Market sentiment can change rapidly."
        ]
    )


# ============================================================
# TECHNICAL AGENT
# ============================================================

async def run_technical_agent(
    signals_data: dict
) -> SubAgentOutput:

    if DEMO_MODE:

        return mock_technical_agent()


    prompt = f"""
You are the Technical Analysis Agent.

Your ONLY responsibility is technical market analysis.

Analyze ONLY the supplied information.

MARKET DATA:

{signals_data}

Evaluate:

- price momentum
- RSI
- volume anomalies
- trend information

Rules:

1. Do not invent data.

2. Do not use outside information.

3. Choose exactly one:
   Bullish
   Bearish
   Neutral

4. Confidence must be between 0.0 and 1.0.

5. Explain the conclusion concisely.

6. Identify important technical risks.

7. Include evidence from the supplied data.

Do not provide hidden chain-of-thought.

Return structured output only.
"""


    result = await generate_structured(
        prompt,
        SubAgentOutput
    )


    result.agent_name = (
        "Technical Analysis Agent"
    )


    return result


# ============================================================
# FUNDAMENTAL AGENT
# ============================================================

async def run_fundamental_agent(
    retrieved_docs: list
) -> SubAgentOutput:

    if DEMO_MODE:

        return mock_fundamental_agent()


    prompt = f"""
You are the Fundamental & Regulatory Analysis Agent.

Your ONLY responsibility is financial and regulatory analysis.

Analyze ONLY these documents:

{retrieved_docs}

Evaluate:

- profitability
- debt
- margins
- management guidance
- financial health
- regulatory information
- financial risks

Rules:

1. Do not invent financial numbers.

2. Do not use outside information.

3. Every important conclusion must be supported
   by a supplied document.

4. Choose exactly one:
   Bullish
   Bearish
   Neutral

5. Confidence must be between 0.0 and 1.0.

6. Keep the rationale concise.

Do not provide hidden chain-of-thought.

Return structured output only.
"""


    result = await generate_structured(
        prompt,
        SubAgentOutput
    )


    result.agent_name = (
        "Fundamental & Regulatory Agent"
    )


    return result


# ============================================================
# SENTIMENT AGENT
# ============================================================

async def run_sentiment_agent(
    signals_data: dict
) -> SubAgentOutput:

    if DEMO_MODE:

        return mock_sentiment_agent()


    sentiment_score = signals_data.get(
        "sentiment_score",
        0
    )


    news_context = signals_data.get(
        "news_context",
        []
    )


    prompt = f"""
You are the Market Sentiment & Context Agent.

Your ONLY responsibility is market sentiment analysis.

SENTIMENT SCORE:

{sentiment_score}

NEWS / EXTERNAL CONTEXT:

{news_context}

Rules:

1. Do not invent news.

2. Use only the supplied information.

3. Choose exactly one:
   Bullish
   Bearish
   Neutral

4. Confidence must be between 0.0 and 1.0.

5. Explain the conclusion concisely.

6. Identify important sentiment risks.

Do not provide hidden chain-of-thought.

Return structured output only.
"""


    result = await generate_structured(
        prompt,
        SubAgentOutput
    )


    result.agent_name = (
        "Sentiment & Context Agent"
    )


    return result