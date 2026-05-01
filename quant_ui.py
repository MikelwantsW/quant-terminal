import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide")

# --- PROFESSIONAL CSS & THEME OVERRIDES ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, p, span, label { color: #f8fafc !important; }
    
    /* 🐛 FIX FOR THE WHITE EXPANDER BUG */
    [data-testid="stExpander"] { background-color: transparent !important; }
    [data-testid="stExpander"] details summary { 
        background-color: #1e293b !important; 
        color: #f8fafc !important; 
        border: 1px solid #334155 !important; 
        border-radius: 8px !important; 
    }
    [data-testid="stExpander"] details summary:hover, 
    [data-testid="stExpander"] details summary:focus, 
    [data-testid="stExpander"] details summary:active { 
        background-color: #334155 !important; 
        color: #f8fafc !important; 
        outline: none !important; 
        box-shadow: none !important;
    }
    
    /* TAB STYLING */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #16a34a !important; color: white !important; border-radius: 6px; }
    
    /* UI COMPONENTS */
    .league-header { background-color: #1e293b; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; border-left: 4px solid #f97316; }
    
    /* 💵 GREEN & ORANGE MONEY THEME */
    .big-pick-box { 
        background-color: #16a34a; 
        padding: 30px; 
        border-radius: 8px; 
        text-align: center; 
        border: 2px solid #22c55e; 
        height: 100%; 
        display: flex; 
        flex-direction: column; 
        justify-content: center;
    }
    .big-pick-text { font-size: 28px !important; font-weight: 900 !important; color: white !important; margin-bottom: 8px; }
    .referee-tag { color: #fef08a; font-size: 14px; font-weight: bold; text-decoration: none; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; display: inline-block;}
    
    .edge-stats { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; height: 100%; border-top: 3px solid #f97316; }
    .edge-stats-title { color: #f97316; font-size: 12px; margin-bottom: 10px; text-transform: uppercase; font-weight: 900; letter-spacing: 1px; }
    .stat-line { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 4px; }
    
    /* LIVE BADGE */
    .live-badge { background-color: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR LIVE CONTROLS ---
st.sidebar.title("⚡ Terminal Settings")
live_refresh = st.sidebar.toggle("Enable Live Auto-Refresh (60s)", value=False)
if live_refresh:
    st.sidebar.caption("🟢 Live Mode: ACTIVE")
    # This triggers a rerun of the script every 60 seconds
    time.sleep(60)
    st.rerun()
else:
    st.sidebar.caption("🔴 Live Mode: PAUSED")

# --- DATA SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')

top_leagues = ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League", "Championship", "Eredivisie", "Primeira Liga", "Scottish Premiership", "Süper Lig", "First Division A", "Major League Soccer", "Brasileirão Série A", "Liga Profesional Argentina", "Saudi Pro League"]
top_countries = ["England", "Italy", "Spain", "Germany", "France", "eurocups", "Netherlands", "Portugal", "Scotland", "Turkey", "Belgium", "USA", "Brazil", "Argentina", "Saudi Arabia"]

def safe_num(v):
    if v is None: return 0.0
    try:
        cleaned = str(v).replace("%", "").strip()
        return float(cleaned) if (cleaned and not any(c.isalpha() for c in cleaned)) else 0.0
    except: return 0.0

@st.cache_data(ttl=600)
def fetch_stats(team_id, venue):
    url = f"https://apiv3.apifootball.com/?action=get_events&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}"
    try:
        res = requests.get(url).json()
        s = {"gf":0, "ga":0, "cf":0, "ca":0, "sotf":0, "sota":0, "cards":0, "cnt":0}
        if isinstance(res, list):
            finished = [m for m in res if m.get("match_status") == "Finished"]
            relevant_games = [m for m in finished if m.get("match_hometeam_id" if venue=="home" else "match_awayteam_id") == team_id][-5:]
            for m in relevant_games:
                is_h = m.get("match_hometeam_id") == team_id
                s["gf"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
                s["ga"] += safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
                for row in m.get("statistics", []):
                    team_val, opp_val = safe_num(row.get("home" if is_h else "away")), safe_num(row.get("away" if is_h else "home"))
                    stype = row.get("type")
                    if stype == "Corners": s["cf"] += team_val; s["ca"] += opp_val
                    elif stype == "Yellow Cards": s["cards"] += team_val
                    elif stype == "Shots On Goal": s["sotf"] += team_val; s["sota"] += opp_val
                s["cnt"] += 1
        return {k: (v/s["cnt"] if s["cnt"] > 0 else 0) for k, v in s.items() if k != "cnt"}, s["cnt"]
    except: return None, 0

def generate_ai_pick(h_st, a_st):
    proj_goals = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
    proj_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
    proj_cards = h_st['cards'] + a_st['cards']
    plays = []
    if proj_goals >= 3.2: plays.append(("⚽ Over 2.5 Goals", 90))
    if proj_corners >= 11.0: plays.append(("🔥 Over 8.5 Corners", 95))
    elif proj_corners >= 9.5: plays.append(("📊 Over 8.5 Corners", 75))
    if proj_cards >= 5.8: plays.append(("🟨 Over 4.5 Cards", 80))
    if not plays: return "⚠️ NO PLAY", 0
    plays.sort(key=lambda x: x[1], reverse=True)
    return plays[0]

# --- APP LAYOUT ---
st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)
daily_matches = requests.get(f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}").json()

tab1, tab2, tab3, tab4 = st.tabs(["🎟️ Auto-Acca", "📝 Weekly Slip", "🔥 Daily Picks", "📊 Accuracy"])

# DAILY PICKS WITH LIVE INTEGRATION
with tab3:
    st.markdown("### 🔥 All System Picks Today")
    if isinstance(daily_matches, list):
        filtered_games = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
        leagues = sorted(list(set([m.get("league_name") for m in filtered_games])))
        for l_name in leagues:
            st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
            for m in [g for g in filtered_games if g.get("league_name") == l_name]:
                status = m.get("match_status")
                is_live = status not in ["", "Finished", "Postponed", "Cancelled"] and not status.isdigit()
                live_label = "<span class='live-badge'>LIVE</span> " if is_live else ""
                
                with st.expander(f"{live_label}🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}"):
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    if h_st and a_st:
                        pick, _ = generate_ai_pick(h_st, a_st)
                        referee = m.get('match_referee')
                        ref_html = f"<a href='https://www.google.com/search?q=football+referee+{referee.replace(' ', '+')}+stats' target='_blank' class='referee-tag'>⚖️ {referee}</a>" if referee else "⚖️ TBD"
                        
                        c1, c2 = st.columns([3, 1.2])
                        with c1:
                            st.markdown(f"<div class='big-pick-box'><div class='big-pick-text'>{pick}</div><div style='margin-top:10px;'>{ref_html}</div></div>", unsafe_allow_html=True)
                        with c2:
                            proj_goals = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
                            proj_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
                            st.markdown(f"<div class='edge-stats'><div class='edge-stats-title'>🔥 Math Edge</div><div class='stat-line'><span>xG</span> <b>{proj_goals:.2f}</b></div><div class='stat-line'><span>Corners</span> <b>{proj_corners:.1f}</b></div><div class='stat-line'><span>Cards</span> <b>{h_st['cards']+a_st['cards']:.1f}</b></div></div>", unsafe_allow_html=True)

# ACCURACY TAB
with tab4:
    st.markdown("### 📊 Yesterday's Accuracy")
    # ... logic for Tab 4 ...
