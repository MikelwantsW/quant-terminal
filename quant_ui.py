import streamlit as st
import requests
import time
import math
from datetime import datetime, timedelta

st.set_page_config(page_title="Institutional Radar", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');
.stApp { background-color: #080d14 !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif; }
section[data-testid="stSidebar"] { background-color: #0d1520 !important; border-right: 1px solid #1e293b; }
/* ── Sidebar text & controls — fully visible ── */
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p { color: #e2e8f0 !important; font-weight: 600; }
section[data-testid="stSidebar"] .stMarkdown p { color: #94a3b8 !important; font-size: 13px; }
/* Toggles */
section[data-testid="stSidebar"] [data-testid="stToggleLabel"] { color: #e2e8f0 !important; font-size: 13px !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] [role="switch"] { background-color: #1e293b !important; border-color: #334155 !important; }
section[data-testid="stSidebar"] [role="switch"][aria-checked="true"] { background-color: #16a34a !important; border-color: #16a34a !important; }
/* Checkboxes */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label,
section[data-testid="stSidebar"] [data-testid="stCheckbox"] span { color: #cbd5e1 !important; font-size: 13px !important; font-weight: 500 !important; }
section[data-testid="stSidebar"] [data-baseweb="checkbox"] div { border-color: #334155 !important; background-color: #1e293b !important; }
section[data-testid="stSidebar"] [data-baseweb="checkbox"][aria-checked="true"] div { background-color: #16a34a !important; border-color: #16a34a !important; }
/* Slider */
section[data-testid="stSidebar"] [data-testid="stSlider"] label { color: #e2e8f0 !important; font-size: 13px !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div { background-color: #334155 !important; }
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background-color: #16a34a !important; border-color: #16a34a !important; }
/* Number input */
section[data-testid="stSidebar"] [data-testid="stNumberInput"] label { color: #e2e8f0 !important; font-size: 13px !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] [data-testid="stNumberInput"] input { background-color: #1e293b !important; color: #e2e8f0 !important; border-color: #334155 !important; border-radius: 6px !important; }
/* Divider */
section[data-testid="stSidebar"] hr { border-color: #1e293b !important; }
/* Success / info boxes inside sidebar */
section[data-testid="stSidebar"] [data-testid="stAlert"] { background-color: #0d2218 !important; border-color: #16a34a !important; color: #4ade80 !important; }
.stTabs [data-baseweb="tab-list"] { background: #0d1520; border-radius: 10px; padding: 6px; gap: 6px; border: 1px solid #1e293b; }
.stTabs [data-baseweb="tab"] { color: #64748b; font-weight: 600; font-size: 13px; padding: 10px 18px; border-radius: 7px; }
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
.pick-card { background: linear-gradient(135deg, #0d2218, #0a1f15); border: 1px solid #166534; border-radius: 12px; padding: 22px; text-align: center; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 8px 24px rgba(22,163,74,0.12); }
.pick-label { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; color: #4ade80; margin-bottom: 10px; }
.sniper-card { background: linear-gradient(135deg, #1a0a00, #2a1200); border: 2px solid #f97316; border-radius: 12px; padding: 22px; text-align: center; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 8px 32px rgba(249,115,22,0.25); }
.sniper-label { font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 800; color: #fb923c; margin-bottom: 6px; }
.sniper-badge { display: inline-block; background: #f97316; color: white; padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 900; letter-spacing: 2px; margin-bottom: 10px; font-family: 'DM Mono', monospace; }
.value-card { background: linear-gradient(135deg, #0a0d1a, #0a1020); border: 2px solid #3b82f6; border-radius: 12px; padding: 16px; margin-top: 10px; }
.value-title { font-family: 'DM Mono', monospace; font-size: 10px; color: #60a5fa; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
.value-row { display: flex; justify-content: space-between; font-size: 12px; color: #64748b; padding: 4px 0; border-bottom: 1px solid #0d1520; }
.value-row:last-child { border-bottom: none; }
.value-num { font-family: 'DM Mono', monospace; font-weight: 700; }
.positive-edge { color: #4ade80; }
.negative-edge { color: #f87171; }
.neutral-edge  { color: #fbbf24; }
.kelly-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-family: 'DM Mono', monospace; font-size: 12px; font-weight: 700; margin-top: 6px; }
.kelly-strong { background: rgba(22,163,74,0.2); color: #4ade80; border: 1px solid rgba(22,163,74,0.4); }
.kelly-moderate { background: rgba(234,179,8,0.15); color: #fbbf24; border: 1px solid rgba(234,179,8,0.3); }
.kelly-skip { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.ref-tag { display: inline-block; background: rgba(249,115,22,0.12); color: #fb923c; border: 1px solid rgba(249,115,22,0.3); padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-decoration: none; margin-top: 8px; font-family: 'DM Mono', monospace; }
.stats-panel { background: #080d14; border: 1px solid #1e293b; border-top: 2px solid #f97316; border-radius: 10px; padding: 16px; }
.stats-title { color: #f97316; font-size: 10px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; font-family: 'DM Mono', monospace; }
.stat-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #64748b; padding: 6px 0; border-bottom: 1px solid #0d1520; }
.stat-row:last-child { border-bottom: none; }
.stat-val { font-family: 'DM Mono', monospace; color: #e2e8f0; font-weight: 600; font-size: 14px; }
.conf-bar-wrap { margin-top: 12px; }
.conf-label { font-size: 10px; color: #475569; font-family: 'DM Mono', monospace; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.conf-bar-bg { background: #1e293b; border-radius: 20px; height: 6px; width: 100%; overflow: hidden; }
.conf-bar-fill { height: 6px; border-radius: 20px; }
.slip-box { background: #0d1520; border: 1px dashed #f97316; border-radius: 10px; padding: 20px; margin-top: 12px; }
.slip-row { padding: 12px 0; border-bottom: 1px solid #1e293b; }
.slip-row:last-child { border-bottom: none; }
.slip-league { font-size: 10px; color: #64748b; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; font-family: 'DM Mono', monospace; }
.slip-match { font-weight: 600; color: #e2e8f0; margin: 3px 0; font-size: 14px; }
.slip-pick { font-weight: 800; font-family: 'Syne', sans-serif; font-size: 15px; }
.live-banner { background: #7f1d1d; border: 1px solid #ef4444; color: #fca5a5; padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
.live-dot { height: 8px; width: 8px; background: #ef4444; border-radius: 50%; display: inline-block; animation: pulse 1.2s ease infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1);}50%{opacity:0.4;transform:scale(0.7);} }
.risk-badge { padding: 12px 20px; border-radius: 8px; text-align: center; font-family: 'Syne', sans-serif; font-weight: 800; font-size: 18px; letter-spacing: 1px; color: white; margin-bottom: 20px; }
.empty-state { text-align: center; padding: 60px 20px; color: #334155; }
.empty-state-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state-text { font-size: 16px; font-weight: 600; }
.empty-state-sub { font-size: 13px; color: #1e293b; margin-top: 6px; }
.accuracy-row { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #0d1520; border-radius: 8px; margin-bottom: 6px; border: 1px solid #1e293b; font-size: 13px; }
.acc-win  { border-left: 3px solid #16a34a; }
.acc-loss { border-left: 3px solid #ef4444; }
.info-box    { background: #0d1520; border: 1px solid #1e293b; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; font-size: 13px; color: #64748b; }
.warning-box { background: #1a0a00; border: 1px solid #f97316; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px; font-size: 13px; color: #fb923c; }
.tip-box     { background: #080d14; border: 1px solid #3b82f6; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; font-size: 13px; color: #60a5fa; }
.gate-tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; font-family: 'DM Mono', monospace; margin: 2px; }
.gate-pass { background: rgba(22,163,74,0.15); color: #4ade80; border: 1px solid rgba(22,163,74,0.3); }
.gate-fail { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
/* nav stat card select buttons — invisible overlay */
button[kind="secondary"][data-testid*="nav_"] { opacity: 0 !important; height: 2px !important; min-height: 0 !important; padding: 0 !important; margin: -6px 0 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── CONFIG ───────────────────────────────────────────────────────────────────
_DEFAULT_KEY  = "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a"
API_KEY       = (
    st.session_state.get("user_api_key")
    or st.secrets.get("APIFOOTBALL_KEY", "")
    or _DEFAULT_KEY
)
now           = datetime.utcnow() + timedelta(hours=1)
today_str     = now.strftime('%Y-%m-%d')
tomorrow_str  = (now + timedelta(days=1)).strftime('%Y-%m-%d')
yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str  = (now + timedelta(days=7)).strftime('%Y-%m-%d')
past_str      = (now - timedelta(days=120)).strftime('%Y-%m-%d')

FINISHED_STATUSES = {"Finished","FT","AET","PEN","Awarded","Cancelled","Postponed","Suspended","Abandoned"}
LIVE_STATUSES     = {"1H","HT","2H","ET","P","LIVE","Break"}

SPORTSBOOK_TIER_A = {
    # Exact names
    "Premier League","Serie A","La Liga","Bundesliga","Ligue 1",
    "UEFA Champions League","UEFA Europa League","UEFA Europa Conference League","Championship",
    # API variant names (apifootball.com sometimes returns these)
    "France Ligue 1","Ligue 1 Uber Eats","Ligue 1 McDonald's",
    "Spanish La Liga","Spain La Liga","Primera Division",
    "German Bundesliga","Germany Bundesliga","1. Bundesliga",
    "Italian Serie A","Italy Serie A",
    "English Premier League","England Premier League",
    "English Championship","England Championship",
    "Champions League","Europa League","Conference League",
    "UEFA CL","UEFA EL",
}
SPORTSBOOK_TIER_B = {
    "Eredivisie","Primeira Liga","Süper Lig","Scottish Premiership","Scottish Premier League",
    "Belgian Pro League","Belgian First Division A","Swiss Super League",
    "Austrian Football Bundesliga","Austrian Bundesliga",
    "Allsvenskan","Eliteserien","Superliga","Major League Soccer",
    "Brasileirao Serie A","Argentine Primera División",
    # ── CONMEBOL Continental (South America) ─────────────────────────────────
    "Copa Libertadores","CONMEBOL Libertadores","Copa CONMEBOL Libertadores",
    "Copa Sudamericana","CONMEBOL Sudamericana","Copa CONMEBOL Sudamericana",
    "Recopa Sudamericana",
    # ── API variants ─────────────────────────────────────────────────────────
    "Dutch Eredivisie","Netherlands Eredivisie",
    "Portuguese Primeira Liga","Portugal Primeira Liga","Primeira Liga Portugal",
    "Turkish Süper Lig","Turkey Süper Lig","Super Lig",
    "Scotland Premiership","Scotland Premier League",
    "Belgium First Division A","Belgium Pro League",
    "Austria Bundesliga","Austrian Bundesliga",
    "Sweden Allsvenskan","Norway Eliteserien","Denmark Superliga",
    "USA MLS","MLS","American MLS",
    "Brazil Serie A","Brazilian Serie A","Brasileirão",
    "Argentina Primera Division","Argentine Primera Division",
}
SPORTSBOOK_TIER_C = {
    "Veikkausliiga","SuperLiga","Serbian SuperLiga","Greek Super League",
    "Czech First League","Polish Ekstraklasa","Saudi Pro League",
    "Saudi Professional League","J1 League",
}
TOP_LEAGUES = SPORTSBOOK_TIER_A | SPORTSBOOK_TIER_B | SPORTSBOOK_TIER_C

# ── STRICT ALLOWED COUNTRY PREFIXES ──────────────────────────────────────────
# Only leagues from these countries/competitions are allowed through.
# This is the hard gate that stops Egyptian, Ethiopian, Romanian etc. leaking in.
ALLOWED_COUNTRY_KEYWORDS = {
    # Competitions
    "uefa","champions league","europa league","conference league",
    # Big 5 countries
    "england","english","premier league","championship",
    "spain","spanish","la liga",
    "germany","german","bundesliga",
    "italy","italian","serie a",
    "france","french","ligue 1",
    # Tier B countries
    "netherlands","dutch","eredivisie",
    "portugal","portuguese","primeira liga",
    "turkey","turkish","süper lig","super lig",
    "scotland","scottish",
    "belgium","belgian",
    "switzerland","swiss",
    "austria","austrian",
    "sweden","swedish","allsvenskan",
    "norway","norwegian","eliteserien",
    "denmark","danish","superliga",
    "usa","american","mls",
    "brazil","brazilian","brasileirao",
    "argentina","argentine",
    # Tier C countries
    "finland","veikkausliiga",
    "serbia","serbian",
    "greece","greek",
    "czech",
    "poland","polish","ekstraklasa",
    "saudi",
    "japan","j1 league","j-league",
    # CONMEBOL continental
    "copa","libertadores","sudamericana","conmebol","recopa",
}

# Fuzzy map — only called AFTER country whitelist check passes
_FUZZY_MAP = {
    "ligue 1":           "Ligue 1",
    # "premier league" alone is too broad — matches Sudan/Rwanda/African leagues
    # Only match when preceded by "english" or "england" or alone as exact phrase
    "english premier league": "Premier League",
    "england premier league": "Premier League",
    "la liga":           "La Liga",
    "primera division":  "La Liga",
    "serie a":           "Serie A",
    "bundesliga":        "Bundesliga",
    "champions league":  "UEFA Champions League",
    "europa league":              "UEFA Europa League",
    "uel":                        "UEFA Europa League",
    "conference league":          "UEFA Europa Conference League",
    "uecl":                       "UEFA Europa Conference League",
    "europa conference":          "UEFA Europa Conference League",
    "conference league": "UEFA Europa Conference League",
    "eredivisie":        "Eredivisie",
    "primeira liga":     "Primeira Liga",
    "süper lig":         "Süper Lig",
    "super lig":         "Süper Lig",
    "scottish premiership": "Scottish Premiership",
    "allsvenskan":       "Allsvenskan",
    "eliteserien":       "Eliteserien",
    "superliga":         "Superliga",
    "mls":               "Major League Soccer",
    "brasileirao":       "Brasileirao Serie A",
    "brazil serie a":    "Brasileirao Serie A",
    "argentina primera": "Argentine Primera División",
    "veikkausliiga":     "Veikkausliiga",
    "serbian superliga": "Serbian SuperLiga",
    "greek super":       "Greek Super League",
    "czech first":       "Czech First League",
    "ekstraklasa":       "Polish Ekstraklasa",
    "saudi pro":              "Saudi Pro League",
    "saudi professional":     "Saudi Professional League",
    "saudi league":           "Saudi Pro League",
    "roshn":                  "Saudi Pro League",  # Roshn Saudi League (sponsored name)
    "saudi roshn":            "Saudi Pro League",
    "j1 league":         "J1 League",
    "belgian pro":       "Belgian Pro League",
    "swiss super":       "Swiss Super League",
    "austrian":                "Austrian Football Bundesliga",
    # English Championship — must match EXACTLY, not "Romanian Championship"
    "english championship":    "Championship",
    "england championship":    "Championship",
    # CONMEBOL continental competitions
    "copa libertadores":       "Copa Libertadores",
    "libertadores":            "Copa Libertadores",
    "conmebol libertadores":   "Copa Libertadores",
    "copa sudamericana":       "Copa Sudamericana",
    "sudamericana":            "Copa Sudamericana",
    "conmebol sudamericana":   "Copa Sudamericana",
    "recopa sudamericana":     "Recopa Sudamericana",
}

# Explicit BLOCK list — leagues whose names partially match allowed keywords
# but are NOT on major sportsbooks
BLOCKED_LEAGUE_KEYWORDS = {
    # ── Africa (comprehensive) ────────────────────────────────────────────────
    "egypt","egyptian","ethiopia","ethiopian","mauritania","mauritanian",
    "algeria","algerian","morocco","moroccan","tunisia","tunisian",
    "kenya","kenyan","ghana","ghanaian","cameroon","zimbabwe","zambia",
    "tanzania","uganda","south africa","south african",
    "nigeria","nigerian","senegal","senegalese","ivory coast","côte d'ivoire",
    "angola","mali","guinea","liberia","sierra leone","rwanda","rwandan",
    "sudan","sudanese","south sudan","burundi","mozambique","madagascar",
    "namibia","botswana","malawi","eritrea","djibouti","somalia","ethiopia",
    "chad","niger","togo","benin","burkina","gabon","equatorial guinea",
    "central african","libya","mauritius","reunion","cape verde",
    # specific African clubs that slip through
    "al-merreikh","el merreikh","etincelles","apr fc","rayon sports",
    "al hilal omdurman","al-hilal omdurman","gor mahia","tp mazembe",
    "al ahly","zamalek","esperance","wydad","raja casablanca",
    # ── Middle East ───────────────────────────────────────────────────────────
    "iran","iranian","iraq","iraqi","uae","qatar","kuwait",
    "bahrain","oman","jordan","lebanon","syria","yemen",
    # ── Central/East Asia ────────────────────────────────────────────────────
    "uzbekistan","kazakhstan","azerbaijan","armenia","georgia",
    "vietnam","indonesia","malaysia","thailand","south korea","china",
    "india","pakistan","bangladesh","philippines","myanmar","cambodia",
    "laos","mongolia","nepal","sri lanka","maldives",
    # ── Americas (non-top leagues) ────────────────────────────────────────────
    "mexico","colombia","chile","peru","ecuador","venezuela","bolivia",
    "paraguay","costa rica","honduras","guatemala","panama","nicaragua",
    "el salvador","jamaica","trinidad","barbados","haiti","cuba",
    # NOTE: Uruguay excluded — could have edge cases, handled by ALLOWED list
    # ── Lower divisions / amateur ────────────────────────────────────────────
    "scotland a league","highland","lowland",
    "amateur","reserve","u21","u23","u19","u18","youth","women","w league",
    "second division","third division","division 2","division 3",
    "liga 2","liga 3","serie b","serie c","division b",
    "ligue 2","championship 2","primeira b","2. bundesliga",
    "national league","vanarama","non-league",
    # ── Non-bookable European domestic leagues ─────────────────────────────
    # NOTE: We block the DOMESTIC leagues, NOT the countries themselves.
    # Ukrainian/Croatian/etc. CLUBS play in UEFA competitions under correct names.
    # Only block when the league itself is clearly a minor domestic competition.
    "romanian liga","romanian football","liga i romania",
    "israeli premier league","ligat haal",
    "bulgarian first league","efbet liga",
    "hungarian otp bank liga","nb i",
    "latvian virsliga","estonian meistriliiga",
    "moldovan national division","belarusian premier league",
    "northern ireland premiership","faroe islands",
    "icelandic league","andorra primera",
    "maltese premier","san marino campionato",
}

# Additional exact team name blocks (clubs that slip through league filter)
BLOCKED_TEAM_NAMES = {
    "al-merreikh","el merreikh","merreikh","etincelles","apr fc","rayon sports",
    "al hilal omdurman","omdurman","gor mahia","tp mazembe","vita club",
    "al ahly","zamalek","esperance","wydad","raja","renaissance berkane",
    "mamelodi sundowns","orlando pirates","kaizer chiefs","al merrikh",
    "al-merrikh","young africans","simba sc","azam fc",
}

def is_team_blocked(home: str, away: str) -> bool:
    """Return True if either team name contains a blocked keyword."""
    combined = (home + " " + away).lower()
    return any(bt in combined for bt in BLOCKED_TEAM_NAMES)

def canonical_league(name: str) -> str:
    """
    Return canonical league name or original if unknown.
    STRICT: blocks unrecognised countries, youth/amateur leagues, lower divisions.
    """
    if name in TOP_LEAGUES:
        return name   # exact match — fast path
    # Exact phrase "Premier League" with no prefix = English PL
    if name.strip().lower() == "premier league":
        return "Premier League"

    low = name.lower()

    # Hard block — reject immediately if a blocked keyword appears
    for bkw in BLOCKED_LEAGUE_KEYWORDS:
        if bkw in low:
            return "__BLOCKED__"

    # Hard-pass for Copa competitions (before country check)
    # API returns many name variants — catch ALL of them here
    if "libertadores" in low: return "Copa Libertadores"
    if "sudamericana"  in low and "copa" in low: return "Copa Sudamericana"
    if "sudamericana"  in low and "conmebol" in low: return "Copa Sudamericana"
    if "recopa"        in low and ("sud" in low or "conmebol" in low): return "Recopa Sudamericana"

    # Must contain at least one allowed country/competition keyword
    has_allowed = any(akw in low for akw in ALLOWED_COUNTRY_KEYWORDS)
    if not has_allowed:
        return "__BLOCKED__"

    # Try fuzzy map (more specific phrases first — sort by length descending)
    for keyword, canonical in sorted(_FUZZY_MAP.items(), key=lambda x: -len(x[0])):
        if keyword in low:
            return canonical

    # No match — block it
    return "__BLOCKED__"

# ─────────────────────────────────────────────────────────────────────────────
#  DYNAMIC PLAYER INTELLIGENCE ENGINE
#
#  Philosophy: Instead of a brittle hand-coded list of 25 players that goes
#  stale within weeks, we compute player influence scores DYNAMICALLY from
#  the same API data we already fetch. This covers EVERY player in EVERY league.
#
#  How it works:
#  1. Fetch the last N matches for a team (already done via fetch_stats)
#  2. For each match, pull player-level stats from the API
#  3. Compute each player's personal contribution scores:
#       - goals_contrib   = goals scored / team goals (when playing)
#       - sot_contrib     = shots on target / team SOT (when playing)
#       - corner_contrib  = corners won / team corners (when playing) [from event data]
#       - card_risk       = yellow cards per game
#  4. When a lineup is confirmed, sum up absent key players' contributions
#     and apply them as multipliers to proj_g, proj_c, proj_sot, proj_cd
#  5. If a player with high_contrib is ABSENT → reduce that projection
#     If a player with high_contrib is CONFIRMED → slight confidence boost
#
#  Thresholds for "key player":
#       goals_contrib  > 0.30  → responsible for 30%+ of team's goals
#       sot_contrib    > 0.25  → responsible for 25%+ of team's shots on target
#       corner_contrib > 0.20  → involved in 20%+ of team's corners
#       card_risk      > 0.60  → averages >0.6 cards/game (disciplinary risk)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=7200, show_spinner=False)  # 2hr cache
def fetch_player_stats(team_id: str, past_from: str, past_to: str) -> dict:
    """
    Fetch last 8 finished matches for a team and compute per-player contribution
    scores across all markets: goals, SOT, corners, cards.
    Returns dict keyed by player_name with contribution scores.
    """
    url = (f"https://apiv3.apifootball.com/?action=get_events"
           f"&team_id={team_id}&from={past_from}&to={past_to}&APIkey={API_KEY}")
    try:
        res = requests.get(url, timeout=12).json()
        if not isinstance(res, list):
            return {}

        finished = [m for m in res if m.get("match_status") == "Finished"][-8:]
        if not finished:
            return {}

        # Accumulate per-player stats across matches
        player_acc = {}   # name → {goals, sot, cards, matches_played, team_goals, team_sot, team_corners, team_cards}
        team_totals = {"goals": 0, "sot": 0, "corners": 0, "cards": 0, "matches": 0}

        for m in finished:
            is_home = m.get("match_hometeam_id") == team_id
            team_goals   = safe_num(m.get("match_hometeam_score" if is_home else "match_awayteam_score", 0))
            match_stats  = {r.get("type"): safe_num(r.get("home" if is_home else "away", 0))
                            for r in m.get("statistics", [])}
            team_sot     = match_stats.get("Shots On Goal", 0)
            team_corners = match_stats.get("Corners", 0)
            team_cards   = match_stats.get("Yellow Cards", 0)

            team_totals["goals"]   += team_goals
            team_totals["sot"]     += team_sot
            team_totals["corners"] += team_corners
            team_totals["cards"]   += team_cards
            team_totals["matches"] += 1

            # Player-level stats from scorers / lineups
            # Goals
            for scorer in m.get("goalscorer", []):
                pname = scorer.get("home_scorer" if is_home else "away_scorer", "")
                if pname:
                    player_acc.setdefault(pname, {"goals":0,"sot":0,"cards":0,"mp":0})
                    player_acc[pname]["goals"] += 1

            # Cards
            for card in m.get("cards", []):
                side = card.get("home_fault","") if is_home else card.get("away_fault","")
                pname = side
                if pname:
                    player_acc.setdefault(pname, {"goals":0,"sot":0,"cards":0,"mp":0})
                    player_acc[pname]["cards"] += 1

            # Lineup — count appearances
            lineup_side = "lineup_home" if is_home else "lineup_away"
            lineup_data = m.get(lineup_side, {})
            if isinstance(lineup_data, dict):
                for pos_group in lineup_data.values():
                    if isinstance(pos_group, list):
                        for p in pos_group:
                            pname = p.get("player","") if isinstance(p, dict) else str(p)
                            if pname:
                                player_acc.setdefault(pname, {"goals":0,"sot":0,"cards":0,"mp":0})
                                player_acc[pname]["mp"] += 1

        if not player_acc or team_totals["matches"] == 0:
            return {}

        n = team_totals["matches"]
        # Compute contribution scores for each player
        result = {}
        for pname, stats in player_acc.items():
            if stats["mp"] < 2:   # skip players with fewer than 2 appearances
                continue
            goals_contrib = stats["goals"] / max(team_totals["goals"], 1)
            card_risk     = stats["cards"] / max(stats["mp"], 1)
            result[pname] = {
                "goals_contrib":  round(goals_contrib, 3),
                "card_risk":      round(card_risk, 3),
                "appearances":    stats["mp"],
                "goals":          stats["goals"],
                "cards":          stats["cards"],
            }
        return result

    except Exception:
        return {}


def compute_player_impact(
    home_player_stats: dict,  # from fetch_player_stats for home team
    away_player_stats: dict,  # from fetch_player_stats for away team
    confirmed_names: set,     # from fetch_lineups_for_match
    home_name: str,
    away_name: str,
) -> dict:
    """
    Given player stats and confirmed lineup, compute market-specific multipliers.

    Returns dict:
        g_mult    : goals projection multiplier
        c_mult    : corners projection multiplier
        k_mult    : cards projection multiplier
        s_mult    : SOT projection multiplier
        conf_bonus: confidence bonus points (positive or negative)
        key_absent : list of (name, market, contribution, side)
        key_playing: list of (name, market, contribution, side)
        lineups_available: bool
    """
    lineups_available = len(confirmed_names) > 0

    result = {
        "g_mult": 1.0, "c_mult": 1.0, "k_mult": 1.0, "s_mult": 1.0,
        "conf_bonus": 0.0,
        "key_absent": [], "key_playing": [],
        "lineups_available": lineups_available,
    }

    if not lineups_available:
        # No lineup data = no intel. Don't guess, don't show UNCONFIRMED.
        # The projections will use base stats only, which is fine.
        return result

    # ── Thresholds for "key player" classification ────────────────────────────
    GOAL_KEY_THRESH    = 0.28   # responsible for 28%+ of team goals
    CARD_KEY_THRESH    = 0.55   # averages 0.55+ cards per game
    # Corners & SOT: derived from goals_contrib as proxy (direct data unavailable)
    SOT_KEY_THRESH     = 0.22   # proxy: if high goals_contrib, likely high SOT too

    def check_side(player_stats: dict, side: str):
        for pname, pdata in player_stats.items():
            # Check if player name appears in confirmed lineup
            surname = pname.split()[-1].lower() if pname.split() else ""
            firstname = pname.split()[0].lower() if pname.split() else ""
            in_lineup = any(
                (surname and surname in c.lower()) or
                (firstname and len(firstname) > 2 and firstname in c.lower())
                for c in confirmed_names
            )

            is_goal_key  = pdata["goals_contrib"] >= GOAL_KEY_THRESH
            is_card_key  = pdata["card_risk"]      >= CARD_KEY_THRESH
            is_sot_key   = pdata["goals_contrib"]  >= SOT_KEY_THRESH

            if not (is_goal_key or is_card_key or is_sot_key):
                continue   # not a key player in any market

            if in_lineup:
                # Key player confirmed → mild confidence boost
                if is_goal_key:
                    result["g_mult"]    *= (1.0 + pdata["goals_contrib"] * 0.15)
                    result["s_mult"]    *= (1.0 + pdata["goals_contrib"] * 0.10)
                    result["c_mult"]    *= (1.0 + pdata["goals_contrib"] * 0.08)
                    result["conf_bonus"] += pdata["goals_contrib"] * 8
                    result["key_playing"].append((pname, "goals/SOT/corners",
                                                  f"{pdata['goals_contrib']*100:.0f}% goal share", side))
                if is_card_key:
                    result["k_mult"]    *= (1.0 + pdata["card_risk"] * 0.20)
                    result["conf_bonus"] += pdata["card_risk"] * 4
                    result["key_playing"].append((pname, "cards",
                                                  f"{pdata['card_risk']:.2f} cards/game", side))
            else:
                # Key player ABSENT → reduce relevant projections
                if is_goal_key:
                    drop = pdata["goals_contrib"]  # e.g. 0.35 → reduce by 35% of their share
                    result["g_mult"]    *= max(0.65, 1.0 - drop * 0.55)
                    result["s_mult"]    *= max(0.70, 1.0 - drop * 0.45)
                    result["c_mult"]    *= max(0.75, 1.0 - drop * 0.35)
                    result["conf_bonus"] -= drop * 12   # confidence drops when key attacker missing
                    result["key_absent"].append((pname, "goals/SOT/corners",
                                                 f"{pdata['goals_contrib']*100:.0f}% goal share absent", side))
                if is_card_key:
                    result["k_mult"]    *= max(0.75, 1.0 - pdata["card_risk"] * 0.25)
                    result["conf_bonus"] -= pdata["card_risk"] * 3
                    result["key_absent"].append((pname, "cards",
                                                 f"{pdata['card_risk']:.2f} cards/game — absent", side))

    check_side(home_player_stats, "HOME")
    check_side(away_player_stats, "AWAY")

    # Clamp multipliers to sane range
    for k in ("g_mult","c_mult","k_mult","s_mult"):
        result[k] = round(max(0.60, min(1.45, result[k])), 3)
    result["conf_bonus"] = round(max(-15.0, min(12.0, result["conf_bonus"])), 2)

    return result


# Which player market categories are relevant to each pick type
PICK_MARKET_MAP = {
    "goals":         {"goals/SOT/corners", "goals"},
    "under_goals":   {"goals/SOT/corners", "goals"},
    "sot":           {"goals/SOT/corners", "goals"},
    "under_sot":     {"goals/SOT/corners", "goals"},
    "corners":       {"goals/SOT/corners", "corners"},   # corners influenced by attackers too
    "under_corners": {"goals/SOT/corners", "corners"},
    "cards":         {"cards"},
    "under_cards":   {"cards"},
}

def player_intel_html(impact: dict, pick_type: str = "") -> str:
    """
    Build player intelligence panel.
    Rules:
    - NEVER show UNCONFIRMED players — if lineups not confirmed, show nothing
    - Only show players relevant to the pick_type market
    - Show confirmed playing/absent players with their actual impact
    - If no relevant confirmed data → return empty string silently
    """
    lineups = impact.get("lineups_available", False)

    # Rule 1: No lineups = no panel. Period.
    # Showing UNCONFIRMED is noise — it adds no decision value.
    if not lineups:
        return ""

    playing = impact.get("key_playing", [])
    absent  = impact.get("key_absent",  [])

    # Rule 2: Filter to only players relevant to this pick's market
    relevant_markets = PICK_MARKET_MAP.get(pick_type, {"goals/SOT/corners", "cards"})

    def is_relevant(entry):
        name, market, detail, side = entry
        return any(rm in market for rm in relevant_markets)

    playing_relevant = [p for p in playing if is_relevant(p)]
    absent_relevant  = [p for p in absent  if is_relevant(p)]

    # Rule 3: Nothing relevant confirmed = show nothing
    if not playing_relevant and not absent_relevant:
        return ""

    # Build rows — only confirmed playing or confirmed absent
    rows = ""
    for name, market, detail, side in (playing_relevant + absent_relevant)[:8]:
        is_playing = (name, market, detail, side) in playing_relevant
        if is_playing:
            tag    = ("<span style='background:rgba(74,222,128,.15);color:#4ade80;"
                      "border:1px solid rgba(74,222,128,.35);padding:3px 8px;"
                      "border-radius:8px;font-size:10px;font-family:DM Mono,monospace;"
                      "font-weight:700;'>▶ CONFIRMED</span>")
            mcolor = "#4ade80"
            impact_label = f"+edge · {detail}"
        else:
            tag    = ("<span style='background:rgba(239,68,68,.12);color:#f87171;"
                      "border:1px solid rgba(239,68,68,.28);padding:3px 8px;"
                      "border-radius:8px;font-size:10px;font-family:DM Mono,monospace;"
                      "font-weight:700;'>✗ ABSENT</span>")
            mcolor = "#f87171"
            impact_label = f"−edge · {detail}"

        rows += (
            f"<div style='display:flex;align-items:center;gap:8px;padding:6px 0;"
            f"border-bottom:1px solid #09111c;flex-wrap:wrap;'>"
            f"<span style='color:#e2e8f0;font-weight:600;font-size:12px;min-width:130px;'>{name}</span>"
            f"<span style='color:#334d66;font-size:10px;font-family:DM Mono,monospace;'>{side}</span>"
            f"{tag}"
            f"<span style='color:{mcolor};font-family:DM Mono,monospace;font-size:10px;"
            f"margin-left:auto;text-align:right;'>{impact_label}</span>"
            f"</div>"
        )

    # Confidence impact summary
    bonus   = impact.get("conf_bonus", 0.0)
    b_color = "#4ade80" if bonus > 0 else "#f87171" if bonus < 0 else "#4b6080"
    b_sign  = "+" if bonus > 0 else ""

    # Show only the multiplier for the relevant market
    mult_parts = []
    if any(rm in {"goals/SOT/corners","goals"} for rm in relevant_markets):
        g_m = impact.get("g_mult", 1.0)
        if abs(g_m - 1.0) > 0.01:
            c = "#4ade80" if g_m > 1 else "#f87171"
            mult_parts.append(f"<span style='color:{c};'>Goals ×{g_m:.2f}</span>")
    if "corners" in str(relevant_markets):
        c_m = impact.get("c_mult", 1.0)
        if abs(c_m - 1.0) > 0.01:
            c = "#4ade80" if c_m > 1 else "#f87171"
            mult_parts.append(f"<span style='color:{c};'>Corners ×{c_m:.2f}</span>")
    if any(rm in {"cards"} for rm in relevant_markets):
        k_m = impact.get("k_mult", 1.0)
        if abs(k_m - 1.0) > 0.01:
            c = "#4ade80" if k_m > 1 else "#f87171"
            mult_parts.append(f"<span style='color:{c};'>Cards ×{k_m:.2f}</span>")

    mults_html = " &nbsp; ".join(mult_parts) if mult_parts else ""

    return (
        f"<div style='background:linear-gradient(135deg,#060b18,#080d20);"
        f"border:1px solid #1e3a5f;border-radius:10px;padding:14px;margin-top:10px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;"
        f"margin-bottom:10px;'>"
        f"<span style='font-family:DM Mono,monospace;font-size:10px;color:#60a5fa;"
        f"letter-spacing:2px;text-transform:uppercase;'>🧠 Player Intel · Lineups Confirmed</span>"
        f"<span style='font-size:11px;color:{b_color};font-family:DM Mono,monospace;"
        f"font-weight:700;'>{b_sign}{bonus:.1f}pts</span>"
        f"</div>"
        f"{rows}"
        f"{'<div style=\'margin-top:8px;font-size:11px;font-family:DM Mono,monospace;\'>' + mults_html + '</div>' if mults_html else ''}"
        f"</div>"
    )


LEAGUE_PROFILE = {
    "La Liga":(0.90,0.85,1.05,0.0),"Serie A":(0.88,0.92,1.10,0.0),
    "Bundesliga":(1.05,0.95,0.90,0.0),"Premier League":(1.00,1.00,1.00,0.0),
    "Ligue 1":(0.95,1.00,1.05,0.0),"UEFA Champions League":(1.00,1.00,1.00,0.0),
"Copa Libertadores":(1.05,1.08,1.25,1.0),
    "Copa Sudamericana":(1.02,1.05,1.20,1.0),
    "CONMEBOL Libertadores":(1.05,1.08,1.25,1.0),
    "CONMEBOL Sudamericana":(1.02,1.05,1.20,1.0),
        "UEFA Europa League":(1.00,1.00,1.00,0.0),"UEFA Europa Conference League":(1.00,1.00,1.00,0.0),
    "Championship":(1.05,1.10,1.00,0.0),"Eredivisie":(1.10,1.00,0.90,0.0),
    "Primeira Liga":(0.90,1.05,1.10,1.0),"Süper Lig":(1.00,1.00,1.15,1.0),
    "Scottish Premiership":(1.05,1.10,1.00,1.0),"Scottish Premier League":(1.05,1.10,1.00,1.0),
    "Austrian Football Bundesliga":(1.05,1.00,0.95,1.0),"Austrian Bundesliga":(1.05,1.00,0.95,1.0),
    "Belgian Pro League":(1.05,1.00,1.00,1.0),"Belgian First Division A":(1.05,1.00,1.00,1.0),
    "Swiss Super League":(0.95,1.00,0.95,1.0),"Allsvenskan":(0.95,1.05,0.85,2.0),
    "Eliteserien":(1.00,1.05,0.85,2.0),"Superliga":(1.00,1.00,0.90,2.0),
    "Major League Soccer":(1.05,0.95,0.90,2.0),"Brasileirao Serie A":(1.00,1.05,1.15,2.0),
    "Argentine Primera División":(1.00,1.00,1.20,2.0),"Veikkausliiga":(1.00,1.05,0.85,3.0),
    "SuperLiga":(0.95,1.00,1.15,2.0),"Serbian SuperLiga":(0.95,1.00,1.15,2.0),
    "Greek Super League":(0.90,1.00,1.20,3.0),"Czech First League":(0.95,1.00,1.05,2.0),
    "Polish Ekstraklasa":(0.95,1.05,1.05,2.0),"Saudi Pro League":(1.00,0.90,1.20,3.0),
    "Saudi Professional League":(1.00,0.90,1.20,3.0),"J1 League":(0.95,1.00,0.85,3.0),
}
DEFAULT_PROFILE = (1.0,1.0,1.0,2.0)

# ── HOME ADVANTAGE PROFILE ────────────────────────────────────────────────────
# Per-league home/away asymmetry factors derived from multi-season research.
# Each entry: (home_goal_boost, away_goal_drop, home_corner_boost,
#              away_card_boost, home_advantage_strength)
# home_advantage_strength: 0=neutral, 1=moderate, 2=strong, 3=very strong
#
# Usage:
#   home team projections  → multiply by home_goal_boost / home_corner_boost
#   away team projections  → multiply by away_goal_drop
#   away team cards        → multiply by away_card_boost
#   confidence bonus       → home_advantage_strength × 1.5 pts when home team is favourite
HOME_AWAY_PROFILE = {
    # League                     hG     aG    hC    aC    str
    "Premier League":           (1.10, 0.90, 1.08, 1.18,  1),
    "La Liga":                  (1.12, 0.88, 1.10, 1.22,  2),
    "Serie A":                  (1.15, 0.85, 1.12, 1.28,  2),  # strong home fortress culture
    "Bundesliga":               (1.08, 0.93, 1.06, 1.12,  1),  # near-neutral
    "Ligue 1":                  (1.12, 0.88, 1.09, 1.20,  2),
    "UEFA Champions League":    (1.08, 0.92, 1.07, 1.15,  1),
    "UEFA Europa League":       (1.10, 0.90, 1.08, 1.18,  1),
    "UEFA Europa Conference League":(1.10, 0.90, 1.08, 1.18, 1),
    "Copa Libertadores":        (1.18, 0.82, 1.12, 1.30,  3),
    "Copa Sudamericana":        (1.15, 0.85, 1.10, 1.28,  2),
    "CONMEBOL Libertadores":    (1.18, 0.82, 1.12, 1.30,  3),
    "CONMEBOL Sudamericana":    (1.15, 0.85, 1.10, 1.28,  2),
    "Championship":             (1.12, 0.88, 1.10, 1.20,  2),
    "Eredivisie":               (1.06, 0.95, 1.05, 1.10,  1),  # fairly neutral
    "Primeira Liga":            (1.15, 0.85, 1.12, 1.25,  2),
    "Süper Lig":                (1.18, 0.82, 1.14, 1.35,  3),  # very strong home advantage
    "Scottish Premiership":     (1.12, 0.88, 1.10, 1.18,  2),
    "Scottish Premier League":  (1.12, 0.88, 1.10, 1.18,  2),
    "Belgian Pro League":       (1.10, 0.90, 1.08, 1.18,  1),
    "Belgian First Division A": (1.10, 0.90, 1.08, 1.18,  1),
    "Swiss Super League":       (1.08, 0.93, 1.06, 1.14,  1),
    "Austrian Football Bundesliga":(1.10, 0.90, 1.08, 1.18, 1),
    "Austrian Bundesliga":      (1.10, 0.90, 1.08, 1.18,  1),
    "Allsvenskan":              (1.10, 0.91, 1.07, 1.15,  1),
    "Eliteserien":              (1.10, 0.91, 1.07, 1.15,  1),
    "Superliga":                (1.10, 0.91, 1.08, 1.16,  1),
    "Major League Soccer":      (1.12, 0.88, 1.08, 1.15,  2),  # travel factor in MLS huge
    "Brasileirao Serie A":      (1.18, 0.82, 1.12, 1.30,  3),  # hostile away environments
    "Argentine Primera División":(1.20, 0.80, 1.14, 1.35, 3),  # some of the strongest home advantage in world football
    "Veikkausliiga":            (1.08, 0.93, 1.06, 1.12,  1),
    "SuperLiga":                (1.15, 0.86, 1.10, 1.25,  2),
    "Serbian SuperLiga":        (1.15, 0.86, 1.10, 1.28,  2),
    "Greek Super League":       (1.18, 0.83, 1.12, 1.32,  3),
    "Czech First League":       (1.10, 0.91, 1.08, 1.18,  1),
    "Polish Ekstraklasa":       (1.12, 0.89, 1.09, 1.20,  2),
    "Saudi Pro League":         (1.15, 0.86, 1.08, 1.22,  2),
    "Saudi Professional League":(1.15, 0.86, 1.08, 1.22,  2),
    "J1 League":                (1.10, 0.91, 1.07, 1.12,  1),
}
DEFAULT_HA = (1.10, 0.90, 1.08, 1.18, 1)  # fallback

def get_ha_profile(league: str) -> tuple:
    return HOME_AWAY_PROFILE.get(league, DEFAULT_HA)

# ── MARKET DEPTH MAP ──────────────────────────────────────────────────────────
# Defines which specialty markets are reliably offered by sportsbooks per league.
# Based on real-world availability on Bet365 / Betano / Betway / 1xBet.
#   goals   = Over/Under goals (always available everywhere)
#   corners = Corner totals (available Tier A + most Tier B)
#   cards   = Card totals   (available Tier A + some Tier B, NOT J-League/Saudi/Nordic)
#   sot     = Shots on target (Tier A only — rarely offered elsewhere)
MARKET_DEPTH = {
    # ── Tier A — full markets on all books ──
    "Premier League":                   {"goals","corners","cards","sot"},
    "La Liga":                          {"goals","corners","cards","sot"},
    "Serie A":                          {"goals","corners","cards","sot"},
    "Bundesliga":                       {"goals","corners","cards","sot"},
    "Ligue 1":                          {"goals","corners","cards","sot"},
    "UEFA Champions League":            {"goals","corners","cards","sot"},
    "UEFA Europa League":               {"goals","corners","cards","sot"},
    "UEFA Europa Conference League":    {"goals","corners","cards","sot"},
    "Copa Libertadores":                {"goals","corners","cards"},
    "Copa Sudamericana":                {"goals","corners","cards"},
    "CONMEBOL Libertadores":            {"goals","corners","cards"},
    "CONMEBOL Sudamericana":            {"goals","corners","cards"},
    "Recopa Sudamericana":              {"goals","corners"},
    "Championship":                     {"goals","corners","cards","sot"},
    # ── Tier B — goals + corners + cards, no SOT ──
    "Eredivisie":                       {"goals","corners","cards"},
    "Primeira Liga":                    {"goals","corners","cards"},
    "Süper Lig":                        {"goals","corners","cards"},
    "Scottish Premiership":             {"goals","corners","cards"},
    "Scottish Premier League":          {"goals","corners","cards"},
    "Belgian Pro League":               {"goals","corners","cards"},
    "Belgian First Division A":         {"goals","corners","cards"},
    "Swiss Super League":               {"goals","corners","cards"},
    "Austrian Football Bundesliga":     {"goals","corners","cards"},
    "Austrian Bundesliga":              {"goals","corners","cards"},
    "Major League Soccer":              {"goals","corners","cards"},
    "Brasileirao Serie A":              {"goals","corners","cards"},
    "Argentine Primera División":       {"goals","corners","cards"},
    # ── Nordic — goals + corners ONLY, no cards/SOT on most books ──
    "Allsvenskan":                      {"goals","corners"},
    "Eliteserien":                      {"goals","corners"},
    "Superliga":                        {"goals","corners"},
    # ── Tier C — goals ONLY reliably; corners sometimes; cards/SOT almost never ──
    "Veikkausliiga":                    {"goals"},
    "SuperLiga":                        {"goals","corners"},
    "Serbian SuperLiga":                {"goals","corners"},
    "Greek Super League":               {"goals","corners"},
    "Czech First League":               {"goals","corners"},
    "Polish Ekstraklasa":               {"goals","corners"},
    "Saudi Pro League":                 {"goals"},
    "Saudi Professional League":        {"goals"},
    "J1 League":                        {"goals"},          # ← The exact bug you hit
}
DEFAULT_MARKETS = {"goals"}  # fallback for unknown leagues — goals only

# ── CARD COUNTING SYSTEMS ─────────────────────────────────────────────────────
# Betano: Yellow=1, Red=2, Max per player=3. Lines typically 4.5/5.5/6.5
# Bet365/standard: Yellow=1. Lines typically 2.5/3.5/4.5
RED_CARD_RATE = {
    "La Liga":0.32,"Serie A":0.28,"Ligue 1":0.25,"Premier League":0.22,
    "Bundesliga":0.18,"UEFA Champions League":0.20,"UEFA Europa League":0.22,
    "UEFA Europa Conference League":0.20,
    "Copa Libertadores":0.38,"Copa Sudamericana":0.35,
    "CONMEBOL Libertadores":0.38,"CONMEBOL Sudamericana":0.35,"Championship":0.28,"Süper Lig":0.35,
    "Greek Super League":0.38,"Argentine Primera División":0.40,
    "Brasileirao Serie A":0.32,"Scottish Premiership":0.25,
    "Eredivisie":0.20,"Primeira Liga":0.28,
}
DEFAULT_RED_RATE = 0.25

def yellows_to_card_points(yellow_proj: float, league: str) -> float:
    red_rate = RED_CARD_RATE.get(league, DEFAULT_RED_RATE)
    return round(yellow_proj + red_rate * 2.0, 2)

CARD_LINES_YELLOW = [2.5, 3.5, 4.5, 5.5]
CARD_LINES_POINTS = [3.5, 4.5, 5.5, 6.5]

def get_card_line_options(proj_yellows: float, league: str = "", card_mode: str = "both") -> list:
    proj_pts = yellows_to_card_points(proj_yellows, league)
    options  = []
    def evaluate(proj, line, sys_label):
        gap = proj - line
        if gap >= 0.3:
            note = "Strong" if gap >= 2.0 else "Moderate" if gap >= 1.0 else "Slight"
            options.append((line, "OVER", round(gap,2), note, sys_label))
        elif gap <= -1.0:
            note = "Strong" if abs(gap) >= 2.0 else "Moderate"
            options.append((line, "UNDER", round(abs(gap),2), note, sys_label))
    if card_mode in ("yellow","both"):
        for ln in CARD_LINES_YELLOW:
            evaluate(proj_yellows, ln, "Yellow cards")
    if card_mode in ("points","both"):
        for ln in CARD_LINES_POINTS:
            evaluate(proj_pts, ln, "Card pts (Betano)")
    seen = {}
    for opt in options:
        key = (opt[0], opt[1])
        if key not in seen or opt[2] > seen[key][2]:
            seen[key] = opt
    return sorted(seen.values(), key=lambda x: x[2], reverse=True)

def available_markets(league: str) -> set:
    """Return the set of market types available for this league on sportsbooks."""
    return MARKET_DEPTH.get(league, DEFAULT_MARKETS)

# ── LEAGUE PRESTIGE RANKING ───────────────────────────────────────────────────
# Lower number = shown first. Used to sort leagues before displaying matches.
LEAGUE_PRESTIGE = {
    # Tier 1 — global showpiece
    "UEFA Champions League":            1,
    "UEFA Europa League":               2,
    "UEFA Europa Conference League":    3,
    "Copa Libertadores":                4,    # South America's UCL
    "Copa Sudamericana":                5,    # South America's UEL
    "Recopa Sudamericana":              6,
            # Tier 2 — Big Five
    "Premier League":                   10,
    "La Liga":                          11,
    "Bundesliga":                       12,
    "Serie A":                          13,
    "Ligue 1":                          14,
    # Tier 3 — Strong domestic
    "Championship":                     20,
    "Eredivisie":                       21,
    "Primeira Liga":                    22,
    "Süper Lig":                        23,
    "Scottish Premiership":             24,
    "Scottish Premier League":          24,
    "Belgian Pro League":               25,
    "Belgian First Division A":         25,
    "Austrian Football Bundesliga":     26,
    "Austrian Bundesliga":              26,
    "Swiss Super League":               27,
    # Tier 4 — Nordic / Americas
    "Allsvenskan":                      30,
    "Eliteserien":                      31,
    "Superliga":                        32,
    "Major League Soccer":              33,
    "Brasileirao Serie A":              34,
    "Argentine Primera División":       35,
    # Tier 5 — Rest
    "Veikkausliiga":                    40,
    "SuperLiga":                        41,
    "Serbian SuperLiga":                41,
    "Greek Super League":               42,
    "Czech First League":               43,
    "Polish Ekstraklasa":               44,
    "Saudi Pro League":                 45,
    "Saudi Professional League":        45,
    "J1 League":                        46,
}

# Known heavyweight clubs — boosts a match's importance score
ELITE_CLUBS = {
    # European giants
    "Real Madrid","Barcelona","Bayern Munich","Manchester City","Liverpool",
    "Chelsea","Arsenal","Manchester United","Tottenham","Newcastle",
    "Inter Milan","AC Milan","Juventus","Napoli","Roma","Lazio",
    "PSG","Marseille","Lyon","Borussia Dortmund","Bayer Leverkusen",
    "RB Leipzig","Atletico Madrid","Sevilla","Valencia","Athletic Bilbao",
    "Porto","Benfica","Sporting CP","Galatasaray","Fenerbahce","Besiktas",
    "Ajax","PSV","Feyenoord","Anderlecht","Club Brugge",
    # Americas
    "Flamengo","Palmeiras","Boca Juniors","River Plate",
}

# Derby / rivalry keyword pairs — any match containing both words gets a big boost
DERBY_KEYWORDS = [
    ("manchester","city"),("manchester","united"),
    ("real","barcelona"),("inter","milan"),("ac milan","inter"),
    ("juventus","napoli"),("liverpool","everton"),
    ("arsenal","tottenham"),("celtic","rangers"),
    ("boca","river"),("flamengo","fluminense"),
    ("ajax","psv"),("dortmund","schalke"),("dortmund","leverkusen"),
    ("atletico","real"),("roma","lazio"),
]

def match_importance(m: dict) -> float:
    """
    Returns a score (higher = more important). Used to sort matches
    within a league so the most interesting games appear first.
    Components:
      - League prestige base (inverted so lower prestige rank = higher score)
      - Elite club bonus (+15 per elite team involved)
      - Derby/rivalry bonus (+25)
      - Kickoff time (earlier today = higher, so today's early games stay at top)
    """
    league = m.get("league_name","")
    home   = m.get("match_hometeam_name","")
    away   = m.get("match_awayteam_name","")

    # Base: invert prestige so rank 1 = score 100, rank 46 = score ~55
    prestige_rank = LEAGUE_PRESTIGE.get(league, 50)
    score = 100 - prestige_rank

    # Elite club bonus
    for club in ELITE_CLUBS:
        if club.lower() in home.lower(): score += 15
        if club.lower() in away.lower(): score += 15

    # Derby bonus
    combined = (home + " " + away).lower()
    for w1, w2 in DERBY_KEYWORDS:
        if w1 in combined and w2 in combined:
            score += 25
            break

    # Time bonus — earlier kick-off gets a slight boost so games sort naturally
    try:
        t = m.get("match_time","23:59")
        h, mn = int(t.split(":")[0]), int(t.split(":")[1])
        score += max(0, 10 - (h * 60 + mn) // 60)
    except: pass

    return score


def sort_matches(matches: list) -> list:
    """Sort a list of matches: most important first."""
    return sorted(matches, key=match_importance, reverse=True)


def sort_leagues_and_matches(matches: list) -> list[tuple[str, list]]:
    """
    Returns [(league_name, [sorted_matches]), ...] ordered by prestige.
    Within each league, matches are sorted by importance score.
    """
    league_order = sorted(
        set(m.get("league_name","") for m in matches),
        key=lambda lg: LEAGUE_PRESTIGE.get(lg, 99)
    )
    result = []
    for lg in league_order:
        lg_matches = [m for m in matches if m.get("league_name","") == lg]
        result.append((lg, sort_matches(lg_matches)))
    return result


TIER_CONFIG  = [(2,"SAFE DOUBLE","#16a34a","🟢"),(4,"MODERATE","#eab308","🟡"),(6,"AGGRESSIVE","#f97316","🟠"),(8,"SYSTEM ACCA","#dc2626","🔴"),(12,"WHALE TIER","#9333ea","🟣"),(15,"QUANT JACKPOT","#2563eb","🔵"),(18,"THE GAUNTLET","#ea580c","🔥"),(25,"MOONSHOT","#6b21a8","🌌")]
ODDS_LABELS  = ["2.0×","5.0×","10.0×","20.0×","100.0×","250.0×","500.0×","1000.0×+"]

# ── HELPERS ──────────────────────────────────────────────────────────────────
def safe_num(v):
    if v is None: return 0.0
    try: return float(str(v).replace("%","").strip())
    except: return 0.0

def is_live_status(s):
    s=str(s).strip()
    return s in LIVE_STATUSES or (s.isdigit() and 1<=int(s)<=120)

def is_finished(s):
    return str(s).strip() in FINISHED_STATUSES

def is_upcoming(m):
    status=str(m.get("match_status","")).strip()
    if not status or status=="": return True
    if is_finished(status): return False
    if is_live_status(status): return False
    return True

def sportsbook_tier(league):
    if league in SPORTSBOOK_TIER_A: return "A"
    if league in SPORTSBOOK_TIER_B: return "B"
    if league in SPORTSBOOK_TIER_C: return "C"
    return "?"

def implied_prob(odds):
    return 1.0/odds if odds>1.0 else 1.0

def kelly_fraction(win_prob, odds, divisor=4.0):
    b=odds-1.0; q=1.0-win_prob
    k=(b*win_prob-q)/b
    return round(max(0.0,k/divisor)*100,2)

def edge_percent(model_prob, odds):
    return round((model_prob-implied_prob(odds))*100,2)

def conf_to_prob(conf):
    return min(0.97,(conf/100)*0.82)

# ── DATA FETCHING ─────────────────────────────────────────────────────────────

# ═════════════════════════════════════════════════════════════════════════════
#  WEATHER INTELLIGENCE ENGINE
#
#  Source: Open-Meteo API (free, no key required, highly accurate)
#  https://api.open-meteo.com — returns hourly forecasts by lat/lon
#
#  How weather affects each market:
#
#  RAIN (precipitation > 2mm/hr):
#    goals    × 0.90  — wet ball, harder finishing, more defensive errors
#    corners  × 1.12  — slippery pitch → more clearances → more corners
#    cards    × 1.10  — more sliding tackles on wet surface
#    sot      × 0.88  — less accurate shooting in rain
#    conf_bonus: +3pts for Under goals, +3pts for Over corners in heavy rain
#
#  STRONG WIND (windspeed > 30 km/h):
#    goals    × 0.92  — aerial duels unpredictable, crossing impossible
#    corners  × 0.88  — set pieces fail, teams go more direct (fewer corners)
#    cards    × 1.05  — frustration from disrupted play
#    sot      × 0.85  — shots off target in wind
#    conf_bonus: +4pts for Under goals, +4pts for Under corners in strong wind
#
#  EXTREME HEAT (temp > 30°C):
#    goals    × 0.93  — 2nd half fatigue, game slows significantly
#    corners  × 0.95  — less pressing in heat
#    cards    × 1.12  — player frustration, heat-related aggression
#    sot      × 0.92  — less energy for shooting runs
#
#  COLD/FREEZING (temp < 2°C):
#    goals    × 1.06  — goalkeeper errors more common, cold hands
#    corners  × 1.05  — more cleared balls, more corners
#    cards    × 0.95  — players more cautious on hard pitch
#    sot      × 1.04  — goalkeepers less agile
#
#  IDEAL CONDITIONS (dry, 8-22°C, wind < 20 km/h):
#    All multipliers = 1.0 (no adjustment)
#    conf_bonus: +2pts — conditions don't introduce variance
#
#  INDOOR/COVERED STADIUMS → weather fetch skipped entirely
# ═════════════════════════════════════════════════════════════════════════════

# ── STADIUM COORDINATE DATABASE ───────────────────────────────────────────────
# lat/lon for major stadia. Used to fetch hyperlocal weather for the exact venue.
# For unlisted stadia, we fall back to team city coordinates.
STADIUM_COORDS = {
    # ── Premier League ────────────────────────────────────────────────────────
    "Manchester City":      (53.4831, -2.2004),   # Etihad
    "Manchester United":    (53.4631, -2.2913),   # Old Trafford
    "Liverpool":            (53.4308, -2.9608),   # Anfield
    "Arsenal":              (51.5549, -0.1084),   # Emirates
    "Chelsea":              (51.4816, -0.1910),   # Stamford Bridge
    "Tottenham":            (51.6042, -0.0665),   # Tottenham Hotspur Stadium
    "Newcastle":            (54.9756, -1.6217),   # St James Park
    "West Ham":             (51.5386, -0.0164),   # London Stadium
    "Aston Villa":          (52.5090, -1.8847),   # Villa Park
    "Brighton":             (50.8618, -0.0834),   # Amex
    "Fulham":               (51.4750, -0.2211),   # Craven Cottage
    "Brentford":            (51.4907, -0.3088),   # Gtech
    "Crystal Palace":       (51.3983, -0.0854),   # Selhurst Park
    "Everton":              (53.4388, -2.9661),   # Goodison
    "Wolves":               (52.5904, -2.1302),   # Molineux
    "Leicester":            (52.6204, -1.1420),   # King Power
    "Southampton":          (50.9058, -1.3914),   # St Marys
    "Nottingham Forest":    (52.9400, -1.1326),   # City Ground
    "Ipswich":              (52.0552, 1.1451),    # Portman Road
    # ── La Liga ───────────────────────────────────────────────────────────────
    "Real Madrid":          (40.4530, -3.6883),   # Bernabeu
    "Barcelona":            (41.3809, 2.1228),    # Camp Nou / Estadi Olimpic
    "Atletico Madrid":      (40.4361, -3.5994),   # Metropolitano
    "Athletic Bilbao":      (43.2641, -2.9494),   # San Mames
    "Real Sociedad":        (43.3015, -1.9731),   # Reale Arena
    "Sevilla":              (37.3839, -5.9706),   # Ramon Sanchez Pizjuan
    "Valencia":             (39.4745, -0.3583),   # Mestalla
    "Villarreal":           (39.9444, -0.1038),   # Ceramica
    # ── Bundesliga ────────────────────────────────────────────────────────────
    "Bayern Munich":        (48.2188, 11.6247),   # Allianz Arena
    "Borussia Dortmund":    (51.4926, 7.4517),    # Signal Iduna
    "Bayer Leverkusen":     (51.0380, 7.0024),    # BayArena
    "RB Leipzig":           (51.3457, 12.3483),   # Red Bull Arena
    "Eintracht Frankfurt":  (50.0687, 8.6454),    # Deutsche Bank Park
    "Freiburg":             (47.9894, 7.8993),    # Europa Park Stadion
    # ── Serie A ───────────────────────────────────────────────────────────────
    "Inter Milan":          (45.4781, 9.1240),    # San Siro
    "AC Milan":             (45.4781, 9.1240),    # San Siro
    "Juventus":             (45.1096, 7.6412),    # Allianz Stadium
    "Napoli":               (40.8279, 14.1930),   # Maradona
    "Roma":                 (41.9340, 12.4547),   # Olimpico
    "Lazio":                (41.9340, 12.4547),   # Olimpico
    "Atalanta":             (45.7086, 9.6803),    # Gewiss Stadium
    "Fiorentina":           (43.7806, 11.2822),   # Artemio Franchi
    # ── Ligue 1 ───────────────────────────────────────────────────────────────
    "PSG":                  (48.8414, 2.2530),    # Parc des Princes
    "Paris Saint Germain":  (48.8414, 2.2530),
    "Marseille":            (43.2696, 5.3959),    # Velodrome
    "Lyon":                 (45.7653, 4.9822),    # Groupama
    "Monaco":               (43.7274, 7.4154),    # Stade Louis II
    "Lille":                (50.6120, 3.1303),    # Pierre Mauroy
    "Nice":                 (43.7050, 7.2592),    # Allianz Riviera
    # ── Champions League / European ───────────────────────────────────────────
    "Celtic":               (55.8497, -4.2053),   # Celtic Park — Glasgow very rainy
    "Rangers":              (55.8508, -4.3094),   # Ibrox
    "Ajax":                 (52.3143, 4.9420),    # Johan Cruyff ArenA (partial roof)
    "PSV":                  (51.4416, 5.4674),    # Philips Stadion
    "Feyenoord":            (51.8938, 4.5231),    # De Kuip
    "Porto":                (41.1616, -8.5834),   # Estadio do Dragao
    "Benfica":              (38.7521, -9.1845),   # Estadio da Luz
    "Sporting CP":          (38.7614, -9.1589),   # Jose Alvalade
    "Galatasaray":          (41.0699, 29.0100),   # RAMS Park
    "Fenerbahce":           (41.0137, 29.0343),   # Sukru Saracoglu
    # ── Nordic (high weather variance) ───────────────────────────────────────
    "Rosenborg":            (63.4225, 10.3927),
    "Brann":                (60.3613, 5.3442),    # Bergen — one of Europe's rainiest cities
    "Bodo/Glimt":           (67.2898, 14.3742),   # Arctic Norway
    "IFK Gothenburg":       (57.6964, 11.9861),
    "Malmo FF":             (55.5526, 13.0618),
    "AIK":                  (59.3726, 17.9513),
    # ── Americas ──────────────────────────────────────────────────────────────
    "Flamengo":             (-22.9122, -43.2302), # Maracana
    "Fluminense":           (-22.9122, -43.2302),
    "Palmeiras":            (-23.5454, -46.6741),
    "Boca Juniors":         (-34.6358, -58.3645),
    "River Plate":          (-34.5454, -58.4498),
    # ── City fallbacks (used when team not listed above) ──────────────────────
    "_London":              (51.5074, -0.1278),
    "_Manchester":          (53.4808, -2.2426),
    "_Birmingham":          (52.4862, -1.8904),
    "_Leeds":               (53.8008, -1.5491),
    "_Glasgow":             (55.8642, -4.2518),
    "_Barcelona_city":      (41.3851, 2.1734),
    "_Madrid":              (40.4168, -3.7038),
    "_Munich":              (48.1351, 11.5820),
    "_Berlin":              (52.5200, 13.4050),
    "_Milan_city":          (45.4654, 9.1859),
    "_Rome":                (41.9028, 12.4964),
    "_Paris":               (48.8566, 2.3522),
    "_Amsterdam":           (52.3676, 4.9041),
    "_Lisbon":              (38.7169, -9.1395),
    "_Istanbul":            (41.0082, 28.9784),
    "_Stockholm":           (59.3293, 18.0686),
    "_Oslo":                (59.9139, 10.7522),
    "_Copenhagen":          (55.6761, 12.5683),
    "_Helsinki":            (60.1699, 24.9384),
    "_Buenos_Aires":        (-34.6037, -58.3816),
    "_Sao_Paulo":           (-23.5505, -46.6333),
    "_Rio":                 (-22.9068, -43.1729),
}

# Stadiums that are indoor/domed or have roof coverage — skip weather fetch
COVERED_STADIUMS = {
    "Tottenham",           # retractable roof
    "Manchester City",     # partial — counted as open
}

# City → coordinates mapping for team name fuzzy lookup
CITY_COORDS = {
    "london":      (51.5074, -0.1278),
    "manchester":  (53.4808, -2.2426),
    "liverpool":   (53.4084, -2.9916),
    "birmingham":  (52.4862, -1.8904),
    "newcastle":   (54.9783, -1.6178),
    "glasgow":     (55.8642, -4.2518),
    "edinburgh":   (55.9533, -3.1883),
    "madrid":      (40.4168, -3.7038),
    "barcelona":   (41.3851, 2.1734),
    "seville":     (37.3891, -5.9845),
    "munich":      (48.1351, 11.5820),
    "berlin":      (52.5200, 13.4050),
    "dortmund":    (51.5136, 7.4653),
    "milan":       (45.4654, 9.1859),
    "rome":        (41.9028, 12.4964),
    "naples":      (40.8518, 14.2681),
    "paris":       (48.8566, 2.3522),
    "amsterdam":   (52.3676, 4.9041),
    "lisbon":      (38.7169, -9.1395),
    "porto":       (41.1579, -8.6291),
    "istanbul":    (41.0082, 28.9784),
    "stockholm":   (59.3293, 18.0686),
    "oslo":        (59.9139, 10.7522),
    "copenhagen":  (55.6761, 12.5683),
    "helsinki":    (60.1699, 24.9384),
    "brussels":    (50.8503, 4.3517),
    "vienna":      (48.2082, 16.3738),
    "zurich":      (47.3769, 8.5417),
    "warsaw":      (52.2297, 21.0122),
    "prague":      (50.0755, 14.4378),
    "belgrade":    (44.8176, 20.4633),
    "athens":      (37.9838, 23.7275),
    "buenos aires":(-34.6037,-58.3816),
    "sao paulo":   (-23.5505,-46.6333),
    "rio":         (-22.9068,-43.1729),
    "buenos":      (-34.6037,-58.3816),
}


def get_stadium_coords(home_team: str) -> tuple | None:
    """Return (lat, lon) for a home team's stadium, or None if unknown."""
    # Direct lookup
    for team_key, coords in STADIUM_COORDS.items():
        if team_key.lower() in home_team.lower() or home_team.lower() in team_key.lower():
            return coords
    # City fuzzy lookup
    home_lower = home_team.lower()
    for city, coords in CITY_COORDS.items():
        if city in home_lower:
            return coords
    return None


@st.cache_data(ttl=1800, show_spinner=False)  # 30-min cache — forecast stable
def fetch_weather(lat: float, lon: float, match_date: str, match_time: str) -> dict:
    """
    Fetch hourly weather forecast from Open-Meteo for a specific lat/lon, date and time.
    Returns dict with: temp_c, rain_mm, windspeed_kmh, condition, desc
    Free API, no key required.
    """
    try:
        # Parse match datetime
        hour = int(match_time.split(":")[0]) if match_time else 15
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,precipitation,windspeed_10m,weathercode"
            f"&start_date={match_date}&end_date={match_date}"
            f"&timezone=auto&windspeed_unit=kmh"
        )
        res = requests.get(url, timeout=8).json()
        hourly = res.get("hourly", {})
        times  = hourly.get("time", [])
        temps  = hourly.get("temperature_2m", [])
        rain   = hourly.get("precipitation", [])
        wind   = hourly.get("windspeed_10m", [])
        codes  = hourly.get("weathercode", [])

        # Find the hour closest to match kickoff
        target = f"{match_date}T{hour:02d}:00"
        idx = 0
        for i, t in enumerate(times):
            if t >= target:
                idx = i
                break

        temp_c     = temps[idx]  if temps  else 15.0
        rain_mm    = rain[idx]   if rain   else 0.0
        wind_kmh   = wind[idx]   if wind   else 10.0
        wcode      = codes[idx]  if codes  else 0

        # WMO weather code → human label
        if wcode == 0:            condition = "clear"
        elif wcode in range(1,4): condition = "partly cloudy"
        elif wcode in range(45,68):condition = "foggy"
        elif wcode in range(51,68):condition = "drizzle"
        elif wcode in range(61,68):condition = "rain"
        elif wcode in range(71,78):condition = "snow"
        elif wcode in range(80,83):condition = "showers"
        elif wcode in range(95,100):condition = "thunderstorm"
        else:                     condition = "cloudy"

        return {
            "temp_c":    round(temp_c, 1),
            "rain_mm":   round(rain_mm, 1),
            "wind_kmh":  round(wind_kmh, 1),
            "condition": condition,
            "available": True,
        }
    except Exception:
        return {"available": False}


def compute_weather_impact(weather: dict) -> dict:
    """
    Translate weather conditions into market multipliers and confidence adjustments.
    Returns dict: g_mult, c_mult, k_mult, s_mult, conf_bonus, desc, badge_html
    """
    if not weather.get("available"):
        return {
            "g_mult":1.0,"c_mult":1.0,"k_mult":1.0,"s_mult":1.0,
            "conf_bonus":0.0,"desc":"Weather unavailable","badge_html":"",
            "available":False
        }

    temp   = weather["temp_c"]
    rain   = weather["rain_mm"]
    wind   = weather["wind_kmh"]
    cond   = weather["condition"]

    g_mult = c_mult = k_mult = s_mult = 1.0
    conf_bonus = 0.0
    factors = []

    # ── RAIN ─────────────────────────────────────────────────────────────────
    if rain >= 5.0:        # heavy rain
        g_mult  *= 0.88; c_mult *= 1.15; k_mult *= 1.12; s_mult *= 0.85
        conf_bonus += 3.0  # Under goals and Over corners both get edge
        factors.append(f"🌧️ Heavy rain ({rain}mm)")
    elif rain >= 2.0:      # moderate rain
        g_mult  *= 0.93; c_mult *= 1.08; k_mult *= 1.06; s_mult *= 0.91
        conf_bonus += 1.5
        factors.append(f"🌦️ Rain ({rain}mm)")
    elif rain >= 0.5:      # light rain / drizzle
        g_mult  *= 0.97; c_mult *= 1.03; k_mult *= 1.02; s_mult *= 0.97
        factors.append(f"🌦️ Drizzle ({rain}mm)")

    # ── WIND ─────────────────────────────────────────────────────────────────
    if wind >= 45:         # severe wind
        g_mult  *= 0.88; c_mult *= 0.82; k_mult *= 1.08; s_mult *= 0.80
        conf_bonus += 4.0  # Under goals + Under corners both strengthened
        factors.append(f"💨 Severe wind ({wind}km/h)")
    elif wind >= 30:       # strong wind
        g_mult  *= 0.93; c_mult *= 0.90; k_mult *= 1.05; s_mult *= 0.87
        conf_bonus += 2.5
        factors.append(f"💨 Strong wind ({wind}km/h)")
    elif wind >= 20:       # moderate wind
        g_mult  *= 0.97; c_mult *= 0.96; s_mult *= 0.95
        factors.append(f"🌬️ Windy ({wind}km/h)")

    # ── TEMPERATURE ──────────────────────────────────────────────────────────
    if temp >= 32:         # extreme heat
        g_mult  *= 0.91; k_mult *= 1.15; s_mult *= 0.90; c_mult *= 0.94
        conf_bonus += 2.0
        factors.append(f"🌡️ Extreme heat ({temp}°C)")
    elif temp >= 27:       # hot
        g_mult  *= 0.95; k_mult *= 1.08; s_mult *= 0.94
        conf_bonus += 1.0
        factors.append(f"☀️ Hot ({temp}°C)")
    elif temp <= 0:        # freezing
        g_mult  *= 1.06; c_mult *= 1.05; k_mult *= 0.94; s_mult *= 1.04
        conf_bonus += 1.5
        factors.append(f"🧊 Freezing ({temp}°C)")
    elif temp <= 5:        # cold
        g_mult  *= 1.03; c_mult *= 1.03; k_mult *= 0.97; s_mult *= 1.02
        factors.append(f"❄️ Cold ({temp}°C)")
    elif 10 <= temp <= 22 and rain < 1 and wind < 20:
        # Perfect conditions — slight confidence boost (less variance)
        conf_bonus += 2.0
        factors.append(f"✅ Ideal conditions ({temp}°C)")

    # Clamp all multipliers
    g_mult = round(max(0.75, min(1.20, g_mult)), 3)
    c_mult = round(max(0.75, min(1.25, c_mult)), 3)
    k_mult = round(max(0.85, min(1.25, k_mult)), 3)
    s_mult = round(max(0.75, min(1.15, s_mult)), 3)
    conf_bonus = round(max(-5.0, min(6.0, conf_bonus)), 1)

    desc = " · ".join(factors) if factors else f"☁️ {cond.title()} ({temp}°C)"

    # Build badge HTML
    if rain >= 2 or wind >= 30 or temp >= 30 or temp <= 2:
        badge_color = "#f97316"; badge_bg = "rgba(249,115,22,.12)"
        badge_icon = "⚠️"
    elif rain >= 0.5 or wind >= 20:
        badge_color = "#fbbf24"; badge_bg = "rgba(251,191,36,.1)"
        badge_icon = "🌦️"
    else:
        badge_color = "#4ade80"; badge_bg = "rgba(74,222,128,.1)"
        badge_icon = "✅"

    badge_html = (
        f"<span style='display:inline-block;background:{badge_bg};color:{badge_color};"
        f"border:1px solid {badge_color}40;padding:3px 10px;border-radius:20px;"
        f"font-size:11px;font-family:DM Mono,monospace;font-weight:700;margin-top:6px;'>"
        f"{badge_icon} {weather['condition'].title()} · {temp}°C · "
        f"💨{wind}km/h · 🌧️{rain}mm</span>"
    )

    return {
        "g_mult": g_mult, "c_mult": c_mult,
        "k_mult": k_mult, "s_mult": s_mult,
        "conf_bonus": conf_bonus,
        "desc": desc, "badge_html": badge_html,
        "available": True,
        "temp": temp, "rain": rain, "wind": wind,
    }

@st.cache_data(ttl=1800,show_spinner=False)  # 30 min cache
def fetch_stats(team_id,venue):
    _ak=st.session_state.get("user_api_key") or st.secrets.get("APIFOOTBALL_KEY","") or _DEFAULT_KEY
    url=f"https://apiv3.apifootball.com/?action=get_events&team_id={team_id}&from={past_str}&to={today_str}&APIkey={_ak}"
    try:
        res=requests.get(url,timeout=10).json()
        s={"gf":0,"ga":0,"cf":0,"ca":0,"sotf":0,"sota":0,"shotsf":0,"shotsa":0,"cards":0,"cnt":0}
        if not isinstance(res,list): return None,0
        id_key="match_hometeam_id" if venue=="home" else "match_awayteam_id"
        finished=[m for m in res if m.get("match_status")=="Finished" and m.get(id_key)==team_id][-8:]
        for m in finished:
            is_h=m.get("match_hometeam_id")==team_id
            s["gf"]+=safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
            s["ga"]+=safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
            for row in m.get("statistics",[]):
                t_val=safe_num(row.get("home" if is_h else "away"))
                o_val=safe_num(row.get("away" if is_h else "home"))
                stype=row.get("type")
                if stype=="Corners": s["cf"]+=t_val;s["ca"]+=o_val
                elif stype=="Yellow Cards": s["cards"]+=t_val
                elif stype=="Shots On Goal": s["sotf"]+=t_val;s["sota"]+=o_val
                elif stype=="Shots Total": s["shotsf"]+=t_val;s["shotsa"]+=o_val
            s["cnt"]+=1
        n=s["cnt"]
        return {k:(v/n if n else 0) for k,v in s.items() if k!="cnt"},n
    except: return None,0

@st.cache_data(ttl=300,show_spinner=False)
def fetch_lineups_for_match(match_id: str) -> set:
    """
    Fetch confirmed starting lineup names for a match.
    Returns a set of player name strings (empty set if not yet available).
    Cached 5 minutes — lineups change close to kickoff.
    """
    _ak2=st.session_state.get("user_api_key") or st.secrets.get("APIFOOTBALL_KEY","") or _DEFAULT_KEY
    url = f"https://apiv3.apifootball.com/?action=get_lineups&match_id={match_id}&APIkey={_ak2}"
    try:
        res = requests.get(url, timeout=8).json()
        names = set()
        # API returns dict keyed by match_id or a list
        data = res.get(str(match_id), res) if isinstance(res, dict) else {}
        for side in ["lineup_home","lineup_away"]:
            side_data = data.get(side, {})
            if isinstance(side_data, dict):
                for pos_group in side_data.values():
                    if isinstance(pos_group, list):
                        for p in pos_group:
                            n = p.get("player","") if isinstance(p,dict) else str(p)
                            if n: names.add(n.strip())
        return names
    except:
        return set()


@st.cache_data(ttl=900,show_spinner=False)  # 15 min cache
def fetch_events(date_from, date_to):
    # Always use current key (may have been updated in sidebar)
    _active_key = (
        st.session_state.get("user_api_key")
        or st.secrets.get("APIFOOTBALL_KEY", "")
        or _DEFAULT_KEY
    )
    url = f"https://apiv3.apifootball.com/?action=get_events&from={date_from}&to={date_to}&APIkey={_active_key}"
    try:
        resp = requests.get(url, timeout=15)
        res  = resp.json()

        # ── Detect API errors before processing ──────────────────────────
        if isinstance(res, dict):
            err = res.get("error", "") or res.get("message", "") or str(res)
            st.session_state["api_error"] = f"API returned error: {err}"
            return []

        if not isinstance(res, list):
            st.session_state["api_error"] = f"Unexpected API response type: {type(res)}"
            return []

        if len(res) == 0:
            st.session_state["api_error"] = (
                f"API returned 0 matches for {date_from}→{date_to}. "
                "Possible causes: API rate limit exceeded, no matches scheduled, or API key issue."
            )
            return []

        # Clear any previous error
        st.session_state.pop("api_error", None)

        out = []
        for m in res:
            raw_lg = m.get("league_name", "")
            canon  = canonical_league(raw_lg)
            if canon != "__BLOCKED__" and canon in TOP_LEAGUES:
                _continental = any(kw in canon for kw in
                    ("UEFA","Copa","CONMEBOL","Recopa","Europa","Champions","Conference"))
                if not _continental:
                    home_t = m.get("match_hometeam_name","")
                    away_t = m.get("match_awayteam_name","")
                    if is_team_blocked(home_t, away_t):
                        continue
                m["league_name"] = canon
                out.append(m)

        if len(out) == 0 and len(res) > 0:
            # API returned matches but ALL were filtered — useful diagnostic
            raw_leagues = sorted(set(m.get("league_name","") for m in res))
            st.session_state["api_filter_warn"] = (
                f"API returned {len(res)} matches but all were filtered. "
                f"Raw leagues: {', '.join(raw_leagues[:10])}"
            )
        else:
            st.session_state.pop("api_filter_warn", None)

        return out

    except requests.exceptions.Timeout:
        st.session_state["api_error"] = "API request timed out. Check your internet connection."
        return []
    except Exception as e:
        st.session_state["api_error"] = f"API fetch error: {str(e)}"
        return []

# ── EDGE ENGINE ───────────────────────────────────────────────────────────────
def generate_ai_pick(h_st,a_st,league,sniper_mode=False,h_cnt=5,a_cnt=5,**kwargs):
    gm,cm,kdm,pen = LEAGUE_PROFILE.get(league,DEFAULT_PROFILE)
    markets  = available_markets(league)
    g_mult   = kwargs.get('g_mult',   1.0)
    c_mult   = kwargs.get('c_mult',   1.0)
    k_mult   = kwargs.get('k_mult',   1.0)
    s_mult   = kwargs.get('s_mult',   1.0)
    ib       = kwargs.get('intel_bonus', 0.0)
    # Weather multipliers stacked on top of player intel
    wg = kwargs.get('w_g_mult', 1.0)
    wc = kwargs.get('w_c_mult', 1.0)
    wk = kwargs.get('w_k_mult', 1.0)
    ws = kwargs.get('w_s_mult', 1.0)
    wb = kwargs.get('w_conf_bonus', 0.0)
    g_mult *= wg; c_mult *= wc; k_mult *= wk; s_mult *= ws; ib += wb

    # ── HOME / AWAY VENUE WEIGHTING ─────────────────────────────────────────
    # h_st = home team's stats IN HOME GAMES (already venue-split by fetch_stats)
    # a_st = away team's stats IN AWAY GAMES (already venue-split by fetch_stats)
    # We apply league-specific HA multipliers to each side separately,
    # then combine. This means a strong home team playing at home gets
    # their home boost AND the away team gets their away penalty.
    hG, aG, hC, aC_card, ha_str = get_ha_profile(league)

    # Goals: home team attack × home boost + away team attack × away drop
    # Formula: weighted average of expected goals from each side
    proj_g_home = (h_st['gf'] * hG + a_st['ga'] * hG) / 2   # home team scoring
    proj_g_away = (a_st['gf'] * aG + h_st['ga'] * aG) / 2   # away team scoring
    proj_g = (proj_g_home + proj_g_away) * gm * g_mult

    # Corners: home teams win more corners (attacking intent + crowd pressure)
    proj_c_home = (h_st['cf'] * hC + a_st['ca'] * hC) / 2
    proj_c_away = (a_st['cf'] + h_st['ca']) / 2              # away side unaffected
    proj_c_raw  = (proj_c_home + proj_c_away) * cm * c_mult
    proj_c      = min(proj_c_raw, 12.0)

    # SOT: follows goal projection shape
    proj_sot = ((h_st['sotf'] * hG + a_st['sota'] * hG) / 2 +
                (a_st['sotf'] * aG + h_st['sota'] * aG) / 2) * s_mult

    # Cards: away team gets significantly more cards in most leagues
    home_cards = h_st['cards'] * kdm              # home team cards (baseline)
    away_cards = a_st['cards'] * kdm * aC_card    # away team gets the penalty
    proj_cd = (home_cards + away_cards) * k_mult

    # Home advantage confidence bonus: when the home team has strong
    # historical home form, slightly boost confidence
    ha_conf_bonus = ha_str * 1.2  # +1.2 to +3.6 pts depending on league
    sigs={
        "Both score form":       h_st['gf']>1.0 and a_st['gf']>0.8,
        "High scoring":          proj_g>=2.8,
        "Low scoring":           proj_g<=2.2,
        "High SOT":              proj_sot>=8.0,
        "Low SOT":               proj_sot<=6.5,
        "High corners":          proj_c>=9.0,
        "Low corners":           proj_c<=8.0,
        "SOT confirms goals":    proj_g>=2.8 and proj_sot>=8.0,
        "SOT confirms under":    proj_g<=2.2 and proj_sot<=6.5,
        # ── Home/Away signals ──────────────────────────────────────────
        "Strong home advantage": ha_str >= 2,
        "Home goals boost":      h_st['gf'] * hG > 1.8,   # home team prolific at home
        "Away card risk":         a_st['cards'] * aC_card > 2.5,  # away team card-prone
        "Away attack suppressed": a_st['gf'] * aG < 0.9,  # away team struggles to score
    }
    base=65.0-pen+max(0.0,ib)+ha_conf_bonus; min_conf=82.0 if sniper_mode else 72.0; plays=[]
    # Sample size penalty — reduce confidence for small samples
    avg_cnt = (h_cnt + a_cnt) / 2
    sample_pen = max(0.0, (5 - avg_cnt) * 4.0)   # -4pts per game below 5-game avg
    base = max(50.0, base - sample_pen)
    # Minimum sample gates: goals need 3 games, exotic markets need 5
    min_sample_goals   = 3
    min_sample_exotic  = 5   # corners, cards, SOT

    if "goals" in markets and avg_cnt >= min_sample_goals:
        if proj_g>=2.8:
            line=3.5 if proj_g>=4.2 else 2.5 if proj_g>=3.2 else 1.5; gap=proj_g-line
            if gap>=0.8:
                conf=min(99.0,base+(gap/max(line,.01))*90)
                if sigs["SOT confirms goals"]:    conf=min(99.0,conf+5)
                if sigs["Both score form"]:        conf=min(99.0,conf+3)
                if sigs["Strong home advantage"]:  conf=min(99.0,conf+2.5)
                if sigs["Home goals boost"]:       conf=min(99.0,conf+2.0)
                plays.append((f"⚽ Over {line} Goals","goals",line,conf,{k:v for k,v in sigs.items() if k in ("SOT confirms goals","Both score form","High corners")}))
        elif proj_g<=2.2:
            line=1.5 if proj_g<=1.2 else 2.5 if proj_g<=1.8 else 3.5; gap=line-proj_g
            if gap>=0.8:
                conf=min(99.0,base+(gap/max(line,.01))*90)
                if sigs["SOT confirms under"]:       conf=min(99.0,conf+5)
                if sigs["Away attack suppressed"]:   conf=min(99.0,conf+3.0)
                plays.append((f"🔒 Under {line} Goals","under_goals",line,conf,{k:v for k,v in sigs.items() if k in ("SOT confirms under","Low corners","Low SOT")}))

    if "corners" in markets and avg_cnt >= min_sample_exotic:
        # ── CORNER ENGINE v3: Player-aware, reality-capped ────────────────────
        #
        # Line philosophy (based on real hit rates):
        #   Over 8.5 corners  → needs 9+  corners → hits ~62% of PL games naturally
        #   Over 9.5 corners  → needs 10+ corners → hits ~50% — needs clear signal
        #   HARD CAP: max Over line = 9.5.  No more 10.5, 11.5, 13.5 nonsense.
        #
        # Player intel gate:
        #   - If lineup available and NO corner-specialist is confirmed playing → SKIP
        #   - If a key corner player is absent → apply absence multiplier, may drop below threshold
        #   - If 2+ corner specialists confirmed playing → confidence bonus

        # proj_c already includes player intel c_mult applied above
        proj_c_adj = proj_c  # already capped at 12.0
        players_confirmed = kwargs.get("lineups_available", False)

        # Player intel is already baked into proj_c_adj and base confidence
        # via the g_mult/c_mult/intel_bonus kwargs applied above.
        # Corner gate: require lineups OR fall back to base stats only
        corner_gate_passed = True   # always attempt; intel already adjusted proj
        corner_base_conf   = base   # intel_bonus already included in base

        # ── OVER CORNERS ──────────────────────────────────────────────────────
        if proj_c_adj >= 9.5 and corner_gate_passed:
            # Offer 8.5 when projection is 9.5–10.9, 9.5 when projection is 11+
            if proj_c_adj >= 11.0:
                line = 9.5
            else:
                line = 8.5
            gap = proj_c_adj - line
            if gap >= 2.0:  # need at least 2.0 margin above line
                conf = min(99.0, corner_base_conf + (gap / max(line, .01)) * 70)
                if sigs["High SOT"]: conf = min(99.0, conf + 4)
                sigs_corner = {k:v for k,v in sigs.items() if k in ("High SOT","High scoring")}
                if c_mult > 1.05:
                    sigs_corner["Player intel boosted"] = True
                plays.append((f"🔥 Over {line} Corners","corners",line,conf,sigs_corner))

        # ── UNDER CORNERS ─────────────────────────────────────────────────────
        elif proj_c_adj <= 7.5:
            # Under 8.5 when projection ≤ 7.5 (plenty of margin)
            line = 8.5
            gap = line - proj_c_adj
            if gap >= 2.0:
                conf = min(99.0, corner_base_conf + (gap / max(line, .01)) * 70)
                if sigs["Low SOT"]: conf = min(99.0, conf + 4)
                # Under corners strengthened when c_mult < 1 (key wide player absent)
                if c_mult < 0.95:
                    conf = min(99.0, conf + (1.0 - c_mult) * 20)
                sigs_corner = {k:v for k,v in sigs.items() if k in ("Low SOT","Low scoring")}
                if c_mult < 0.95:
                    sigs_corner["Key wide player absent"] = True
                plays.append((f"🛡️ Under 8.5 Corners","under_corners",8.5,conf,sigs_corner))

    if "cards" in markets and avg_cnt >= min_sample_exotic:
        if proj_cd>=5.0:
            valid=[l for l in [3.5,4.5,5.5,6.5] if l<=proj_cd-1.5]
            if valid:
                line=max(valid);gap=proj_cd-line;conf=min(99.0,base+(gap/max(line,.01))*55)
                if sigs["Away card risk"]: conf=min(99.0,conf+3.5)  # away team historically card-prone
                if sigs["Strong home advantage"]: conf=min(99.0,conf+2.0)  # referee bias in strong HA leagues
                plays.append((f"🟨 Over {line} Cards","cards",line,conf,{"High card league":kdm>=1.1,"Away card risk":sigs["Away card risk"],"Home advantage":sigs["Strong home advantage"]}))
        elif proj_cd<=2.5:
            valid=[l for l in [3.5,4.5] if l>=proj_cd+1.5]
            if valid:
                line=min(valid);gap=line-proj_cd;conf=min(99.0,base+(gap/max(line,.01))*55)
                plays.append((f"🧊 Under {line} Cards","under_cards",line,conf,{"Low card league":kdm<=0.92}))

    if "sot" in markets and avg_cnt >= min_sample_exotic:
        if proj_sot>=9.0:
            valid=[l for l in [7.5,8.5,9.5,10.5,11.5] if l<=proj_sot-1.8]
            if valid:
                line=max(valid);gap=proj_sot-line;conf=min(99.0,base+(gap/max(line,.01))*65)
                if sigs["High scoring"]: conf=min(99.0,conf+3)
                plays.append((f"🎯 Over {line} SOT","sot",line,conf,{k:v for k,v in sigs.items() if k in ("High scoring","Both score form")}))
        elif proj_sot<=6.0:
            valid=[l for l in [5.5,6.5,7.5] if l>=proj_sot+1.8]
            if valid:
                line=min(valid);gap=line-proj_sot;conf=min(99.0,base+(gap/max(line,.01))*65)
                plays.append((f"🧱 Under {line} SOT","under_sot",line,conf,{"Low scoring":sigs["Low scoring"]}))

    plays=[p for p in plays if p[3]>=min_conf]
    plays.sort(key=lambda x:x[3],reverse=True)
    if plays:
        lbl,pt,ln,cf,sg=plays[0]; return lbl,pt,ln,cf,sg,plays
    return "⚠️ NO PLAY","pass",0,0,{},[]

def check_result(p_type,thresh,match):
    goals=safe_num(match.get("match_hometeam_score","0"))+safe_num(match.get("match_awayteam_score","0"))
    stats={r.get("type"):safe_num(r.get("home",0))+safe_num(r.get("away",0)) for r in match.get("statistics",[])}
    if p_type=="goals":          return goals>thresh
    if p_type=="under_goals":    return goals<thresh
    if p_type=="corners":        return stats.get("Corners",0)>thresh
    if p_type=="under_corners":  return stats.get("Corners",0)<thresh
    if p_type=="cards":          return stats.get("Yellow Cards",0)>thresh
    if p_type=="under_cards":    return stats.get("Yellow Cards",0)<thresh
    if p_type=="sot":            return stats.get("Shots On Goal",0)>thresh
    if p_type=="under_sot":      return stats.get("Shots On Goal",0)<thresh
    return None

# ── HTML HELPERS ──────────────────────────────────────────────────────────────
def conf_bar_html(conf,color="#16a34a"):
    pct=int(conf); c="#ef4444" if pct<72 else "#eab308" if pct<82 else color
    return f"<div class='conf-bar-wrap'><div class='conf-label'>EDGE · {pct}%</div><div class='conf-bar-bg'><div class='conf-bar-fill' style='width:{pct}%;background:{c};'></div></div></div>"

def signals_html(sigs):
    tags="".join(f"<span class='gate-tag {'gate-pass' if v else 'gate-fail'}'>{'✓' if v else '✗'} {k}</span>" for k,v in sigs.items())
    return f"<div style='margin-top:8px;'>{tags}</div>"

def book_tier_badge(tier):
    colors={"A":("#16a34a","#0d2218"),"B":("#eab308","#1a1500"),"C":("#f97316","#1a0800")}
    fc,bg=colors.get(tier,("#64748b","#0d1520"))
    labels={"A":"📚 All Books","B":"📖 Most Books","C":"🔍 Specialist"}
    lbl=labels.get(tier,"❓")
    return f"<span style='font-size:10px;font-weight:700;font-family:DM Mono,monospace;background:{bg};color:{fc};border:1px solid {fc}40;padding:3px 8px;border-radius:10px;'>{lbl}</span>"

def value_panel_html(conf,decimal_odds,kelly_div):
    if decimal_odds<=1.0 or conf==0: return ""
    win_prob=conf_to_prob(conf); book_prob=implied_prob(decimal_odds)
    edge=edge_percent(win_prob,decimal_odds); kelly=kelly_fraction(win_prob,decimal_odds,kelly_div)
    edge_cls="positive-edge" if edge>2 else "negative-edge" if edge<-2 else "neutral-edge"
    kelly_cls="kelly-strong" if kelly>=2 else "kelly-moderate" if kelly>0 else "kelly-skip"
    kelly_txt=f"{kelly:.1f}% of bankroll" if kelly>0 else "SKIP — No edge"
    return f"""<div class='value-card'><div class='value-title'>⚡ SPORTSBOOK EDGE ANALYSIS</div>
    <div class='value-row'><span>Book odds entered</span><span class='value-num'>{decimal_odds:.2f}</span></div>
    <div class='value-row'><span>Book implied prob</span><span class='value-num'>{book_prob*100:.1f}%</span></div>
    <div class='value-row'><span>Model win prob</span><span class='value-num'>{win_prob*100:.1f}%</span></div>
    <div class='value-row'><span>Your edge vs book</span><span class='value-num {edge_cls}'>{edge:+.1f}%</span></div>
    <div style='margin-top:8px;text-align:center;'><span class='kelly-badge {kelly_cls}'>🎯 Stake: {kelly_txt}</span></div></div>"""

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Terminal")
    st.markdown(f"<div style='font-family:DM Mono,monospace;font-size:11px;color:#475569;'>DATE · {today_str} · {now.strftime('%H:%M')} UTC+1</div>",unsafe_allow_html=True)
    st.divider()
    # ── API Key (shows expanded when error) ──────────────────────
    _has_err = bool(st.session_state.get("api_error",""))
    with st.expander("🔑 API Key" + (" ⚠️" if _has_err else ""), expanded=_has_err):
        st.markdown("<div style='font-size:11px;color:#64748b;'>"  
                    "Free key at <a href='https://apifootball.com' target='_blank' "
                    "style='color:#60a5fa;'>apifootball.com</a> · 100 req/day</div>",
                    unsafe_allow_html=True)
        _new_key = st.text_input("API Key", type="password",
                                  value=st.session_state.get("user_api_key",""),
                                  placeholder="Paste your key here")
        if _new_key and _new_key != st.session_state.get("user_api_key",""):
            st.session_state["user_api_key"] = _new_key
            st.cache_data.clear()
            st.session_state.pop("api_error", None)
            st.rerun()
        if "404" in st.session_state.get("api_error",""):
            st.markdown("<div style='font-size:11px;color:#f87171;margin-top:6px;'>"
                        "🔴 404 = key invalid/expired. Get new key above.</div>",
                        unsafe_allow_html=True)
    st.divider()
    sniper_mode=st.toggle("🎯 Sniper Mode (82%+)",value=False)
    if sniper_mode:
        st.markdown("<div style='background:#1a0a00;border:1px solid #f97316;border-radius:8px;padding:10px;font-size:12px;color:#fb923c;'>⚡ Ultra-high-confidence only.</div>",unsafe_allow_html=True)
    st.divider()
    st.markdown("**📚 Book Coverage Filter**")
    tier_a=st.checkbox("Tier A — All Books",value=True)
    tier_b=st.checkbox("Tier B — Most Books",value=True)
    tier_c=st.checkbox("Tier C — Specialist Books",value=False)
    if tier_c:
        st.markdown("<div style='background:rgba(249,115,22,.08);border:1px solid rgba(249,115,22,.25);border-radius:6px;padding:8px 10px;font-size:11px;color:#fb923c;margin-top:4px;'>⚠️ Tier C games may not appear on major books (Betano, Bet365, Betway). Accuracy stats may be inflated.</div>",unsafe_allow_html=True)
    st.divider()
    st.divider()
    st.markdown("**🟨 Card Counting System**")
    card_mode = st.radio(
        "Your book's card system",
        ["both","points","yellow"],
        format_func=lambda x: {
            "both":"Show both systems",
            "points":"🟠 Card Points — Betano (Y=1, R=2)",
            "yellow":"🟡 Raw Yellow Cards",
        }[x],
        index=0)
    st.session_state["card_mode"] = card_mode
    st.divider()
    st.markdown("**💰 Kelly Calculator**")
    kelly_divisor=st.slider("Kelly fraction (safety)",2,8,4)
    bankroll=st.number_input("Bankroll",min_value=10.0,value=1000.0,step=50.0)
    st.divider()
    # API quota warning
    _api_e = st.session_state.get("api_error","")
    if _api_e:
        st.markdown(f"<div style='background:#2d0a0a;border:1px solid #ef4444;"
                    f"border-radius:6px;padding:8px;font-size:11px;color:#fca5a5;"
                    f"margin-bottom:8px;'>⚠️ API issue detected</div>",unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px;color:#334d66;'>"
        "💡 Free API key: ~100 calls/day. "
        "If seeing 0 matches, key may be rate-limited.</div>",unsafe_allow_html=True)
    with st.expander("🔍 League Debug", expanded=False):
        st.markdown("<div style='font-size:11px;color:#475569;'>Shows raw league names from API to diagnose filtering</div>",unsafe_allow_html=True)
        if st.button("Run League Audit", use_container_width=True):
            import requests as _rq
            _url = f"https://apiv3.apifootball.com/?action=get_events&from={today_str}&to={today_str}&APIkey={API_KEY}"
            try:
                _raw = _rq.get(_url, timeout=10).json()
                if isinstance(_raw, list):
                    _leagues = sorted(set(m.get("league_name","") for m in _raw))
                    _copa = [l for l in _leagues if any(k in l.lower() for k in ("libertadores","sudamericana","copa","conmebol"))]
                    st.markdown("**Copa leagues found:**")
                    for l in _copa: st.code(l)
                    st.markdown(f"**Total leagues in API today:** {len(_leagues)}")
                    with st.expander("All leagues"):
                        for l in _leagues: st.text(l)
            except Exception as e:
                st.error(f"API error: {e}")
    if st.button("🧹 Refresh Cache",use_container_width=True):
        st.cache_data.clear(); st.rerun()
    live_refresh=st.toggle("🔴 Live Auto-Refresh (60s)",value=False)
    if live_refresh: st.success("🟢 LIVE MODE")
    st.divider()
    st.markdown("<div style='font-size:11px;color:#334155;'>⚠️ Research only. Not financial advice.</div>",unsafe_allow_html=True)

ACTIVE_LEAGUES=set()
if tier_a: ACTIVE_LEAGUES|=SPORTSBOOK_TIER_A
if tier_b: ACTIVE_LEAGUES|=SPORTSBOOK_TIER_B
if tier_c: ACTIVE_LEAGUES|=SPORTSBOOK_TIER_C

# STRICT_BOOKABLE = leagues reliably on Bet365 + Betway + Betano with full markets.
# Used in accuracy tab to avoid inflating win rate with unbettable games.
STRICT_BOOKABLE = {
    "Premier League","Serie A","La Liga","Bundesliga","Ligue 1",
    "UEFA Champions League","UEFA Europa League","UEFA Europa Conference League",
    "Championship","Eredivisie","Primeira Liga","Süper Lig",
    "Scottish Premiership","Scottish Premier League",
    "Belgian Pro League","Belgian First Division A",
    "Swiss Super League","Austrian Football Bundesliga","Austrian Bundesliga",
    "Allsvenskan","Eliteserien","Superliga",
    "Major League Soccer","Brasileirao Serie A","Argentine Primera División",
    "Copa Libertadores","Copa Sudamericana","CONMEBOL Libertadores","CONMEBOL Sudamericana",
}

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>🏦 Institutional Quant Radar</div>",unsafe_allow_html=True)
mode_tag="🎯 SNIPER" if sniper_mode else "STANDARD"
st.markdown(f"<div class='page-sub'>ALGORITHMIC EDGE · {len(ACTIVE_LEAGUES)} LEAGUES · {mode_tag} MODE · UPCOMING ONLY</div>",unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Fetching fixtures…"):
    raw_daily    = fetch_events(today_str,    today_str)
    raw_tomorrow = fetch_events(tomorrow_str,  tomorrow_str)
    raw_weekly   = fetch_events(today_str,     week_out_str)

daily_matches    = [m for m in raw_daily    if m.get("league_name") in ACTIVE_LEAGUES and is_upcoming(m)]
daily_live       = [m for m in raw_daily    if m.get("league_name") in ACTIVE_LEAGUES and is_live_status(m.get("match_status",""))]
daily_finished   = [m for m in raw_daily    if m.get("league_name") in ACTIVE_LEAGUES and is_finished(m.get("match_status",""))]
tomorrow_matches = [m for m in raw_tomorrow if m.get("league_name") in ACTIVE_LEAGUES and is_upcoming(m)]
weekly_matches   = [m for m in raw_weekly   if m.get("league_name") in ACTIVE_LEAGUES and is_upcoming(m)]

# ── CLICKABLE NAVIGATION STATS BAR ──────────────────────────────────────────
# Clicking a card sets session_state["nav_view"] which controls Tab 3 display
if "nav_view" not in st.session_state:
    # Smart default: if most today's games are finished, show Tomorrow
    _today_remaining = len(daily_matches)
    _today_done      = len(daily_finished)
    if _today_remaining == 0 and _today_done > 0 and len(tomorrow_matches) > 0:
        st.session_state["nav_view"] = "📅 Tomorrow"
    else:
        st.session_state["nav_view"] = "⏳ Today (Upcoming)"

def nav_card(col, icon, label, count, view_key, active_color="#16a34a"):
    is_active = st.session_state["nav_view"] == view_key
    bg  = active_color if is_active else "#09111c"
    bdr = active_color if is_active else "#1a2535"
    cnt_color = "#ffffff" if is_active else "#4ade80"
    with col:
        st.markdown(
            f"<div style='background:{bg};border:1px solid {bdr};border-radius:10px;"
            f"padding:12px 8px;text-align:center;cursor:pointer;'>"
            f"<div style='font-size:11px;color:{'#fff' if is_active else '#475569'};"
            f"text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:4px;'>"
            f"{icon} {label}</div>"
            f"<div style='font-family:DM Mono,monospace;font-size:24px;"
            f"font-weight:700;color:{cnt_color};'>{count}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        if st.button(f"Select", key=f"nav_{view_key}", use_container_width=True):
            st.session_state["nav_view"] = view_key
            st.rerun()

_nc = st.columns(5)
nav_card(_nc[0], "⏳", "Today",    len(daily_matches),   "⏳ Today (Upcoming)",  "#16a34a")
nav_card(_nc[1], "📅", "Tomorrow",  len(tomorrow_matches), "📅 Tomorrow",          "#2563eb")
nav_card(_nc[2], "🔴", "Live Now",  len(daily_live),       "🔴 Live Now",          "#dc2626")
nav_card(_nc[3], "✅", "Finished",  len(daily_finished),   "✅ Finished",          "#475569")
nav_card(_nc[4], "📆", "This Week", len(weekly_matches),   "📆 This Week",         "#9333ea")
st.write("")

# ── API STATUS BANNER ────────────────────────────────────────────────────────
_api_err  = st.session_state.get("api_error", "")
_api_warn = st.session_state.get("api_filter_warn", "")
if _api_err:
    st.markdown(
        f"<div style='background:#2d0a0a;border:1px solid #ef4444;border-radius:10px;"
        f"padding:14px 18px;margin-bottom:16px;'>"  
        f"<div style='font-family:DM Mono,monospace;font-size:11px;color:#ef4444;"
        f"letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>⚠️ API Issue</div>"
        f"<div style='font-size:13px;color:#fca5a5;'>{_api_err}</div>"
        f"<div style='margin-top:10px;font-size:12px;color:#7f1d1d;'>"
        f"{"<b>404 = Key invalid/expired.</b> Open 🔑 API Key in sidebar → paste new key from apifootball.com" if "404" in _api_err else "<b>What to do:</b> 1) Wait and refresh — free API resets hourly. 2) Check apifootball.com quota. 3) Enter a new key in 🔑 API Key sidebar section."}"
        f"</div></div>",
        unsafe_allow_html=True
    )
elif _api_warn:
    st.markdown(
        f"<div style='background:#1a1000;border:1px solid #f97316;border-radius:10px;"
        f"padding:12px 16px;margin-bottom:14px;'>"  
        f"<div style='font-size:12px;color:#fb923c;'>{_api_warn}</div>"
        f"<div style='font-size:11px;color:#78350f;margin-top:6px;'>"
        f"Open <b>🔍 League Debug</b> in the sidebar to see raw API league names.</div>"
        f"</div>",
        unsafe_allow_html=True
    )

# ── TABS ──────────────────────────────────────────────────────────────────────
# ═════════════════════════════════════════════════════════════════════════════
#  ACCURACY HISTORY ENGINE
#  Stores daily accuracy records in a local JSON file.
#  Falls back to session_state if file I/O fails (e.g. read-only filesystem).
# ═════════════════════════════════════════════════════════════════════════════
import json, os, csv
from io import StringIO

HISTORY_FILE = "accuracy_history.json"

def load_history() -> list:
    """Load accuracy history from file. Returns list of daily records."""
    # Try session state cache first (fast path)
    if "acc_history" in st.session_state:
        return st.session_state["acc_history"]
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                st.session_state["acc_history"] = data
                return data
    except Exception:
        pass
    st.session_state["acc_history"] = []
    return []

def save_history(history: list):
    """Save history to file and session state."""
    st.session_state["acc_history"] = history
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass  # read-only FS on some cloud deployments — session_state still works

def upsert_daily_record(date_str: str, wins: int, losses: int,
                         picks: int, market_breakdown: dict, sniper: bool):
    """
    Add or update a daily accuracy record.
    If the date already exists, overwrite it (re-run of same day).
    """
    history = load_history()
    record = {
        "date":       date_str,
        "wins":       wins,
        "losses":     losses,
        "picks":      picks,
        "win_rate":   round(wins / max(picks, 1) * 100, 1),
        "sniper":     sniper,
        "markets":    market_breakdown,
        "logged_at":  now.strftime("%Y-%m-%d %H:%M"),
    }
    # Remove existing record for this date if present
    history = [r for r in history if r.get("date") != date_str]
    history.append(record)
    # Keep chronological order
    history.sort(key=lambda x: x["date"])
    save_history(history)
    return record

def history_to_csv(history: list) -> str:
    """Convert history list to CSV string for download."""
    if not history: return ""
    output = StringIO()
    fields = ["date","wins","losses","picks","win_rate","sniper","logged_at"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(history)
    return output.getvalue()

def rolling_win_rate(history: list, days: int) -> float | None:
    """Compute win rate over the last N days of history."""
    recent = history[-days:] if len(history) >= days else history
    if not recent: return None
    total_w = sum(r["wins"] for r in recent)
    total_p = sum(r["picks"] for r in recent)
    return round(total_w / max(total_p, 1) * 100, 1)

def market_totals(history: list) -> dict:
    """Aggregate per-market wins/losses across all history."""
    totals = {}
    for r in history:
        for mkt, rec in r.get("markets", {}).items():
            totals.setdefault(mkt, {"w": 0, "l": 0})
            totals[mkt]["w"] += rec.get("w", 0)
            totals[mkt]["l"] += rec.get("l", 0)
    return totals

tab1,tab2,tab3,tab4,tab5=st.tabs(["🎟️ Auto-Acca","📝 Weekly Slip","🔥 Daily Picks","📊 Accuracy","💡 Edge Guide"])

# ══ TAB 1 ═════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🎟️ Algorithmic Ticket Generator")
    st.markdown("<div class='info-box'>Only <b>upcoming</b> matches included. Finished and live games are automatically excluded.</div>",unsafe_allow_html=True)
    if "acca_selection" not in st.session_state: st.session_state.acca_selection=None
    r1=st.columns(4);r2=st.columns(4)
    for i,(n,lbl,color,icon) in enumerate(TIER_CONFIG):
        with (r1 if i<4 else r2)[i%4]:
            if st.button(f"{icon} {ODDS_LABELS[i]}",key=f"tier_{i}",use_container_width=True):
                st.session_state.acca_selection=(n,lbl,color)
    sel=st.session_state.acca_selection
    if sel:
        n_picks,lbl,color=sel
        st.markdown(f"<div class='risk-badge' style='background:{color};'>{lbl} · {n_picks}-LEG</div>",unsafe_allow_html=True)
        valid_picks=[]
        with st.spinner(f"Building {n_picks}-leg acca…"):
            for m in daily_matches:
                h_st,h_cnt=fetch_stats(m.get("match_hometeam_id"),"home")
                a_st,a_cnt=fetch_stats(m.get("match_awayteam_id"),"away")
                if h_st and a_st and h_cnt>=3 and a_cnt>=3:
                    pick,pt,ln,cf,sg,_=generate_ai_pick(h_st,a_st,m.get("league_name",""),sniper_mode,h_cnt,a_cnt)
                    if cf>0:
                        valid_picks.append({"match":f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}","league":m.get("league_name",""),"pick":pick,"conf":cf,"time":m.get("match_time",""),"sigs":sg,"tier":sportsbook_tier(m.get("league_name","")),"imp":match_importance(m)})
        # Primary sort: confidence; secondary: match importance (big games preferred at equal conf)
        valid_picks.sort(key=lambda x:(x["conf"], x.get("imp",0)), reverse=True)
        chosen=valid_picks[:n_picks]
        if not chosen:
            st.markdown("<div class='empty-state'><div class='empty-state-icon'>🎯</div><div class='empty-state-text'>No picks meet the threshold today</div><div class='empty-state-sub'>Try disabling Sniper Mode or enabling more book tiers</div></div>",unsafe_allow_html=True)
        else:
            avg_conf=sum(p["conf"] for p in chosen)/len(chosen)
            m1,m2,m3=st.columns(3);m1.metric("Legs",len(chosen));m2.metric("Avg Confidence",f"{avg_conf:.1f}%");m3.metric("Mode","🎯 SNIPER" if sniper_mode else "STANDARD")
            st.markdown("<div class='slip-box'>",unsafe_allow_html=True)
            for i,p in enumerate(chosen,1):
                imp_s="⭐ " if p.get("imp",0)>=130 else "🔥 " if p.get("imp",0)>=110 else ""
                st.markdown(f"<div class='slip-row'><div class='slip-league'>{i}. {imp_s}{p['league']} · {p['time']} &nbsp; {book_tier_badge(p['tier'])}</div><div class='slip-match'>{p['match']}</div><div class='slip-pick' style='color:{color};'>{p['pick']}</div>{conf_bar_html(p['conf'],color)}{signals_html(p['sigs'])}</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

# ══ TAB 2 ═════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📝 Weekly Fixture Browser")
    if st.session_state.get("nav_view") == "📆 This Week":
        st.markdown("<div class='info-box'>📆 Showing <b>This Week</b> fixtures — navigated from stats bar</div>",unsafe_allow_html=True)
    st.markdown("<div class='info-box'>Only upcoming matches shown. Finished games removed automatically.</div>",unsafe_allow_html=True)
    c_search,c_tier_filter=st.columns([3,1])
    with c_search: search_q=st.text_input("🔍 Search team",placeholder="e.g. Chelsea, Brann, Santos…")
    with c_tier_filter: only_tier_a=st.checkbox("Tier A only",value=False)
    filtered=[m for m in weekly_matches if (not search_q or search_q.lower() in m.get("match_hometeam_name","").lower() or search_q.lower() in m.get("match_awayteam_name","").lower()) and (not only_tier_a or sportsbook_tier(m.get("league_name",""))=="A")]
    if not filtered:
        st.markdown("<div class='empty-state'><div class='empty-state-icon'>🔍</div><div class='empty-state-text'>No upcoming fixtures found</div></div>",unsafe_allow_html=True)
    else:
        dates=sorted(set(m.get("match_date","") for m in filtered))
        for d in dates:
            day_ms=[m for m in filtered if m.get("match_date")==d]
            st.markdown(f"#### 📅 {d} &nbsp;<span style='color:#475569;font-size:13px;'>({len(day_ms)} upcoming)</span>",unsafe_allow_html=True)
            for m in day_ms:
                tier=sportsbook_tier(m.get("league_name",""))
                tier_icons={"A":"📚","B":"📖","C":"🔍"}
                st.checkbox(f"🕒 {m.get('match_time','')} {tier_icons.get(tier,'')} | **{m.get('match_hometeam_name','')}** vs **{m.get('match_awayteam_name','')}** · _{m.get('league_name','')}_",key=f"w_{m.get('match_id')}")

# ══ TAB 3 ═════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔥 Today's System Picks")
    # Pre-select based on nav card clicked from stats bar
    _nav_default = st.session_state.get("nav_view","⏳ Today (Upcoming)")
    _radio_opts  = ["⏳ Today (Upcoming)","📅 Tomorrow","🔴 Live Now","✅ Finished"]
    _radio_idx   = _radio_opts.index(_nav_default) if _nav_default in _radio_opts else 0
    view_mode=st.radio("Show", _radio_opts, horizontal=True, index=_radio_idx,
                       key="daily_view_radio")
    if view_mode=="⏳ Today (Upcoming)":    show_matches=daily_matches
    elif view_mode=="📅 Tomorrow":          show_matches=tomorrow_matches
    elif view_mode=="🔴 Live Now":          show_matches=daily_live
    else:                                   show_matches=daily_finished
    if sniper_mode: st.markdown("<div class='warning-box'>🎯 Sniper Mode — only picks ≥82% confidence shown.</div>",unsafe_allow_html=True)
    if not show_matches:
        st.markdown("<div class='empty-state'><div class='empty-state-icon'>📭</div><div class='empty-state-text'>No matches in this category right now</div></div>",unsafe_allow_html=True)
    else:
        for l_name, l_matches in sort_leagues_and_matches(show_matches):
            tier=sportsbook_tier(l_name)
            prestige_rank = LEAGUE_PRESTIGE.get(l_name, 99)
            prestige_crown = "👑" if prestige_rank <= 3 else "⚽" if prestige_rank <= 14 else "🏆"
            st.markdown(f"<div class='league-header'>{prestige_crown} {l_name} &nbsp; {book_tier_badge(tier)}</div>",unsafe_allow_html=True)
            for m in l_matches:
                imp=match_importance(m)
                star_pfx="⭐ " if imp>=130 else "🔥 " if imp>=110 else ""
                status=m.get("match_status",""); home=m.get("match_hometeam_name","?"); away=m.get("match_awayteam_name","?"); t=m.get("match_time","")
                live=is_live_status(status); prefix="🔴 LIVE · " if live else "✅ FT · " if is_finished(status) else ""
                with st.expander(f"{prefix}{star_pfx}🕒 {t} | {home} vs {away}"):
                    if live: st.markdown(f"<div class='live-banner'><span class='live-dot'></span>LIVE: {m.get('match_hometeam_score','?')} – {m.get('match_awayteam_score','?')} ({status}')</div>",unsafe_allow_html=True)
                    with st.spinner("Fetching stats…"):
                        h_st,h_cnt=fetch_stats(m.get("match_hometeam_id"),"home")
                        a_st,a_cnt=fetch_stats(m.get("match_awayteam_id"),"away")
                    if not h_st or not a_st: st.warning("⚠️ Insufficient data."); continue
                    if h_cnt<3 or a_cnt<3: st.info(f"📉 Low sample: {home}({h_cnt}) / {away}({a_cnt})")
                    # ── Dynamic player intelligence ──────────────────────────────────
                    confirmed_names = fetch_lineups_for_match(m.get("match_id",""))
                    h_pstats = fetch_player_stats(m.get("match_hometeam_id",""), past_str, today_str)
                    a_pstats = fetch_player_stats(m.get("match_awayteam_id",""), past_str, today_str)
                    impact   = compute_player_impact(h_pstats, a_pstats, confirmed_names, home, away)
                    lineups_ready = impact["lineups_available"]

                    # ── Weather intelligence ──────────────────────────────────────────
                    stadium_coords = get_stadium_coords(home)
                    weather_impact = {"g_mult":1.0,"c_mult":1.0,"k_mult":1.0,"s_mult":1.0,"conf_bonus":0.0,"available":False,"badge_html":""}
                    if stadium_coords:
                        raw_wx = fetch_weather(stadium_coords[0], stadium_coords[1],
                                               m.get("match_date", today_str), t)
                        weather_impact = compute_weather_impact(raw_wx)

                    pick,p_type,thresh,conf,sigs,all_plays=generate_ai_pick(
                        h_st,a_st,l_name,sniper_mode,h_cnt,a_cnt,
                        g_mult=impact["g_mult"],
                        c_mult=impact["c_mult"],
                        k_mult=impact["k_mult"],
                        s_mult=impact["s_mult"],
                        intel_bonus=impact["conf_bonus"],
                        lineups_available=lineups_ready,
                        w_g_mult=weather_impact["g_mult"],
                        w_c_mult=weather_impact["c_mult"],
                        w_k_mult=weather_impact["k_mult"],
                        w_s_mult=weather_impact["s_mult"],
                        w_conf_bonus=weather_impact["conf_bonus"],
                    )
                    avail_mkts = available_markets(l_name)
                    mkt_icons  = {"goals":"⚽ Goals","corners":"🔥 Corners","cards":"🟨 Cards","sot":"🎯 SOT"}
                    mkt_tags   = " ".join(f"<span style='font-size:10px;background:rgba(74,222,128,.1);color:#4ade80;border:1px solid rgba(74,222,128,.25);padding:2px 6px;border-radius:8px;font-family:DM Mono,monospace;'>{mkt_icons[k]}</span>" for k in mkt_icons if k in avail_mkts)
                    ref=m.get("match_referee","")

                    intel_panel_html = player_intel_html(impact, p_type)
                    # Card line options — all systems
                    card_lines_html = ""
                    if p_type in ("cards","under_cards"):
                        _card_mode    = st.session_state.get("card_mode","both")
                        _proj_yellows = ((h_st["cards"]+a_st["cards"]) *
                                        LEAGUE_PROFILE.get(l_name,DEFAULT_PROFILE)[2] *
                                        impact.get("k_mult",1.0) * weather_impact.get("k_mult",1.0))
                        _proj_pts     = yellows_to_card_points(_proj_yellows, l_name)
                        _card_opts    = get_card_line_options(_proj_yellows, l_name, _card_mode)
                        if _card_opts:
                            _rc = RED_CARD_RATE.get(l_name, DEFAULT_RED_RATE)
                            _row_parts = []
                            for _cl,_cd,_cg,_cn,_cs in _card_opts:
                                _cc = "#4ade80" if _cg>=2 else "#fbbf24" if _cg>=1 else "#60a5fa"
                                _row_parts.append(
                                    f"<div style='display:flex;align-items:center;padding:6px 0;"
                                    f"border-bottom:1px solid #09111c;gap:6px;'>"
                                    f"<span style='font-family:DM Mono;font-size:13px;"
                                    f"color:#e2e8f0;font-weight:700;min-width:120px;'>{_cd} {_cl} Cards</span>"
                                    f"<span style='font-size:10px;color:#64748b;flex:1;'>{_cs}</span>"
                                    f"<span style='color:{_cc};font-size:11px;'>{_cn} Δ{_cg:.1f}</span>"
                                    f"</div>"
                                )
                            _rows_str = "".join(_row_parts)
                            card_lines_html = (
                                f"<div style='background:#080d14;border:1px solid #1e293b;"
                                f"border-top:2px solid #fbbf24;border-radius:8px;"
                                f"padding:14px;margin-top:10px;'>"
                                f"<div style='display:flex;justify-content:space-between;"
                                f"margin-bottom:8px;'>"
                                f"<span style='font-family:DM Mono;font-size:10px;"
                                f"color:#fbbf24;letter-spacing:1px;text-transform:uppercase;'>"
                                f"🟨 Card Lines</span>"
                                f"<span style='font-size:10px;color:#64748b;'>"
                                f"Yellows: {_proj_yellows:.1f} | Card pts: {_proj_pts:.1f}</span></div>"
                                f"<div style='font-size:11px;color:#475569;margin-bottom:8px;'>"
                                f"Betano: Y=1 R=2 | ~{_rc:.2f} reds/game | {l_name}</div>"
                                f"{_rows_str}</div>"
                            )
                    ref_html=f"<a href='https://www.google.com/search?q={ref.replace(' ','+')}+referee+stats' target='_blank' class='ref-tag'>⚖️ {ref}</a>" if ref else "<span class='ref-tag'>⚖️ TBD</span>"
                    odds_key=f"odds_{m.get('match_id','')}"
                    if odds_key not in st.session_state: st.session_state[odds_key]=1.90
                    c_pick,c_stats=st.columns([3,1.5])
                    with c_pick:
                        is_sniper=conf>=82; card_cls="sniper-card" if is_sniper else "pick-card"; lbl_cls="sniper-label" if is_sniper else "pick-label"
                        badge="<div class='sniper-badge'>🎯 SNIPER PICK</div>" if is_sniper else ""
                        wx_badge = weather_impact.get("badge_html","")
                        st.markdown(
                            f"<div class='{card_cls}'>{badge}"
                            f"<div class='{lbl_cls}'>{pick}</div>"
                            f"{ref_html}"
                            f"{wx_badge}"
                            f"{conf_bar_html(conf,'#f97316' if is_sniper else '#16a34a')}"
                            f"{signals_html(sigs)}"
                            f"<div style='margin-top:8px;'>{mkt_tags}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        # Player intel panel — always shown when data available
                        if card_lines_html:
                            st.markdown(card_lines_html, unsafe_allow_html=True)
                        if intel_panel_html:
                            st.markdown(intel_panel_html, unsafe_allow_html=True)
                        # ── Telegram alert button ──────────────────────────────
                        _tg_tok = st.session_state.get("tg_token","")
                        _tg_cid = st.session_state.get("tg_chat","")
                        _tg_min = st.session_state.get("tg_min_conf",85)
                        if _tg_tok and _tg_cid and conf > 0 and p_type != "pass":
                            _wx_desc = weather_impact.get("desc","") if weather_impact.get("available") else ""
                            _tg_msg  = format_telegram_pick(
                                f"{home} vs {away}", l_name, pick,
                                conf, t, book_tier(l_name) or "?", _wx_desc)
                            if conf >= _tg_min:
                                # Auto-send if above threshold
                                _sent_key = f"tg_sent_{m.get('match_id','')}_auto"
                                if not st.session_state.get(_sent_key):
                                    if send_telegram(_tg_tok, _tg_cid, _tg_msg):
                                        st.session_state[_sent_key] = True
                                        st.success("🔔 Alert sent to Telegram!")
                            else:
                                # Manual send button for picks below threshold
                                _btn_key = f"tg_btn_{m.get('match_id','')}" 
                                if st.button(f"🔔 Send to Telegram ({conf:.0f}%)", key=_btn_key):
                                    if send_telegram(_tg_tok, _tg_cid, _tg_msg):
                                        st.success("✅ Sent!")
                                    else:
                                        st.error("❌ Failed — check token & chat ID")
                        user_odds=st.number_input("Enter bookmaker odds (decimal)",min_value=1.01,max_value=50.0,step=0.05,value=st.session_state[odds_key],key=odds_key)
                        if conf>0 and user_odds>1.0:
                            kelly_stake=kelly_fraction(conf_to_prob(conf),user_odds,kelly_divisor)
                            actual_stake=round(bankroll*kelly_stake/100,2)
                            st.markdown(value_panel_html(conf,user_odds,kelly_divisor)+(f"<div style='text-align:center;margin-top:6px;font-size:13px;color:#64748b;'>= <b style='color:#e2e8f0;'>{actual_stake} units</b></div>" if kelly_stake>0 else ""),unsafe_allow_html=True)
                    with c_stats:
                        gm,cm,kdm,_=LEAGUE_PROFILE.get(l_name,DEFAULT_PROFILE)
                        # Pre-compute weather display strings (avoids nested f-string errors)
                        _wx_avail = weather_impact.get('available', False)
                        _wx_cond  = weather_impact.get('condition','N/A').title() if _wx_avail else '—'
                        _wx_str   = (f"{weather_impact['temp']:.0f}°C · {weather_impact['rain']:.1f}mm · "
                                     f"{weather_impact['wind']:.0f}km/h") if _wx_avail else '—'
                        hG,aG,hC,aC_c,ha_s=get_ha_profile(l_name)
                        # HA-weighted projections for display
                        pg=((h_st['gf']*hG+a_st['ga']*hG)/2+(a_st['gf']*aG+h_st['ga']*aG)/2)*gm
                        pc=min(12.0,((h_st['cf']*hC+a_st['ca']*hC)/2+(a_st['cf']+h_st['ca'])/2)*cm)
                        pcd=(h_st['cards']+a_st['cards']*aC_c)*kdm
                        psot=((h_st['sotf']*hG+a_st['sota']*hG)/2+(a_st['sotf']*aG+h_st['sota']*aG)/2)
                        ha_labels={0:'Neutral',1:'Moderate',2:'Strong',3:'Very Strong'}
                        ha_icon='🏠' if ha_s>=2 else '⚖️'
                        st.markdown(f"<div class='stats-panel'><div class='stats-title'>Math Edge</div>"
                            f"<div class='stat-row'><span>xG (HA-adj)</span><span class='stat-val'>{pg:.2f}</span></div>"
                            f"<div class='stat-row'><span>Corners (adj)</span><span class='stat-val'>{pc:.1f}</span></div>"
                            f"<div class='stat-row'><span>Cards (adj)</span><span class='stat-val'>{pcd:.1f}</span></div>"
                            f"<div class='stat-row'><span>SOT (adj)</span><span class='stat-val'>{psot:.1f}</span></div>"
                            f"<div class='stat-row'><span>Sample H/A</span><span class='stat-val'>{h_cnt}/{a_cnt}</span></div>"
                            f"<div class='stat-row'><span>{ha_icon} Home Advantage</span><span class='stat-val' style='font-size:12px;'>{ha_labels.get(ha_s,'?')}</span></div>"
                            f"<div class='stat-row'><span>Home goal boost</span><span class='stat-val' style='color:#4ade80;'>×{hG:.2f}</span></div>"
                            f"<div class='stat-row'><span>Away card risk</span><span class='stat-val' style='color:#f97316;'>×{aC_c:.2f}</span></div>"
                            f"<div class='stat-row'><span>🌤️ Weather</span><span class='stat-val' style='font-size:11px;'>{_wx_cond}</span></div>"
                            f"<div class='stat-row'><span>Temp / Rain / Wind</span><span class='stat-val' style='font-size:11px;'>{_wx_str}</span></div>"
                            f"</div>",unsafe_allow_html=True)
                        if len(all_plays)>1:
                            st.markdown("<div style='margin-top:10px;font-size:11px;color:#475569;'>Alt plays:</div>",unsafe_allow_html=True)
                            for alt in all_plays[1:3]: st.markdown(f"<div style='font-size:12px;color:#64748b;padding:3px 0;'>• {alt[0]} ({alt[3]:.0f}%)</div>",unsafe_allow_html=True)

# ══ TAB 4 ═════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📊 Accuracy Tracker")

    # Strict bookable filter — ON by default to prevent inflated stats
    acc_col1, acc_col2 = st.columns([3,1])
    with acc_col1:
        st.markdown("<div class='info-box'>Accuracy is tracked against finished matches. Enable <b>Strict Mode</b> to only count games that are reliably listed on major sportsbooks — this gives you a true win rate you can actually replicate.</div>",unsafe_allow_html=True)
    with acc_col2:
        strict_acc = st.toggle("📚 Strict Bookable Only", value=True,
                               help="Only count picks from Tier A + Tier B leagues that are on Bet365/Betway/Betano")
        st.session_state["_strict_acc"] = strict_acc
    acc_filter_leagues = STRICT_BOOKABLE if strict_acc else ACTIVE_LEAGUES

    history = load_history()

    # ── Sub-tabs: Today's Results | Historical Trends | Per-Market | Manage ──
    acc_t1, acc_t2, acc_t3, acc_t4 = st.tabs([
        "📅 Yesterday's Results", "📈 Win Rate Over Time",
        "🎯 Per-Market History", "⚙️ Manage Records"
    ])

    # ══ SUB-TAB 1: Yesterday's Results + auto-log ════════════════════════════
    with acc_t1:
        st.markdown(f"<div style='color:#475569;font-size:13px;margin-bottom:16px;'>📅 Backtesting {yesterday_str} · Results auto-saved to history</div>",unsafe_allow_html=True)
        with st.spinner("Fetching yesterday's results…"):
            yesterday_res = fetch_events(yesterday_str, yesterday_str)
        finished_yday = [m for m in yesterday_res if is_finished(m.get("match_status",""))]

        if not finished_yday:
            st.markdown("<div class='empty-state'><div class='empty-state-icon'>📭</div><div class='empty-state-text'>No finished matches yesterday</div></div>",unsafe_allow_html=True)
        else:
            results_by_type = {}; wins = losses = skipped = 0
            pick_log = []

            with st.spinner("Back-testing picks…"):
                for m in finished_yday:
                    lg_name = m.get("league_name","")
                    if lg_name not in acc_filter_leagues: continue
                    if st.session_state.get("_strict_acc",True) and book_tier(lg_name) not in ("A","B"): continue
                    h_st,_ = fetch_stats(m.get("match_hometeam_id"),"home")
                    a_st,_ = fetch_stats(m.get("match_awayteam_id"),"away")
                    if not h_st or not a_st: continue
                    pick,p_type,thresh,conf,sigs,_ = generate_ai_pick(
                    h_st,a_st,m.get("league_name",""),sniper_mode,8,8)
                    if conf==0 or p_type=="pass": continue
                    won = check_result(p_type, thresh, m)
                    if won is None: skipped+=1; continue
                    results_by_type.setdefault(p_type, {"w":0,"l":0})
                    if won: wins+=1; results_by_type[p_type]["w"]+=1
                    else:   losses+=1; results_by_type[p_type]["l"]+=1
                    pick_log.append({"won":won,"pick":pick,"conf":conf,
                    "home":m.get("match_hometeam_name",""),
                    "away":m.get("match_awayteam_name",""),
                    "hs":m.get("match_hometeam_score","?"),
                    "as_":m.get("match_awayteam_score","?"),
                    "league":m.get("league_name",""),
                    "tier":book_tier(m.get("league_name",""))})

            total = wins + losses
            if total > 0:
                # Auto-save to history
                upsert_daily_record(yesterday_str, wins, losses, total,
                                    results_by_type, sniper_mode)
                history = load_history()  # reload with new record

                wr = wins/total*100
                mc1,mc2,mc3,mc4 = st.columns(4)
                mc1.metric("Win Rate",  f"{wr:.1f}%", delta=f"+{wins}W / -{losses}L")
                mc2.metric("Picks",     total)
                mc3.metric("Wins",      wins)
                mc4.metric("Losses",    losses)
                st.divider()

            # Match-by-match results
            for p in pick_log:
                ico = "✅" if p["won"] else "❌"
                cls = "acc-win" if p["won"] else "acc-loss"
                tier = p.get("tier") or sportsbook_tier(p["league"])
                # Flag picks not on strict bookable list
                not_bookable = strict_acc and tier == "C"
                nb_warn = " <span style='color:#f97316;font-size:10px;font-family:DM Mono,monospace;'>⚠️ CHECK AVAILABILITY</span>" if not_bookable else ""
                st.markdown(
                    f"<div class='accuracy-row {cls}' style='opacity:{"0.6" if not_bookable else "1"};'>"    
                    f"<span style='font-size:18px;'>{ico}</span>"
                    f"<div style='flex:1;'>"
                    f"<div style='font-weight:600;font-size:13px;'>{p['home']} vs {p['away']}</div>"
                    f"<div style='font-size:11px;color:#64748b;'>FT: {p['hs']}–{p['as_']} · {p['league']} {book_tier_badge(tier)}{nb_warn}</div>"
                    f"</div>"
                    f"<div style='text-align:right;'>"
                    f"<div style='font-family:DM Mono,monospace;font-size:12px;color:#e2e8f0;'>{p['pick']}</div>"
                    f"<div style='font-size:11px;color:#475569;'>{p['conf']:.0f}% conf</div>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

            if results_by_type:
                st.markdown("#### Market Breakdown — Yesterday")
                for pt,rec in sorted(results_by_type.items(),
                                     key=lambda x:-(x[1]['w']/(x[1]['w']+x[1]['l'])
                                                    if x[1]['w']+x[1]['l'] else 0)):
                    tc = rec['w']+rec['l']
                    pct = rec['w']/tc*100 if tc else 0
                    c = "#16a34a" if pct>=70 else "#f97316" if pct>=50 else "#ef4444"
                    st.markdown(
                        f"<div style='margin-bottom:10px;'>"
                        f"<div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;'>"
                        f"<span style='font-weight:600;'>{pt.replace('_',' ').title()}</span>"
                        f"<span style='font-family:DM Mono,monospace;color:{c};'>{pct:.0f}% ({tc} picks)</span>"
                        f"</div>"
                        f"<div class='conf-bar-bg'><div class='conf-bar-fill' style='width:{int(pct)}%;background:{c};'></div></div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            # ── Tier breakdown ───────────────────────────────────────────────
            tier_counts = {"A":0,"B":0,"C":0,"?":0}
            for p in pick_log:
                tier_counts[p.get("tier","?") or "?"] += 1
            if any(v>0 for v in tier_counts.values()):
                st.markdown("#### Source Tier Breakdown")
                tier_rows = [
                    ("A","📚 Tier A — All Books","#4ade80","Bet365, Betway, Betano etc."),
                    ("B","📖 Tier B — Most Books","#fbbf24","Most international books"),
                    ("C","🔍 Tier C — Specialist","#f97316","May NOT be listed everywhere"),
                ]
                for tk, tlabel, tc_color, tdesc in tier_rows:
                    cnt = tier_counts.get(tk, 0)
                    if cnt == 0: continue
                    pct_t = cnt/max(total,1)*100
                    warn = " ⚠️" if tk == "C" else ""
                    st.markdown(
                        f"<div style='display:flex;align-items:center;gap:10px;padding:6px 0;'>"
                        f"<span style='color:{tc_color};font-weight:700;font-size:13px;min-width:160px;'>{tlabel}{warn}</span>"
                        f"<span style='color:#64748b;font-size:12px;flex:1;'>{tdesc}</span>"
                        f"<span style='font-family:DM Mono,monospace;color:{tc_color};font-size:13px;font-weight:700;'>{cnt} picks ({pct_t:.0f}%)</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

    # ══ SUB-TAB 2: Win Rate Over Time Chart ══════════════════════════════════
    with acc_t2:
        if len(history) < 2:
            st.markdown("<div class='empty-state'><div class='empty-state-icon'>📈</div><div class='empty-state-text'>Need at least 2 days of data</div><div class='empty-state-sub'>Come back tomorrow — records build automatically every day</div></div>",unsafe_allow_html=True)
        else:
            # Rolling metrics
            r7  = rolling_win_rate(history, 7)
            r14 = rolling_win_rate(history, 14)
            r30 = rolling_win_rate(history, 30)
            all_w = sum(r["wins"]  for r in history)
            all_p = sum(r["picks"] for r in history)
            all_wr = round(all_w/max(all_p,1)*100, 1)

            col1,col2,col3,col4 = st.columns(4)
            col1.metric("All-Time",  f"{all_wr}%",  f"{all_w}W / {all_p-all_w}L")
            col2.metric("Last 7d",   f"{r7}%"  if r7  else "—")
            col3.metric("Last 14d",  f"{r14}%" if r14 else "—")
            col4.metric("Last 30d",  f"{r30}%" if r30 else "—")
            st.divider()

            # Build chart data as SVG sparkline
            dates    = [r["date"][-5:] for r in history]   # MM-DD
            wr_vals  = [r["win_rate"] for r in history]
            picks_v  = [r["picks"]    for r in history]
            n = len(dates)
            W, H = 700, 220
            pad_l, pad_r, pad_t, pad_b = 45, 20, 20, 40

            def scale_x(i):
                return pad_l + (i / max(n-1,1)) * (W - pad_l - pad_r)
            def scale_y(v):
                return pad_t + (1 - (v - 0) / 100) * (H - pad_t - pad_b)

            # Polyline points
            pts = " ".join(f"{scale_x(i):.1f},{scale_y(v):.1f}" for i,v in enumerate(wr_vals))

            # Bar chart for daily picks count (secondary axis)
            max_picks = max(picks_v) if picks_v else 1
            bar_html = ""
            for i, pk in enumerate(picks_v):
                bh = int((pk / max_picks) * 30)
                bx = scale_x(i) - 4
                by = H - pad_b - bh
                bar_html += f'<rect x="{bx:.0f}" y="{by}" width="8" height="{bh}" fill="rgba(96,165,250,0.3)" rx="2"/>'

            # X-axis labels (show every 2nd label if many)
            x_labels = ""
            step = max(1, n // 12)
            for i, d in enumerate(dates):
                if i % step == 0:
                    x_labels += f'<text x="{scale_x(i):.1f}" y="{H - pad_b + 16}" text-anchor="middle" font-size="9" fill="#475569">{d}</text>'

            # Y-axis grid lines and labels
            grid_html = ""
            for pct in [0, 25, 50, 70, 80, 100]:
                yp = scale_y(pct)
                col_g = "#16a34a33" if pct == 70 else "#1e293b"
                lw = "1.5" if pct == 70 else "0.5"
                grid_html += (f'<line x1="{pad_l}" y1="{yp:.1f}" x2="{W-pad_r}" y2="{yp:.1f}" '
                              f'stroke="{col_g}" stroke-width="{lw}" stroke-dasharray="{"4,4" if pct!=70 else "none"}"/>'
                              f'<text x="{pad_l-6}" y="{yp+4:.1f}" text-anchor="end" font-size="9" fill="#475569">{pct}%</text>')

            # Area fill under the line
            area_pts = f"{scale_x(0):.1f},{H-pad_b} " + pts + f" {scale_x(n-1):.1f},{H-pad_b}"

            # Data point dots
            dots = ""
            for i,(v,p) in enumerate(zip(wr_vals, picks_v)):
                fc = "#4ade80" if v>=70 else "#f97316" if v>=50 else "#ef4444"
                dots += (f'<circle cx="{scale_x(i):.1f}" cy="{scale_y(v):.1f}" r="4" '
                         f'fill="{fc}" stroke="#080d14" stroke-width="2"/>')

            svg = f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;background:#09111c;border-radius:10px;border:1px solid #1e293b;">
  <defs>
    <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#16a34a" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#16a34a" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  {grid_html}
  {bar_html}
  <polygon points="{area_pts}" fill="url(#lineGrad)"/>
  <polyline points="{pts}" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  {dots}
  {x_labels}
  <text x="{pad_l}" y="12" font-size="10" fill="#475569" font-family="monospace">WIN RATE %</text>
  <text x="{W-pad_r}" y="{H-pad_b+16}" text-anchor="end" font-size="9" fill="#3b82f6">■ daily picks (bars)</text>
  <line x1="{pad_l}" y1="{scale_y(70):.1f}" x2="{pad_l+60}" y2="{scale_y(70):.1f}" stroke="#16a34a" stroke-width="1.5"/>
  <text x="{pad_l+65}" y="{scale_y(70)+4:.1f}" font-size="9" fill="#4ade80">70% target</text>
</svg>"""

            st.markdown(svg, unsafe_allow_html=True)
            st.write("")

            # Day-by-day table
            st.markdown("#### Day-by-Day Log")
            # Header
            st.markdown(
                "<div style='display:grid;grid-template-columns:100px 70px 60px 60px 80px 80px;gap:4px;"
                "font-size:11px;color:#475569;font-family:DM Mono,monospace;padding:6px 10px;"
                "border-bottom:1px solid #1e293b;text-transform:uppercase;letter-spacing:1px;'>"
                "<span>Date</span><span>Win Rate</span><span>Wins</span><span>Losses</span>"
                "<span>Picks</span><span>Mode</span></div>",
                unsafe_allow_html=True
            )
            for r in reversed(history[-30:]):   # show last 30, most recent first
                wr_c = "#4ade80" if r["win_rate"]>=70 else "#f97316" if r["win_rate"]>=50 else "#ef4444"
                mode = "🎯 Sniper" if r.get("sniper") else "Standard"
                st.markdown(
                    f"<div style='display:grid;grid-template-columns:100px 70px 60px 60px 80px 80px;"
                    f"gap:4px;font-size:12px;padding:7px 10px;border-bottom:1px solid #0d1520;"
                    f"align-items:center;'>"
                    f"<span style='color:#94a3b8;font-family:DM Mono,monospace;'>{r['date']}</span>"
                    f"<span style='color:{wr_c};font-weight:700;font-family:DM Mono,monospace;'>{r['win_rate']}%</span>"
                    f"<span style='color:#4ade80;'>+{r['wins']}</span>"
                    f"<span style='color:#f87171;'>-{r['losses']}</span>"
                    f"<span style='color:#64748b;'>{r['picks']}</span>"
                    f"<span style='color:#475569;font-size:11px;'>{mode}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # ══ SUB-TAB 3: Per-Market History ════════════════════════════════════════
    with acc_t3:
        if not history:
            st.markdown("<div class='empty-state'><div class='empty-state-icon'>🎯</div><div class='empty-state-text'>No history yet</div></div>",unsafe_allow_html=True)
        else:
            mkt_data = market_totals(history)
            if not mkt_data:
                st.info("Market breakdown data not available in older records.")
            else:
                st.markdown("#### All-Time Performance by Market")
                st.markdown(f"<div style='color:#475569;font-size:13px;margin-bottom:16px;'>Based on {len(history)} days of recorded data</div>",unsafe_allow_html=True)

                # Sort by win rate descending
                sorted_mkts = sorted(mkt_data.items(),
                                     key=lambda x: x[1]['w']/(x[1]['w']+x[1]['l'])
                                     if x[1]['w']+x[1]['l'] else 0, reverse=True)

                mkt_icons = {
                    "goals":"⚽","under_goals":"🔒","corners":"🔥","under_corners":"🛡️",
                    "cards":"🟨","under_cards":"🧊","sot":"🎯","under_sot":"🧱"
                }
                for mkt, rec in sorted_mkts:
                    tc  = rec['w'] + rec['l']
                    if tc == 0: continue
                    pct = rec['w']/tc*100
                    c   = "#16a34a" if pct>=70 else "#f97316" if pct>=50 else "#ef4444"
                    icon = mkt_icons.get(mkt, "📊")
                    label = mkt.replace("_"," ").title()
                    # Expectation box
                    expected = "✅ Profitable" if pct>=70 else "⚠️ Marginal" if pct>=55 else "❌ Underperforming"
                    st.markdown(
                        f"<div style='background:#09111c;border:1px solid #1e293b;border-radius:10px;"
                        f"padding:14px 18px;margin-bottom:10px;'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                        f"<span style='font-size:14px;font-weight:700;color:#e2e8f0;'>{icon} {label}</span>"
                        f"<span style='font-family:DM Mono,monospace;font-size:13px;color:{c};font-weight:700;'>{pct:.1f}%</span>"
                        f"</div>"
                        f"<div class='conf-bar-bg' style='margin-bottom:8px;'>"
                        f"<div class='conf-bar-fill' style='width:{int(pct)}%;background:{c};'></div></div>"
                        f"<div style='display:flex;gap:16px;font-size:12px;color:#64748b;'>"
                        f"<span>✅ {rec['w']} wins</span>"
                        f"<span>❌ {rec['l']} losses</span>"
                        f"<span>📊 {tc} total picks</span>"
                        f"<span style='margin-left:auto;color:{c};font-weight:600;'>{expected}</span>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )

                # Best / worst market callout
                best_mkt  = sorted_mkts[0]  if sorted_mkts else None
                worst_mkt = sorted_mkts[-1] if len(sorted_mkts)>1 else None
                if best_mkt and worst_mkt:
                    bc1, bc2 = st.columns(2)
                    bm_tc = best_mkt[1]['w']+best_mkt[1]['l']
                    bm_wr = round(best_mkt[1]['w']/max(bm_tc,1)*100,1)
                    wm_tc = worst_mkt[1]['w']+worst_mkt[1]['l']
                    wm_wr = round(worst_mkt[1]['w']/max(wm_tc,1)*100,1)
                    with bc1:
                        st.markdown(
                            f"<div style='background:#071a10;border:1px solid #166534;border-radius:10px;padding:14px;text-align:center;'>"
                            f"<div style='font-size:11px;color:#4ade80;font-family:DM Mono,monospace;letter-spacing:1px;'>🏆 BEST MARKET</div>"
                            f"<div style='font-size:20px;font-weight:800;color:#4ade80;margin:6px 0;'>"
                            f"{mkt_icons.get(best_mkt[0],'📊')} {best_mkt[0].replace('_',' ').title()}</div>"
                            f"<div style='font-size:24px;font-family:DM Mono,monospace;color:#4ade80;font-weight:700;'>{bm_wr}%</div>"
                            f"<div style='font-size:11px;color:#2d5a3d;'>{bm_tc} picks</div></div>",
                            unsafe_allow_html=True
                        )
                    with bc2:
                        st.markdown(
                            f"<div style='background:#1a0505;border:1px solid #7f1d1d;border-radius:10px;padding:14px;text-align:center;'>"
                            f"<div style='font-size:11px;color:#f87171;font-family:DM Mono,monospace;letter-spacing:1px;'>⚠️ NEEDS WORK</div>"
                            f"<div style='font-size:20px;font-weight:800;color:#f87171;margin:6px 0;'>"
                            f"{mkt_icons.get(worst_mkt[0],'📊')} {worst_mkt[0].replace('_',' ').title()}</div>"
                            f"<div style='font-size:24px;font-family:DM Mono,monospace;color:#f87171;font-weight:700;'>{wm_wr}%</div>"
                            f"<div style='font-size:11px;color:#5a2d2d;'>{wm_tc} picks</div></div>",
                            unsafe_allow_html=True
                        )

    # ══ SUB-TAB 4: Manage Records ════════════════════════════════════════════
    with acc_t4:
        st.markdown("#### ⚙️ Manage Accuracy Records")
        col_dl, col_ul = st.columns(2)

        with col_dl:
            st.markdown("**📥 Export History**")
            if history:
                csv_str = history_to_csv(history)
                st.download_button(
                    label=f"⬇️ Download {len(history)} days as CSV",
                    data=csv_str,
                    file_name=f"quant_radar_accuracy_{today_str}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                # Also offer JSON
                json_str = json.dumps(history, indent=2)
                st.download_button(
                    label="⬇️ Download full JSON backup",
                    data=json_str,
                    file_name=f"quant_radar_backup_{today_str}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.info("No history to export yet.")

        with col_ul:
            st.markdown("**📤 Import / Restore History**")
            uploaded = st.file_uploader("Upload a JSON backup file", type=["json"])
            if uploaded:
                try:
                    imported = json.load(uploaded)
                    if isinstance(imported, list) and all("date" in r for r in imported):
                        save_history(imported)
                        st.success(f"✅ Restored {len(imported)} days of history!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid format — must be a JSON list with 'date' fields")
                except Exception as e:
                    st.error(f"❌ Import failed: {e}")

        st.divider()
        st.markdown("**🗑️ Clear Records**")
        col_warn, col_btn = st.columns([3, 1])
        with col_warn:
            st.markdown("<div class='warning-box'>⚠️ This permanently deletes all accuracy history. Export a backup first.</div>",unsafe_allow_html=True)
        with col_btn:
            if st.button("🗑️ Clear All", use_container_width=True):
                save_history([])
                st.success("History cleared.")
                st.rerun()

        # Summary stats at bottom
        if history:
            st.divider()
            st.markdown(f"**📊 Database Stats:** {len(history)} days recorded · "
                        f"Oldest: {history[0]['date']} · "
                        f"Latest: {history[-1]['date']} · "
                        f"File: `{HISTORY_FILE}`")

# ══ TAB 5 ═════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 💡 How to Beat the Sportsbook")
    st.markdown("<div class='tip-box'><b>🎯 Core principle:</b> Books profit through the <b>overround</b> (vig/margin) — they price markets so total implied probability exceeds 100%. Your goal is to find markets where your model's probability is <b>higher</b> than the book's implied probability. That gap is your edge.</div>",unsafe_allow_html=True)
    with st.expander("📐 Understanding the Edge Calculator"):
        st.markdown("""
**How it works:**
1. Enter the bookmaker's decimal odds for the recommended market
2. System converts to **implied probability** (what the book thinks)
3. Compares to **your model's win probability**
4. If model says 62% and book implies 52%, you have **+10% edge** — that's a value bet
5. **Kelly Criterion** tells you exactly how much of your bankroll to stake

**Edge thresholds:**
- 🟢 **+5% or more** — Strong value, bet with recommended stake
- 🟡 **+2% to +5%** — Mild value, consider halving the stake
- 🔴 **Below +2%** — No edge, skip this market
        """)
    with st.expander("🧠 5 Strategies That Actually Beat Books"):
        st.markdown("""
**1. Closing Line Value (CLV)**
If you bet at 2.10 and it closes at 1.80, you had +17% CLV. Tracking CLV is the most reliable long-run edge metric.

**2. Target Inefficient Markets**
Books are sharpest on 1X2 results. They are *softer* on Asian corners, total cards in Nordic leagues, SOT lines. Focus our system here.

**3. Early Market Timing**
Books open corners/cards lines 24–48hrs before kickoff and update slowly. Bet early when the line first opens — that's your window.

**4. Line Shopping**
Never use one book. Bet365 might price Over 9.5 corners at 1.85, Betway at 1.95, 1xBet at 2.05. Always compare — 10 cents compounds over hundreds of bets.

**5. Bankroll Discipline (Most Important)**
Even a 60% win rate goes on 10-game losing runs. Without Kelly staking, you bust before the edge materializes. Treat it like a fund.
        """)
    with st.expander("🔢 Kelly Calculator — Interactive"):
        col1,col2=st.columns(2)
        with col1:
            ex_odds=st.number_input("Example odds",value=1.90,step=0.05,key="guide_odds")
            ex_prob=st.slider("Your win probability %",40,95,62,key="guide_prob")
        with col2:
            b=ex_odds-1.0; p=ex_prob/100; q=1.0-p
            k_full=max(0.0,(b*p-q)/b); k_qtr=k_full/4; edge_v=(p-1/ex_odds)*100
            c2_color="#4ade80" if edge_v>2 else "#f87171"
            st.markdown(f"<div class='value-card' style='margin-top:12px;'><div class='value-title'>CALCULATION RESULT</div><div class='value-row'><span>Full Kelly</span><span class='value-num'>{k_full*100:.1f}%</span></div><div class='value-row'><span>Quarter Kelly (rec)</span><span class='value-num'>{k_qtr*100:.1f}%</span></div><div class='value-row'><span>Edge vs book</span><span class='value-num' style='color:{c2_color};'>{edge_v:+.1f}%</span></div></div>",unsafe_allow_html=True)

if live_refresh:
    time.sleep(60); st.rerun()
