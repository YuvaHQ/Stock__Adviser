import os
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. "
        "Create a .env file and add your Gemini API key."
    )


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.7-flash"
)


# ============================================================
# DEVELOPMENT MODE
# ============================================================

DEMO_MODE = (
    os.getenv("DEMO_MODE", "true").lower()
    == "true"
)


# ============================================================
# RETRY CONFIGURATION
# ============================================================

# We do NOT repeatedly retry 429 quota errors.
# We only retry temporary server failures such as 503.

MAX_RETRIES = 2

INITIAL_RETRY_DELAY = 5


# ============================================================
# MOCK MARKET DATA
# ============================================================

MOCK_SIGNALS = {

    "price_momentum": "Bullish",

    "rsi": 72,

    "volume_anomaly":
        "180% volume spike above 10-day moving average",

    "sentiment_score": 0.68,

    "news_context": [
        "Market sentiment is moderately positive."
    ]
}


# ============================================================
# MOCK CORPORATE DOCUMENTS
# ============================================================

MOCK_DOCS = [

    {
        "source":
            "SEBI Corporate Disclosure Q3 - Page 14",

        "content":
            "Net profit grew 14% YoY. "
            "Debt-to-equity ratio reduced from 1.2 to 0.8 "
            "following debt clearance."
    },

    {
        "source":
            "Earnings Call Transcript Q3 - Page 4",

        "content":
            "Management projected lower margin guidance "
            "for next quarter due to rising raw material costs."
    }
]


# ============================================================
# MOCK USER PROFILE
# ============================================================

MOCK_USER_PROFILE = {

    "risk_tolerance": "Conservative",

    "portfolio_concentration": "High",

    "sector_allocation": "35% energy"
}
