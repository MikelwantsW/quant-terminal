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

# --- SETTINGS & TIME ZONES ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
future_str = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d') # Fetch games up to 3 days out
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
        s = {"goals":0, "corners":0, "cards":0, "conceded":0, "shots":0, "goalkicks":0, "cnt":0}
        if isinstance(res, list):
            recent = [m for m in res if m.get("match_status") == "Finished"][-5:]
            for m in recent:
                is_h = m.get("match_hometeam_id") == team_id
                s["goals"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
                s["conceded"] += safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
                for row in m.get("statistics", []):
                    val = safe_num(row.get("home" if is_h else "away"))
                    stype = row.get("type")
                    if stype == "Corners": s["corners"] += val
                    if stype == "Yellow Cards": s["cards"] += val
                    if stype == "Shots Total": s["shots"] += val
                    if stype == "Goal Kicks": s["goalkicks"] += val
                s["cnt"] += 1
        return {k: (v/s["cnt"] if s["cnt"] > 0 else 0) for k, v in s.items()}, s["cnt"]
    except: return None, 0

# --- APP LAYOUT ---
st.title("🎯 Mikel Bet Radar: The Engine")

col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("🔍 Search Teams or Leagues (e.g. United, Serie A):")
with col2:
    # Optional Live Sync so it doesn't interrupt your searching
    auto_sync = st.checkbox("🔄 Auto-Live Sync (60s)", value=False) 

if auto_sync:
    time.sleep(60)
    st.rerun()

# Fetch upcoming matches (Today -> Next 3 Days)
fixtures_url = f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={future_str}&APIkey={API_KEY}"
resp = requests.get(fixtures_url).json()

if isinstance(resp, list):
    if search_query:
        terms = [t.strip().lower() for t in search_query.split(",") if t.strip()]
        final_list = [m for m in resp if any(term in str(m.get("match_hometeam_name","")).lower() or term in str(m.get("match_awayteam_name","")).lower() or term in str(m.get("league_name","")).lower() for term in terms)]
    else:
        # Default view: Next 15 upcoming/live matches
        final_list = [m for m in resp if m.get("match_status") not in ["Finished", "Cancelled"]][:15]

    if not final_list:
        st.warning("No matches found. Try a different search term.")

    for m in final_list:
        h_n, a_n = m.get("match_hometeam_name"), m.get("match_awayteam_name")
        h_s, a_s = m.get("match_hometeam_score", "0"), m.get("match_awayteam_score", "0")
        status = m.get("match_status", "")
        
        # Check if match is live (has a minute attached, not just empty or "Finished")
        is_live = status not in ["", "Finished", "Cancelled", "Postponed"] and ":" not in status
        display_status = f"<span class='live-indicator'>● LIVE {status}'</span>" if is_live else f"🕒 {m.get('match_date')} | {m.get('match_time')}"
        
        with st.expander(f"{h_n} {h_s} - {a_s} {a_n}"):
            st.markdown(f"**Status:** {display_status}", unsafe_allow_html=True)
            
            h_st, h_c = fetch_stats(m.get("match_hometeam_id"))
            a_st, a_c = fetch_stats(m.get("match_awayteam_id"))

            if h_st and a_st:
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1:
                    st.metric(f"{h_n} Corners", f"{h_st['corners']:.1f}")
                    st.metric("Avg Goals Scored", f"{h_st['goals']:.1f}")
                with c2: 
                    st.markdown("<h3 style='text-align:center;'>VS</h3>", unsafe_allow_html=True)
                with c3:
                    st.metric(f"{a_n} Corners", f"{a_st['corners']:.1f}")
                    st.metric("Avg Goals Scored", f"{a_st['goals']:.1f}")
                
                st.markdown("### 🧬 AI Probability Engine")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.write(f"**Corner Target:** {h_st['corners'] + a_st['corners']:.1f}")
                with m2:
                    st.write(f"**Total Goal Kicks:** {h_st['goalkicks'] + a_st['goalkicks']:.1f}")
                with m3:
                    st.write(f"**Expected Goals:** {h_st['goals'] + a_st['goals']:.1f}")
else:
    st.error("API Error or no games loaded from the server.")
