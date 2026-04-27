import streamlit as st
import requests
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- 1. LIVE HEARTBEAT (Auto-refresh every 60 seconds) ---
st_autorefresh(interval=60000, key="datarefresh")

st.set_page_config(page_title="Mikel Bet Radar", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, p, span, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    input { border: 2px solid #2563eb !important; border-radius: 8px !important; color: #0f172a !important; }
    div[data-testid="stMetric"] { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .stButton>button { background-color: #dc2626 !important; color: white !important; width: 100%; height: 50px; font-weight: 800; border-radius: 10px; border: none; }
    .live-indicator { color: #dc2626; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Mikel Bet Radar: Live Terminal")
st.markdown("### Real-Time Quantitative Sweep (Auto-Refreshing)")

# --- 2. SETTINGS ---
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

# --- 3. LIVE ENGINE ---
search_query = st.text_input("🔍 Search Teams (or leave blank for Live games):", placeholder="Enter team name...")

# Toggle for Live Matches Only
show_live = st.checkbox("📡 Focus ONLY on Live Matches", value=True)

fixtures_url = f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}"
if show_live:
    fixtures_url += "&match_live=1"

resp = requests.get(fixtures_url).json()

if isinstance(resp, list):
    if search_query:
        terms = [t.strip().lower() for t in search_query.split(",") if t.strip()]
        final_list = [m for m in resp if any(term in str(m.get("match_hometeam_name","")).lower() or term in str(m.get("match_awayteam_name","")).lower() for term in terms)]
    else:
        final_list = resp[:15]

    for m in final_list:
        status = m.get("match_status")
        is_live = status not in ["", "Finished", "Cancelled", "Postponed"]
        status_display = f"<span class='live-indicator'>● LIVE {status}'</span>" if is_live else f"🕒 {m.get('match_time')}"
        
        h_n, a_n = m.get("match_hometeam_name"), m.get("match_awayteam_name")
        h_score, a_score = m.get("match_hometeam_score", "0"), m.get("match_awayteam_score", "0")

        with st.expander(f"{h_n} {h_score} - {a_score} {a_n}"):
            st.markdown(f"**Status:** {status_display}", unsafe_allow_html=True)
            h_st, h_c = fetch_stats(m.get("match_hometeam_id"))
            a_st, a_c = fetch_stats(m.get("match_awayteam_id"))

            if h_st and a_st:
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1:
                    st.metric(f"{h_n} Avg Corners", f"{h_st['corners']:.1f}")
                with c2: st.markdown("<h3 style='text-align:center;'>VS</h3>", unsafe_allow_html=True)
                with c3:
                    st.metric(f"{a_n} Avg Corners", f"{a_st['corners']:.1f}")

                st.markdown("### 🧬 AI Probability vs Live Score")
                m1, m2, m3 = st.columns(3)
                with m1:
                    if is_live and safe_num(h_score)+safe_num(a_score) == 0 and (h_st['goals']+a_st['goals'] > 2.5):
                        st.success("🔥 **LATE GOAL VALUE:** High Goal Avg but 0-0 live.")
                with m2:
                    total_corners = h_st['corners'] + a_st['corners']
                    st.write(f"Corner Target: {total_corners:.1f}")
                with m3:
                    st.write(f"Goal Kick Proj: {h_st['goalkicks'] + a_st['goalkicks']:.1f}")
else:
    st.info("No live matches at the moment. Uncheck 'Focus ONLY on Live Matches' to see upcoming games.")
