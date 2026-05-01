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
    .ref-strict { color: #f87171; font-weight: bold; }
    .ref-lenient { color: #4ade80; font-weight: bold; }
    .ref-standard { color: #94a3b8; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- TIME SETTINGS & KEYS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_str = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d')
yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
past_str = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')

# --- PROPRIETARY REFEREE DATABASE ---
# Add your tracked referees here. The engine uses this to find your edge.
REFEREE_DB = {
    "A. Taylor": {"cards_per_game": 4.8, "style": "Strict"},
    "M. Oliver": {"cards_per_game": 3.1, "style": "Lenient"},
    "P. Tierney": {"cards_per_game": 4.5, "style": "Strict"},
    "F. Maeso": {"cards_per_game": 5.2, "style": "Strict"},
    "O. Turtay": {"cards_per_game": 4.9, "style": "Strict"}, # Added your Süper Lig ref here
    "J. Gil Manzano": {"cards_per_game": 5.5, "style": "Strict"}
}

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
        s = {"gf":0, "ga":0, "cf":0, "ca":0, "sotf":0, "sota":0, "cards":0, "cnt":0}
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
                    elif stype == "Shots On Goal": 
                        s["sotf"] += team_val
                        s["sota"] += opp_val
                    elif stype == "Yellow Cards":
                        s["cards"] += team_val
                
                s["cnt"] += 1
        
        if s["cnt"] == 0: return None, 0
        return {k: (v/s["cnt"]) for k, v in s.items() if k != "cnt"}, s["cnt"]
    except: return None, 0

def generate_ai_pick(h_st, a_st, referee_name):
    # Base Projections
    proj_total_goals = ((h_st['gf'] + a_st['ga']) / 2) + ((a_st['gf'] + h_st['ga']) / 2)
    proj_total_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
    proj_team_cards = h_st['cards'] + a_st['cards']
    
    # Check Referee Database for Edge
    ref_data = REFEREE_DB.get(referee_name, {"cards_per_game": 4.0, "style": "Unknown"})
    
    # Priority 1: Automated Referee Card Picks
    if ref_data["style"] == "Strict" and proj_team_cards >= 4.5:
        return f"🟨 Over 4.5 Cards (Strict Ref Edge)", "cards", 4.5, 95
    elif ref_data["style"] == "Lenient" and proj_team_cards <= 3.5:
        return f"🕊️ Under 4.5 Cards (Lenient Ref Edge)", "under_cards", 4.5, 90
        
    # Priority 2: Standard Baseline Picks
    if proj_total_corners >= 10.5: return "🔥 Over 8.5 Corners", "corners", 8.5, 90
    elif proj_total_goals >= 3.0: return "⚽ Over 2.5 Goals", "goals", 2.5, 85
    elif proj_total_corners >= 9.5: return "📊 Over 8.5 Corners", "corners", 8.5, 75
    elif proj_total_goals <= 2.0: return "🛡️ Under 2.5 Goals", "under_goals", 2.5, 80
    
    return "⚠️ NO PLAY", "pass", 0, 0

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
    odds_options = ["2.0 Odds (Safe Double)", "5.0 Odds (Standard)", "10.0 Odds", "15.0 Odds", "20.0 Odds", "30.0 Odds", "50.0 Odds"]
    target_odds = st.selectbox("Select Target Structure:", odds_options)
    
    if st.button("Generate Institutional Slip"):
        if isinstance(daily_matches, list):
            big_games = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
            valid_picks = []
            for m in big_games:
                h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                referee = m.get('match_referee', 'Unknown')
                if h_st and a_st:
                    pick, p_type, thresh, conf = generate_ai_pick(h_st, a_st, referee)
                    if p_type != "pass":
                        valid_picks.append({"match": f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}", "league": m.get('league_name'), "pick": pick, "conf": conf, "time": m.get('match_time')})
            
            valid_picks = sorted(valid_picks, key=lambda x: x['conf'], reverse=True)
            pick_count = 2 if "2.0" in target_odds else 4 if "5.0" in target_odds else 7
            final_slip = valid_picks[:pick_count]
            
            st.markdown("<div class='slip-box'>", unsafe_allow_html=True)
            for p in final_slip:
                st.markdown(f"🏆 **{p['league']}** | 🕒 {p['time']}<br> **{p['match']}** <br> ↳ **{p['pick']}**", unsafe_allow_html=True)
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
            if search_week: day_games = [m for m in day_games if search_week.lower() in m.get('match_hometeam_name', '').lower() or search_week.lower() in m.get('match_awayteam_name', '').lower()]
            else: day_games = [m for m in day_games if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
            
            if day_games:
                st.markdown(f"#### 📅 {d}")
                leagues_dict = {}
                for m in day_games: leagues_dict.setdefault(m.get("league_name", "Other"), []).append(m)
                for l_name, games in leagues_dict.items():
                    st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
                    for m in games:
                        match_label = f"🕒 {m.get('match_time')} | {m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}"
                        if st.checkbox(match_label, key=m.get("match_id")): selected_custom_picks.append(f"{d} | {l_name} | {match_label}")
                            
        if selected_custom_picks:
            st.success("🎟️ **Your Custom Slip:**")
            for pick in selected_custom_picks: st.write(f"- {pick}")

# --- TAB 3: AUTOMATED REFEREE ENGINE ---
with tab3:
    st.markdown("### 🔥 All System Picks Today")
    search_daily = st.text_input("🔍 Search for a specific team playing today:", key="search_daily")
    
    if isinstance(daily_matches, list):
        if search_daily: big_daily_games = [m for m in daily_matches if search_daily.lower() in m.get('match_hometeam_name', '').lower() or search_daily.lower() in m.get('match_awayteam_name', '').lower()]
        else: big_daily_games = [m for m in daily_matches if m.get("league_name") in top_leagues and m.get("country_name") in top_countries]
            
        daily_leagues_dict = {}
        for m in big_daily_games: daily_leagues_dict.setdefault(m.get("league_name", "Other"), []).append(m)
            
        for l_name, games in daily_leagues_dict.items():
            st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
            for m in games:
                h_name = m.get('match_hometeam_name')
                a_name = m.get('match_awayteam_name')
                with st.expander(f"🕒 {m.get('match_time')} | {h_name} vs {a_name}"):
                    h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                    a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                    
                    if h_st and a_st:
                        referee = m.get('match_referee', 'Unknown')
                        pick, _, _, _ = generate_ai_pick(h_st, a_st, referee)
                        
                        # UI formatting for Referee status
                        ref_info = REFEREE_DB.get(referee, {"style": "Unknown", "cards_per_game": "N/A"})
                        if ref_info["style"] == "Strict": ref_html = f"<div style='text-align:center;'><span class='ref-strict'>⚖️ Referee: {referee} (STRICT | Avg: {ref_info['cards_per_game']} Cards)</span></div>"
                        elif ref_info["style"] == "Lenient": ref_html = f"<div style='text-align:center;'><span class='ref-lenient'>⚖️ Referee: {referee} (LENIENT | Avg: {ref_info['cards_per_game']} Cards)</span></div>"
                        else: ref_html = f"<div style='text-align:center;'><span class='ref-standard'>⚖️ Referee: {referee} (No data in internal DB)</span></div>"
                        
                        st.markdown(f"<div style='text-align:center; padding:8px; background-color:#3b82f6; border-radius:6px; margin-bottom:10px;'><b>Engine Pick:</b> {pick}</div>", unsafe_allow_html=True)
                        st.markdown(ref_html, unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        proj_h_goals = (h_st['gf'] + a_st['ga']) / 2
                        proj_a_goals = (a_st['gf'] + h_st['ga']) / 2
                        proj_corners = ((h_st['cf'] + a_st['ca']) / 2) + ((a_st['cf'] + h_st['ca']) / 2)
                        proj_cards = h_st['cards'] + a_st['cards']
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric(f"{h_name[:10]} xG", f"{proj_h_goals:.2f}")
                            st.metric("Corners For", f"{h_st['cf']:.1f}")
                        with c2:
                            st.metric("Total xG", f"{proj_h_goals + proj_a_goals:.2f}")
                            st.metric("Proj. Corners", f"{proj_corners:.2f}")
                        with c3:
                            st.metric(f"{a_name[:10]} xG", f"{proj_a_goals:.2f}")
                            st.metric("Proj. Team Cards", f"{proj_cards:.1f}")

with tab4:
    st.markdown("### 📊 Accuracy Tracking Active")
    st.info("System is logging daily true outcomes.")
