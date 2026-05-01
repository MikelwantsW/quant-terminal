import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide")

# --- ULTIMATE CSS OVERRIDE ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; font-family: 'Inter', sans-serif; }
    
    /* FIX FOR THE WHITE EXPANDER BUG */
    [data-testid="stExpander"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    [data-testid="stExpander"] details summary { background-color: #1e293b !important; color: #f8fafc !important; }
    
    /* TAB STYLING */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #16a34a !important; color: white !important; border-radius: 6px; }
    
    /* ODDS BUTTON STYLING */
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; transition: 0.3s; }
    
    /* UI COMPONENTS */
    .slip-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px dashed #f97316; margin-top: 10px; }
    .league-header { background-color: #1e293b; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-top: 20px; border-left: 4px solid #f97316; }
    
    .big-pick-box { background-color: #16a34a; padding: 25px; border-radius: 8px; text-align: center; border: 2px solid #22c55e; height: 100%; display: flex; flex-direction: column; justify-content: center;}
    .big-pick-text { font-size: 26px !important; font-weight: 900 !important; color: white !important; }
    
    .edge-stats { background-color: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; border-top: 3px solid #f97316; height: 100%; }
    .stat-line { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
    
    .risk-meter { padding: 10px; border-radius: 8px; text-align: center; font-weight: 900; text-transform: uppercase; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR LIVE CONTROLS ---
st.sidebar.title("⚡ Terminal Settings")
live_refresh = st.sidebar.toggle("Enable Live Auto-Refresh (60s)", value=False)
if live_refresh:
    time.sleep(60)
    st.rerun()

# --- CORE SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
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
        s = {"gf":0, "ga":0, "cf":0, "ca":0, "sotf":0, "sota":0, "shotsf":0, "shotsa":0, "cards":0, "cnt":0}
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
                    elif stype == "Shots Total": s["shotsf"] += t_val; s["shotsa"] += o_val
                s["cnt"] += 1
        return {k: (v/s["cnt"] if s["cnt"] > 0 else 0) for k, v in s.items() if k != "cnt"}, s["cnt"]
    except: return None, 0

def generate_ai_pick(h_st, a_st):
    proj_g = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
    proj_c = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
    proj_cd = h_st['cards'] + a_st['cards']
    picks = []
    if proj_g >= 3.2: picks.append(("⚽ Over 2.5 Goals", "goals", 2.5, 90))
    elif proj_g <= 1.8: picks.append(("🛡️ Under 2.5 Goals", "under_goals", 2.5, 85))
    if proj_c >= 11.0: picks.append(("🔥 Over 8.5 Corners", "corners", 8.5, 95))
    elif proj_c >= 9.5: picks.append(("📊 Over 8.5 Corners", "corners", 8.5, 75))
    if proj_cd >= 5.8: picks.append(("🟨 Over 4.5 Cards", "cards", 4.5, 80))
    picks.sort(key=lambda x: x[3], reverse=True)
    return picks[0] if picks else ("⚠️ NO PLAY", "pass", 0, 0)

# --- GET DATA ---
daily_matches = requests.get(f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}").json()
weekly_matches = requests.get(f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={week_out_str}&APIkey={API_KEY}").json()

st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["🎟️ Auto-Acca", "📝 Weekly Slip", "🔥 Daily Picks", "📊 Accuracy"])

# --- TAB 1: UPGRADED AUTO ACCA ---
with tab1:
    st.markdown("### 🎟️ Algorithmic Ticket Generator")
    st.caption("Select your target risk level to filter the engine's top institutional plays.")
    
    # Visual Selection Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: low_risk = st.button("🟢 2.0 Odds")
    with c2: mid_risk = st.button("🟡 5.0 Odds")
    with c3: std_risk = st.button("🟠 10.0 Odds")
    with c4: high_risk = st.button("🔴 50.0 Odds")
    with c5: moon_risk = st.button("🟣 1000.0+ Odds")

    selected_tier = None
    if low_risk: selected_tier = (2, "LOW RISK - CONSERVATIVE", "#16a34a")
    if mid_risk: selected_tier = (4, "MODERATE RISK", "#eab308")
    if std_risk: selected_tier = (7, "AGGRESSIVE QUANT", "#f97316")
    if high_risk: selected_tier = (12, "HIGH RISK - VOLATILE", "#ef4444")
    if moon_risk: selected_tier = (20, "INSTITUTIONAL MOONSHOT", "#a855f7")

    if selected_tier:
        st.markdown(f"<div class='risk-meter' style='background-color:{selected_tier[2]};'>{selected_tier[1]}</div>", unsafe_allow_html=True)
        
        if isinstance(daily_matches, list):
            big_games = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
            valid_picks = []
            with st.spinner("Analyzing high-confidence matchups..."):
                for m in big_games:
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    if h_st and a_st:
                        pick, _, _, conf = generate_ai_pick(h_st, a_st)
                        if conf > 0: valid_picks.append({"match": f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}", "league": m.get('league_name'), "pick": pick, "conf": conf, "time": m.get('match_time')})
            
            valid_picks.sort(key=lambda x: x['conf'], reverse=True)
            st.markdown("<div class='slip-box'>", unsafe_allow_html=True)
            for p in valid_picks[:selected_tier[0]]:
                st.markdown(f"🏆 **{p['league']}** | 🕒 {p['time']}<br> **{p['match']}** <br> ↳ <span style='color:{selected_tier[2]}; font-weight:bold;'>{p['pick']}</span>", unsafe_allow_html=True)
                st.markdown("---")
            st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: WEEKLY SLIP ---
with tab2:
    st.markdown("### 📝 Build Your Own Weekly Slip")
    search_query = st.text_input("🔍 Search for a specific team:")
    if isinstance(weekly_matches, list):
        filtered_weekly = [m for m in weekly_matches if search_query.lower() in m.get('match_hometeam_name','').lower() or search_query.lower() in m.get('match_awayteam_name','').lower()] if search_query else [m for m in weekly_matches if m.get("league_name") in top_leagues]
        dates = sorted(list(set([m.get("match_date") for m in filtered_weekly])))
        for d in dates:
            st.markdown(f"#### 📅 {d}")
            for m in [g for g in filtered_weekly if g.get("match_date") == d]:
                st.checkbox(f"🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}", key=f"{m.get('match_id')}_week")

# --- TAB 3: DAILY PICKS ---
with tab3:
    st.markdown("### 🔥 All System Picks Today")
    if isinstance(daily_matches, list):
        filtered = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
        for l_name in sorted(list(set([m.get("league_name") for m in filtered]))):
            st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
            for m in [g for g in filtered if g.get("league_name") == l_name]:
                status = m.get("match_status")
                is_live = status not in ["", "Finished", "Postponed"] and not status.isdigit()
                with st.expander(f"{'🔴 ' if is_live else ''}🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}"):
                    if is_live: st.markdown(f"<div class='live-score-banner'><span class='live-pulse'></span>LIVE: {m.get('match_hometeam_score')} - {m.get('match_awayteam_score')} ({status}')</div>", unsafe_allow_html=True)
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    if h_st and a_st:
                        pick, _, _, _ = generate_ai_pick(h_st, a_st)
                        ref = m.get('match_referee')
                        ref_html = f"<a href='https://www.google.com/search?q={ref.replace(' ','+')}+referee+stats' target='_blank' class='referee-tag'>⚖️ {ref}</a>" if ref else "⚖️ TBD"
                        c1, c2 = st.columns([3, 1.2])
                        with c1: st.markdown(f"<div class='big-pick-box'><div class='big-pick-text'>{pick}</div><div style='margin-top:10px;'>{ref_html}</div></div>", unsafe_allow_html=True)
                        with c2:
                            pg = ((h_st['gf']+a_st['ga'])/2)+((a_st['gf']+h_st['ga'])/2)
                            pc = ((h_st['cf']+a_st['ca'])/2)+((a_st['cf']+h_st['ca'])/2)
                            st.markdown(f"<div class='edge-stats'><div style='color:#f97316; font-size:11px; font-weight:900; margin-bottom:10px;'>MATH EDGE</div><div class='stat-line'><span>xG</span> <b>{pg:.2f}</b></div><div class='stat-line'><span>Corners</span> <b>{pc:.1f}</b></div><div class='stat-line'><span>Cards</span> <b>{h_st['cards']+a_st['cards']:.1f}</b></div></div>", unsafe_allow_html=True)

# --- TAB 4: ACCURACY ---
with tab4:
    st.markdown("### 📊 Yesterday's Accuracy")
    yesterday_res = requests.get(f"https://apiv3.apifootball.com/?action=get_events&from={yesterday_str}&to={yesterday_str}&APIkey={API_KEY}").json()
    if isinstance(yesterday_res, list):
        finished = [m for m in yesterday_res if m.get("league_name") in top_leagues and m.get("match_status") == "Finished"]
        wins, total = 0, 0
        for m in finished:
            h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
            a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
            if h_st and a_st:
                pick, p_type, thresh, conf = generate_ai_pick(h_st, a_st)
                if conf > 0:
                    total += 1
                    goals = safe_num(m.get("match_hometeam_score")) + safe_num(m.get("match_awayteam_score"))
                    won = (p_type == "goals" and goals > thresh) or (p_type == "under_goals" and goals < thresh)
                    if won: wins += 1
                    st.write(f"{'✅' if won else '❌'} {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')} | {pick}")
        if total > 0: st.metric("Win Rate", f"{(wins/total)*100:.1f}%")
