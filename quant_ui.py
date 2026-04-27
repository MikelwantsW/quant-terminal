import streamlit as st
import requests
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Mikel Bet Radar", page_icon="🎯", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, p, span, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    .live-indicator { color: #dc2626; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    div[data-testid="stMetric"] { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')

def safe_num(v):
    if v is None: return 0.0
    try:
        cleaned = str(v).replace("%", "").strip()
        return float(cleaned) if (cleaned and not any(c.isalpha() for c in cleaned)) else 0.0
    except: return 0.0

def fetch_stats(team_id):
    url = f"https://apiv3.apifootball.com/?action=get_events&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}"
    try:
        res = requests.get(url).json()
        s = {"goals":0, "corners":0, "goalkicks":0, "cnt":0}
        if isinstance(res, list):
            recent = [m for m in res if m.get("match_status") == "Finished"][-5:]
            for m in recent:
                is_h = m.get("match_hometeam_id") == team_id
                s["goals"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
                for row in m.get("statistics", []):
                    val = safe_num(row.get("home" if is_h else "away"))
                    stype = row.get("type")
                    if stype == "Corners": s["corners"] += val
                    if stype == "Goal Kicks": s["goalkicks"] += val
                s["cnt"] += 1
        return {k: (v/s["cnt"] if s["cnt"] > 0 else 0) for k, v in s.items()}, s["cnt"]
    except: return None, 0

# --- APP LAYOUT ---
st.title("🎯 Mikel Bet Radar")

# Automatic Refresh Logic (Built-in)
if st.checkbox("🔄 Enable Auto-Live Sync", value=True):
    st.info("Radar is active. Stats refresh every 60s.")
    time.sleep(60)
    st.rerun()

search_query = st.text_input("🔍 Search Teams or Leagues:", placeholder="e.g. Milan, Premier League")

fixtures_url = f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}"
resp = requests.get(fixtures_url).json()

if isinstance(resp, list):
    # Filter based on search
    if search_query:
        final_list = [m for m in resp if search_query.lower() in str(m).lower()]
    else:
        # Default to Live matches if no search
        final_list = [m for m in resp if m.get("match_status") not in ["", "Finished", "Cancelled"]]

    for m in final_list:
        h_n, a_n = m.get("match_hometeam_name"), m.get("match_awayteam_name")
        h_s, a_s = m.get("match_hometeam_score"), m.get("match_awayteam_score")
        status = m.get("match_status")
        
        with st.expander(f"● {status}' | {h_n} {h_s} - {a_s} {a_n}"):
            h_st, h_c = fetch_stats(m.get("match_hometeam_id"))
            a_st, a_c = fetch_stats(m.get("match_awayteam_id"))

            if h_st and a_st:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"{h_n} Avg Corners", f"{h_st['corners']:.1f}")
                with col2:
                    st.metric(f"{a_n} Avg Corners", f"{a_st['corners']:.1f}")
                
                st.write(f"**Institutional Target:** {h_st['corners'] + a_st['corners']:.1f} Total Corners")
else:
    st.warning("No active matches found. Try searching for a specific team.")
