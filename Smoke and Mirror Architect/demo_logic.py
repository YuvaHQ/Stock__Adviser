"""
demo_logic.py — Hackathon Financial AI Prototype
=================================================
Mock synthesis layer providing:
  1. Dynamic user profile loading from external 'users.json'.
  2. Dynamic risk tolerance calculation based on Age, Income, and ROI.
  3. Session metrics logging to CSV.
  4. Graceful-degradation recommendation engine.
  5. Multi-user concurrent evaluation.

Standard-library only: time, csv, os, json, datetime
"""

import time
import csv
import os
import json
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 1. DYNAMIC USER PROFILE LOADER (Reads from users.json)
# ---------------------------------------------------------------------------

USER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

def load_user_profiles():
    """Load user profiles dynamically from the external JSON file."""
    if os.path.isfile(USER_FILE):
        with open(USER_FILE, "r") as fh:
            return json.load(fh)
    return {}

USER_PROFILES = load_user_profiles()

# ---------------------------------------------------------------------------
# 2. DYNAMIC RISK CALCULATOR
# ---------------------------------------------------------------------------

def calculate_risk_profile(user_data: dict):
    """
    Calculates risk tolerance dynamically based on age, income, and ROI expectation.
    Returns a tuple of (Risk Level String, Numeric Risk Score out of 10).
    """
    score = 0.0
    
    # 1. Age Factor (Younger = Higher capacity for risk)
    if user_data["age"] < 30:
        score += 3.5
    elif user_data["age"] <= 50:
        score += 2.0
    else:
        score += 0.5
        
    # 2. Income Factor (Higher income = Higher buffer for volatility)
    if user_data["annual_income"] > 80000:
        score += 3.0
    elif user_data["annual_income"] >= 50000:
        score += 2.0
    else:
        score += 1.0
        
    # 3. ROI Expectation (Higher expectations require higher risk)
    if user_data["expected_roi_percent"] >= 12.0:
        score += 3.5
    elif user_data["expected_roi_percent"] >= 8.0:
        score += 2.0
    else:
        score += 0.5
        
    # Determine Risk Bracket
    if score >= 7.5:
        return "High", score
    elif score >= 5.0:
        return "Moderate", score
    else:
        return "Low", score

# ---------------------------------------------------------------------------
# 3. SESSION METRICS LOGGER
# ---------------------------------------------------------------------------

METRICS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "hackathon_metrics.csv")

METRICS_HEADERS = ["timestamp", "latency_ms", "risk_score",
                   "data_pipeline_status"]

def log_session_metrics(latency: float, risk_score: float,api_status: str):
    """Append one row of session telemetry to *hackathon_metrics.csv*."""
    file_exists = os.path.isfile(METRICS_FILE) and os.path.getsize(METRICS_FILE) > 0

    with open(METRICS_FILE, mode="a", newline="") as fh:
        writer = csv.writer(fh)
        if not file_exists:
            writer.writerow(METRICS_HEADERS)
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            f"{latency:.2f}",
            risk_score,
            api_status,
        ])

# ---------------------------------------------------------------------------
# 4. GRACEFUL-DEGRADATION RECOMMENDATION ENGINE
# ---------------------------------------------------------------------------

def generate_final_recommendation(user_name: str,live_market_data: dict | None,rag_documents: list[str],simulate_crash: bool = False,):
    """Return a structured recommendation dict for *user_name*."""
    start = time.time()

    # --- Degradation gate ---
    if simulate_crash:
        warning = (
            "\u26a0 SYSTEM WARNING: Live data feed is OFFLINE. "
            "Relying strictly on historical filings."
        )
        api_status = "DEGRADED \u2013 fallback to historical"
        api_source = "historical_cache"
    else:
        warning = None
        api_status = "LIVE"
        api_source = (live_market_data or {}).get("source", "live_market_api")

    # --- Profile lookup & Risk Calculation ---
    profiles = load_user_profiles()
    profile = profiles.get(user_name)
    if profile is None:
        return {
            "error": f"Unknown user: '{user_name}'",
            "available_users": list(profiles.keys()),
        }

    # Dynamic risk calculation based on inputs
    calculated_risk_level, calculated_risk_score = calculate_risk_profile(profile)

    # --- Mock AI reasoning based on calculated risk ---
    if calculated_risk_level == "High":
        action = "BUY"
    elif calculated_risk_level == "Moderate":
        action = "HOLD"
    else:
        action = "AVOID"

    advice = (
        f"Recommendation for {user_name} (age {profile['age']}): "
        f"{action} \u2014 Calculated risk tolerance is '{calculated_risk_level}' "
        f"({calculated_risk_score}/10) aligned with objective '{profile['objective']}'. "
        f"Holdings: {', '.join(profile['holdings'])}."
    )

    # --- Telemetry ---
    latency_ms = (time.time() - start) * 1000
    log_session_metrics(latency_ms, calculated_risk_score, api_status)

    return {
        "user": user_name,
        "action": action,
        "calculated_risk_level": calculated_risk_level,
        "risk_score": calculated_risk_score,
        "advice": advice,
        "system_warning": warning,
        "citations": {
            "rag_sources": rag_documents,
            "api_source": api_source,
        },
        "latency_ms": round(latency_ms, 2),
        "data_pipeline_status": api_status,
    }

# ---------------------------------------------------------------------------
# 5. MULTI-USER DEMO TEST BLOCK
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("  HACKATHON DEMO — Multi-User Dynamic Risk & Attribution Test")
    print("=" * 65)

    profiles = load_user_profiles()
    if not profiles:
        print("[ERROR] users.json not found or empty!")
    else:
        # Automatically loop and compute recommendations for all defined profiles
        for user_name in profiles.keys():
            print(f"\n--- Processing Recommendation for: {user_name} ---")
            
            result = generate_final_recommendation(
                user_name=user_name,
                live_market_data={"source": "Yahoo Finance (yfinance API)"},          
                rag_documents=["SEBI_Circular_2025.pdf", "Market_Sentiment_Log.pdf"],
                simulate_crash=False, # Set to True to test graceful degradation
            )

            print(json.dumps(result, indent=2))

        # Confirm CSV logs all entries
        if os.path.isfile(METRICS_FILE):
            with open(METRICS_FILE) as f:
                contents = f.read()
            print("\n--- hackathon_metrics.csv (All Sessions Logged) ---")
            print(contents)
        else:
            print("\n[ERROR] hackathon_metrics.csv was NOT created.")
