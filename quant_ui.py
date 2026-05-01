import streamlit as st
import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide")

# --- PREMIUM SPORTSBOOK CSS (BETANO STYLE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    .stApp { background-color: #0a0e17 !important; color: #ffffff !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 2px solid #1f2937; padding-bottom: 0; gap: 24px; }
    .stTabs [data-baseweb="tab"] { color: #64748b; font-weight: 700; text-transform: uppercase; font-size: 14px; letter-spacing: 0.5px; padding: 12px 0; border-radius: 0; border-bottom: 3px solid transparent; background-color: transparent !important; }
    .stTabs [aria-selected="true"] { color: #ff5a00 !important; border-bottom: 3px solid #ff5a00 !important; }
    [data-testid="stExpander"] { background-color: #141b26 !important; border: 1px solid #1f2937 !important; border-radius: 10px !important; margin-bottom: 12px; overflow: hidden; }
    [data-testid="stExpander"] details summary { background-color: #1a2230 !important; padding: 16px !important; color: #ffffff !important; border-bottom: 1px solid #1f2937; }
    [data-testid="stExpander"] details summary:hover { background-color: #1f2937 !important; }
    [data-testid="stExpander"] details summary p { font-weight: 700 !important; font-size: 15px !important; }
    .league-header { background-color: #1a2230; color: #ffffff; padding: 12px 16px; border-radius: 8px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; border-left: 4px solid #ff5a00; margin-top: 24px; margin-bottom: 16px; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .big-pick-box { background: linear-gradient(135deg, #ff5a00 0%, #ff8200 100%); padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 8px 25px rgba(255, 90, 0, 0.25); border: none; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .big-pick-text { font-size: 32px !important; font-weight: 900 !important; color: #ffffff !important; text-transform: uppercase; letter-spacing: -0.5px; margin-bottom: 10px; text-shadow: 1px 2px 4px rgba(0,0,0,0.15); }
    .referee-tag { color: #fff7ed; font-size: 13px; font-weight: 600; text-decoration: none; opacity: 0.9; }
    .referee-tag:hover { opacity: 1; text-decoration: underline; }
    .edge-stats { background-color: #141b26; padding: 20px; border-radius: 12px; border: 1px solid #1f2937; height: 100%; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2); }
    .stat-line { display: flex; justify-content: space-between; align-items: center; font-size: 14px; color: #94a3b8; margin-bottom: 12px; border-bottom: 1px solid #1f2937; padding-bottom: 8px; }
    .stat-line:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .stat-line b { font-size: 16px; color: #ffffff; font-weight: 700; }
    .slip-box { background-color: #141b26; padding: 20px; border-radius: 12px; border: 1px solid #ff5a00; border-left: 4px solid #ff5a00; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: LIVE MODE TOGGLE ---
with st.sidebar:
    st.markdown("<h3 style='color: #ff5a00;'>⚡ Terminal Settings</h3>", unsafe_allow_html=True)
    live_mode = st.toggle("Enable Live Auto-Refresh (60s)", value=False)
    if live_mode:
        st.success("Live Mode: ACTIVE")
        st.caption("Dashboard will automatically pull fresh data and live scores every 60 seconds.")
    else:
        st.warning("Live Mode: PAUSED")
        st.caption("Dashboard is static. Toggle on to auto-refresh.")

# --- TIME & FILE SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(hours=23)).strftime('%Y-%m-%d')
week_out_str = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')
LEDGER_FILE = "accuracy_ledger.json"

top_leagues = [
    "Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1",
    "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League",
    "Championship", "Eredivisie", "Primeira Liga", "Scottish Premiership", "Süper Lig", "First Division A",
    "Major League Soccer", "Brasileirão Série A", "Liga Profesional Argentina", "Saudi Pro League"
]
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
        s = {"gf":0, "ga":0, "cf":0, "ca":0, "sotf":0, "sota":0, "shotsf":0, "shotsa":0, "cards":0, "tackles":0, "cnt":0}
        if isinstance(res, list):
            finished = [m for m in res if m.get("match_status") == "Finished"]
            if venue == "home": relevant_games = [m for m in finished if m.get("match_hometeam_id") == team_id][-5:]
            else: relevant_games = [m for m in finished if m.get("match_awayteam_id") == team_id][-5:]
                
            for m in relevant_games:
                is_h = m.get("match_hometeam_id") == team_id
                s["gf"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
                s["ga"] += safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
                
                for row in m.get("statistics", []):
                    team_val = safe_num(row.get("home" if is_h else "away"))
                    opp_val = safe_num(row.get("away" if is_h else "home"))
                    stype = row.get("type")
                    
                    if stype == "Corners": 
                        s["cf"] += team_val
                        s["ca"] += opp_val
                    elif stype == "Yellow Cards":
                        s["cards"] += team_val
                    elif stype == "Shots On Goal":
                        s["sotf"] += team_val
                        s["sota"] += opp_val
                    elif stype == "Shots Total":
                        s["shotsf"] += team_val
                        s["shotsa"] += opp_val
                    elif stype == "Tackles":
                        s["tackles"] += team_val
                
                s["cnt"] += 1
        
        if s["cnt"] == 0: return None, 0
        return {k: (v/s["cnt"]) for k, v in s.items() if k != "cnt"}, s["cnt"]
    except: return None, 0

def generate_ai_pick(h_st, a_st):
    proj_goals = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
    proj_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
    proj_sot = ((h_st['sotf'] + a_st['sota']) / 2) + ((a_st['sotf'] + h_st['sota']) / 2)
    proj_shots = ((h_st['shotsf'] + a_st['shotsa']) / 2) + ((a_st['shotsf'] + h_st['shotsa']) / 2)
    proj_cards = h_st['cards'] + a_st['cards']
    proj_tackles = h_st['tackles'] + a_st['tackles']

    plays = []
    if proj_goals >= 3.2: plays.append(("⚽ Over 2.5 Goals", "goals", 2.5, 90))
    elif proj_goals <= 1.8: plays.append(("🛡️ Under 2.5 Goals", "under_goals", 2.5, 85))
    if proj_corners >= 11.0: plays.append(("🔥 Over 8.5 Corners", "corners", 8.5, 95))
    elif proj_corners >= 10.0: plays.append(("📊 Over 8.5 Corners", "corners", 8.5, 75))
    if proj_sot >= 10.5: plays.append(("🎯 Over 8.5 SOT", "sot", 8.5, 88))
    if proj_shots >= 27.0: plays.append(("🚀 Over 24.5 Shots", "shots", 24.5, 82))
    if proj_cards >= 5.8: plays.append(("🟨 Over 4.5 Cards", "cards", 4.5, 80))
    if proj_tackles >= 34.0: plays.append(("🪓 Over 30.5 Tackles", "tackles", 30.5, 83))

    if not plays: return "⚠️ NO PLAY", "pass", 0, 0
    plays.sort(key=lambda x: x[3], reverse=True)
    return plays[0]

@st.cache_data(ttl=300)
def get_fixtures(start_date, end_date):
    url = f"https://apiv3.apifootball.com/?action=get_events&from={start_date}&to={end_date}&APIkey={API_KEY}"
    return requests.get(url).json()

# --- APP LAYOUT ---
st.markdown("<h2 style='text-align: center; color: #ffffff; font-weight: 900; margin-bottom: 30px;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)

daily_matches = get_fixtures(today_str, today_str)
weekly_matches = get_fixtures(today_str, week_out_str)

tab1, tab2, tab3, tab4 = st.tabs(["🎟️ Auto-Acca", "📝 Weekly Slip", "🔥 Daily Picks", "📊 Accuracy"])

with tab1:
    st.markdown("### 🎟️ Algorithmic Odds Generator")
    odds_options = ["2.0 Odds (Safe Double)", "5.0 Odds (Standard)", "10.0 Odds", "15.0 Odds", "20.0 Odds", "30.0 Odds", "50.0 Odds", "100.0 Odds", "250.0 Odds", "500.0 Odds", "1000.0+ Odds"]
    target_odds = st.selectbox("Select Target Structure:", odds_options)
    
    if st.button("Generate Institutional Slip"):
        if isinstance(daily_matches, list):
            big_games = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
            valid_picks = []
            for m in big_games:
                h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                if h_st and a_st:
                    pick, p_type, thresh, conf = generate_ai_pick(h_st, a_st)
                    if p_type != "pass":
                        valid_picks.append({"match": f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}", "league": m.get('league_name'), "pick": pick, "conf": conf, "time": m.get('match_time')})
            
            valid_picks = sorted(valid_picks, key=lambda x: x['conf'], reverse=True)
            pick_count = 2 if "2.0" in target_odds else 4 if "5.0" in target_odds else 7 if "10.0" in target_odds else 12
            final_slip = valid_picks[:pick_count]
            
            if len(final_slip) < pick_count:
                st.warning(f"Engine is strict: Not enough high-confidence games today. Top {len(final_slip)} plays instead:")
            
            st.markdown("<div class='slip-box'>", unsafe_allow_html=True)
            for p in final_slip:
                st.markdown(f"<span style='color:#ff5a00; font-weight:bold;'>🏆 {p['league']}</span> | 🕒 {p['time']}<br> <b style='font-size:16px;'>{p['match']}</b> <br> ↳ <b style='color:#ffffff;'>{p['pick']}</b> (Conf: {p['conf']}%)", unsafe_allow_html=True)
                st.markdown("<hr style='border-color: #1f2937;'>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("### 📝 Build Your Own Weekly Slip")
    search_week = st.text_input("🔍 Search for a specific team (e.g., Arsenal, SC Braga):", key="search_week")
    
    if isinstance(weekly_matches, list):
        dates = sorted(list(set([m.get("match_date") for m in weekly_matches if m.get("match_status") != "Finished"])))
        selected_custom_picks = []
        for d in dates[:4]: 
            day_games = [m for m in weekly_matches if m.get("match_date") == d]
            if search_week:
                day_games = [m for m in day_games if search_week.lower() in m.get('match_hometeam_name', '').lower() or search_week.lower() in m.get('match_awayteam_name', '').lower()]
            else:
                day_games = [m for m in day_games if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
            
            if day_games:
                st.markdown(f"<h4 style='color:#ff5a00; margin-top:20px;'>📅 {d}</h4>", unsafe_allow_html=True)
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

with tab3:
    st.markdown("### 🔥 All System Picks Today")
    search_daily = st.text_input("🔍 Search for a specific team playing today:", key="search_daily")
    
    if isinstance(daily_matches, list):
        if search_daily:
            big_daily_games = [m for m in daily_matches if search_daily.lower() in m.get('match_hometeam_name', '').lower() or search_daily.lower() in m.get('match_awayteam_name', '').lower()]
        else:
            big_daily_games = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
            
        daily_leagues_dict = {}
        for m in big_daily_games:
            daily_leagues_dict.setdefault(m.get("league_name", "Other"), []).append(m)
            
        if not big_daily_games and search_daily:
            st.warning("No matches found for that team today. Try searching in the Weekly Slip tab.")
            
        for l_name, games in daily_leagues_dict.items():
            st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
            for m in games:
                h_name = m.get('match_hometeam_name')
                a_name = m.get('match_awayteam_name')
                
                # Dynamic title to show live score if match is happening
                match_status = m.get("match_status", "")
                if match_status == "Finished":
                    title_prefix = f"✅ FT | {m.get('match_hometeam_score')} - {m.get('match_awayteam_score')} |"
                elif match_status in ["Half Time", "1st Half", "2nd Half"]:
                    title_prefix = f"🔴 LIVE {m.get('match_hometeam_score')} - {m.get('match_awayteam_score')} |"
                else:
                    title_prefix = f"🕒 {m.get('match_time')} |"

                with st.expander(f"{title_prefix} {h_name} vs {a_name}"):
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    
                    if h_st and a_st:
                        pick, _, _, _ = generate_ai_pick(h_st, a_st)
                        
                        referee = m.get('match_referee')
                        if referee:
                            ref_link = f"https://www.google.com/search?q=football+referee+{referee.replace(' ', '+')}+stats"
                            ref_html = f"<a href='{ref_link}' target='_blank' class='referee-tag'>⚖️ REFEREE: {referee}</a>"
                        else:
                            ref_html = "<div class='referee-tag'>⚖️ TBD</div>"
                        
                        proj_goals = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
                        proj_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
                        proj_sot = ((h_st['sotf'] + a_st['sota']) / 2) + ((a_st['sotf'] + h_st['sota']) / 2)
                        proj_cards = h_st['cards'] + a_st['cards']
                        proj_tackles = h_st['tackles'] + a_st['tackles']
                        
                        c1, c2 = st.columns([2.5, 1.5])
                        with c1:
                            st.markdown(f"""
                                <div class='big-pick-box'>
                                    <div class='big-pick-text'>{pick}</div>
                                    {ref_html}
                                </div>
                            """, unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"""
                                <div class='edge-stats'>
                                    <div style='color:#ff5a00; font-size:11px; margin-bottom:12px; text-transform:uppercase; font-weight:800; letter-spacing:1px;'>Data Engine</div>
                                    <div class='stat-line'><span>Total xG</span> <b>{proj_goals:.2f}</b></div>
                                    <div class='stat-line'><span>Corners</span> <b>{proj_corners:.1f}</b></div>
                                    <div class='stat-line'><span>SOT</span> <b>{proj_sot:.1f}</b></div>
                                    <div class='stat-line'><span>Cards</span> <b>{proj_cards:.1f}</b></div>
                                    <div class='stat-line'><span>Tackles</span> <b>{proj_tackles:.1f}</b></div>
                                </div>
                            """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 📊 Historical Accuracy Ledger")
    
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            try: ledger = json.load(f)
            except: ledger = {}
    else:
        ledger = {}

    if yesterday_str not in ledger:
        with st.spinner(f"Evaluating {yesterday_str} results..."):
            yesterday_matches = get_fixtures(yesterday_str, yesterday_str)
            if isinstance(yesterday_matches, list):
                past_big = [m for m in yesterday_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries and m.get("match_status") == "Finished"]
                wins, total = 0, 0
                day_details = []
                
                for m in past_big:
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    if h_st and a_st:
                        pick, p_type, thresh, _ = generate_ai_pick(h_st, a_st)
                        if p_type != "pass":
                            total += 1
                            act_goals = safe_num(m.get("match_hometeam_score")) + safe_num(m.get("match_awayteam_score"))
                            act_corn = sum([safe_num(s.get("home")) + safe_num(s.get("away")) for s in m.get("statistics", []) if s.get("type") == "Corners"])
                            act_sot = sum([safe_num(s.get("home")) + safe_num(s.get("away")) for s in m.get("statistics", []) if s.get("type") == "Shots On Goal"])
                            act_shots = sum([safe_num(s.get("home")) + safe_num(s.get("away")) for s in m.get("statistics", []) if s.get("type") == "Shots Total"])
                            act_cards = sum([safe_num(s.get("home")) + safe_num(s.get("away")) for s in m.get("statistics", []) if s.get("type") == "Yellow Cards"])
                            act_tackles = sum([safe_num(s.get("home")) + safe_num(s.get("away")) for s in m.get("statistics", []) if s.get("type") == "Tackles"])
                            
                            won = False
                            if p_type == "corners" and act_corn > thresh: won = True
                            elif p_type == "goals" and act_goals > thresh: won = True
                            elif p_type == "under_goals" and act_goals < thresh: won = True
                            elif p_type == "sot" and act_sot > thresh: won = True
                            elif p_type == "shots" and act_shots > thresh: won = True
                            elif p_type == "cards" and act_cards > thresh: won = True
                            elif p_type == "tackles" and act_tackles > thresh: won = True
                            
                            if won: wins += 1
                            badge = "✅" if won else "❌"
                            day_details.append(f"{badge} **{m.get('league_name')}** | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')} | {pick}")
                
                if total > 0:
                    ledger[yesterday_str] = {
                        "win_rate": round((wins/total)*100, 1),
                        "wins": wins,
                        "total": total,
                        "details": day_details
                    }
                    with open(LEDGER_FILE, "w") as f:
                        json.dump(ledger, f)

    if not ledger:
        st.info("No completed games evaluated yet. Your tracker will build automatically.")
    else:
        for date_key in sorted(ledger.keys(), reverse=True):
            data = ledger[date_key]
            rate = data['win_rate']
            
            date_obj = datetime.strptime(date_key, "%Y-%m-%d")
            nice_date = date_obj.strftime("%B %d")
            
            if rate >= 70: color = "🟢"
            elif rate >= 55: color = "🟡"
            else: color = "🔴"
            
            with st.expander(f"{color} {nice_date} — {rate}% ({data['wins']} / {data['total']})"):
                for detail in data['details']:
                    st.markdown(detail)

# --- THE LIVE REFRESH LOOP ---
if live_mode:
    time.sleep(60)
    st.rerun()
