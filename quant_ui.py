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
    
    /* Fix Expander White-Out Bug */
    [data-testid="stExpander"] details summary { background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
    [data-testid="stExpander"] details summary:hover { background-color: #334155 !important; }
    [data-testid="stExpander"] details summary p { color: #f8fafc !important; font-weight: bold !important; }
    
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; padding: 5px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: 600; padding: 10px 15px; }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; border-radius: 6px; }
    .slip-box { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px dashed #38bdf8; margin-top: 10px; }
    .league-header { background-color: #1d4ed8; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; }
    
    /* Minimalist UI Classes */
    .big-pick-box { background-color: #2563eb; padding: 30px; border-radius: 8px; text-align: center; border: 1px solid #3b82f6; height: 100%; display: flex; flex-direction: column; justify-content: center;}
    .big-pick-text { font-size: 28px !important; font-weight: 900 !important; color: white !important; margin-bottom: 8px; }
    .referee-tag { color: #fca5a5; font-size: 14px; font-weight: bold; text-decoration: none; }
    .referee-tag:hover { color: white !important; }
    .edge-stats { background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; height: 100%; }
    .stat-line { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 4px; }
    .stat-line:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- TIME SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')

# --- EXPANDED INSTITUTIONAL WHITELIST ---
top_leagues = [
    "Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1",
    "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League",
    "Championship", "Eredivisie", "Primeira Liga", "Scottish Premiership", "Süper Lig", "First Division A",
    "Major League Soccer", "Brasileirão Série A", "Liga Profesional Argentina", "Saudi Pro League"
]
top_countries = ["England", "Italy", "Spain", "Germany", "France", "eurocups", "Netherlands", "Portugal", "Scotland", "Turkey", "Belgium", "USA", "Brazil", "Argentina", "Saudi Arabia"]

# --- THE SILENT RIVALRY MATRIX ---
# You can add as many local derbies here as you want.
DERBY_DATABASE = [
    ["Arsenal", "Tottenham"], ["Real Madrid", "Barcelona"], ["Galatasaray", "Fenerbahce"],
    ["Boca", "River"], ["Celtic", "Rangers"], ["Man United", "Man City"],
    ["Manchester United", "Manchester City"], ["Inter", "Milan"], ["Lazio", "Roma"],
    ["Liverpool", "Everton"], ["Aston Villa", "Birmingham"], ["Newcastle", "Sunderland"],
    ["Betis", "Sevilla"], ["Atletico", "Real Madrid"], ["Juventus", "Torino"],
    ["Bayern", "Dortmund"], ["PSG", "Marseille"], ["Fenerbahce", "Besiktas"],
    ["Galatasaray", "Besiktas"], ["Sporting", "Benfica"], ["Porto", "Benfica"]
]

def is_derby(h_name, a_name):
    h_lower = h_name.lower()
    a_lower = a_name.lower()
    for pair in DERBY_DATABASE:
        if (pair[0].lower() in h_lower and pair[1].lower() in a_lower) or \
           (pair[1].lower() in h_lower and pair[0].lower() in a_lower):
            return True
    return False

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
        s = {"gf":0, "ga":0, "cf":0, "ca":0, "sotf":0, "sota":0, "shotsf":0, "shotsa":0, "cards":0, "cnt":0}
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
                
                s["cnt"] += 1
        
        if s["cnt"] == 0: return None, 0
        return {k: (v/s["cnt"]) for k, v in s.items() if k != "cnt"}, s["cnt"]
    except: return None, 0

def generate_ai_pick(h_st, a_st, h_name="", a_name=""):
    proj_goals = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
    proj_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
    proj_sot = ((h_st['sotf'] + a_st['sota']) / 2) + ((a_st['sotf'] + h_st['sota']) / 2)
    proj_shots = ((h_st['shotsf'] + a_st['shotsa']) / 2) + ((a_st['shotsf'] + h_st['shotsa']) / 2)
    proj_cards = h_st['cards'] + a_st['cards']

    # AUTOMATED RIVALRY SHIELD: Bumps expected cards massively if a derby is detected
    if is_derby(h_name, a_name):
        proj_cards += 2.5 

    plays = []
    
    # Evaluate Goals
    if proj_goals >= 3.2: plays.append(("⚽ Over 2.5 Goals", "goals", 2.5, 90))
    elif proj_goals <= 1.8: plays.append(("🛡️ Under 2.5 Goals", "under_goals", 2.5, 85))
    
    # Evaluate Corners
    if proj_corners >= 11.0: plays.append(("🔥 Over 8.5 Corners", "corners", 8.5, 95))
    elif proj_corners >= 10.0: plays.append(("📊 Over 8.5 Corners", "corners", 8.5, 75))
    
    # Evaluate SOT
    if proj_sot >= 10.5: plays.append(("🎯 Over 8.5 SOT", "sot", 8.5, 88))
    
    # Evaluate Total Shots
    if proj_shots >= 27.0: plays.append(("🚀 Over 24.5 Shots", "shots", 24.5, 82))
    
    # Evaluate Cards (Will trigger much more often if Derby Shield is active)
    if proj_cards >= 5.8: plays.append(("🟨 Over 4.5 Cards", "cards", 4.5, 80))

    if not plays:
        return "⚠️ NO PLAY", "pass", 0, 0
    
    plays.sort(key=lambda x: x[3], reverse=True)
    return plays[0]

# --- APP LAYOUT ---
st.markdown("<h2 style='text-align: center;'>🏦 Institutional Quant Radar</h2>", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_fixtures(start_date, end_date):
    url = f"https://apiv3.apifootball.com/?action=get_events&from={start_date}&to={end_date}&APIkey={API_KEY}"
    return requests.get(url).json()

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
                h_name = m.get('match_hometeam_name', "")
                a_name = m.get('match_awayteam_name', "")
                if h_st and a_st:
                    pick, p_type, thresh, conf = generate_ai_pick(h_st, a_st, h_name, a_name)
                    if p_type != "pass":
                        valid_picks.append({"match": f"{h_name} vs {a_name}", "league": m.get('league_name'), "pick": pick, "conf": conf, "time": m.get('match_time')})
            
            valid_picks = sorted(valid_picks, key=lambda x: x['conf'], reverse=True)
            pick_count = 2 if "2.0" in target_odds else 4 if "5.0" in target_odds else 7 if "10.0" in target_odds else 12
            final_slip = valid_picks[:pick_count]
            
            if len(final_slip) < pick_count:
                st.warning(f"Engine is strict: Not enough high-confidence games today. Top {len(final_slip)} plays instead:")
            
            st.markdown("<div class='slip-box'>", unsafe_allow_html=True)
            for p in final_slip:
                st.markdown(f"🏆 **{p['league']}** | 🕒 {p['time']}<br> **{p['match']}** <br> ↳ **{p['pick']}** (Conf: {p['conf']}%)", unsafe_allow_html=True)
                st.markdown("---")
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
                st.markdown(f"#### 📅 {d}")
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
                
                with st.expander(f"🕒 {m.get('match_time')} | {h_name} vs {a_name}"):
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    
                    if h_st and a_st:
                        pick, _, _, _ = generate_ai_pick(h_st, a_st, h_name, a_name)
                        
                        referee = m.get('match_referee')
                        if referee:
                            ref_link = f"https://www.google.com/search?q=football+referee+{referee.replace(' ', '+')}+stats"
                            ref_html = f"<a href='{ref_link}' target='_blank' class='referee-tag'>⚖️ {referee}</a>"
                        else:
                            ref_html = "<div class='referee-tag'>⚖️ TBD</div>"
                        
                        proj_goals = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
                        proj_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
                        proj_sot = ((h_st['sotf'] + a_st['sota']) / 2) + ((a_st['sotf'] + h_st['sota']) / 2)
                        proj_cards = h_st['cards'] + a_st['cards']
                        
                        if is_derby(h_name, a_name):
                            proj_cards += 2.5
                            derby_tag = "<div style='color:#ef4444; font-size:12px; font-weight:bold; margin-top:5px;'>🔥 DERBY SHIELD ACTIVE (+2.5 Cards)</div>"
                        else:
                            derby_tag = ""
                        
                        c1, c2 = st.columns([3, 1.2])
                        with c1:
                            st.markdown(f"""
                                <div class='big-pick-box'>
                                    <div class='big-pick-text'>{pick}</div>
                                    {ref_html}
                                    {derby_tag}
                                </div>
                            """, unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"""
                                <div class='edge-stats'>
                                    <div style='color:#94a3b8; font-size:11px; margin-bottom:8px; text-transform:uppercase; font-weight:bold;'>Proj. Data</div>
                                    <div class='stat-line'><span>xG</span> <b>{proj_goals:.2f}</b></div>
                                    <div class='stat-line'><span>Corners</span> <b>{proj_corners:.1f}</b></div>
                                    <div class='stat-line'><span>SOT</span> <b>{proj_sot:.1f}</b></div>
                                    <div class='stat-line'><span>Cards</span> <b>{proj_cards:.1f}</b></div>
                                </div>
                            """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 📊 Yesterday's Accuracy & Calibration")
    yesterday_matches = get_fixtures(yesterday_str, yesterday_str)
    if isinstance(yesterday_matches, list):
        past_big = [m for m in yesterday_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries and m.get("match_status") == "Finished"]
        wins, total = 0, 0
        for m in past_big:
            h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
            a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
            h_name = m.get('match_hometeam_name', "")
            a_name = m.get('match_awayteam_name', "")
            if h_st and a_st:
                pick, p_type, thresh, _ = generate_ai_pick(h_st, a_st, h_name, a_name)
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
                    st.write(f"{badge} **{m.get('league_name')}** | {h_name} vs {a_name} | {pick}")
                    
        if total > 0:
            st.metric("System Win Rate", f"{(wins/total)*100:.1f}%")
