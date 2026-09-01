import streamlit as st
from datetime import datetime
from typing import Any


st.set_page_config(
    page_title="Astra | Financial Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def preview_payload() -> dict[str, Any]:
    """Temporary UI data; replace this with the shared team JSON payload later."""
    return {
        "market": {
            "symbol": "RELIANCE.NS",
            "company": "Reliance Industries Ltd.",
            "price": 2914.65,
            "change_pct": 1.28,
            "updated_at": "Snapshot · 09:30 IST",
            "signals": [
                {"name": "Price momentum", "value": "RSI 62.4", "label": "BULLISH", "confidence": 78},
                {"name": "Volume activity", "value": "1.6× 10D avg", "label": "ELEVATED", "confidence": 69},
                {"name": "Market sentiment", "value": "+0.34", "label": "POSITIVE", "confidence": 71},
            ],
        },
        "agent_trace": [
            {
                "agent": "Fundamental Agent",
                "status": "Complete",
                "summary": "Financial disclosures indicate steady operating momentum; verify valuation against your entry range.",
                "citations": ["Annual report · p. 84", "Quarterly filing · p. 12"],
            },
            {
                "agent": "Technical Agent",
                "status": "Complete",
                "summary": "Price is above its short-term trend line with supportive, but not exceptional, volume.",
                "citations": ["Market snapshot"],
            },
            {
                "agent": "Sentiment Agent",
                "status": "Complete",
                "summary": "Headline tone is mildly constructive; no high-severity adverse signal is currently flagged.",
                "citations": ["News context"],
            },
        ],
        "recommendation": {
            "action": "HOLD",
            "headline": "Constructive setup, but wait for a better risk-adjusted entry.",
            "rationale": "The profile-adjusted recommendation balances positive momentum with the current risk tolerance.",
            "confidence": 74,
            "sources": ["Annual report · p. 84", "Quarterly filing · p. 12", "Market snapshot"],
        },
        "portfolio": [
            {"symbol": "RELIANCE", "allocation": "18%", "return": "+7.2%"},
            {"symbol": "TATAMOTORS", "allocation": "12%", "return": "+4.1%"},
            {"symbol": "NIFTY 50 ETF", "allocation": "36%", "return": "+2.8%"},
        ],
        "system": {"api_online": True, "notice": "All connected data sources are responding.", "latency_s": 1.8},
    }


def pill(text: str, kind: str = "neutral") -> str:
    return f'<span class="pill {kind}">{text}</span>'


def signal_class(label: str) -> str:
    return "positive" if label in {"BULLISH", "POSITIVE"} else "caution" if label in {"ELEVATED", "CAUTION"} else "neutral"


st.markdown(
    """
    <style>
    .stApp { background: #09111f; color: #e6edf7; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { max-width: 1440px; padding-top: 2.2rem; padding-bottom: 2.5rem; }
    .eyebrow { color: #7f93ad; font-size: .73rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
    .app-title { font-size: 2.1rem; font-weight: 750; letter-spacing: -.04em; margin: .15rem 0; }
    .subtle { color: #97a8bf; font-size: .92rem; }
    .panel { background: #101c2e; border: 1px solid #22344e; border-radius: 16px; padding: 1.1rem 1.15rem; margin-bottom: .75rem; }
    .panel-title { color: #aebed2; font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .8rem; }
    .price { font-size: 2rem; font-weight: 750; letter-spacing: -.04em; }
    .up { color: #55d6a6; } .down { color: #ff8b9c; }
    .signal-name { color: #dae4f1; font-weight: 650; font-size: .9rem; }
    .signal-value { color: #91a4bd; font-size: .82rem; }
    .pill { display:inline-block; border-radius:999px; padding:.22rem .52rem; font-size:.67rem; font-weight:800; letter-spacing:.04em; }
    .pill.positive { background:#123c35; color:#69e3b6; } .pill.caution { background:#443717; color:#f3ca66; } .pill.neutral { background:#26364e; color:#bfd0e8; }
    .trace-dot { color: #65d9b1; font-size: 1rem; line-height: 1; }
    .agent-name { font-weight: 700; color: #edf3fb; }
    .trace-copy { color:#a8b8cc; line-height:1.45; font-size:.89rem; }
    .citation { display:inline-block; color:#8fb9ff; background:#162945; border-radius:5px; padding:.16rem .38rem; margin:.35rem .28rem 0 0; font-size:.72rem; }
    .recommendation { background: linear-gradient(135deg, #152b4a, #122037); border: 1px solid #2e5c8d; border-radius: 18px; padding: 1.35rem; }
    .action { font-size: 1.45rem; font-weight: 850; letter-spacing:.06em; color:#68dfb5; }
    .rec-headline { font-size:1.16rem; font-weight:700; margin:.35rem 0 .55rem; line-height:1.35; }
    .portfolio-row { padding:.55rem 0; border-bottom:1px solid #20324b; }
    .portfolio-row:last-child { border-bottom:0; }
    .metric-label { color:#8295af; font-size:.73rem; text-transform:uppercase; letter-spacing:.08em; }
    .metric-value { color:#eaf2fd; font-size:1.05rem; font-weight:700; }
    div[data-testid="stSelectbox"] label { color:#aebed2 !important; font-size:.78rem !important; font-weight:700 !important; text-transform:uppercase; letter-spacing:.08em; }
    .stButton button { border-radius:9px; border:1px solid #38557a; background:#142844; color:#e4efff; font-weight:650; }
    </style>
    """,
    unsafe_allow_html=True,
)


payload = preview_payload()  # TODO(member 5): Replace with integrated session payload.
market = payload["market"]
profile = st.selectbox("Investor risk profile", ["Conservative", "Moderate", "Aggressive"], index=1)

title_col, status_col = st.columns([4, 1])
with title_col:
    st.markdown('<div class="eyebrow">Decision intelligence workspace</div><div class="app-title">Astra Finance</div><div class="subtle">Grounded signals, transparent agent summaries, profile-aware recommendations.</div>', unsafe_allow_html=True)
with status_col:
    st.markdown("<br>", unsafe_allow_html=True)
    state = "API ONLINE" if payload["system"]["api_online"] else "BACKUP MODE"
    st.markdown(pill(state, "positive" if payload["system"]["api_online"] else "caution"), unsafe_allow_html=True)
    st.caption(payload["system"]["notice"])

st.divider()
left, center, right = st.columns([1.03, 1.38, 1.12], gap="large")

with left:
    st.markdown('<div class="panel-title">Watchlist & signals</div>', unsafe_allow_html=True)
    delta_class = "up" if (market["change_pct"] or 0) >= 0 else "down"
    sign = "+" if (market["change_pct"] or 0) >= 0 else ""
    st.markdown(f'''<div class="panel"><div class="signal-name">{market["company"]}</div><div class="subtle">{market["symbol"]} · {market["updated_at"]}</div><div class="price">₹{market["price"]:,.2f}</div><div class="{delta_class}">{sign}{market["change_pct"]:.2f}% today</div></div>''', unsafe_allow_html=True)
    for signal in market["signals"]:
        st.markdown(f'''<div class="panel"><div class="signal-name">{signal["name"]}</div><div class="signal-value">{signal["value"]}</div>{pill(signal["label"], signal_class(signal["label"]))}<span class="signal-value">&nbsp;&nbsp;{signal["confidence"]}% confidence</span></div>''', unsafe_allow_html=True)

with center:
    st.markdown('<div class="panel-title">Agent reasoning trace</div>', unsafe_allow_html=True)
    st.caption("Concise, reviewable agent summaries—full reasoning remains in the orchestration layer.")
    for trace in payload["agent_trace"]:
        citations = "".join(f'<span class="citation">{item}</span>' for item in trace["citations"])
        st.markdown(f'''<div class="panel"><div class="trace-dot">● <span class="agent-name">{trace["agent"]}</span> {pill(trace["status"], "positive")}</div><div class="trace-copy">{trace["summary"]}</div><div>{citations}</div></div>''', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel-title">Profile-adjusted recommendation</div>', unsafe_allow_html=True)
    rec = payload["recommendation"]
    sources = "".join(f'<span class="citation">{source}</span>' for source in rec["sources"])
    st.markdown(f'''<div class="recommendation"><div class="action">{rec["action"]}</div><div class="rec-headline">{rec["headline"]}</div><div class="trace-copy">{rec["rationale"]}</div><div style="margin-top:.9rem">{pill(f"{rec['confidence']}% confidence", "positive")}</div><div>{sources}</div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="panel-title" style="margin-top:1.25rem">Demo portfolio</div>', unsafe_allow_html=True)
    portfolio_html = "".join(f'''<div class="portfolio-row"><span class="signal-name">{row["symbol"]}</span><span style="float:right" class="up">{row["return"]}</span><br><span class="signal-value">Allocation {row["allocation"]}</span></div>''' for row in payload["portfolio"])
    st.markdown(f'<div class="panel">{portfolio_html}</div>', unsafe_allow_html=True)

st.divider()
metric_a, metric_b, metric_c, action_col = st.columns([1, 1, 1, 1.45])
with metric_a:
    st.markdown('<div class="metric-label">Active profile</div><div class="metric-value">' + profile + '</div>', unsafe_allow_html=True)
with metric_b:
    latency = payload["system"]["latency_s"]
    st.markdown(f'<div class="metric-label">Response latency</div><div class="metric-value">{latency:.1f}s</div>', unsafe_allow_html=True)
with metric_c:
    st.markdown(f'<div class="metric-label">Last refreshed</div><div class="metric-value">{datetime.now().strftime("%H:%M")}</div>', unsafe_allow_html=True)
with action_col:
    if st.button("Simulate API offline", use_container_width=True):
        st.warning("Backup mode: showing the last verified snapshot. No new market data was requested.")
