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
</style>
""", unsafe_allow_html=True)

# ── CONFIG ───────────────────────────────────────────────────────────────────
API_KEY       = st.secrets.get("APIFOOTBALL_KEY", "4ca129dfac12e50067e9a115f4d50328619188357f590208bcbacba23789307a")
now           = datetime.utcnow() + timedelta(hours=1)
today_str     = now.strftime('%Y-%m-%d')
yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')
week_out_str  = (now + timedelta(days=7)).strftime('%Y-%m-%d')
past_str      = (now - timedelta(days=120)).strftime('%Y-%m-%d')

FINISHED_STATUSES = {"Finished","FT","AET","PEN","Awarded","Cancelled","Postponed","Suspended","Abandoned"}
LIVE_STATUSES     = {"1H","HT","2H","ET","P","LIVE","Break"}

SPORTSBOOK_TIER_A = {
    "Premier League","Serie A","La Liga","Bundesliga","Ligue 1",
    "UEFA Champions League","UEFA Europa League","UEFA Europa Conference League","Championship",
}
SPORTSBOOK_TIER_B = {
    "Eredivisie","Primeira Liga","Süper Lig","Scottish Premiership","Scottish Premier League",
    "Belgian Pro League","Belgian First Division A","Swiss Super League",
    "Austrian Football Bundesliga","Austrian Bundesliga",
    "Allsvenskan","Eliteserien","Superliga","Major League Soccer",
    "Brasileirao Serie A","Argentine Primera División",
}
SPORTSBOOK_TIER_C = {
    "Veikkausliiga","SuperLiga","Serbian SuperLiga","Greek Super League",
    "Czech First League","Polish Ekstraklasa","Saudi Pro League",
    "Saudi Professional League","J1 League",
}
TOP_LEAGUES = SPORTSBOOK_TIER_A | SPORTSBOOK_TIER_B | SPORTSBOOK_TIER_C

LEAGUE_PROFILE = {
    "La Liga":(0.90,0.85,1.05,0.0),"Serie A":(0.88,0.92,1.10,0.0),
    "Bundesliga":(1.05,0.95,0.90,0.0),"Premier League":(1.00,1.00,1.00,0.0),
    "Ligue 1":(0.95,1.00,1.05,0.0),"UEFA Champions League":(1.00,1.00,1.00,0.0),
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
@st.cache_data(ttl=600,show_spinner=False)
def fetch_stats(team_id,venue):
    url=f"https://apiv3.apifootball.com/?action=get_events&team_id={team_id}&from={past_str}&to={today_str}&APIkey={API_KEY}"
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
def fetch_events(date_from,date_to):
    url=f"https://apiv3.apifootball.com/?action=get_events&from={date_from}&to={date_to}&APIkey={API_KEY}"
    try:
        res=requests.get(url,timeout=15).json()
        if isinstance(res,list):
            return [m for m in res if m.get("league_name") in TOP_LEAGUES]
        return []
    except: return []

# ── EDGE ENGINE ───────────────────────────────────────────────────────────────
def generate_ai_pick(h_st,a_st,league,sniper_mode=False):
    gm,cm,kdm,conf_pen=LEAGUE_PROFILE.get(league,DEFAULT_PROFILE)
    proj_g=(((h_st['gf']+a_st['ga'])/2)+((a_st['gf']+h_st['ga'])/2))*gm
    proj_c=(((h_st['cf']+a_st['ca'])/2)+((a_st['cf']+h_st['ca'])/2))*cm
    proj_sot=((h_st['sotf']+a_st['sota'])/2)+((a_st['sotf']+h_st['sota'])/2)
    proj_cd=(h_st['cards']+a_st['cards'])*kdm
    sigs={
        "Both score form":h_st['gf']>1.0 and a_st['gf']>0.8,
        "High scoring":proj_g>=2.8,"Low scoring":proj_g<=2.2,
        "High SOT":proj_sot>=8.0,"Low SOT":proj_sot<=6.5,
        "High corners":proj_c>=9.0,"Low corners":proj_c<=8.0,
        "SOT confirms goals":proj_g>=2.8 and proj_sot>=8.0,
        "SOT confirms under":proj_g<=2.2 and proj_sot<=6.5,
    }
    base=65.0-conf_pen; min_conf=82.0 if sniper_mode else 72.0; plays=[]

    if proj_g>=2.8:
        line=3.5 if proj_g>=4.2 else 2.5 if proj_g>=3.2 else 1.5; gap=proj_g-line
        if gap>=0.8:
            conf=min(99.0,base+(gap/max(line,.01))*90)
            if sigs["SOT confirms goals"]: conf=min(99.0,conf+5)
            if sigs["Both score form"]:    conf=min(99.0,conf+3)
            plays.append((f"⚽ Over {line} Goals","goals",line,conf,{k:v for k,v in sigs.items() if k in ("SOT confirms goals","Both score form","High corners")}))
    elif proj_g<=2.2:
        line=1.5 if proj_g<=1.2 else 2.5 if proj_g<=1.8 else 3.5; gap=line-proj_g
        if gap>=0.8:
            conf=min(99.0,base+(gap/max(line,.01))*90)
            if sigs["SOT confirms under"]: conf=min(99.0,conf+5)
            plays.append((f"🔒 Under {line} Goals","under_goals",line,conf,{k:v for k,v in sigs.items() if k in ("SOT confirms under","Low corners","Low SOT")}))

    if proj_c>=10.0:
        valid=[l for l in [8.5,9.5,10.5,11.5,12.5,13.5] if l<=proj_c-1.8]
        if valid:
            line=max(valid);gap=proj_c-line;conf=min(99.0,base+(gap/max(line,.01))*75)
            if sigs["High SOT"]: conf=min(99.0,conf+4)
            plays.append((f"🔥 Over {line} Corners","corners",line,conf,{k:v for k,v in sigs.items() if k in ("High SOT","High scoring")}))
    elif proj_c<=8.0:
        valid=[l for l in [6.5,7.5,8.5,9.5] if l>=proj_c+1.8]
        if valid:
            line=min(valid);gap=line-proj_c;conf=min(99.0,base+(gap/max(line,.01))*75)
            if sigs["Low SOT"]: conf=min(99.0,conf+4)
            plays.append((f"🛡️ Under {line} Corners","under_corners",line,conf,{k:v for k,v in sigs.items() if k in ("Low SOT","Low scoring")}))

    if proj_cd>=5.0:
        valid=[l for l in [3.5,4.5,5.5,6.5] if l<=proj_cd-1.5]
        if valid:
            line=max(valid);gap=proj_cd-line;conf=min(99.0,base+(gap/max(line,.01))*55)
            plays.append((f"🟨 Over {line} Cards","cards",line,conf,{"High card league":kdm>=1.1}))
    elif proj_cd<=2.5:
        valid=[l for l in [3.5,4.5] if l>=proj_cd+1.5]
        if valid:
            line=min(valid);gap=line-proj_cd;conf=min(99.0,base+(gap/max(line,.01))*55)
            plays.append((f"🧊 Under {line} Cards","under_cards",line,conf,{"Low card league":kdm<=0.92}))

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
    sniper_mode=st.toggle("🎯 Sniper Mode (82%+)",value=False)
    if sniper_mode:
        st.markdown("<div style='background:#1a0a00;border:1px solid #f97316;border-radius:8px;padding:10px;font-size:12px;color:#fb923c;'>⚡ Ultra-high-confidence only.</div>",unsafe_allow_html=True)
    st.divider()
    st.markdown("**📚 Book Coverage Filter**")
    tier_a=st.checkbox("Tier A — All Books",value=True)
    tier_b=st.checkbox("Tier B — Most Books",value=True)
    tier_c=st.checkbox("Tier C — Specialist Books",value=False)
    st.divider()
    st.markdown("**💰 Kelly Calculator**")
    kelly_divisor=st.slider("Kelly fraction (safety)",2,8,4)
    bankroll=st.number_input("Bankroll",min_value=10.0,value=1000.0,step=50.0)
    st.divider()
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

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>🏦 Institutional Quant Radar</div>",unsafe_allow_html=True)
mode_tag="🎯 SNIPER" if sniper_mode else "STANDARD"
st.markdown(f"<div class='page-sub'>ALGORITHMIC EDGE · {len(ACTIVE_LEAGUES)} LEAGUES · {mode_tag} MODE · UPCOMING ONLY</div>",unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Fetching fixtures…"):
    raw_daily =fetch_events(today_str,today_str)
    raw_weekly=fetch_events(today_str,week_out_str)

daily_matches  =[m for m in raw_daily  if m.get("league_name") in ACTIVE_LEAGUES and is_upcoming(m)]
daily_live     =[m for m in raw_daily  if m.get("league_name") in ACTIVE_LEAGUES and is_live_status(m.get("match_status",""))]
daily_finished =[m for m in raw_daily  if m.get("league_name") in ACTIVE_LEAGUES and is_finished(m.get("match_status",""))]
weekly_matches =[m for m in raw_weekly if m.get("league_name") in ACTIVE_LEAGUES and is_upcoming(m)]

# ── QUICK STATS ───────────────────────────────────────────────────────────────
c1,c2,c3,c4=st.columns(4)
c1.metric("Upcoming Today",len(daily_matches))
c2.metric("🔴 Live Now",len(daily_live))
c3.metric("✅ Finished",len(daily_finished))
c4.metric("This Week",len(weekly_matches))
st.write("")

# ── TABS ──────────────────────────────────────────────────────────────────────
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
                    pick,pt,ln,cf,sg,_=generate_ai_pick(h_st,a_st,m.get("league_name",""),sniper_mode)
                    if cf>0:
                        valid_picks.append({"match":f"{m.get('match_hometeam_name')} vs {m.get('match_awayteam_name')}","league":m.get("league_name",""),"pick":pick,"conf":cf,"time":m.get("match_time",""),"sigs":sg,"tier":sportsbook_tier(m.get("league_name",""))})
        valid_picks.sort(key=lambda x:x["conf"],reverse=True); chosen=valid_picks[:n_picks]
        if not chosen:
            st.markdown("<div class='empty-state'><div class='empty-state-icon'>🎯</div><div class='empty-state-text'>No picks meet the threshold today</div><div class='empty-state-sub'>Try disabling Sniper Mode or enabling more book tiers</div></div>",unsafe_allow_html=True)
        else:
            avg_conf=sum(p["conf"] for p in chosen)/len(chosen)
            m1,m2,m3=st.columns(3);m1.metric("Legs",len(chosen));m2.metric("Avg Confidence",f"{avg_conf:.1f}%");m3.metric("Mode","🎯 SNIPER" if sniper_mode else "STANDARD")
            st.markdown("<div class='slip-box'>",unsafe_allow_html=True)
            for i,p in enumerate(chosen,1):
                st.markdown(f"<div class='slip-row'><div class='slip-league'>{i}. {p['league']} · {p['time']} &nbsp; {book_tier_badge(p['tier'])}</div><div class='slip-match'>{p['match']}</div><div class='slip-pick' style='color:{color};'>{p['pick']}</div>{conf_bar_html(p['conf'],color)}{signals_html(p['sigs'])}</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

# ══ TAB 2 ═════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📝 Weekly Fixture Browser")
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
    view_mode=st.radio("Show",["⏳ Upcoming only","🔴 Live now","✅ Finished today"],horizontal=True,index=0)
    show_matches=daily_matches if view_mode=="⏳ Upcoming only" else daily_live if view_mode=="🔴 Live now" else daily_finished
    if sniper_mode: st.markdown("<div class='warning-box'>🎯 Sniper Mode — only picks ≥82% confidence shown.</div>",unsafe_allow_html=True)
    if not show_matches:
        st.markdown("<div class='empty-state'><div class='empty-state-icon'>📭</div><div class='empty-state-text'>No matches in this category right now</div></div>",unsafe_allow_html=True)
    else:
        for l_name in sorted(set(m.get("league_name","") for m in show_matches)):
            tier=sportsbook_tier(l_name)
            st.markdown(f"<div class='league-header'>🏆 {l_name} &nbsp; {book_tier_badge(tier)}</div>",unsafe_allow_html=True)
            for m in [g for g in show_matches if g.get("league_name")==l_name]:
                status=m.get("match_status",""); home=m.get("match_hometeam_name","?"); away=m.get("match_awayteam_name","?"); t=m.get("match_time","")
                live=is_live_status(status); prefix="🔴 LIVE · " if live else "✅ FT · " if is_finished(status) else ""
                with st.expander(f"{prefix}🕒 {t} | {home} vs {away}"):
                    if live: st.markdown(f"<div class='live-banner'><span class='live-dot'></span>LIVE: {m.get('match_hometeam_score','?')} – {m.get('match_awayteam_score','?')} ({status}')</div>",unsafe_allow_html=True)
                    with st.spinner("Fetching stats…"):
                        h_st,h_cnt=fetch_stats(m.get("match_hometeam_id"),"home")
                        a_st,a_cnt=fetch_stats(m.get("match_awayteam_id"),"away")
                    if not h_st or not a_st: st.warning("⚠️ Insufficient data."); continue
                    if h_cnt<3 or a_cnt<3: st.info(f"📉 Low sample: {home}({h_cnt}) / {away}({a_cnt})")
                    pick,p_type,thresh,conf,sigs,all_plays=generate_ai_pick(h_st,a_st,l_name,sniper_mode)
                    ref=m.get("match_referee","")
                    ref_html=f"<a href='https://www.google.com/search?q={ref.replace(' ','+')}+referee+stats' target='_blank' class='ref-tag'>⚖️ {ref}</a>" if ref else "<span class='ref-tag'>⚖️ TBD</span>"
                    odds_key=f"odds_{m.get('match_id','')}"
                    if odds_key not in st.session_state: st.session_state[odds_key]=1.90
                    c_pick,c_stats=st.columns([3,1.5])
                    with c_pick:
                        is_sniper=conf>=82; card_cls="sniper-card" if is_sniper else "pick-card"; lbl_cls="sniper-label" if is_sniper else "pick-label"
                        badge="<div class='sniper-badge'>🎯 SNIPER PICK</div>" if is_sniper else ""
                        st.markdown(f"<div class='{card_cls}'>{badge}<div class='{lbl_cls}'>{pick}</div>{ref_html}{conf_bar_html(conf,'#f97316' if is_sniper else '#16a34a')}{signals_html(sigs)}</div>",unsafe_allow_html=True)
                        user_odds=st.number_input("Enter bookmaker odds (decimal)",min_value=1.01,max_value=50.0,step=0.05,value=st.session_state[odds_key],key=odds_key)
                        if conf>0 and user_odds>1.0:
                            kelly_stake=kelly_fraction(conf_to_prob(conf),user_odds,kelly_divisor)
                            actual_stake=round(bankroll*kelly_stake/100,2)
                            st.markdown(value_panel_html(conf,user_odds,kelly_divisor)+(f"<div style='text-align:center;margin-top:6px;font-size:13px;color:#64748b;'>= <b style='color:#e2e8f0;'>{actual_stake} units</b></div>" if kelly_stake>0 else ""),unsafe_allow_html=True)
                    with c_stats:
                        gm,cm,kdm,_=LEAGUE_PROFILE.get(l_name,DEFAULT_PROFILE)
                        pg=(((h_st['gf']+a_st['ga'])/2)+((a_st['gf']+h_st['ga'])/2))*gm
                        pc=(((h_st['cf']+a_st['ca'])/2)+((a_st['cf']+h_st['ca'])/2))*cm
                        pcd=(h_st['cards']+a_st['cards'])*kdm; psot=h_st['sotf']+a_st['sotf']
                        st.markdown(f"<div class='stats-panel'><div class='stats-title'>Math Edge</div><div class='stat-row'><span>xG (adj)</span><span class='stat-val'>{pg:.2f}</span></div><div class='stat-row'><span>Corners (adj)</span><span class='stat-val'>{pc:.1f}</span></div><div class='stat-row'><span>Cards (adj)</span><span class='stat-val'>{pcd:.1f}</span></div><div class='stat-row'><span>SOT</span><span class='stat-val'>{psot:.1f}</span></div><div class='stat-row'><span>Sample H/A</span><span class='stat-val'>{h_cnt}/{a_cnt}</span></div></div>",unsafe_allow_html=True)
                        if len(all_plays)>1:
                            st.markdown("<div style='margin-top:10px;font-size:11px;color:#475569;'>Alt plays:</div>",unsafe_allow_html=True)
                            for alt in all_plays[1:3]: st.markdown(f"<div style='font-size:12px;color:#64748b;padding:3px 0;'>• {alt[0]} ({alt[3]:.0f}%)</div>",unsafe_allow_html=True)

# ══ TAB 4 ═════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📊 Yesterday's Accuracy")
    st.markdown(f"<div style='color:#475569;font-size:13px;margin-bottom:16px;'>📅 {yesterday_str}</div>",unsafe_allow_html=True)
    with st.spinner("Fetching results…"):
        yesterday_res=fetch_events(yesterday_str,yesterday_str)
    finished_yday=[m for m in yesterday_res if is_finished(m.get("match_status",""))]
    if not finished_yday:
        st.markdown("<div class='empty-state'><div class='empty-state-icon'>📭</div><div class='empty-state-text'>No finished matches yesterday</div></div>",unsafe_allow_html=True)
    else:
        results_by_type={}; wins=losses=skipped=0
        with st.spinner("Back-testing…"):
            for m in finished_yday:
                if m.get("league_name") not in ACTIVE_LEAGUES: continue
                h_st,_=fetch_stats(m.get("match_hometeam_id"),"home"); a_st,_=fetch_stats(m.get("match_awayteam_id"),"away")
                if not h_st or not a_st: continue
                pick,p_type,thresh,conf,sigs,_=generate_ai_pick(h_st,a_st,m.get("league_name",""),sniper_mode)
                if conf==0 or p_type=="pass": continue
                won=check_result(p_type,thresh,m)
                if won is None: skipped+=1; continue
                results_by_type.setdefault(p_type,{"w":0,"l":0})
                if won: wins+=1;results_by_type[p_type]["w"]+=1
                else: losses+=1;results_by_type[p_type]["l"]+=1
                home=m.get("match_hometeam_name",""); away=m.get("match_awayteam_name",""); hs=m.get("match_hometeam_score","?"); as_=m.get("match_awayteam_score","?")
                tier=sportsbook_tier(m.get("league_name","")); ico="✅" if won else "❌"; cls="acc-win" if won else "acc-loss"
                st.markdown(f"<div class='accuracy-row {cls}'><span style='font-size:18px;'>{ico}</span><div style='flex:1;'><div style='font-weight:600;font-size:13px;'>{home} vs {away}</div><div style='font-size:11px;color:#64748b;'>FT: {hs}–{as_} · {m.get('league_name','')} {book_tier_badge(tier)}</div></div><div style='text-align:right;'><div style='font-family:DM Mono,monospace;font-size:12px;color:#e2e8f0;'>{pick}</div><div style='font-size:11px;color:#475569;'>{conf:.0f}%</div></div></div>",unsafe_allow_html=True)
        total=wins+losses
        if total>0:
            wr=wins/total*100; st.divider()
            mc1,mc2,mc3,mc4=st.columns(4)
            mc1.metric("Win Rate",f"{wr:.1f}%",delta=f"+{wins}W / -{losses}L"); mc2.metric("Picks",total); mc3.metric("Wins",wins); mc4.metric("Losses",losses)
            if results_by_type:
                st.markdown("#### Market Breakdown")
                for pt,rec in sorted(results_by_type.items(),key=lambda x:-(x[1]['w']/(x[1]['w']+x[1]['l']) if x[1]['w']+x[1]['l'] else 0)):
                    t=rec['w']+rec['l'];pct=rec['w']/t*100 if t else 0;c="#16a34a" if pct>=70 else "#ef4444"
                    st.markdown(f"<div style='margin-bottom:10px;'><div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;'><span style='font-weight:600;'>{pt.replace('_',' ').title()}</span><span style='font-family:DM Mono,monospace;color:{c};'>{pct:.0f}% ({t} picks)</span></div><div class='conf-bar-bg'><div class='conf-bar-fill' style='width:{int(pct)}%;background:{c};'></div></div></div>",unsafe_allow_html=True)

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
