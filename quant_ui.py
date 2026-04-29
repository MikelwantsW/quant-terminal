import streamlit as st
import requests
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide")

# --- PROFESSIONAL MOBILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, p, span, label { color: #f8fafc !important; }
    .streamlit-expanderHeader { background-color: #1e293b !important; border-radius: 8px !important; font-weight: bold; font-size: 16px; border: 1px solid #334155; }
    div[data-testid="stMetric"] { background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 24px !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; border-radius: 6px; }
    .win-badge { background-color: #16a34a; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .loss-badge { background-color: #dc2626; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
top_leagues = ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "Championship"]

def safe_num(v):
    if v is None: return 0.0
    try:
        cleaned = str(v).replace("%", "").strip()
        return float(cleaned) if (cleaned and not any(c.isalpha() for c in cleaned)) else 0.0
    except: return 0.0

@st.cache_data(ttl=600)
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

# --- THE AI PICK ALGORITHM ---
def generate_ai_pick(h_st, a_st):
    total_corners = h_st['corners'] + a_st['corners']
    total_goals = h_st['goals'] + a_st['goals']
    
    if total_corners >= 10.5:
        return "🔥 Over 8.5 Corners", "corners", 8.5
    elif total_goals >= 2.8:
        return "⚽ Over 2.5 Goals", "goals", 2.5
    elif total_goals <= 1.5:
        return "🛡️ Under 2.5 Goals", "under_goals", 2.5
    else:
        return "⚠️ NO PLAY (Low Edge)", "pass", 0

def render_match_card(m, is_live=False):
    h_n, a_n = m.get("match_hometeam_name"), m.get("match_awayteam_name")
    h_s, a_s = m.get("match_hometeam_score", "0"), m.get("match_awayteam_score", "0")
    status = m.get("match_status", "")
    
    header = f"🔴 {status}' | {h_n} {h_s} - {a_s} {a_n}" if is_live else f"🕒 {m.get('match_time')} | {h_n} vs {a_n}"

    with st.expander(header):
        h_st, _ = fetch_stats(m.get("match_hometeam_id"))
        a_st, _ = fetch_stats(m.get("match_awayteam_id"))

        if h_st and a_st:
            pick_text, _, _ = generate_ai_pick(h_st, a_st)
            st.markdown(f"<div style='text-align:center; padding:10px; background-color:#3b82f6; border-radius:8px; margin-bottom:15px;'><b>SYSTEM PICK:</b> {pick_text}</div>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(f"{h_n[:10]} Corn", f"{h_st['corners']:.1f}")
            with c2:
                st.metric("Total Corners", f"{h_st['corners'] + a_st['corners']:.1f}")
                st.metric("Total Goals", f"{h_st['goals'] + a_st['goals']:.1f}")
            with c3:
                st.metric(f"{a_n[:10]} Corn", f"{a_st['corners']:.1f}")

# --- APP LAYOUT ---
st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_fixtures(date_str):
    url = f"https://apiv3.apifootball.com/?action=get_events&from={date_str}&to={date_str}&APIkey={API_KEY}"
    return requests.get(url).json()

all_matches = get_fixtures(today_str)
yesterday_matches = get_fixtures(yesterday_str)

tab1, tab2, tab3, tab4 = st.tabs(["🔴 Live", "🔥 Today's Picks", "🔍 Search", "📊 AI Accuracy"])

if isinstance(all_matches, list):
    live_matches = [m for m in all_matches if m.get("match_status") not in ["", "Finished", "Cancelled", "Postponed"] and ":" not in m.get("match_status", "")]
    big_games = [m for m in all_matches if any(league in m.get("league_name", "") for league in top_leagues) and m.get("match_status") != "Finished"]
    
    with tab1:
        st.markdown("### 🔴 In-Play Matches")
        for m in live_matches: render_match_card(m, is_live=True)
        if not live_matches: st.info("No live matches.")

    with tab2:
        st.markdown("### 🔥 System Picks for Big Games")
        for m in big_games: render_match_card(m, is_live=False)

    with tab3:
        query = st.text_input("🔍 Search Team:")
        if query:
            results = [m for m in all_matches if query.lower() in str(m).lower()]
            for m in results: render_match_card(m)

# --- TAB 4: ACCURACY TRACKER ---
with tab4:
    st.markdown("### 📊 Yesterday's Engine Accuracy")
    st.caption("Grading the system's performance on yesterday's top league matches.")
    
    if isinstance(yesterday_matches, list):
        past_big_games = [m for m in yesterday_matches if any(l in m.get("league_name", "") for l in top_leagues) and m.get("match_status") == "Finished"]
        
        wins = 0
        total_plays = 0
        
        for m in past_big_games:
            h_st, _ = fetch_stats(m.get("match_hometeam_id"))
            a_st, _ = fetch_stats(m.get("match_awayteam_id"))
            
            if h_st and a_st:
                pick_txt, p_type, threshold = generate_ai_pick(h_st, a_st)
                
                if p_type != "pass":
                    total_plays += 1
                    actual_goals = safe_num(m.get("match_hometeam_score")) + safe_num(m.get("match_awayteam_score"))
                    
                    actual_corners = 0
                    for stat in m.get("statistics", []):
                        if stat.get("type") == "Corners":
                            actual_corners = safe_num(stat.get("home")) + safe_num(stat.get("away"))
                    
                    won = False
                    if p_type == "corners" and actual_corners > threshold: won = True
                    if p_type == "goals" and actual_goals > threshold: won = True
                    if p_type == "under_goals" and actual_goals < threshold: won = True
                    
                    if won: wins += 1
                    
                    badge = "<span class='win-badge'>✅ WIN</span>" if won else "<span class='loss-badge'>❌ LOSS</span>"
                    st.markdown(f"{badge} **{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}** | Pick: {pick_txt}", unsafe_allow_html=True)
        
        if total_plays > 0:
            win_rate = (wins / total_plays) * 100
            st.markdown(f"<h3 style='text-align:center; margin-top:20px; color:#38bdf8;'>Total Win Rate: {win_rate:.1f}% ({wins}/{total_plays})</h3>", unsafe_allow_html=True)
        else:
            st.info("No system plays were triggered yesterday.")
