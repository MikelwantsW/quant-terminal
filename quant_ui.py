import streamlit as st
import requests
from datetime import datetime, timedelta

# --- PAGE CONFIG (App-like feel) ---
st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide")

# --- PROFESSIONAL MOBILE CSS ---
st.markdown("""
    <style>
    /* Main Background & Typography */
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, p, span, label { color: #f8fafc !important; }
    
    /* Sleek Expander Cards */
    .streamlit-expanderHeader { background-color: #1e293b !important; border-radius: 8px !important; font-weight: bold; font-size: 16px; border: 1px solid #334155; }
    
    /* Metric Boxes */
    div[data-testid="stMetric"] { background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 24px !important; }
    
    /* Live Indicator */
    .live-badge { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }
    
    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

# --- SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
top_leagues = ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "Championship"]

def safe_num(v):
    if v is None: return 0.0
    try:
        cleaned = str(v).replace("%", "").strip()
        return float(cleaned) if (cleaned and not any(c.isalpha() for c in cleaned)) else 0.0
    except: return 0.0

@st.cache_data(ttl=60) # Caches data for 60 seconds to speed up mobile loading
def fetch_stats(team_id):
    url = f"https://apiv3.apifootball.com/?action=get_events&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}"
    try:
        res = requests.get(url).json()
        s = {"goals":0, "corners":0, "cards":0, "shots":0, "goalkicks":0, "cnt":0}
        if isinstance(res, list):
            recent = [m for m in res if m.get("match_status") == "Finished"][-5:]
            for m in recent:
                is_h = m.get("match_hometeam_id") == team_id
                s["goals"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
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

def render_match_card(m, is_live=False):
    h_n, a_n = m.get("match_hometeam_name"), m.get("match_awayteam_name")
    h_s, a_s = m.get("match_hometeam_score", "0"), m.get("match_awayteam_score", "0")
    status = m.get("match_status", "")
    league = m.get("league_name", "")
    
    if is_live:
        header = f"🔴 {status}' | {h_n} {h_s} - {a_s} {a_n}"
    else:
        header = f"🕒 {m.get('match_time')} | {h_n} vs {a_n}"

    with st.expander(header):
        st.caption(f"🏆 {league}")
        h_st, _ = fetch_stats(m.get("match_hometeam_id"))
        a_st, _ = fetch_stats(m.get("match_awayteam_id"))

        if h_st and a_st:
            # Stats Grid (Mobile Friendly)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(f"{h_n[:10]} Corn", f"{h_st['corners']:.1f}")
                st.metric("Cards", f"{h_st['cards']:.1f}")
            with c2:
                st.metric("Total Corners", f"{h_st['corners'] + a_st['corners']:.1f}")
                st.metric("Total Goals", f"{h_st['goals'] + a_st['goals']:.1f}")
            with c3:
                st.metric(f"{a_n[:10]} Corn", f"{a_st['corners']:.1f}")
                st.metric("Cards", f"{a_st['cards']:.1f}")
                
            st.markdown(f"<div style='text-align:center; padding-top:10px; color:#94a3b8;'>⚽ <b>Target Goal Kicks:</b> {h_st['goalkicks'] + a_st['goalkicks']:.1f} | 🎯 <b>Target Shots:</b> {h_st['shots'] + a_st['shots']:.1f}</div>", unsafe_allow_html=True)

# --- APP LAYOUT ---
st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)

# Fetch all games for today
@st.cache_data(ttl=60)
def get_todays_fixtures():
    url = f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}"
    return requests.get(url).json()

all_matches = get_todays_fixtures()

if isinstance(all_matches, list):
    # Sort into categories
    live_matches = [m for m in all_matches if m.get("match_status") not in ["", "Finished", "Cancelled", "Postponed"] and ":" not in m.get("match_status", "")]
    big_games = [m for m in all_matches if any(league in m.get("league_name", "") for league in top_leagues) and m.get("match_status") != "Finished"]
    other_games = [m for m in all_matches if m not in big_games and m.get("match_status") != "Finished"]
    
    # Create App Navigation
    tab1, tab2, tab3 = st.tabs(["🔴 Live Action", "🔥 Today's Big Games", "🔍 Search Engine"])
    
    with tab1:
        st.markdown("### 🔴 In-Play Matches")
        if st.button("🔄 Refresh Live Scores"):
            st.cache_data.clear()
            st.rerun()
            
        if live_matches:
            for m in live_matches:
                render_match_card(m, is_live=True)
        else:
            st.info("No matches are currently live. Check back later.")

    with tab2:
        st.markdown("### 🔥 Top Leagues Today")
        if big_games:
            for m in big_games:
                render_match_card(m, is_live=False)
        else:
            st.info("No 'Big League' games scheduled for today.")
            
        st.markdown("---")
        st.markdown("### 📅 Other Upcoming Matches")
        for m in other_games[:15]: # Show next 15 to prevent mobile lag
            render_match_card(m, is_live=False)

    with tab3:
        st.markdown("### 🔍 Global Market Sweep")
        query = st.text_input("Enter Team or League (e.g., Madrid, Serie A):")
        if query:
            results = [m for m in all_matches if query.lower() in str(m.get("match_hometeam_name","")).lower() or query.lower() in str(m.get("match_awayteam_name","")).lower() or query.lower() in str(m.get("league_name","")).lower()]
            if results:
                for m in results:
                    render_match_card(m, is_live=(m in live_matches))
            else:
                st.warning("No matches found matching your search today.")
else:
    st.error("Error loading data from the API.")
