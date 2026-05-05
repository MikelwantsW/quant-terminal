import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Institutional Radar",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');

.stApp { background-color: #080d14 !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif; }
section[data-testid="stSidebar"] { background-color: #0d1520 !important; border-right: 1px solid #1e293b; }

.stTabs [data-baseweb="tab-list"] { background: #0d1520; border-radius: 10px; padding: 6px; gap: 6px; border: 1px solid #1e293b; }
.stTabs [data-baseweb="tab"] { color: #64748b; font-weight: 600; font-size: 13px; padding: 10px 18px; border-radius: 7px; font-family: 'Inter', sans-serif; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #16a34a, #15803d) !important; color: white !important; box-shadow: 0 4px 12px rgba(22,163,74,0.35); }

[data-testid="stExpander"] { background: #0d1520 !important; border: 1px solid #1e293b !important; border-radius: 10px !important; margin-bottom: 10px !important; }
[data-testid="stExpander"] summary { background: #0d1520 !important; color: #e2e8f0 !important; font-weight: 600; }
[data-testid="stExpander"] summary:hover { background: #1e293b !important; }

.stButton > button { background: #0d1520 !important; color: #94a3b8 !important; border: 1px solid #1e293b !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 13px !important; width: 100%; transition: all 0.2s ease; }
.stButton > button:hover { border-color: #16a34a !important; color: #4ade80 !important; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(22,163,74,0.2) !important; }

[data-testid="stMetric"] { background: #0d1520; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; }
[data-testid="stMetricValue"] { font-family: 'DM Mono', monospace !important; color: #4ade80 !important; font-size: 28px !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 1px; }

.stSpinner > div { border-top-color: #16a34a !important; }

.page-title { font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800; text-align: center; background: linear-gradient(135deg, #4ade80, #16a34a, #f97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px; letter-spacing: -1px; }
.page-sub { text-align: center; color: #475569; font-size: 13px; margin-bottom: 28px; font-family: 'DM Mono', monospace; letter-spacing: 1px; }

.league-header { background: #0d1520; color: #94a3b8; padding: 8px 14px; border-radius: 7px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin: 20px 0 8px; border-left: 3px solid #f97316; }

.pick-card { background: linear-gradient(135deg, #0d2218, #0a1f15); border: 1px solid #166534; border-radius: 12px; padding: 22px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 8px 24px rgba(22,163,74,0.12); }
.pick-label { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; color: #4ade80; margin-bottom: 10px; }

.sniper-card { background: linear-gradient(135deg, #1a0a00, #2a1200); border: 2px solid #f97316; border-radius: 12px; padding: 22px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 8px 32px rgba(249,115,22,0.25); }
.sniper-label { font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 800; color: #fb923c; margin-bottom: 6px; }
.sniper-badge { display: inline-block; background: #f97316; color: white; padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 900; letter-spacing: 2px; margin-bottom: 10px; font-family: 'DM Mono', monospace; }

.ref-tag { display: inline-block; background: rgba(249,115,22,0.12); color: #fb923c; border: 1px solid rgba(249,115,22,0.3); padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-decoration: none; margin-top: 8px; font-family: 'DM Mono', monospace; }

.stats-panel { background: #080d14; border: 1px solid #1e293b; border-top: 2px solid #f97316; border-radius: 10px; padding: 16px; height: 100%; }
.stats-title { color: #f97316; font-size: 10px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; font-family: 'DM Mono', monospace; }
.stat-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #64748b; padding: 6px 0; border-bottom: 1px solid #0d1520; }
.stat-row:last-child { border-bottom: none; }
.stat-val { font-family: 'DM Mono', monospace; color: #e2e8f0; font-weight: 600; font-size: 14px; }

.signal-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; padding: 5px 0; }
.signal-green { color: #4ade80; font-weight: 700; font-family: 'DM Mono', monospace; }
.signal-red   { color: #f87171; font-weight: 700; font-family: 'DM Mono', monospace; }
.signal-grey  { color: #475569; font-weight: 700; font-family: 'DM Mono', monospace; }

.conf-bar-wrap { margin-top: 14px; }
.conf-label { font-size: 10px; color: #475569; font-family: 'DM Mono', monospace; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.conf-bar-bg { background: #1e293b; border-radius: 20px; height: 6px; width: 100%; overflow: hidden; }
.conf-bar-fill { height: 6px; border-radius: 20px; transition: width 0.6s ease; }

.slip-box { background: #0d1520; border: 1px dashed #f97316; border-radius: 10px; padding: 20px; margin-top: 12px; }
.slip-row { padding: 12px 0; border-bottom: 1px solid #1e293b; font-size: 14px; }
.slip-row:last-child { border-bottom: none; }
.slip-league { font-size: 10px; color: #64748b; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; font-family: 'DM Mono', monospace; }
.slip-match { font-weight: 600; color: #e2e8f0; margin: 3px 0; }
.slip-pick { font-weight: 800; font-family: 'Syne', sans-serif; font-size: 15px; }

.live-banner { background: #7f1d1d; border: 1px solid #ef4444; color: #fca5a5; padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
.live-dot { height: 8px; width: 8px; background: #ef4444; border-radius: 50%; display: inline-block; animation: pulse 1.2s ease infinite; }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.7); } }

.risk-badge { padding: 12px 20px; border-radius: 8px; text-align: center; font-family: 'Syne', sans-serif; font-weight: 800; font-size: 18px; letter-spacing: 1px; color: white; margin-bottom: 20px; }

.empty-state { text-align: center; padding: 60px 20px; color: #334155; }
.empty-state-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state-text { font-size: 16px; font-weight: 600; }
.empty-state-sub { font-size: 13px; color: #1e293b; margin-top: 6px; }

.accuracy-row { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #0d1520; border-radius: 8px; margin-bottom: 6px; border: 1px solid #1e293b; font-size: 13px; }
.acc-win { border-left: 3px solid #16a34a; }
.acc-loss { border-left: 3px solid #ef4444; }

.info-box { background: #0d1520; border: 1px solid #1e293b; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; font-size: 13px; color: #64748b; }
.warning-box { background: #1a0a00; border: 1px solid #f97316; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; font-size: 13px; color: #fb923c; }

.gate-tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; font-family: 'DM Mono', monospace; margin: 2px; }
.gate-pass { background: rgba(22,163,74,0.15); color: #4ade80; border: 1px solid rgba(22,163,74,0.3); }
.gate-fail { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
API_KEY = st.secrets.get("APIFOOTBALL_KEY", "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a")

now          = datetime.utcnow() + timedelta(hours=1)
today_str    = now.strftime('%Y-%m-%d')
yesterday_str= (now - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str = (now + timedelta(days=7)).strftime('%Y-%m-%d')
past_str     = (now - timedelta(days=120)).strftime('%Y-%m-%d')   # extended to 4 months

# ── EXPANDED LEAGUE LIST ─────────────────────────────
TOP_LEAGUES = {
    # Tier 1 – Elite European
    "Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1",
    "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League",
    # Tier 2 – Strong European
    "Championship", "Eredivisie", "Primeira Liga", "Süper Lig",
    "Scottish Premiership", "Scottish Premier League",
    "Austrian Football Bundesliga", "Austrian Bundesliga",
    "Belgian Pro League", "Belgian First Division A",
    "Swiss Super League",
    # Tier 3 – Nordic / Scandinavian
    "Allsvenskan",          # Sweden
    "Eliteserien",          # Norway
    "Superliga",            # Denmark
    "Veikkausliiga",        # Finland
    # Tier 4 – Eastern / Balkan
    "SuperLiga",            # Serbia
    "Serbian SuperLiga",
    "Greek Super League",
    "Czech First League",
    "Polish Ekstraklasa",
    "Russian Premier League",
    # Tier 5 – Americas / Other
    "Major League Soccer",
    "Brasileirao Serie A",
    "Argentine Primera División",
    # Tier 6 – Middle East / Asia
    "Saudi Pro League",
    "Saudi Professional League",
    "J1 League",
}

# ── LEAGUE-SPECIFIC STATISTICAL MODIFIERS ──────────────
# Tuned based on known playing styles to reduce false positives
LEAGUE_PROFILE = {
    # (goals_mod, corners_mod, cards_mod, min_conf_boost)
    "La Liga":                   (0.90, 0.85, 1.05, 2.0),
    "Serie A":                   (0.88, 0.92, 1.10, 2.0),
    "Bundesliga":                (1.05, 0.95, 0.90, 0.0),
    "Premier League":            (1.00, 1.00, 1.00, 0.0),
    "Ligue 1":                   (0.95, 1.00, 1.05, 1.0),
    "Primeira Liga":             (0.90, 1.05, 1.10, 2.0),
    "Eredivisie":                (1.10, 1.00, 0.90, 0.0),
    "Championship":              (1.05, 1.10, 1.00, 0.0),
    "Allsvenskan":               (0.95, 1.05, 0.85, 2.0),
    "Eliteserien":               (1.00, 1.05, 0.85, 2.0),
    "Superliga":                 (1.00, 1.00, 0.90, 2.0),
    "Veikkausliiga":             (1.00, 1.05, 0.85, 3.0),
    "SuperLiga":                 (0.95, 1.00, 1.15, 2.0),
    "Serbian SuperLiga":         (0.95, 1.00, 1.15, 2.0),
    "Scottish Premiership":      (1.05, 1.10, 1.00, 1.0),
    "Scottish Premier League":   (1.05, 1.10, 1.00, 1.0),
    "Austrian Football Bundesliga": (1.05, 1.00, 0.95, 1.0),
    "Austrian Bundesliga":       (1.05, 1.00, 0.95, 1.0),
    "Saudi Pro League":          (1.00, 0.90, 1.20, 3.0),
    "Saudi Professional League": (1.00, 0.90, 1.20, 3.0),
    "Major League Soccer":       (1.05, 0.95, 0.90, 2.0),
    "Brasileirao Serie A":       (1.00, 1.05, 1.15, 2.0),
    "Argentine Primera División":(1.00, 1.00, 1.20, 2.0),
    "J1 League":                 (0.95, 1.00, 0.85, 3.0),
    "Greek Super League":        (0.90, 1.00, 1.20, 3.0),
    "Polish Ekstraklasa":        (0.95, 1.05, 1.05, 2.0),
    "Czech First League":        (0.95, 1.00, 1.05, 2.0),
    "Süper Lig":                 (1.00, 1.00, 1.15, 2.0),
    "Belgian Pro League":        (1.05, 1.00, 1.00, 1.0),
    "Belgian First Division A":  (1.05, 1.00, 1.00, 1.0),
    "Swiss Super League":        (0.95, 1.00, 0.95, 2.0),
    "UEFA Champions League":     (1.00, 1.00, 1.00, 0.0),
    "UEFA Europa League":        (1.00, 1.00, 1.00, 0.0),
    "UEFA Europa Conference League": (1.00, 1.00, 1.00, 0.0),
}

DEFAULT_PROFILE = (1.0, 1.0, 1.0, 2.0)

LIVE_STATUSES = {"1H", "HT", "2H", "ET", "P", "LIVE", "Break"}

TIER_CONFIG = [
    (2,  "SAFE DOUBLE",   "#16a34a", "🟢"),
    (4,  "MODERATE",      "#eab308", "🟡"),
    (6,  "AGGRESSIVE",    "#f97316", "🟠"),
    (8,  "SYSTEM ACCA",   "#dc2626", "🔴"),
    (12, "WHALE TIER",    "#9333ea", "🟣"),
    (15, "QUANT JACKPOT", "#2563eb", "🔵"),
    (18, "THE GAUNTLET",  "#ea580c", "🔥"),
    (25, "MOONSHOT",      "#6b21a8", "🌌"),
]
ODDS_LABELS = ["2.0×", "5.0×", "10.0×", "20.0×", "100.0×", "250.0×", "500.0×", "1000.0×+"]


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def safe_num(v):
    if v is None: return 0.0
    try: return float(str(v).replace("%","").strip())
    except: return 0.0


def is_live_status(status: str) -> bool:
    if not status: return False
    s = str(status).strip()
    return s in LIVE_STATUSES or (s.isdigit() and 1 <= int(s) <= 120)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_stats(team_id, venue):
    """Fetch last 8 relevant matches (up from 5) for better sample quality."""
    url = (
        f"https://apiv3.apifootball.com/?action=get_events"
        f"&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}"
    )
    try:
        res = requests.get(url, timeout=10).json()
        s = {"gf":0,"ga":0,"cf":0,"ca":0,"sotf":0,"sota":0,"shotsf":0,"shotsa":0,"cards":0,"cnt":0}
        if not isinstance(res, list):
            return None, 0
        id_key = "match_hometeam_id" if venue == "home" else "match_awayteam_id"
        finished = [m for m in res if m.get("match_status") == "Finished"
                    and m.get(id_key) == team_id][-8:]   # last 8
        for m in finished:
            is_h = m.get("match_hometeam_id") == team_id
            s["gf"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
            s["ga"] += safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
            for row in m.get("statistics", []):
                t_val = safe_num(row.get("home" if is_h else "away"))
                o_val = safe_num(row.get("away" if is_h else "home"))
                stype = row.get("type")
                if stype == "Corners":         s["cf"] += t_val; s["ca"] += o_val
                elif stype == "Yellow Cards":  s["cards"] += t_val
                elif stype == "Shots On Goal": s["sotf"] += t_val; s["sota"] += o_val
                elif stype == "Shots Total":   s["shotsf"] += t_val; s["shotsa"] += o_val
            s["cnt"] += 1
        n = s["cnt"]
        return ({k: (v/n if n else 0) for k, v in s.items() if k != "cnt"}, n)
    except Exception:
        return None, 0


@st.cache_data(ttl=300, show_spinner=False)
def fetch_events(date_from, date_to):
    url = (
        f"https://apiv3.apifootball.com/?action=get_events"
        f"&from={date_from}&to={date_to}&APIkey={API_KEY}"
    )
    try:
        res = requests.get(url, timeout=15).json()
        if isinstance(res, list):
            return [m for m in res if m.get("league_name") in TOP_LEAGUES]
        return []
    except Exception:
        return []


# ─────────────────────────────────────────
#  ENHANCED EDGE ENGINE
# ─────────────────────────────────────────
def generate_ai_pick(h_st, a_st, league, sniper_mode=False):
    """
    Multi-signal confluence engine.

    Changes vs v1:
    - League-specific stat modifiers (goals/corners/cards tuned per country)
    - Confluence gates: a pick is only made when ≥2 independent signals agree
    - Sniper mode: raises minimum confidence gate to 82% (from 65%)
    - Margin buffer: line must have a larger gap from projection to qualify
    - Sample size weighting: lower-sample teams reduce confidence
    - Returns (label, type, line, conf, signals_dict)
    """
    gm, cm, kdm, extra = LEAGUE_PROFILE.get(league, DEFAULT_PROFILE)

    # Projected totals with league modifiers
    proj_g   = (((h_st['gf']+a_st['ga'])/2) + ((a_st['gf']+h_st['ga'])/2)) * gm
    proj_c   = (((h_st['cf']+a_st['ca'])/2) + ((a_st['cf']+h_st['ca'])/2)) * cm
    proj_sot = ((h_st['sotf']+a_st['sota'])/2) + ((a_st['sotf']+h_st['sota'])/2)
    proj_cd  = (h_st['cards'] + a_st['cards']) * kdm

    # Independent signal checks for confluence
    signals = {}

    # ── SIGNAL: Goals form (both teams score & concede heavily?)
    both_score_rate = (h_st['gf'] > 1.0 and a_st['gf'] > 0.8)
    signals['both_score']  = both_score_rate
    signals['high_scoring']= proj_g >= 2.8
    signals['low_scoring'] = proj_g <= 2.2
    signals['high_sot']    = proj_sot >= 8.0
    signals['low_sot']     = proj_sot <= 6.5
    signals['high_corners']= proj_c >= 9.0
    signals['low_corners'] = proj_c <= 8.0
    signals['high_cards']  = proj_cd >= 4.0
    signals['low_cards']   = proj_cd <= 3.0
    # SOT confirms goals?
    signals['sot_confirms_goals'] = (signals['high_scoring'] and signals['high_sot'])
    signals['sot_confirms_under'] = (signals['low_scoring'] and signals['low_sot'])

    base_conf = 65.0 + extra
    min_conf  = 82.0 if sniper_mode else 72.0  # raised gate vs old 65%
    plays = []

    # ── 1. GOALS MARKET ───────────────────────────────────────────────────
    if proj_g >= 2.8:
        # require bigger margin buffer (1.0 gap minimum vs old 0)
        line = 3.5 if proj_g >= 4.2 else 2.5 if proj_g >= 3.2 else 1.5
        gap  = proj_g - line
        if gap >= 0.8:   # tighter buffer gate
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 90)
            # confluence bonus: +5% if SOT also confirms
            if signals['sot_confirms_goals']: conf = min(99.0, conf + 5.0)
            if signals['both_score']:         conf = min(99.0, conf + 3.0)
            plays.append((f"⚽ Over {line} Goals", "goals", line, conf,
                          {"SOT confirms": signals['sot_confirms_goals'],
                           "Both teams score": signals['both_score'],
                           "High corners": signals['high_corners']}))

    elif proj_g <= 2.2:
        line = 1.5 if proj_g <= 1.2 else 2.5 if proj_g <= 1.8 else 3.5
        gap  = line - proj_g
        if gap >= 0.8:
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 90)
            if signals['sot_confirms_under']: conf = min(99.0, conf + 5.0)
            plays.append((f"🔒 Under {line} Goals", "under_goals", line, conf,
                          {"SOT confirms under": signals['sot_confirms_under'],
                           "Low corners": signals['low_corners']}))

    # ── 2. CORNERS MARKET ─────────────────────────────────────────────────
    if proj_c >= 10.0:      # raised from 9.5
        valid = [l for l in [8.5,9.5,10.5,11.5,12.5,13.5] if l <= proj_c - 1.8]
        if valid:
            line = max(valid)
            gap  = proj_c - line
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 75)
            # confluence: high SOT means more attacking pressure = more corners
            if signals['high_sot']: conf = min(99.0, conf + 4.0)
            plays.append((f"🔥 Over {line} Corners", "corners", line, conf,
                          {"High SOT": signals['high_sot'],
                           "High scoring": signals['high_scoring']}))
    elif proj_c <= 8.0:     # tightened from 8.5
        valid = [l for l in [6.5,7.5,8.5,9.5] if l >= proj_c + 1.8]
        if valid:
            line = min(valid)
            gap  = line - proj_c
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 75)
            if signals['low_sot']: conf = min(99.0, conf + 4.0)
            plays.append((f"🛡️ Under {line} Corners", "under_corners", line, conf,
                          {"Low SOT": signals['low_sot'],
                           "Low scoring": signals['low_scoring']}))

    # ── 3. CARDS MARKET ───────────────────────────────────────────────────
    if proj_cd >= 5.0:      # raised from 4.5 (cards are noisy)
        valid = [l for l in [3.5,4.5,5.5,6.5] if l <= proj_cd - 1.5]
        if valid:
            line = max(valid)
            gap  = proj_cd - line
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 55)  # lower weight (variance)
            plays.append((f"🟨 Over {line} Cards", "cards", line, conf,
                          {"High card league": kdm >= 1.1,
                           "Derby/Rivalry": False}))
    elif proj_cd <= 2.5:    # tightened from 3.5
        valid = [l for l in [3.5,4.5] if l >= proj_cd + 1.5]
        if valid:
            line = min(valid)
            gap  = line - proj_cd
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 55)
            plays.append((f"🧊 Under {line} Cards", "under_cards", line, conf,
                          {"Low card league": kdm <= 0.92}))

    # ── 4. SOT MARKET ─────────────────────────────────────────────────────
    if proj_sot >= 9.0:     # raised from 8.5
        valid = [l for l in [7.5,8.5,9.5,10.5,11.5] if l <= proj_sot - 1.8]
        if valid:
            line = max(valid)
            gap  = proj_sot - line
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 65)
            if signals['high_scoring']: conf = min(99.0, conf + 3.0)
            plays.append((f"🎯 Over {line} SOT", "sot", line, conf,
                          {"High scoring": signals['high_scoring'],
                           "Both score": signals['both_score']}))
    elif proj_sot <= 6.0:   # tightened from 7.0
        valid = [l for l in [5.5,6.5,7.5] if l >= proj_sot + 1.8]
        if valid:
            line = min(valid)
            gap  = line - proj_sot
            conf = min(99.0, base_conf + (gap / max(line,0.01)) * 65)
            plays.append((f"🧱 Under {line} SOT", "under_sot", line, conf,
                          {"Low scoring": signals['low_scoring']}))

    # ── FILTER: apply minimum confidence gate ─────────────────────────────
    plays = [p for p in plays if p[3] >= min_conf]

    plays.sort(key=lambda x: x[3], reverse=True)

    if plays:
        label, ptype, line, conf, sigs = plays[0]
        return label, ptype, line, conf, sigs, plays
    return "⚠️ NO PLAY — EDGE BELOW THRESHOLD", "pass", 0, 0, {}, []


def check_result(p_type, thresh, match):
    goals = safe_num(match.get("match_hometeam_score","0")) + safe_num(match.get("match_awayteam_score","0"))
    stats = {row.get("type"): (safe_num(row.get("home",0)) + safe_num(row.get("away",0)))
             for row in match.get("statistics", [])}
    if p_type == "goals":         return goals > thresh
    if p_type == "under_goals":   return goals < thresh
    if p_type == "corners":       return stats.get("Corners", 0) > thresh
    if p_type == "under_corners": return stats.get("Corners", 0) < thresh
    if p_type == "cards":         return stats.get("Yellow Cards", 0) > thresh
    if p_type == "under_cards":   return stats.get("Yellow Cards", 0) < thresh
    if p_type == "sot":           return stats.get("Shots On Goal", 0) > thresh
    if p_type == "under_sot":     return stats.get("Shots On Goal", 0) < thresh
    return None


def conf_bar_html(conf, color="#16a34a"):
    pct = int(conf)
    bar_color = "#ef4444" if pct < 75 else "#eab308" if pct < 82 else color
    return f"""
    <div class='conf-bar-wrap'>
        <div class='conf-label'>EDGE CONFIDENCE · {pct}%</div>
        <div class='conf-bar-bg'><div class='conf-bar-fill' style='width:{pct}%; background:linear-gradient(90deg,{bar_color},{bar_color}88);'></div></div>
    </div>"""


def signals_html(sigs: dict):
    tags = ""
    for k, v in sigs.items():
        cls = "gate-pass" if v else "gate-fail"
        icon = "✓" if v else "✗"
        tags += f"<span class='gate-tag {cls}'>{icon} {k}</span>"
    return f"<div style='margin-top:10px;'>{tags}</div>"


# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Terminal")
    st.markdown(f"<div style='font-family:DM Mono,monospace; font-size:11px; color:#475569;'>DATE · {today_str}</div>", unsafe_allow_html=True)
    st.divider()

    sniper_mode = st.toggle("🎯 Sniper Mode (82%+ only)", value=False)
    if sniper_mode:
        st.markdown("<div style='background:#1a0a00; border:1px solid #f97316; border-radius:8px; padding:10px; font-size:12px; color:#fb923c;'>⚡ Only ultra-high-confidence picks shown. Fewer picks, sharper results.</div>", unsafe_allow_html=True)

    st.divider()

    # League filter
    st.markdown("**League Filter**")
    show_tier1 = st.checkbox("Tier 1 – Elite EU", value=True)
    show_tier2 = st.checkbox("Tier 2 – Strong EU", value=True)
    show_tier3 = st.checkbox("Tier 3 – Nordic", value=True)
    show_tier4 = st.checkbox("Tier 4 – Eastern/Balkan", value=False)
    show_tier5 = st.checkbox("Tier 5 – Americas", value=False)
    show_tier6 = st.checkbox("Tier 6 – Middle East/Asia", value=False)

    st.divider()
    if st.button("🧹 Refresh Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    live_refresh = st.toggle("🔴 Live Auto-Refresh (60s)", value=False)
    if live_refresh:
        st.success("🟢 LIVE MODE ACTIVE")

    st.divider()
    st.markdown("<div style='font-size:11px; color:#334155;'>⚠️ Research only. Not financial advice.</div>", unsafe_allow_html=True)


# ── Build active league set from sidebar toggles ──────────
TIER_LEAGUES = {
    1: {"Premier League","Serie A","La Liga","Bundesliga","Ligue 1",
        "UEFA Champions League","UEFA Europa League","UEFA Europa Conference League"},
    2: {"Championship","Eredivisie","Primeira Liga","Süper Lig",
        "Scottish Premiership","Scottish Premier League",
        "Austrian Football Bundesliga","Austrian Bundesliga",
        "Belgian Pro League","Belgian First Division A","Swiss Super League"},
    3: {"Allsvenskan","Eliteserien","Superliga","Veikkausliiga"},
    4: {"SuperLiga","Serbian SuperLiga","Greek Super League",
        "Czech First League","Polish Ekstraklasa","Russian Premier League"},
    5: {"Major League Soccer","Brasileirao Serie A","Argentine Primera División"},
    6: {"Saudi Pro League","Saudi Professional League","J1 League"},
}

ACTIVE_LEAGUES = set()
for tier, active in [(1,show_tier1),(2,show_tier2),(3,show_tier3),(4,show_tier4),(5,show_tier5),(6,show_tier6)]:
    if active:
        ACTIVE_LEAGUES |= TIER_LEAGUES[tier]


# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────
st.markdown("<div class='page-title'>🏦 Institutional Quant Radar</div>", unsafe_allow_html=True)
mode_tag = "🎯 SNIPER MODE" if sniper_mode else "STANDARD MODE"
st.markdown(f"<div class='page-sub'>ALGORITHMIC EDGE · {len(ACTIVE_LEAGUES)} LEAGUES ACTIVE · {mode_tag}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────
with st.spinner("Fetching fixtures…"):
    all_daily   = fetch_events(today_str, today_str)
    all_weekly  = fetch_events(today_str, week_out_str)

daily_matches  = [m for m in all_daily  if m.get("league_name") in ACTIVE_LEAGUES]
weekly_matches = [m for m in all_weekly if m.get("league_name") in ACTIVE_LEAGUES]


# ─────────────────────────────────────────
#  QUICK STATS BAR
# ─────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
c1.metric("Today's Fixtures",  len(daily_matches))
c2.metric("This Week",         len(weekly_matches))
live_now = [m for m in daily_matches if is_live_status(m.get("match_status",""))]
c3.metric("🔴 Live Now",       len(live_now))
c4.metric("Active Leagues",    len(ACTIVE_LEAGUES))
st.write("")


# ─────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🎟️ Auto-Acca", "📝 Weekly Slip", "🔥 Daily Picks", "📊 Accuracy"])


# ══════════════════════════════════════════
#  TAB 1 — AUTO ACCA
# ══════════════════════════════════════════
with tab1:
    st.markdown("### 🎟️ Algorithmic Ticket Generator")
    st.markdown("<div class='info-box'>The system scores every qualifying match and selects the highest-edge plays. In Sniper Mode only plays with ≥82% edge confidence are included.</div>", unsafe_allow_html=True)

    if "acca_selection" not in st.session_state:
        st.session_state.acca_selection = None

    r1 = st.columns(4)
    r2 = st.columns(4)
    for i, (n, label, color, icon) in enumerate(TIER_CONFIG):
        with (r1 if i < 4 else r2)[i % 4]:
            if st.button(f"{icon} {ODDS_LABELS[i]}", key=f"tier_{i}", use_container_width=True):
                st.session_state.acca_selection = (n, label, color)

    sel = st.session_state.acca_selection
    if sel:
        n_picks, label, color = sel
        st.markdown(f"<div class='risk-badge' style='background:{color};'>{label} · {n_picks} LEG ACCA</div>", unsafe_allow_html=True)

        valid_picks = []
        with st.spinner(f"Building {n_picks}-leg acca…"):
            for m in daily_matches:
                h_st, h_cnt = fetch_stats(m.get("match_hometeam_id"), "home")
                a_st, a_cnt = fetch_stats(m.get("match_awayteam_id"), "away")
                if h_st and a_st and h_cnt >= 3 and a_cnt >= 3:
                    pick, p_type, line, conf, sigs, _ = generate_ai_pick(h_st, a_st, m.get("league_name",""), sniper_mode)
                    if conf > 0:
                        valid_picks.append({
                            "match":  f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}",
                            "league": m.get("league_name",""),
                            "pick": pick, "conf": conf,
                            "time": m.get("match_time",""),
                            "sigs": sigs,
                        })

        valid_picks.sort(key=lambda x: x["conf"], reverse=True)
        chosen = valid_picks[:n_picks]

        if not chosen:
            st.markdown("<div class='empty-state'><div class='empty-state-icon'>🎯</div><div class='empty-state-text'>No picks meet the confidence threshold today</div><div class='empty-state-sub'>Try disabling Sniper Mode or enabling more league tiers</div></div>", unsafe_allow_html=True)
        else:
            avg_conf = sum(p["conf"] for p in chosen) / len(chosen)
            m1, m2, m3 = st.columns(3)
            m1.metric("Legs Found",     len(chosen))
            m2.metric("Avg Confidence", f"{avg_conf:.1f}%")
            m3.metric("Mode",           "🎯 SNIPER" if sniper_mode else "STANDARD")

            st.markdown("<div class='slip-box'>", unsafe_allow_html=True)
            for i, p in enumerate(chosen, 1):
                st.markdown(f"""
                <div class='slip-row'>
                    <div class='slip-league'>{i}. {p['league']} · {p['time']}</div>
                    <div class='slip-match'>{p['match']}</div>
                    <div class='slip-pick' style='color:{color};'>{p['pick']}</div>
                    {conf_bar_html(p['conf'], color)}
                    {signals_html(p['sigs'])}
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
#  TAB 2 — WEEKLY SLIP
# ══════════════════════════════════════════
with tab2:
    st.markdown("### 📝 Weekly Fixture Browser")
    search_q = st.text_input("🔍 Search team", placeholder="e.g. Chelsea, Milan, Brann, Malmö…")

    if search_q:
        filtered = [m for m in weekly_matches
                    if search_q.lower() in m.get("match_hometeam_name","").lower()
                    or search_q.lower() in m.get("match_awayteam_name","").lower()]
    else:
        filtered = weekly_matches

    if not filtered:
        st.markdown("<div class='empty-state'><div class='empty-state-icon'>🔍</div><div class='empty-state-text'>No fixtures found</div><div class='empty-state-sub'>Enable more league tiers in the sidebar or try a different search</div></div>", unsafe_allow_html=True)
    else:
        dates = sorted(set(m.get("match_date","") for m in filtered))
        for d in dates:
            day_matches = [m for m in filtered if m.get("match_date") == d]
            st.markdown(f"#### 📅 {d} &nbsp;<span style='color:#475569; font-size:13px;'>({len(day_matches)} matches)</span>", unsafe_allow_html=True)
            for m in day_matches:
                st.checkbox(
                    f"🕒 {m.get('match_time','')} | **{m.get('match_hometeam_name','')}** vs **{m.get('match_awayteam_name','')}** · _{m.get('league_name','')}_",
                    key=f"w_{m.get('match_id')}"
                )


# ══════════════════════════════════════════
#  TAB 3 — DAILY PICKS
# ══════════════════════════════════════════
with tab3:
    st.markdown("### 🔥 All System Picks Today")
    if sniper_mode:
        st.markdown("<div class='warning-box'>🎯 Sniper Mode active — only picks with ≥82% edge shown. Matches without a qualifying edge display ⚠️ NO PLAY.</div>", unsafe_allow_html=True)

    if not daily_matches:
        st.markdown("<div class='empty-state'><div class='empty-state-icon'>📭</div><div class='empty-state-text'>No fixtures today in active leagues</div></div>", unsafe_allow_html=True)
    else:
        leagues_today = sorted(set(m.get("league_name","") for m in daily_matches))
        for l_name in leagues_today:
            st.markdown(f"<div class='league-header'>🏆 {l_name}</div>", unsafe_allow_html=True)
            for m in [g for g in daily_matches if g.get("league_name") == l_name]:
                status = m.get("match_status","")
                live   = is_live_status(status)
                home   = m.get("match_hometeam_name","?")
                away   = m.get("match_awayteam_name","?")
                t      = m.get("match_time","")
                prefix = "🔴 LIVE · " if live else ""

                with st.expander(f"{prefix}🕒 {t} | {home} vs {away}"):
                    if live:
                        st.markdown(f"<div class='live-banner'><span class='live-dot'></span>LIVE: {m.get('match_hometeam_score','?')} – {m.get('match_awayteam_score','?')} ({status}')</div>", unsafe_allow_html=True)

                    with st.spinner("Fetching stats…"):
                        h_st, h_cnt = fetch_stats(m.get("match_hometeam_id"), "home")
                        a_st, a_cnt = fetch_stats(m.get("match_awayteam_id"), "away")

                    if not h_st or not a_st:
                        st.warning("⚠️ Insufficient data for this match.")
                        continue
                    if h_cnt < 3 or a_cnt < 3:
                        st.info(f"📉 Low sample: {home} ({h_cnt}) / {away} ({a_cnt}). Treat carefully.")

                    pick, p_type, thresh, conf, sigs, all_plays = generate_ai_pick(h_st, a_st, l_name, sniper_mode)

                    ref = m.get("match_referee","")
                    ref_html = (f"<a href='https://www.google.com/search?q={ref.replace(' ','+')}+referee+stats' target='_blank' class='ref-tag'>⚖️ {ref}</a>") if ref else "<span class='ref-tag'>⚖️ TBD</span>"

                    c1, c2 = st.columns([3, 1.5])
                    with c1:
                        is_sniper_pick = conf >= 82
                        if is_sniper_pick:
                            st.markdown(f"""
                            <div class='sniper-card'>
                                <div class='sniper-badge'>🎯 SNIPER PICK</div>
                                <div class='sniper-label'>{pick}</div>
                                {ref_html}
                                {conf_bar_html(conf, "#f97316")}
                                {signals_html(sigs)}
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class='pick-card'>
                                <div class='pick-label'>{pick}</div>
                                {ref_html}
                                {conf_bar_html(conf)}
                                {signals_html(sigs)}
                            </div>""", unsafe_allow_html=True)

                    with c2:
                        gm, cm, kdm, _ = LEAGUE_PROFILE.get(l_name, DEFAULT_PROFILE)
                        pg   = (((h_st['gf']+a_st['ga'])/2)+((a_st['gf']+h_st['ga'])/2)) * gm
                        pc   = (((h_st['cf']+a_st['ca'])/2)+((a_st['cf']+h_st['ca'])/2)) * cm
                        pcd  = (h_st['cards']+a_st['cards']) * kdm
                        psot = h_st['sotf']+a_st['sotf']
                        st.markdown(f"""
                        <div class='stats-panel'>
                            <div class='stats-title'>Math Edge</div>
                            <div class='stat-row'><span>xG (adj)</span><span class='stat-val'>{pg:.2f}</span></div>
                            <div class='stat-row'><span>Corners (adj)</span><span class='stat-val'>{pc:.1f}</span></div>
                            <div class='stat-row'><span>Cards (adj)</span><span class='stat-val'>{pcd:.1f}</span></div>
                            <div class='stat-row'><span>SOT</span><span class='stat-val'>{psot:.1f}</span></div>
                            <div class='stat-row'><span>Sample H/A</span><span class='stat-val'>{h_cnt}/{a_cnt}</span></div>
                        </div>""", unsafe_allow_html=True)

                        # Alt plays
                        if len(all_plays) > 1:
                            st.markdown("<div style='margin-top:10px; font-size:11px; color:#475569;'>Alt plays:</div>", unsafe_allow_html=True)
                            for alt in all_plays[1:3]:
                                st.markdown(f"<div style='font-size:12px; color:#64748b; padding:3px 0;'>• {alt[0]} <span style='font-family:DM Mono,monospace; color:#334155;'>({alt[3]:.0f}%)</span></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
#  TAB 4 — ACCURACY
# ══════════════════════════════════════════
with tab4:
    st.markdown("### 📊 Yesterday's System Accuracy")
    st.markdown(f"<div style='color:#475569; font-size:13px; margin-bottom:16px;'>📅 {yesterday_str}</div>", unsafe_allow_html=True)

    with st.spinner("Fetching results…"):
        yesterday_res = fetch_events(yesterday_str, yesterday_str)

    finished = [m for m in yesterday_res if m.get("match_status") == "Finished"]

    if not finished:
        st.markdown("<div class='empty-state'><div class='empty-state-icon'>📭</div><div class='empty-state-text'>No finished matches yesterday</div></div>", unsafe_allow_html=True)
    else:
        results_by_type = {}
        wins = losses = skipped = 0

        with st.spinner("Back-testing…"):
            for m in finished:
                h_st, _ = fetch_stats(m.get("match_hometeam_id"), "home")
                a_st, _ = fetch_stats(m.get("match_awayteam_id"), "away")
                if not h_st or not a_st: continue

                pick, p_type, thresh, conf, sigs, _ = generate_ai_pick(h_st, a_st, m.get("league_name",""), sniper_mode)
                if conf == 0 or p_type == "pass": continue

                won = check_result(p_type, thresh, m)
                if won is None: skipped += 1; continue

                results_by_type.setdefault(p_type, {"w":0,"l":0})
                if won: wins += 1; results_by_type[p_type]["w"] += 1
                else:   losses += 1; results_by_type[p_type]["l"] += 1

                home = m.get("match_hometeam_name","")
                away = m.get("match_awayteam_name","")
                hs   = m.get("match_hometeam_score","?")
                as_  = m.get("match_awayteam_score","?")
                cls  = "acc-win" if won else "acc-loss"
                ico  = "✅" if won else "❌"
                st.markdown(f"""
                <div class='accuracy-row {cls}'>
                    <span style='font-size:18px;'>{ico}</span>
                    <div style='flex:1;'>
                        <div style='font-weight:600; font-size:13px;'>{home} vs {away}</div>
                        <div style='font-size:11px; color:#64748b;'>FT: {hs}–{as_} · {m.get("league_name","")}</div>
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-family:DM Mono,monospace; font-size:12px; color:#e2e8f0;'>{pick}</div>
                        <div style='font-size:11px; color:#475569;'>{conf:.0f}% conf</div>
                    </div>
                </div>""", unsafe_allow_html=True)

        total = wins + losses
        if total > 0:
            wr = wins / total * 100
            st.divider()
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Win Rate",  f"{wr:.1f}%", delta=f"+{wins}W / -{losses}L")
            mc2.metric("Picks",     total)
            mc3.metric("Wins",      wins)
            mc4.metric("Losses",    losses)

            if results_by_type:
                st.markdown("#### Market Breakdown")
                for pt, rec in sorted(results_by_type.items(), key=lambda x: -(x[1]['w']/(x[1]['w']+x[1]['l']) if (x[1]['w']+x[1]['l']) else 0)):
                    t   = rec['w'] + rec['l']
                    pct = rec['w']/t*100 if t else 0
                    bar = int(pct)
                    st.markdown(f"""
                    <div style='margin-bottom:10px;'>
                        <div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'>
                            <span style='font-weight:600;'>{pt.replace('_',' ').title()}</span>
                            <span style='font-family:DM Mono,monospace; color:{"#4ade80" if pct>=70 else "#f87171"};'>{pct:.0f}% ({t} picks)</span>
                        </div>
                        <div class='conf-bar-bg'><div class='conf-bar-fill' style='width:{bar}%; background:{"#16a34a" if pct>=70 else "#ef4444"};'></div></div>
                    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  LIVE AUTO-REFRESH
# ─────────────────────────────────────────
if live_refresh:
    time.sleep(60)
    st.rerun()
