import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide")

# --- ULTIMATE CSS OVERRIDE (Fixes White-out & Theme) ---
st.markdown("""
    <style>
    /* Main App Background */
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; font-family: 'Inter', sans-serif; }
    
    /* FORCE DARK EXPANDERS - Prevents the White-out Bug */
    [data-testid="stExpander"] { 
        background-color: #1e293b !important; 
        border: 1px solid #334155 !important; 
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stExpander"] details summary { 
        background-color: #1e293b !important; 
        color: #f8fafc !important; 
    }
    /* This specific block kills the white highlight when the game is Live/Active */
    [data-testid="stExpander"] details summary:hover, 
    [data-testid="stExpander"] details summary:focus, 
    [data-testid="stExpander"] details summary:active,
    [data-testid="stHeader"] { 
        background-color: #1e293b !important; 
        color: #f8fafc !important; 
        outline: none !important; 
        box-shadow: none !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #16a34a !important; color: white !important; border-radius: 6px; }
    
    /* Live/Money Theme Elements */
    .league-header { background-color: #1e293b; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-top: 20px; border-left: 4px solid #f97316; }
    .big-pick-box { background-color: #16a34a; padding: 25px; border-radius: 8px; text-align: center; border: 2px solid #22c55e; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .big-pick-text { font-size: 26px !important; font-weight: 900 !important; color: white !important; }
    .referee-tag { color: #fef08a; font-size: 13px; font-weight: bold; text-decoration: none; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; }
    
    .edge-stats { background-color: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; border-top: 3px solid #f97316; }
    .stat-line { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
    
    /* Live Scoring Banner */
    .live-score-banner { background-color: #ef4444; color: white; padding: 5px 15px; border-radius: 5px; font-weight: 900; font-size: 18px; margin-bottom: 15px; text-align: center; }
    .live-pulse { height: 10px; width: 10px; background-color: #fff; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- LIVE AUTO-REFRESH LOGIC ---
st.sidebar.title("⚡ Terminal Settings")
live_mode = st.sidebar.toggle("Enable Live Auto-Refresh (60s)", value=False)
if live_mode:
    st.sidebar.success("🟢 LIVE MODE ACTIVE")
    time.sleep(60)
    st.rerun()

# --- CORE FUNCTIONS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')

top_leagues = ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League", "Championship", "Eredivisie", "Primeira Liga", "Scottish Premiership", "Süper Lig", "First Division A", "Major League Soccer", "Brasileirão Série A", "Liga Profesional Argentina", "Saudi Pro League"]
top_countries = ["England", "Italy", "Spain", "Germany", "France", "eurocups", "Netherlands", "Portugal", "Scotland", "Turkey", "Belgium", "USA", "Brazil", "Argentina", "Saudi Arabia"]

def safe_num(v):
    if v is None: return 0.0
    try: return float(str(v).replace("%", "").strip())
    except: return 0.0

@st.cache_data(ttl=600)
def fetch_stats(team_id, venue):
    url = f"https://apiv3.apifootball.com/?action=get_events&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}"
    try:
        res = requests.get(url).json()
        s = {"gf":0, "ga":0, "cf":0, "ca":0, "sotf":0, "sota":0, "cards":0, "cnt":0}
        if isinstance(res, list):
            finished = [m for m in res if m.get("match_status") == "Finished"]
            relevant = [m for m in finished if m.get("match_hometeam_id" if venue=="home" else "match_awayteam_id") == team_id][-5:]
            for m in relevant:
                is_h = m.get("match_hometeam_id") == team_id
                s["gf"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
                s["ga"] += safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
                for row in m.get("statistics", []):
                    t_val, o_val = safe_num(row.get("home" if is_h else "away")), safe_num(row.get("away" if is_h else "home"))
                    stype = row.get("type")
                    if stype == "Corners": s["cf"] += t_val; s["ca"] += o_val
                    elif stype == "Yellow Cards": s["cards"] += t_val
                    elif stype == "Shots On Goal": s["sotf"] += t_val; s["sota"] += o_val
                s["cnt"] += 1
        return {k: (v/s["cnt"] if s["cnt"] > 0 else 0) for k, v in s.items() if k != "cnt"}, s["cnt"]
    except: return None, 0

def generate_ai_pick(h_st, a_st):
    proj_g = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
    proj_c = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
    proj_cd = h_st['cards'] + a_st['cards']
    picks = []
    if proj_g >= 3.2: picks.append(("⚽ Over 2.5 Goals", 90))
    if proj_c >= 11.0: picks.append(("🔥 Over 8.5 Corners", 95))
    elif proj_c >= 9.5: picks.append(("📊 Over 8.5 Corners", 75))
    if proj_cd >= 5.8: picks.append(("🟨 Over 4.5 Cards", 80))
    picks.sort(key=lambda x: x[1], reverse=True)
    return picks[0] if picks else ("⚠️ NO PLAY", 0)

# --- MAIN UI ---
st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)
daily_matches = requests.get(f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}").json()

tab1, tab2, tab3, tab4 = st.tabs(["🎟️ Auto-Acca", "📝 Weekly Slip", "🔥 Daily Picks", "📊 Accuracy"])

with tab3:
    st.markdown("### 🔥 All System Picks Today")
    if isinstance(daily_matches, list):
        filtered = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
        for l_name in sorted(list(set([m.get("league_name") for m in filtered]))):
            st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
            for m in [g for g in filtered if g.get("league_name") == l_name]:
                status = m.get("match_status")
                h_score, a_score = m.get("match_hometeam_score", "0"), m.get("match_awayteam_score", "0")
                is_live = status not in ["", "Finished", "Postponed"] and not status.isdigit()
                
                with st.expander(f"{'🔴 ' if is_live else ''}🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}"):
                    if is_live:
                        st.markdown(f"<div class='live-score-banner'><span class='live-pulse'></span>LIVE: {h_score} - {a_score} ({status}')</div>", unsafe_allow_html=True)
                    
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    if h_st and a_st:
                        pick, _ = generate_ai_pick(h_st, a_st)
                        ref = m.get('match_referee')
                        ref_html = f"<a href='https://www.google.com/search?q={ref.replace(' ','+')}+referee+stats' target='_blank' class='referee-tag'>⚖️ {ref}</a>" if ref else "⚖️ TBD"
                        
                        col1, col2 = st.columns([3, 1.2])
                        with col1:
                            st.markdown(f"<div class='big-pick-box'><div class='big-pick-text'>{pick}</div><div style='margin-top:10px;'>{ref_html}</div></div>", unsafe_allow_html=True)
                        with col2:
                            pg = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
                            pc = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
                            st.markdown(f"<div class='edge-stats'><div style='color:#f97316; font-size:11px; font-weight:900; margin-bottom:10px;'>MATH EDGE</div><div class='stat-line'><span>xG</span> <b>{pg:.2f}</b></div><div class='stat-line'><span>Corners</span> <b>{pc:.1f}</b></div><div class='stat-line'><span>Cards</span> <b>{h_st['cards']+a_st['cards']:.1f}</b></div><div class='stat-line'><span>SOT</span> <b>{h_st['sotf']+a_st['sotf']:.1f}</b></div></div>", unsafe_allow_html=True)
