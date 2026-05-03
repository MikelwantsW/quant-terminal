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
    [data-testid="stExpander"] details summary:hover, [data-testid="stExpander"] details summary:focus { background-color: #334155 !important; color: #f8fafc !important; outline: none !important; }
    
    /* TAB STYLING */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #16a34a !important; color: white !important; border-radius: 6px; }
    
    /* UI COMPONENTS */
    .slip-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px dashed #f97316; margin-top: 10px; }
    .league-header { background-color: #1e293b; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-top: 20px; border-left: 4px solid #f97316; }
    .big-pick-box { background-color: #16a34a; padding: 25px; border-radius: 8px; text-align: center; border: 2px solid #22c55e; height: 100%; display: flex; flex-direction: column; justify-content: center;}
    .big-pick-text { font-size: 26px !important; font-weight: 900 !important; color: white !important; }
    .referee-tag { color: #fef08a; font-size: 13px; font-weight: bold; text-decoration: none; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; display: inline-block;}
    
    .edge-stats { background-color: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; border-top: 3px solid #f97316; height: 100%; }
    .stat-line { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
    .risk-meter { padding: 12px; border-radius: 8px; text-align: center; font-weight: 900; text-transform: uppercase; margin-bottom: 20px; color: white !important; }
    
    .live-score-banner { background-color: #ef4444; color: white; padding: 5px 15px; border-radius: 5px; font-weight: 900; font-size: 18px; margin-bottom: 15px; text-align: center; }
    .live-pulse { height: 10px; width: 10px; background-color: #fff; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & CACHE CONTROL ---
st.sidebar.title("⚡ Terminal Settings")
if st.sidebar.button("🧹 Nuclear Cache Refresh"):
    st.cache_data.clear()
    st.rerun()

live_refresh = st.sidebar.toggle("Enable Live Auto-Refresh (60s)", value=False)
if live_refresh:
    st.sidebar.success("🟢 LIVE MODE ACTIVE")
    time.sleep(60)
    st.rerun()

# --- DATA SETTINGS & VERIFIED WHITELIST ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')

top_leagues = ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League", "Championship", "Eredivisie", "Primeira Liga", "Süper Lig", "Major League Soccer"]

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

def generate_ai_pick(h_st, a_st, league):
    # Dynamic Math Edge Overhaul
    modifier = 0.80 if league == "La Liga" else 1.0 
    
    proj_g = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
    proj_c = (((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)) * modifier
    proj_sot = ((h_st['sotf'] + a_st['sota']) / 2) + ((a_st['sotf'] + h_st['sota']) / 2)
    proj_cd = h_st['cards'] + a_st['cards']
    
    plays = []
    
    # 1. DYNAMIC GOALS EDGE
    if proj_g >= 2.8:
        line = 3.5 if proj_g >= 4.0 else 2.5 if proj_g >= 3.0 else 1.5
        conf = min(99.0, 65.0 + ((proj_g - line) / line) * 100)
        plays.append((f"⚽ Over {line} Goals", "goals", line, conf))
    elif proj_g <= 2.2:
        line = 1.5 if proj_g <= 1.2 else 2.5 if proj_g <= 2.0 else 3.5
        conf = min(99.0, 65.0 + ((line - proj_g) / line) * 100)
        plays.append((f"🔒 Under {line} Goals", "under_goals", line, conf))

    # 2. DYNAMIC CORNERS EDGE
    if proj_c >= 9.5:
        lines = [7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5]
        valid = [l for l in lines if l <= proj_c - 1.5]
        if valid:
            line = max(valid)
            conf = min(99.0, 65.0 + ((proj_c - line) / line) * 80) # Scaled down so it doesn't overpower SOT/Goals
            plays.append((f"🔥 Over {line} Corners", "corners", line, conf))
    elif proj_c <= 8.5:
        lines = [6.5, 7.5, 8.5, 9.5, 10.5, 11.5]
        valid = [l for l in lines if l >= proj_c + 1.5]
        if valid:
            line = min(valid)
            conf = min(99.0, 65.0 + ((line - proj_c) / line) * 80)
            plays.append((f"🛡️ Under {line} Corners", "under_corners", line, conf))

    # 3. DYNAMIC CARDS EDGE
    if proj_cd >= 4.5:
        lines = [3.5, 4.5, 5.5, 6.5]
        valid = [l for l in lines if l <= proj_cd - 1.0]
        if valid:
            line = max(valid)
            conf = min(99.0, 65.0 + ((proj_cd - line) / line) * 60) # High variance, lower weight
            plays.append((f"🟨 Over {line} Cards", "cards", line, conf))
    elif proj_cd <= 3.5:
        lines = [3.5, 4.5, 5.5]
        valid = [l for l in lines if l >= proj_cd + 1.0]
        if valid:
            line = min(valid)
            conf = min(99.0, 65.0 + ((line - proj_cd) / line) * 60)
            plays.append((f"🧊 Under {line} Cards", "under_cards", line, conf))

    # 4. DYNAMIC SOT EDGE
    if proj_sot >= 8.5:
        lines = [7.5, 8.5, 9.5, 10.5, 11.5]
        valid = [l for l in lines if l <= proj_sot - 1.5]
        if valid:
            line = max(valid)
            conf = min(99.0, 65.0 + ((proj_sot - line) / line) * 70)
            plays.append((f"🎯 Over {line} SOT", "sot", line, conf))
    elif proj_sot <= 7.0:
        lines = [6.5, 7.5, 8.5, 9.5]
        valid = [l for l in lines if l >= proj_sot + 1.5]
        if valid:
            line = min(valid)
            conf = min(99.0, 65.0 + ((line - proj_sot) / line) * 70)
            plays.append((f"🧱 Under {line} SOT", "under_sot", line, conf))

    # Sort to find the highest percentage edge relative to the line
    plays.sort(key=lambda x: x[3], reverse=True)
    return plays[0] if plays else ("⚠️ NO PLAY", "pass", 0, 0)

# --- FETCH VERIFIED DATA ---
def get_verified_data(date_str):
    url = f"https://apiv3.apifootball.com/?action=get_events&from={date_str}&to={date_str}&APIkey={API_KEY}"
    res = requests.get(url).json()
    if isinstance(res, list):
        return [m for m in res if m.get("league_name") in top_leagues]
    return []

daily_matches = get_verified_data(today_str)
weekly_matches = requests.get(f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={week_out_str}&APIkey={API_KEY}").json()

st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["🎟️ Auto-Acca", "📝 Weekly Slip", "🔥 Daily Picks", "📊 Accuracy"])

# --- TAB 1: AUTO ACCA ---
with tab1:
    st.markdown("### 🎟️ Algorithmic Ticket Generator")
    r1 = st.columns(4)
    r2 = st.columns(4)
    
    selection = None
    with r1[0]:
        if st.button("🟢 2.0 Odds"): selection = (2, "SAFE DOUBLE", "#16a34a")
    with r1[1]:
        if st.button("🟡 5.0 Odds"): selection = (4, "MODERATE", "#eab308")
    with r1[2]:
        if st.button("🟠 10.0 Odds"): selection = (6, "AGGRESSIVE", "#f97316")
    with r1[3]:
        if st.button("🔴 20.0 Odds"): selection = (8, "SYSTEM ACCA", "#dc2626")
    with r2[0]:
        if st.button("🟣 100.0 Odds"): selection = (12, "WHALE TIER", "#9333ea")
    with r2[1]:
        if st.button("🔵 250.0 Odds"): selection = (15, "QUANT JACKPOT", "#2563eb")
    with r2[2]:
        if st.button("🔥 500.0 Odds"): selection = (18, "THE GAUNTLET", "#ea580c")
    with r2[3]:
        if st.button("🌌 1000.0+ Odds"): selection = (25, "MOONSHOT", "#000000")

    if selection:
        st.markdown(f"<div class='risk-meter' style='background-color:{selection[2]};'>{selection[1]}</div>", unsafe_allow_html=True)
        valid_picks = []
        with st.spinner("Crunching dynamic edges across all markets..."):
            for m in daily_matches:
                h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                if h_st and a_st:
                    pick, _, _, conf = generate_ai_pick(h_st, a_st, m.get('league_name'))
                    if conf > 0:
                        valid_picks.append({"match": f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}", "league": m.get('league_name'), "pick": pick, "conf": conf, "time": m.get('match_time')})
        valid_picks.sort(key=lambda x: x['conf'], reverse=True)
        st.markdown("<div class='slip-box'>", unsafe_allow_html=True)
        for p in valid_picks[:selection[0]]:
            st.markdown(f"🏆 **{p['league']}** | 🕒 {p['time']}<br> **{p['match']}** <br> ↳ <span style='color:{selection[2]}; font-weight:bold;'>{p['pick']}</span>", unsafe_allow_html=True)
            st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: WEEKLY SLIP ---
with tab2:
    st.markdown("### 📝 Build Your Own Weekly Slip")
    search_q = st.text_input("🔍 Search for a team (e.g., Chelsea, Milan):")
    if isinstance(weekly_matches, list):
        filtered_weekly = [m for m in weekly_matches if search_q.lower() in m.get('match_hometeam_name','').lower() or search_q.lower() in m.get('match_awayteam_name','').lower()] if search_q else [m for m in weekly_matches if m.get("league_name") in top_leagues]
        for d in sorted(list(set([m.get("match_date") for m in filtered_weekly]))):
            st.markdown(f"#### 📅 {d}")
            for m in [g for g in filtered_weekly if g.get("match_date") == d]:
                st.checkbox(f"🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}", key=f"{m.get('match_id')}_w")

# --- TAB 3: DAILY PICKS ---
with tab3:
    st.markdown("### 🔥 All System Picks Today")
    leagues = sorted(list(set([m.get("league_name") for m in daily_matches])))
    for l_name in leagues:
        st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
        for m in [g for g in daily_matches if g.get("league_name") == l_name]:
            status = m.get("match_status")
            is_live = status not in ["", "Finished", "Postponed"] and not status.isdigit()
            with st.expander(f"{'🔴 ' if is_live else ''}🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}"):
                if is_live: st.markdown(f"<div class='live-score-banner'><span class='live-pulse'></span>LIVE: {m.get('match_hometeam_score')} - {m.get('match_awayteam_score')} ({status}')</div>", unsafe_allow_html=True)
                h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                if h_st and a_st:
                    pick, _, _, _ = generate_ai_pick(h_st, a_st, l_name)
                    ref = m.get('match_referee')
                    ref_html = f"<a href='https://www.google.com/search?q={ref.replace(' ','+')}+referee+stats' target='_blank' class='referee-tag'>⚖️ {ref}</a>" if ref else "⚖️ TBD"
                    c1, c2 = st.columns([3, 1.2])
                    with c1: st.markdown(f"<div class='big-pick-box'><div class='big-pick-text'>{pick}</div><div style='margin-top:10px;'>{ref_html}</div></div>", unsafe_allow_html=True)
                    with c2:
                        pg = ((h_st['gf']+a_st['ga'])/2)+((a_st['gf']+h_st['ga'])/2)
                        pc = ((h_st['cf']+a_st['ca'])/2)+((a_st['cf']+h_st['ca'])/2)
                        st.markdown(f"<div class='edge-stats'><div style='color:#f97316; font-size:11px; font-weight:900; margin-bottom:10px;'>MATH EDGE</div><div class='stat-line'><span>xG</span> <b>{pg:.2f}</b></div><div class='stat-line'><span>Corners</span> <b>{pc:.1f}</b></div><div class='stat-line'><span>Cards</span> <b>{h_st['cards']+a_st['cards']:.1f}</b></div><div class='stat-line'><span>SOT</span> <b>{h_st['sotf']+a_st['sotf']:.1f}</b></div></div>", unsafe_allow_html=True)

# --- TAB 4: ACCURACY ---
with tab4:
    st.markdown("### 📊 Yesterday's Accuracy")
    yesterday_res = get_verified_data(yesterday_str)
    finished = [m for m in yesterday_res if m.get("match_status") == "Finished"]
    wins, total = 0, 0
    for m in finished:
        h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
        a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
        if h_st and a_st:
            pick, p_type, thresh, conf = generate_ai_pick(h_st, a_st, m.get('league_name'))
            if conf > 0:
                total += 1
                goals = safe_num(m.get("match_hometeam_score")) + safe_num(m.get("match_awayteam_score"))
                won = (p_type == "goals" and goals > thresh) or (p_type == "under_goals" and goals < thresh)
                if won: wins += 1
                st.write(f"{'✅' if won else '❌'} {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')} | {pick}")
    if total > 0: st.metric("System Win Rate", f"{(wins/total)*100:.1f}%")
