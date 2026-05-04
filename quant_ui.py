Import streamlit as st
import requests
from datetime import datetime, timedelta

# ─────────────────────────────────────────────

# PAGE CONFIG

# ─────────────────────────────────────────────

st.set_page_config(page_title=“Institutional Radar”, page_icon=“🏦”, layout=“wide”)

# ─────────────────────────────────────────────

# STYLES

# ─────────────────────────────────────────────

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] { font-family: 'Space Mono', monospace !important; }

.stApp { background: #080c14 !important; color: #e2e8f0 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0f172a; border-radius: 8px; padding: 4px; gap: 6px;
    border: 1px solid #1e293b;
}
.stTabs [data-baseweb="tab"] { color: #64748b; font-weight: 700; font-size: 13px; padding: 8px 18px; border-radius: 6px; }
.stTabs [aria-selected="true"] { background: #f97316 !important; color: #080c14 !important; }

/* Expanders */
[data-testid="stExpander"] {
    background: #0f172a !important; border: 1px solid #1e293b !important;
    border-radius: 10px !important; margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary { color: #e2e8f0 !important; background: #0f172a !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #080c14 !important; border-right: 1px solid #1e293b; }

/* Inputs */
[data-testid="stTextInput"] input {
    background: #0f172a !important; border: 1px solid #334155 !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
}

/* Metric */
[data-testid="metric-container"] { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 12px; }

/* Divider */
hr { border-color: #1e293b !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

/* Custom components */
.page-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.2rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(135deg, #f97316, #fb923c, #fbbf24);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; padding: 10px 0 4px;
}
.sub-title { text-align: center; color: #475569; font-size: 12px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 20px; }

.league-bar {
    background: #0f172a; border-left: 3px solid #f97316;
    padding: 7px 14px; border-radius: 6px; font-weight: 700; font-size: 13px;
    letter-spacing: 1px; text-transform: uppercase; color: #f97316; margin: 18px 0 8px;
}

.pick-card {
    background: linear-gradient(135deg, #0f2d1a, #0f1f2d);
    border: 1px solid #22c55e; border-radius: 12px;
    padding: 20px; text-align: center;
}
.pick-label { font-family: 'Syne', sans-serif !important; font-size: 1.5rem; font-weight: 800; color: #22c55e; }
.conf-bar-bg { background: #1e293b; border-radius: 4px; height: 6px; margin-top: 10px; overflow: hidden; }
.conf-bar-fill { height: 6px; border-radius: 4px; background: linear-gradient(90deg, #f97316, #22c55e); }

.stat-box { background: #0f172a; border: 1px solid #1e293b; border-top: 2px solid #f97316; border-radius: 10px; padding: 14px; }
.stat-row { display: flex; justify-content: space-between; font-size: 12px; padding: 5px 0; border-bottom: 1px solid #1e293b; }
.stat-row:last-child { border-bottom: none; }
.stat-label { color: #64748b; }
.stat-val { font-weight: 700; color: #f8fafc; }

.live-banner {
    background: #7f1d1d; border: 1px solid #ef4444; color: #fca5a5;
    border-radius: 8px; padding: 8px 14px; font-weight: 700; font-size: 14px;
    display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}
.live-dot { width:8px; height:8px; background:#ef4444; border-radius:50%; display:inline-block; animation: pulse 1s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.2} }

.slip-item {
    background: #0f172a; border: 1px solid #1e293b; border-radius: 10px;
    padding: 14px 16px; margin-bottom: 8px;
}
.slip-match { font-size: 13px; font-weight: 700; color: #e2e8f0; }
.slip-meta { font-size: 11px; color: #475569; margin-bottom: 6px; }
.slip-pick { font-size: 13px; color: #f97316; font-weight: 700; }
.slip-conf { font-size: 11px; color: #22c55e; }

.risk-badge {
    border-radius: 8px; padding: 10px 0; text-align: center;
    font-family: 'Syne', sans-serif; font-weight: 800; font-size: 14px;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;
}

.acc-row {
    background: #0f172a; border: 1px solid #1e293b; border-radius: 8px;
    padding: 10px 14px; margin-bottom: 6px; display: flex;
    justify-content: space-between; align-items: center; font-size: 12px;
}
.acc-match { color: #cbd5e1; font-weight: 700; }
.acc-pick  { color: #94a3b8; font-size: 11px; }
.acc-win   { color: #22c55e; font-weight: 900; font-size: 16px; }
.acc-loss  { color: #ef4444; font-weight: 900; font-size: 16px; }

.ref-tag {
    background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.3);
    color: #fbbf24; font-size: 11px; padding: 3px 8px; border-radius: 4px;
    text-decoration: none; display: inline-block; margin-top: 6px;
}

.no-play { color: #475569; font-size: 12px; font-style: italic; padding: 10px; text-align: center; }
</style>

“””, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# CONFIG  (move API key to st.secrets in prod)

# ─────────────────────────────────────────────

API_KEY = st.secrets.get(“APIFOOTBALL_KEY”, “4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a”)

today      = datetime.utcnow() + timedelta(hours=1)
today_str  = today.strftime(’%Y-%m-%d’)
yest_str   = (today - timedelta(days=1)).strftime(’%Y-%m-%d’)
week_str   = (today + timedelta(days=7)).strftime(’%Y-%m-%d’)
past_str   = (today - timedelta(days=90)).strftime(’%Y-%m-%d’)

TOP_LEAGUES = {
“Premier League”, “Serie A”, “La Liga”, “Bundesliga”, “Ligue 1”,
“UEFA Champions League”, “UEFA Europa League”, “UEFA Europa Conference League”,
“Championship”, “Eredivisie”, “Primeira Liga”, “Süper Lig”, “Major League Soccer”,
}

RISK_TIERS = [
(2,  “SAFE DOUBLE”,    “#16a34a”, 2),
(4,  “MODERATE”,       “#ca8a04”, 4),
(6,  “AGGRESSIVE”,     “#ea580c”, 6),
(8,  “SYSTEM ACCA”,    “#dc2626”, 8),
(12, “WHALE TIER”,     “#7c3aed”, 12),
(15, “QUANT JACKPOT”,  “#1d4ed8”, 15),
(18, “THE GAUNTLET”,   “#c2410c”, 18),
(25, “MOONSHOT”,       “#881337”, 25),
]

# ─────────────────────────────────────────────

# UTILITIES

# ─────────────────────────────────────────────

def safe_num(v):
if v is None: return 0.0
try: return float(str(v).replace(”%”,””).strip())
except: return 0.0

def match_is_live(status: str) -> bool:
“”“Returns True only for genuinely live statuses.”””
if not status: return False
finished_tokens = {“finished”, “postponed”, “cancelled”, “awarded”, “abandoned”, “”}
if status.lower() in finished_tokens: return False
if status.isdigit(): return True          # e.g. “45”, “90+2”
live_tokens = {“ht”, “et”, “pen”, “live”, “in play”}
return any(t in status.lower() for t in live_tokens)

# ─────────────────────────────────────────────

# DATA FETCHING

# ─────────────────────────────────────────────

@st.cache_data(ttl=600)
def fetch_team_stats(team_id, venue):
url = (f”https://apiv3.apifootball.com/?action=get_events”
f”&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}”)
try:
res = requests.get(url, timeout=10).json()
except Exception:
return None, 0

```
s = {"gf":0,"ga":0,"cf":0,"ca":0,"sotf":0,"sota":0,"shotsf":0,"shotsa":0,"cards":0,"cnt":0}
if not isinstance(res, list):
    return None, 0

venue_key = "match_hometeam_id" if venue == "home" else "match_awayteam_id"
finished  = [m for m in res if m.get("match_status","").lower() == "finished"]
relevant  = [m for m in finished if m.get(venue_key) == team_id][-5:]

for m in relevant:
    is_h = m.get("match_hometeam_id") == team_id
    s["gf"] += safe_num(m.get("match_hometeam_score" if is_h else "match_awayteam_score"))
    s["ga"] += safe_num(m.get("match_awayteam_score" if is_h else "match_hometeam_score"))
    for row in m.get("statistics", []):
        t_v = safe_num(row.get("home" if is_h else "away"))
        o_v = safe_num(row.get("away" if is_h else "home"))
        st_ = row.get("type","")
        if st_ == "Corners":          s["cf"] += t_v; s["ca"] += o_v
        elif st_ == "Yellow Cards":   s["cards"] += t_v
        elif st_ == "Shots On Goal":  s["sotf"] += t_v; s["sota"] += o_v
        elif st_ == "Shots Total":    s["shotsf"] += t_v; s["shotsa"] += o_v
    s["cnt"] += 1

n = s["cnt"]
if n == 0:
    return None, 0
return {k: v/n for k,v in s.items() if k != "cnt"}, n
```

@st.cache_data(ttl=600)
def fetch_fixtures(date_from, date_to):
url = (f”https://apiv3.apifootball.com/?action=get_events”
f”&from={date_from}&to={date_to}&APIkey={API_KEY}”)
try:
res = requests.get(url, timeout=15).json()
if isinstance(res, list):
return [m for m in res if m.get(“league_name”) in TOP_LEAGUES]
except Exception:
pass
return []

# ─────────────────────────────────────────────

# PICK ENGINE

# ─────────────────────────────────────────────

CORNER_MOD = {“La Liga”: 0.80, “Serie A”: 0.90}

def generate_pick(h, a, league):
“””
Returns list of (label, market_type, line, confidence).
Sorted best-first. Empty list = no play.
“””
mod  = CORNER_MOD.get(league, 1.0)
pg   = ((h[“gf”]+a[“ga”])/2) + ((a[“gf”]+h[“ga”])/2)
pc   = (((h[“cf”]+a[“ca”])/2) + ((a[“cf”]+h[“ca”])/2)) * mod
psot = ((h[“sotf”]+a[“sota”])/2) + ((a[“sotf”]+h[“sota”])/2)
pcd  = h[“cards”] + a[“cards”]

```
plays = []

def add(label, mtype, line, raw_edge, weight):
    conf = min(99.0, 65.0 + (raw_edge / max(line,0.01)) * weight)
    plays.append((label, mtype, line, round(conf,1)))

# Goals
if pg >= 2.8:
    line = 3.5 if pg >= 4.0 else 2.5 if pg >= 3.0 else 1.5
    add(f"⚽ Over {line} Goals",  "over_goals",  line, pg-line, 100)
elif pg <= 2.2:
    line = 1.5 if pg <= 1.2 else 2.5 if pg <= 2.0 else 3.5
    add(f"🔒 Under {line} Goals", "under_goals", line, line-pg, 100)

# Corners
if pc >= 9.5:
    valid = [l for l in [7.5,8.5,9.5,10.5,11.5,12.5,13.5] if l <= pc-1.5]
    if valid: add(f"🔥 Over {max(valid)} Corners",  "over_corners",  max(valid), pc-max(valid), 80)
elif pc <= 8.5:
    valid = [l for l in [6.5,7.5,8.5,9.5,10.5,11.5] if l >= pc+1.5]
    if valid: add(f"🛡️ Under {min(valid)} Corners", "under_corners", min(valid), min(valid)-pc, 80)

# Cards
if pcd >= 4.5:
    valid = [l for l in [3.5,4.5,5.5,6.5] if l <= pcd-1.0]
    if valid: add(f"🟨 Over {max(valid)} Cards",  "over_cards",  max(valid), pcd-max(valid), 60)
elif pcd <= 3.5:
    valid = [l for l in [3.5,4.5,5.5] if l >= pcd+1.0]
    if valid: add(f"🧊 Under {min(valid)} Cards", "under_cards", min(valid), min(valid)-pcd, 60)

# Shots on target
if psot >= 8.5:
    valid = [l for l in [7.5,8.5,9.5,10.5,11.5] if l <= psot-1.5]
    if valid: add(f"🎯 Over {max(valid)} SOT",  "over_sot",  max(valid), psot-max(valid), 70)
elif psot <= 7.0:
    valid = [l for l in [6.5,7.5,8.5,9.5] if l >= psot+1.5]
    if valid: add(f"🧱 Under {min(valid)} SOT", "under_sot", min(valid), min(valid)-psot, 70)

plays.sort(key=lambda x: x[3], reverse=True)
return plays
```

def top_pick(h, a, league):
plays = generate_pick(h, a, league)
return plays[0] if plays else (“⚠️ NO PLAY”, “none”, 0, 0)

def check_result(p_type, thresh, match):
“”“Returns True/False/None (None = unverifiable market).”””
goals = safe_num(match.get(“match_hometeam_score”,0)) + safe_num(match.get(“match_awayteam_score”,0))
corners = cards = sot = None

```
for row in match.get("statistics", []):
    val = safe_num(row.get("home",0)) + safe_num(row.get("away",0))
    t   = row.get("type","")
    if t == "Corners":        corners = val
    elif t == "Yellow Cards": cards   = val
    elif t == "Shots On Goal":sot     = val

checks = {
    "over_goals":   lambda: goals   > thresh if goals   is not None else None,
    "under_goals":  lambda: goals   < thresh if goals   is not None else None,
    "over_corners": lambda: corners > thresh if corners is not None else None,
    "under_corners":lambda: corners < thresh if corners is not None else None,
    "over_cards":   lambda: cards   > thresh if cards   is not None else None,
    "under_cards":  lambda: cards   < thresh if cards   is not None else None,
    "over_sot":     lambda: sot     > thresh if sot     is not None else None,
    "under_sot":    lambda: sot     < thresh if sot     is not None else None,
}
fn = checks.get(p_type)
return fn() if fn else None
```

# ─────────────────────────────────────────────

# SIDEBAR

# ─────────────────────────────────────────────

with st.sidebar:
st.markdown(”<div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#f97316;padding:8px 0 4px;'>⚡ RADAR TERMINAL</div>”, unsafe_allow_html=True)
st.caption(f”Session date: {today_str}”)

```
if st.button("🧹 Clear Cache & Refresh"):
    st.cache_data.clear()
    st.rerun()

auto_refresh = st.toggle("🔄 Auto-refresh (60s)", value=False)
if auto_refresh:
    st.success("🟢 LIVE MODE")
    import time; time.sleep(60); st.rerun()

st.divider()
st.caption("ℹ️ Data: last 5 venue-specific matches · TTL 10 min")
st.caption("⚠️ For entertainment purposes only.")
```

# ─────────────────────────────────────────────

# HEADER

# ─────────────────────────────────────────────

st.markdown(”<div class='page-title'>🏦 Institutional Quant Radar</div>”, unsafe_allow_html=True)
st.markdown(”<div class='sub-title'>algorithmic edge · verified fixtures · real-time data</div>”, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# LOAD DATA (once, shared across tabs)

# ─────────────────────────────────────────────

with st.spinner(“Loading fixture data…”):
daily   = fetch_fixtures(today_str, today_str)
weekly  = fetch_fixtures(today_str, week_str)
yest    = fetch_fixtures(yest_str,  yest_str)

# ─────────────────────────────────────────────

# TABS

# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([“🎟️ Auto-Acca”, “📝 Weekly Slip”, “🔥 Daily Picks”, “📊 Accuracy”])

# ════════════════════════════════════════════

# TAB 1 — AUTO ACCA

# ════════════════════════════════════════════

with tab1:
st.markdown(”### 🎟️ Algorithmic Ticket Generator”)
st.caption(“Select a target odds tier to generate the best picks.”)

```
cols = st.columns(4)
selection = None
for i, (odds, label, color, n_picks) in enumerate(RISK_TIERS):
    with cols[i % 4]:
        emoji = ["🟢","🟡","🟠","🔴","🟣","🔵","🔥","🌌"][i]
        if st.button(f"{emoji} {odds}.0x", use_container_width=True):
            selection = (n_picks, label, color)

if selection:
    n_picks, label, color = selection
    st.markdown(f"<div class='risk-badge' style='background:{color}22;border:1px solid {color};color:{color};'>{label} — TOP {n_picks} PICKS</div>", unsafe_allow_html=True)

    valid_picks = []
    with st.spinner("Running edge model across all markets…"):
        for m in daily:
            h_st, h_n = fetch_team_stats(m.get("match_hometeam_id"), "home")
            a_st, a_n = fetch_team_stats(m.get("match_awayteam_id"), "away")
            if h_st and a_st:
                pk, ptype, thresh, conf = top_pick(h_st, a_st, m.get("league_name",""))
                if conf > 0:
                    valid_picks.append({
                        "match":  f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}",
                        "league": m.get("league_name",""),
                        "time":   m.get("match_time",""),
                        "pick":   pk,
                        "conf":   conf,
                        "h_n":    h_n,
                        "a_n":    a_n,
                    })

    valid_picks.sort(key=lambda x: x["conf"], reverse=True)
    shown = valid_picks[:n_picks]

    if not shown:
        st.warning("No qualifying picks found for today. Try again later.")
    else:
        for p in shown:
            data_quality = "🟢" if min(p["h_n"], p["a_n"]) >= 4 else "🟡" if min(p["h_n"], p["a_n"]) >= 2 else "🔴"
            st.markdown(f"""
            <div class='slip-item'>
              <div class='slip-meta'>🏆 {p['league']} &nbsp;·&nbsp; 🕒 {p['time']} &nbsp;·&nbsp; {data_quality} {min(p['h_n'], p['a_n'])} games sampled</div>
              <div class='slip-match'>{p['match']}</div>
              <div style='display:flex;justify-content:space-between;align-items:center;margin-top:6px;'>
                <div class='slip-pick'>{p['pick']}</div>
                <div class='slip-conf'>{p['conf']}% edge</div>
              </div>
              <div class='conf-bar-bg'><div class='conf-bar-fill' style='width:{min(p['conf'],99)}%;'></div></div>
            </div>
            """, unsafe_allow_html=True)
```

# ════════════════════════════════════════════

# TAB 2 — WEEKLY SLIP

# ════════════════════════════════════════════

with tab2:
st.markdown(”### 📝 Weekly Fixture Browser”)
search_q = st.text_input(“🔍 Filter by team name:”, placeholder=“e.g. Arsenal, Milan, PSG”)

```
filtered = [
    m for m in weekly
    if not search_q
    or search_q.lower() in m.get("match_hometeam_name","").lower()
    or search_q.lower() in m.get("match_awayteam_name","").lower()
]

if not filtered:
    st.info("No fixtures found for that search.")
else:
    dates = sorted(set(m.get("match_date","") for m in filtered))
    for d in dates:
        st.markdown(f"#### 📅 {d}")
        day_matches = [m for m in filtered if m.get("match_date") == d]
        for m in day_matches:
            with st.expander(f"🕒 {m.get('match_time','')} | {m.get('match_hometeam_name','')} vs {m.get('match_awayteam_name','')}"):
                h_st, h_n = fetch_team_stats(m.get("match_hometeam_id"), "home")
                a_st, a_n = fetch_team_stats(m.get("match_awayteam_id"), "away")
                if h_st and a_st:
                    plays = generate_pick(h_st, a_st, m.get("league_name",""))
                    if plays:
                        c1, c2 = st.columns(2)
                        with c1:
                            for pk, _, _, conf in plays[:3]:
                                st.markdown(f"<div style='background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:10px;margin-bottom:6px;'>"
                                            f"<div style='color:#f97316;font-weight:700;font-size:13px;'>{pk}</div>"
                                            f"<div style='color:#22c55e;font-size:11px;margin-top:4px;'>{conf}% edge</div>"
                                            f"<div class='conf-bar-bg'><div class='conf-bar-fill' style='width:{conf}%;'></div></div></div>",
                                            unsafe_allow_html=True)
                        with c2:
                            pg  = ((h_st['gf']+a_st['ga'])/2)+((a_st['gf']+h_st['ga'])/2)
                            pc  = ((h_st['cf']+a_st['ca'])/2)+((a_st['cf']+h_st['ca'])/2)
                            pcd = h_st['cards']+a_st['cards']
                            st.markdown(f"""<div class='stat-box'>
                                <div style='color:#f97316;font-size:10px;font-weight:700;margin-bottom:8px;letter-spacing:1px;'>PROJECTIONS</div>
                                <div class='stat-row'><span class='stat-label'>xGoals</span><span class='stat-val'>{pg:.2f}</span></div>
                                <div class='stat-row'><span class='stat-label'>xCorners</span><span class='stat-val'>{pc:.1f}</span></div>
                                <div class='stat-row'><span class='stat-label'>xCards</span><span class='stat-val'>{pcd:.1f}</span></div>
                                <div class='stat-row'><span class='stat-label'>Home sample</span><span class='stat-val'>{h_n} games</span></div>
                                <div class='stat-row'><span class='stat-label'>Away sample</span><span class='stat-val'>{a_n} games</span></div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='no-play'>No qualifying edge found for this match.</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='no-play'>Insufficient data for this match.</div>", unsafe_allow_html=True)
```

# ════════════════════════════════════════════

# TAB 3 — DAILY PICKS

# ════════════════════════════════════════════

with tab3:
st.markdown(”### 🔥 All System Picks Today”)

```
if not daily:
    st.info("No top-league fixtures found for today.")
else:
    leagues = sorted(set(m.get("league_name","") for m in daily))
    for league in leagues:
        st.markdown(f"<div class='league-bar'>🏆 {league}</div>", unsafe_allow_html=True)
        for m in [g for g in daily if g.get("league_name") == league]:
            status   = m.get("match_status","")
            is_live  = match_is_live(status)
            label    = f"{'🔴 LIVE ' if is_live else ''}🕒 {m.get('match_time','')} | {m.get('match_hometeam_name','')} vs {m.get('match_awayteam_name','')}"

            with st.expander(label):
                if is_live:
                    st.markdown(f"<div class='live-banner'><span class='live-dot'></span> LIVE: {m.get('match_hometeam_score','-')} – {m.get('match_awayteam_score','-')} &nbsp;({status}')</div>", unsafe_allow_html=True)

                h_st, h_n = fetch_team_stats(m.get("match_hometeam_id"), "home")
                a_st, a_n = fetch_team_stats(m.get("match_awayteam_id"), "away")

                if not (h_st and a_st):
                    st.caption("⚠️ Insufficient historical data for this fixture.")
                    continue

                plays = generate_pick(h_st, a_st, league)
                pk_label, _, _, pk_conf = plays[0] if plays else ("⚠️ NO PLAY","none",0,0)

                ref     = m.get("match_referee","")
                ref_url = f"https://www.google.com/search?q={ref.replace(' ','+')}+referee+stats"
                ref_html= f"<a href='{ref_url}' target='_blank' class='ref-tag'>⚖️ {ref}</a>" if ref else "<span class='ref-tag' style='opacity:0.5;'>⚖️ Referee TBD</span>"

                c1, c2 = st.columns([3, 1.5])
                with c1:
                    bar_w = min(pk_conf, 99) if pk_conf else 0
                    st.markdown(f"""
                    <div class='pick-card'>
                      <div class='pick-label'>{pk_label}</div>
                      <div style='color:#4ade80;font-size:13px;margin-top:6px;'>{f'{pk_conf}% confidence' if pk_conf else ''}</div>
                      <div class='conf-bar-bg' style='margin-top:8px;'><div class='conf-bar-fill' style='width:{bar_w}%;'></div></div>
                      <div style='margin-top:12px;'>{ref_html}</div>
                      {'<div style="color:#475569;font-size:11px;margin-top:6px;">🟡 Low sample — treat with caution</div>' if min(h_n,a_n)<3 else ''}
                    </div>""", unsafe_allow_html=True)

                    if len(plays) > 1:
                        st.markdown("<div style='margin-top:10px;color:#475569;font-size:11px;font-weight:700;letter-spacing:1px;'>OTHER EDGES</div>", unsafe_allow_html=True)
                        for pl,_,_,cf in plays[1:3]:
                            st.markdown(f"<div style='font-size:12px;color:#64748b;padding:4px 0;'>{pl} &nbsp; <span style='color:#22c55e;'>{cf}%</span></div>", unsafe_allow_html=True)

                with c2:
                    pg  = ((h_st['gf']+a_st['ga'])/2)+((a_st['gf']+h_st['ga'])/2)
                    pc  = ((h_st['cf']+a_st['ca'])/2)+((a_st['cf']+h_st['ca'])/2)
                    pcd = h_st['cards']+a_st['cards']
                    pst = h_st['sotf']+a_st['sotf']
                    st.markdown(f"""<div class='stat-box'>
                        <div style='color:#f97316;font-size:10px;font-weight:700;margin-bottom:10px;letter-spacing:2px;'>MATH EDGE</div>
                        <div class='stat-row'><span class='stat-label'>xGoals</span>   <span class='stat-val'>{pg:.2f}</span></div>
                        <div class='stat-row'><span class='stat-label'>xCorners</span> <span class='stat-val'>{pc:.1f}</span></div>
                        <div class='stat-row'><span class='stat-label'>xCards</span>   <span class='stat-val'>{pcd:.1f}</span></div>
                        <div class='stat-row'><span class='stat-label'>xSOT</span>     <span class='stat-val'>{pst:.1f}</span></div>
                        <div class='stat-row'><span class='stat-label'>H sample</span> <span class='stat-val'>{h_n}g</span></div>
                        <div class='stat-row'><span class='stat-label'>A sample</span> <span class='stat-val'>{a_n}g</span></div>
                    </div>""", unsafe_allow_html=True)
```

# ════════════════════════════════════════════

# TAB 4 — ACCURACY

# ════════════════════════════════════════════

with tab4:
st.markdown(”### 📊 Yesterday’s System Accuracy”)
st.caption(f”Results for {yest_str} — all markets evaluated (goals, corners, cards, SOT)”)

```
finished = [m for m in yest if m.get("match_status","").lower() == "finished"]

if not finished:
    st.info("No finished top-league matches found for yesterday.")
else:
    wins = losses = no_data = unverifiable = 0
    results = []

    for m in finished:
        h_st, _ = fetch_team_stats(m.get("match_hometeam_id"), "home")
        a_st, _ = fetch_team_stats(m.get("match_awayteam_id"), "away")
        if not (h_st and a_st):
            no_data += 1
            continue

        pk_label, p_type, thresh, conf = top_pick(h_st, a_st, m.get("league_name",""))
        if conf == 0:
            continue

        outcome = check_result(p_type, thresh, m)
        match_str = f"{m.get('match_hometeam_name','')} vs {m.get('match_awayteam_name','')}"
        score_str = f"{m.get('match_hometeam_score','-')} – {m.get('match_awayteam_score','-')}"

        if outcome is True:
            wins += 1
            results.append(("✅", match_str, pk_label, score_str, conf))
        elif outcome is False:
            losses += 1
            results.append(("❌", match_str, pk_label, score_str, conf))
        else:
            unverifiable += 1
            results.append(("❓", match_str, pk_label, score_str, conf))

    total_verifiable = wins + losses
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("✅ Wins",  wins)
    m2.metric("❌ Losses", losses)
    m3.metric("Win Rate", f"{(wins/total_verifiable*100):.1f}%" if total_verifiable else "—")
    m4.metric("❓ No data", unverifiable)

    st.divider()
    for icon, match_s, pick_s, score_s, conf in results:
        st.markdown(f"""
        <div class='acc-row'>
          <div>
            <div class='acc-match'>{icon} {match_s} <span style='color:#475569;font-size:11px;'>({score_s})</span></div>
            <div class='acc-pick'>{pick_s} &nbsp;·&nbsp; {conf}% predicted confidence</div>
          </div>
        </div>""", unsafe_allow_html=True)
```
