import streamlit as st
import requests
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide")

# --- PROFESSIONAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, p, span, label { color: #f8fafc !important; }
    .streamlit-expanderHeader { background-color: #1e293b !important; border-radius: 8px !important; font-weight: bold; border: 1px solid #334155; }
    div[data-testid="stMetric"] { background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 20px !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; border-radius: 6px; }
    .slip-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px dashed #38bdf8; margin-top: 10px; }
    .league-header { background-color: #2563eb; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- TIME SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')

# --- EXPANDED INSTITUTIONAL WHITELIST ---
top_leagues = [
    "Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1",
    "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League",
    "Championship", "Eredivisie", "Primeira Liga", "Scottish Premiership", "Süper Lig", "First Division A",
    "Major League Soccer", "Brasileirão Série A", "Liga Profesional Argentina", "Saudi Pro League"
]

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
        s = {"goals":0, "corners":0, "cards":0, "shots":0, "sot":0, "goalkicks":0, "cnt":0}
        if isinstance(res, list):
            recent = [m for m in res if m.get("match_status") == "Finished"][-5:]
            for m in recent:
                is_h = m.get("match_hometeam_id") == team_id
                s["goals"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
                for row in m.get("statistics", []):
                    val = safe_num(row.get("home" if is_h else "away"))
                    stype = row.get("type")
                    if stype == "Corners": s["corners"] += val
                    elif stype == "Yellow Cards": s["cards"] += val
                    elif stype == "Shots Total": s["shots"] += val
                    elif stype == "Shots On Goal": s["sot"] += val
                    elif stype == "Goal Kicks": s["goalkicks"] += val
                s["cnt"] += 1
        return {k: (v/s["cnt"] if s["cnt"] > 0 else 0) for k, v in s.items()}, s["cnt"]
    except: return None, 0

def generate_ai_pick(h_st, a_st):
    total_corners = h_st['corners'] + a_st['corners']
    total_goals = h_st['goals'] + a_st['goals']
    
    if total_corners >= 11.5: return "🔥 Over 8.5 Corners", "corners", 8.5, 95
    elif total_goals >= 3.2: return "⚽ Over 2.5 Goals", "goals", 2.5, 90
    elif total_corners >= 10.0: return "📊 Over 8.5 Corners", "corners", 8.5, 75
    elif total_goals <= 1.5: return "🛡️ Under 2.5 Goals", "under_goals", 2.5, 80
    else: return "⚠️ NO PLAY", "pass", 0, 0

# --- APP LAYOUT ---
st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_fixtures(start_date, end_date):
    url = f"https://apiv3.apifootball.com/?action=get_events&from={start_date}&to={end_date}&APIkey={API_KEY}"
    return requests.get(url).json()

daily_matches = get_fixtures(today_str, today_str)
weekly_matches = get_fixtures(today_str, week_out_str)

tab1, tab2, tab3, tab4 = st.tabs(["🎟️ Auto-Acca", "📝 Weekly Slip", "🔥 Daily Picks", "📊 Accuracy"])

# --- TAB 1: AUTO ACCUMULATOR ---
with tab1:
    st.markdown("### 🎟️ Algorithmic Odds Generator")
    target_odds = st.radio("Select Target Structure:", ["2.0 Odds (Safe Double)", "5.0 Odds (Standard)", "10.0+ Odds (Moonshot)"])
    if st.button("Generate Institutional Slip"):
        if isinstance(daily_matches, list):
            big_games = [m for m in daily_matches if any(l in m.get("league_name", "") for l in top_leagues)]
            valid_picks = []
            for m in big_games:
                h_st, _ = fetch_stats(m.get("match_hometeam_id"))
                a_st, _ = fetch_stats(m.get("match_awayteam_id"))
                if h_st and a_st:
                    pick, p_type, thresh, conf = generate_ai_pick(h_st, a_st)
                    if p_type != "pass":
                        valid_picks.append({"match": f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}", "league": m.get('league_name'), "pick": pick, "conf": conf, "time": m.get('match_time')})
            valid_picks = sorted(valid_picks, key=lambda x: x['conf'], reverse=True)
            pick_count = 2 if "2.0" in target_odds else 4 if "5.0" in target_odds else 7
            final_slip = valid_picks[:pick_count]
            st.markdown("<div class='slip-box'>", unsafe_allow_html=True)
            for p in final_slip:
                st.markdown(f"🏆 **{p['league']}** | 🕒 {p['time']}<br> **{p['match']}** <br> ↳ **{p['pick']}** (Conf: {p['conf']}%)", unsafe_allow_html=True)
                st.markdown("---")
            st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: MANUAL WEEKLY SLIP BUILDER ---
with tab2:
    st.markdown("### 📝 Build Your Own Weekly Slip")
    if isinstance(weekly_matches, list):
        dates = sorted(list(set([m.get("match_date") for m in weekly_matches if m.get("match_status") != "Finished"])))
        selected_custom_picks = []
        for d in dates[:4]: 
            st.markdown(f"#### 📅 {d}")
            day_games = [m for m in weekly_matches if m.get("match_date") == d and any(l in m.get("league_name", "") for l in top_leagues)]
            leagues_dict = {}
            for m in day_games:
                leagues_dict.setdefault(m.get("league_name", "Other"), []).append(m)
            for l_name, games in leagues_dict.items():
                st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
                for m in games:
                    match_label = f"🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}"
                    if st.checkbox(match_label, key=m.get("match_id")):
                        selected_custom_picks.append(f"{d} | {l_name} | {match_label}")
        if selected_custom_picks:
            st.success("🎟️ **Your Custom Slip:**")
            for pick in selected_custom_picks: st.write(f"- {pick}")

# --- TAB 3: DAILY PICKS (DEEP STATS RESTORED) ---
with tab3:
    st.markdown("### 🔥 All System Picks Today")
    if isinstance(daily_matches, list):
        big_daily_games = [m for m in daily_matches if any(l in m.get("league_name", "") for l in top_leagues)]
        daily_leagues_dict = {}
        for m in big_daily_games:
            daily_leagues_dict.setdefault(m.get("league_name", "Other"), []).append(m)
            
        for l_name, games in daily_leagues_dict.items():
            st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
            for m in games:
                h_name = m.get('match_hometeam_name')
                a_name = m.get('match_awayteam_name')
                with st.expander(f"🕒 {m.get('match_time')} | {h_name} vs {a_name}"):
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"))
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"))
                    
                    if h_st and a_st:
                        pick, _, _, _ = generate_ai_pick(h_st, a_st)
                        st.markdown(f"<div style='text-align:center; padding:8px; background-color:#3b82f6; border-radius:6px; margin-bottom:10px;'><b>Engine Pick:</b> {pick}</div>", unsafe_allow_html=True)
                        
                        # --- THE FULL INSTITUTIONAL GRID ---
                        st.caption("Average metrics over the last 5 completed games")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric(f"{h_name[:10]} SOT", f"{h_st['sot']:.1f}")
                            st.metric("Total Shots", f"{h_st['shots']:.1f}")
                            st.metric("Cards", f"{h_st['cards']:.1f}")
                        with c2:
                            st.metric("Target Total SOT", f"{h_st['sot'] + a_st['sot']:.1f}")
                            st.metric("Target Goal Kicks", f"{h_st['goalkicks'] + a_st['goalkicks']:.1f}")
                            st.metric("Target Corners", f"{h_st['corners'] + a_st['corners']:.1f}")
                        with c3:
                            st.metric(f"{a_name[:10]} SOT", f"{a_st['sot']:.1f}")
                            st.metric("Total Shots", f"{a_st['shots']:.1f}")
                            st.metric("Cards", f"{a_st['cards']:.1f}")

# --- TAB 4: ACCURACY TRACKER ---
with tab4:
    st.markdown("### 📊 Yesterday's Accuracy & Calibration")
    yesterday_matches = get_fixtures(yesterday_str, yesterday_str)
    if isinstance(yesterday_matches, list):
        past_big = [m for m in yesterday_matches if any(l in m.get("league_name", "") for l in top_leagues) and m.get("match_status") == "Finished"]
        wins, total = 0, 0
        for m in past_big:
            h_st, _ = fetch_stats(m.get("match_hometeam_id"))
            a_st, _ = fetch_stats(m.get("match_awayteam_id"))
            if h_st and a_st:
                pick, p_type, thresh, _ = generate_ai_pick(h_st, a_st)
                if p_type != "pass":
                    total += 1
                    act_goals = safe_num(m.get("match_hometeam_score")) + safe_num(m.get("match_awayteam_score"))
                    act_corn = sum([safe_num(s.get("home")) + safe_num(s.get("away")) for s in m.get("statistics", []) if s.get("type") == "Corners"])
                    
                    won = False
                    if p_type == "corners" and act_corn > thresh: won = True
                    if p_type == "goals" and act_goals > thresh: won = True
                    if p_type == "under_goals" and act_goals < thresh: won = True
                    
                    if won: wins += 1
                    badge = "✅" if won else "❌"
                    st.write(f"{badge} **{m.get('league_name')}** | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')} | {pick}")
                    
        if total > 0:
            st.metric("System Win Rate", f"{(wins/total)*100:.1f}%")
