import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. UI CONFIG ---
st.set_page_config(page_title="Quant Universal Terminal", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, p, span, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    input { border: 2px solid #2563eb !important; border-radius: 8px !important; color: #0f172a !important; }
    div[data-testid="stMetric"] { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .stButton>button { background-color: #dc2626 !important; color: white !important; width: 100%; height: 55px; font-weight: 800; border-radius: 10px; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Institutional Universal Terminal")
st.markdown("### Total Market Analysis: Goals, Corners, Cards & Volume")

# --- 2. SETTINGS ---
API_KEY = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
today_dt = datetime.utcnow() + timedelta(hours=1) 
today_str = today_dt.strftime('%Y-%m-%d')
past_str = (today_dt - timedelta(days=30)).strftime('%Y-%m-%d')

ELITE_LEAGUES = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Champions League", "Europa League"]

def safe_num(v):
    if v is None: return 0.0
    try:
        cleaned = str(v).replace("%", "").strip()
        return float(cleaned) if (cleaned and not any(c.isalpha() for c in cleaned)) else 0.0
    except: return 0.0

def fetch_universal_stats(team_id):
    url = f"https://apiv3.apifootball.com/?action=get_events&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}"
    try:
        res = requests.get(url).json()
        s = {"goals":0, "corners":0, "sot":0, "cards":0, "conceded":0, "shots":0, "goalkicks":0, "cnt":0}
        if isinstance(res, list):
            recent = [m for m in res if m.get("match_status") == "Finished"][-5:]
            for m in recent:
                is_h = m.get("match_hometeam_id") == team_id
                s["goals"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
                s["conceded"] += safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
                for row in m.get("statistics", []):
                    val = safe_num(row.get("home" if is_h else "away"))
                    stype = row.get("type")
                    if stype == "Corners": s["corners"] += val
                    if stype == "Shots On Goal": s["sot"] += val
                    if stype == "Yellow Cards": s["cards"] += val
                    if stype == "Shots Total": s["shots"] += val
                    if stype == "Goal Kicks": s["goalkicks"] += val
                s["cnt"] += 1
        return {k: (v/s["cnt"] if s["cnt"] > 0 else 0) for k, v in s.items()}, s["cnt"]
    except: return None, 0

# --- 3. UI SEARCH & ENGINE ---
search_query = st.text_input("🔍 Search Teams:", placeholder="Type team name...")

if st.button("⚡ RUN FULL MARKET SWEEP"):
    fixtures_url = f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}"
    resp = requests.get(fixtures_url).json()
    
    if isinstance(resp, list):
        upcoming = [m for m in resp if m.get("match_status") == ""]
        if search_query:
            terms = [t.strip().lower() for t in search_query.split(",") if t.strip()]
            final_list = [m for m in upcoming if any(term in str(m.get("match_hometeam_name","")).lower() or term in str(m.get("match_awayteam_name","")).lower() for term in terms)]
        else:
            final_list = [m for m in upcoming if any(lg in m.get("league_name", "") for lg in ELITE_LEAGUES)][:20]

        for i, m in enumerate(final_list):
            h_n, a_n = m.get("match_hometeam_name"), m.get("match_awayteam_name")
            h_st, h_c = fetch_universal_stats(m.get("match_hometeam_id"))
            a_st, a_c = fetch_universal_stats(m.get("match_awayteam_id"))
            
            if h_st and a_st:
                with st.expander(f"⭐ {m.get('match_time')} | {h_n} vs {a_n}"):
                    c1, c2, c3 = st.columns([2, 1, 2])
                    with c1:
                        st.subheader(h_n)
                        st.metric("Avg Corners", f"{h_st['corners']:.1f}")
                        st.metric("Avg Goal Kicks", f"{h_st['goalkicks']:.1f}")
                    with c2: st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)
                    with c3:
                        st.subheader(a_n)
                        st.metric("Avg Corners", f"{a_st['corners']:.1f}")
                        st.metric("Avg Goal Kicks", f"{a_st['goalkicks']:.1f}")

                    st.markdown("### 🧬 AI Market Projections")
                    m1, m2, m3 = st.columns(3)
                    
                    with m1:
                        # --- THE CORNER ENGINE ---
                        total_corners = h_st['corners'] + a_st['corners']
                        if total_corners > 10.5: st.success(f"🚩 **OVER 9.5 CORNERS** ({total_corners:.1f})")
                        elif total_corners < 7.5: st.warning(f"🚩 **UNDER 8.5 CORNERS** ({total_corners:.1f})")
                        else: st.write(f"Corner Avg: {total_corners:.1f}")

                    with m2:
                        # --- GOALS & BTTS ---
                        total_goals = h_st['goals'] + a_st['goals']
                        if h_st['goals'] >= 1.0 and a_st['goals'] >= 1.0: st.success("⚽ **BTTS: YES**")
                        elif total_goals < 2.0: st.warning("🧱 **UNDER 2.5 GOALS**")
                        
                        if (total_goals > 2.2) or (h_st['goals'] >= 0.9 and a_st['goals'] >= 0.9):
                            st.success("🔥 **BTTS OR OVER 2.5**")

                    with m3:
                        # --- CARDS & VOLUME ---
                        total_cards = h_st['cards'] + a_st['cards']
                        if total_cards < 3.0: st.success("🕊️ **UNDER 3.5 CARDS**")
                        elif total_cards > 4.5: st.error("🟨 **OVER 3.5 CARDS**")
                        
                        total_gk = h_st['goalkicks'] + a_st['goalkicks']
                        if total_gk > 15: st.error(f"🧤 **HIGH GOAL KICKS** ({total_gk:.1f})")
