import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import numpy as np

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Liability Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  LOGIN SYSTEM
# ─────────────────────────────────────────────
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Login Page UI
        st.markdown("""
        <style>
        .login-box {
            max-width: 400px;
            margin: 80px auto;
            background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
            border: 1px solid rgba(56,139,253,0.25);
            border-radius: 20px;
            padding: 40px 36px;
            text-align: center;
        }
        .login-title {
            color: #f0f6fc;
            font-size: 26px;
            font-weight: 800;
            margin-bottom: 6px;
            font-family: 'Outfit', sans-serif;
        }
        .login-sub {
            color: #8b949e;
            font-size: 13px;
            margin-bottom: 28px;
        }
        </style>
        <div class='login-box'>
            <div style='font-size:48px'>📊</div>
            <div class='login-title'>Liability Sales Dashboard</div>
            <div class='login-sub'>Please login to continue</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
            login_btn = st.button("Login →", use_container_width=True)

            if login_btn:
                correct_user = st.secrets.get("login_username", "admin")
                correct_pass = st.secrets.get("login_password", "admin123")
                if username == correct_user and password == correct_pass:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Galat Username ya Password!")
        st.stop()

check_login()

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

.stApp {
    background: #060d1a;
    background-image:
        radial-gradient(ellipse at 20% 0%, rgba(14,70,140,0.25) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 100%, rgba(6,40,90,0.3) 0%, transparent 60%);
}

/* KPI CARDS */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 6px; }
.kpi-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 20px; }

.kpi-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(56,139,253,0.18);
    border-radius: 16px;
    padding: 18px 18px 14px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, transform 0.2s;
}
.kpi-card:hover { border-color: rgba(56,139,253,0.45); transform: translateY(-2px); }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.c1::before { background: linear-gradient(90deg,#388bfd,#58a6ff); }
.c2::before { background: linear-gradient(90deg,#3fb950,#56d364); }
.c3::before { background: linear-gradient(90deg,#bc8cff,#d2a8ff); }
.c4::before { background: linear-gradient(90deg,#ff7b72,#ffa198); }
.c5::before { background: linear-gradient(90deg,#d29922,#e3b341); }
.c6::before { background: linear-gradient(90deg,#79c0ff,#a5d6ff); }
.c7::before { background: linear-gradient(90deg,#56d364,#85e89d); }

.kpi-icon  { font-size: 20px; margin-bottom: 6px; }
.kpi-label { color:#8b949e; font-size:10px; font-weight:700; letter-spacing:2px; text-transform:uppercase; margin-bottom:5px; }
.kpi-value { color:#f0f6fc; font-size:26px; font-family:'JetBrains Mono',monospace; font-weight:700; line-height:1; margin-bottom:4px; }
.kpi-sub   { color:#484f58; font-size:10px; }

/* TARGET BADGE */
.tgt-above { color:#3fb950; font-size:11px; font-weight:600; }
.tgt-below { color:#ff7b72; font-size:11px; font-weight:600; }

/* SECTION HEADER */
.sec-head {
    display:flex; align-items:center; gap:10px;
    margin:22px 0 12px;
    color:#58a6ff; font-size:11px; font-weight:700;
    letter-spacing:2.5px; text-transform:uppercase;
}
.sec-head::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(56,139,253,0.3),transparent); }

/* SIDEBAR */
section[data-testid="stSidebar"] { background:#0d1117 !important; border-right:1px solid rgba(56,139,253,0.12) !important; }
section[data-testid="stSidebar"] label { color:#8b949e !important; font-size:11px !important; font-weight:600 !important; letter-spacing:1.5px !important; text-transform:uppercase !important; }

.sidebar-brand { text-align:center; padding:10px 0 18px; border-bottom:1px solid rgba(56,139,253,0.12); margin-bottom:18px; }
.sidebar-brand h2 { color:#58a6ff !important; font-size:17px !important; font-weight:800 !important; margin:0 !important; }
.sidebar-brand p  { color:#484f58; font-size:11px; margin:4px 0 0; }

/* BUTTONS */
.stButton > button {
    background:linear-gradient(135deg,#1f6feb,#1158c7) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important; font-family:'Outfit',sans-serif !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,#388bfd,#1f6feb) !important;
    box-shadow:0 4px 20px rgba(31,111,235,0.4) !important; transform:translateY(-1px) !important;
}
.stDownloadButton > button {
    background:rgba(56,139,253,0.1) !important; color:#58a6ff !important;
    border:1px solid rgba(56,139,253,0.28) !important; border-radius:10px !important; font-weight:600 !important;
}

/* LIVE BADGE */
.live-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(63,185,80,0.1); border:1px solid rgba(63,185,80,0.25);
    color:#3fb950; padding:5px 14px; border-radius:20px;
    font-size:11px; font-weight:700; letter-spacing:1px;
}
.dot { width:6px; height:6px; background:#3fb950; border-radius:50%; display:inline-block; }

h1 { color:#f0f6fc !important; font-weight:800 !important; font-family:'Outfit',sans-serif !important; }
p  { color:#8b949e !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  GOOGLE SHEETS LOADER
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_google_sheets():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        creds  = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(st.secrets["sheet_id"]).get_worksheet_by_id(342091003)
        df     = pd.DataFrame(sheet.get_all_records())
        return df, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
#  SAMPLE DATA
# ─────────────────────────────────────────────
def make_sample():
    np.random.seed(42)
    n = 400
    rms      = ["Raj Sharma","Priya Mehta","Amit Verma","Sneha Joshi","Vikram Singh","Neha Gupta","Rohit Yadav","Kavya Nair"]
    leaders  = ["Sunita Agarwal","Deepak Kapoor","Meena Pillai"]
    products = ["Term Plan","ULIP","Endowment","Health Shield","Pension Plus"]
    statuses = ["Active","Lapsed","Pending","Cancelled"]
    s_m      = ["Single","Multi"]
    modes    = ["Online","Cheque","NEFT","Cash","UPI"]
    months   = ["Jan 2024","Feb 2024","Mar 2024","Apr 2024","May 2024","Jun 2024",
                "Jul 2024","Aug 2024","Sep 2024","Oct 2024","Nov 2024","Dec 2024"]

    dates = pd.date_range("2024-01-01","2024-12-31", periods=n)
    df = pd.DataFrame({
        "Date":              np.random.choice(dates, n),
        "Month":             np.random.choice(months, n),
        "RM Name":           np.random.choice(rms, n),
        "Leader Name":       np.random.choice(leaders, n),
        "Product":           np.random.choice(products, n),
        "Single/Multi":      np.random.choice(s_m, n),
        "Policy Status":     np.random.choice(statuses, n, p=[0.60,0.15,0.15,0.10]),
        "Payment Mode":      np.random.choice(modes, n),
        "Total Premium":     np.random.randint(10000, 300000, n),
        "W/GST":             np.random.randint(11800, 354000, n),
        "CP Premium":        np.random.randint(5000,  150000, n),
        "CP Premium W/GST":  np.random.randint(5900,  177000, n),
        "PISY":              np.random.randint(1000,   50000, n),
        "PIMY":              np.random.randint(500,    25000, n),
        "MTD Target":        np.random.randint(50000, 500000, n),
        "PI Target":         np.random.randint(30000, 300000, n),
        "CP Target":         np.random.randint(20000, 200000, n),
    })
    df["Date"] = pd.to_datetime(df["Date"])
    return df


# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
df_raw, err = load_google_sheets()
demo_mode   = False

if err or df_raw is None or df_raw.empty:
    df_raw    = make_sample()
    demo_mode = True
else:
    df_raw["Date"] = pd.to_datetime(df_raw["Date"], errors="coerce")
    for c in ["Total Premium","W/GST","CP Premium","CP Premium W/GST","MTD Target","PI Target","CP Target","PISY","PIMY"]:
        if c in df_raw.columns:
            df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce").fillna(0)

df_raw["_MonthPeriod"] = df_raw["Date"].dt.to_period("M")


# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-brand'>
        <h2>📊 Liability Sales</h2>
        <p>Sales Analytics Platform</p>
    </div>""", unsafe_allow_html=True)

    # Month filter
    if "Month" in df_raw.columns:
        month_opts = df_raw["Month"].dropna().unique().tolist()
        sel_months = st.multiselect("📅  Month", month_opts, default=month_opts)
    else:
        sel_months = []

    # Date filter
    st.markdown(" ")
    min_d = df_raw["Date"].min().date()
    max_d = df_raw["Date"].max().date()
    d_range = st.date_input("📆  Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    st.markdown(" ")

    # Categorical filters
    filter_def = {
        "RM Name":      "👤  RM Name",
        "Product":      "📦  Product",
        "Single/Multi": "🔀  Single / Multi",
        "Leader Name":  "🏅  Leader Name",
        "Policy Status":"📋  Policy Status",
    }
    sel = {}
    for col, label in filter_def.items():
        if col in df_raw.columns:
            opts       = sorted(df_raw[col].dropna().unique().tolist())
            sel[col]   = st.multiselect(label, opts, default=opts)

    st.markdown("---")
    if st.button("🔄  Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if demo_mode:
        st.warning("⚠️ Demo Mode\nGoogle Sheets nahi mila.\nSETUP_GUIDE.md padho.")


# ─────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────
df = df_raw.copy()

if sel_months:
    df = df[df["Month"].isin(sel_months)]

if len(d_range) == 2:
    df = df[(df["Date"].dt.date >= d_range[0]) & (df["Date"].dt.date <= d_range[1])]

for col, chosen in sel.items():
    if chosen:
        df = df[df[col].isin(chosen)]


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
h1, h2 = st.columns([5, 1])
with h1:
    st.markdown("# 📊 Liability Sales Dashboard")
    st.markdown(f"<p style='margin-top:-10px;font-size:13px;'>{len(df):,} records · Filtered view</p>", unsafe_allow_html=True)
with h2:
    st.markdown("<br>", unsafe_allow_html=True)
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f"<div class='live-badge'><span class='dot'></span> LIVE &nbsp;·&nbsp; {now}</div>", unsafe_allow_html=True)

st.markdown("---")


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def fmt(val, prefix="₹"):
    if val >= 1_00_00_000: return f"{prefix}{val/1_00_00_000:.2f} Cr"
    if val >= 1_00_000:    return f"{prefix}{val/1_00_000:.2f} L"
    if val >= 1_000:       return f"{prefix}{val/1_000:.1f}K"
    return f"{prefix}{val:,.0f}"

def target_badge(actual, target):
    if target == 0: return ""
    pct = actual / target * 100
    icon = "▲" if pct >= 100 else "▼"
    cls  = "tgt-above" if pct >= 100 else "tgt-below"
    return f"<span class='{cls}'>{icon} {pct:.1f}% of target</span>"

BG   = "rgba(0,0,0,0)"
GRID = "rgba(56,139,253,0.07)"
TXT  = "#8b949e"
PAL  = ["#388bfd","#3fb950","#d29922","#bc8cff","#ff7b72","#79c0ff","#56d364","#e3b341"]

def base(title="", h=320):
    return dict(
        title=dict(text=title, font=dict(color="#c9d1d9", size=13, family="Outfit"), x=0.01),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=TXT, family="Outfit"),
        xaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=TXT, size=11)),
        yaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=TXT, size=11)),
        margin=dict(l=10, r=10, t=42, b=10),
        legend=dict(font=dict(color=TXT, size=11), bgcolor="rgba(0,0,0,0)"),
        height=h,
    )


# ─────────────────────────────────────────────
#  KPI ROW 1 — 4 cards
# ─────────────────────────────────────────────
st.markdown("<div class='sec-head'>📊 Key Performance Indicators</div>", unsafe_allow_html=True)

total_premium   = df["Total Premium"].sum()   if "Total Premium"   in df.columns else 0
total_wgst      = df["W/GST"].sum()           if "W/GST"           in df.columns else 0
total_cp_wgst   = df["CP Premium W/GST"].sum()if "CP Premium W/GST" in df.columns else 0
total_nop       = len(df)
total_mtd       = df["MTD Target"].sum()      if "MTD Target"      in df.columns else 0
total_pi_target = df["PI Target"].sum()       if "PI Target"       in df.columns else 0
total_cp_target = df["CP Target"].sum()       if "CP Target"       in df.columns else 0

st.markdown(f"""
<div class='kpi-grid'>
  <div class='kpi-card c1'>
    <div class='kpi-icon'>💰</div>
    <div class='kpi-label'>Total Premium</div>
    <div class='kpi-value'>{fmt(total_premium)}</div>
    <div class='kpi-sub'>Sum of all premiums</div>
  </div>
  <div class='kpi-card c2'>
    <div class='kpi-icon'>🧾</div>
    <div class='kpi-label'>Achievement</div>
    <div class='kpi-value'>{fmt(total_wgst)}</div>
    <div class='kpi-sub'>{target_badge(total_wgst, total_mtd)}</div>
  </div>
  <div class='kpi-card c3'>
    <div class='kpi-icon'>🛡️</div>
    <div class='kpi-label'>CP Premium W/GST</div>
    <div class='kpi-value'>{fmt(total_cp_wgst)}</div>
    <div class='kpi-sub'>{target_badge(total_cp_wgst, total_cp_target)}</div>
  </div>
  <div class='kpi-card c4'>
    <div class='kpi-icon'>📋</div>
    <div class='kpi-label'>Total NOP</div>
    <div class='kpi-value'>{total_nop:,}</div>
    <div class='kpi-sub'>Number of Policies</div>
  </div>
</div>
""", unsafe_allow_html=True)

# KPI ROW 2 — 3 target cards
st.markdown(f"""
<div class='kpi-grid-3'>
  <div class='kpi-card c5'>
    <div class='kpi-icon'>🎯</div>
    <div class='kpi-label'>MTD Target</div>
    <div class='kpi-value'>{fmt(total_mtd)}</div>
    <div class='kpi-sub'>MTD Target for period</div>
  </div>
  <div class='kpi-card c6'>
    <div class='kpi-icon'>🎯</div>
    <div class='kpi-label'>PI Target</div>
    <div class='kpi-value'>{fmt(total_pi_target)}</div>
    <div class='kpi-sub'>PI Target for period</div>
  </div>
  <div class='kpi-card c7'>
    <div class='kpi-icon'>🎯</div>
    <div class='kpi-label'>CP Target</div>
    <div class='kpi-value'>{fmt(total_cp_target)}</div>
    <div class='kpi-sub'>CP Target for period</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MONTHLY TREND — W/GST vs MTD Target + NOP + CP Achievement vs CP Target

# ─────────────────────────────────────────────
#  MONTHLY TREND — 2 Separate Charts
# ─────────────────────────────────────────────
st.markdown("<div class='sec-head'>📈 Monthly Trend</div>", unsafe_allow_html=True)

trend = (
    df.groupby("Month")
    .agg(
        WGST       =("W/GST",           "sum"),
        MTD_Target =("MTD Target",       "sum"),
        NOP        =("Policy Status",    "count"),
        CP_WGST    =("CP Premium W/GST", "sum"),
        CP_Target  =("CP Target",        "sum"),
    )
    .reset_index()
)

# Sort months properly
month_order = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
trend["_mo"] = trend["Month"].apply(lambda x: month_order.index(x) if x in month_order else 99)
trend = trend.sort_values("_mo").drop("_mo", axis=1)

tc1, tc2 = st.columns(2)

with tc1:
    fig_wgst = go.Figure()
    fig_wgst.add_trace(go.Scatter(
        x=trend["Month"], y=trend["WGST"],
        name="Achievement (Actual)", mode="lines+markers+text",
        line=dict(color="#388bfd", width=3),
        marker=dict(size=8, color="#388bfd", line=dict(color="#060d1a", width=2)),
        fill="tozeroy", fillcolor="rgba(56,139,253,0.07)",
        text=[fmt(v) for v in trend["WGST"]],
        textposition="top center", textfont=dict(color="#388bfd", size=10),
    ))
    fig_wgst.add_trace(go.Scatter(
        x=trend["Month"], y=trend["MTD_Target"],
        name="MTD Target", mode="lines+markers+text",
        line=dict(color="#d29922", width=2, dash="dash"),
        marker=dict(size=7, color="#d29922"),
        text=[fmt(v) for v in trend["MTD_Target"]],
        textposition="bottom center", textfont=dict(color="#d29922", size=10),
    ))
    fig_wgst.add_trace(go.Scatter(
        x=trend["Month"], y=trend["CP_WGST"],
        name="CP Achievement", mode="lines+markers+text",
        line=dict(color="#bc8cff", width=2),
        marker=dict(size=7, color="#bc8cff"),
        text=[fmt(v) for v in trend["CP_WGST"]],
        textposition="top center", textfont=dict(color="#bc8cff", size=10),
    ))
    fig_wgst.add_trace(go.Scatter(
        x=trend["Month"], y=trend["CP_Target"],
        name="CP Target", mode="lines+markers+text",
        line=dict(color="#56d364", width=2, dash="dot"),
        marker=dict(size=6, color="#56d364"),
        text=[fmt(v) for v in trend["CP_Target"]],
        textposition="bottom center", textfont=dict(color="#56d364", size=10),
    ))
    fig_wgst.update_layout(
        **base("📊 Achievement vs MTD Target · CP Achievement vs CP Target", h=350),
        hovermode="x unified",
    )
    fig_wgst.update_layout(legend=dict(orientation="h", y=-0.22, font=dict(color=TXT, size=10), bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_wgst, use_container_width=True)

with tc2:
    fig_nop = go.Figure()
    fig_nop.add_trace(go.Scatter(
        x=trend["Month"], y=trend["NOP"],
        name="NOP", mode="lines+markers+text",
        line=dict(color="#ff7b72", width=3),
        marker=dict(size=8, color="#ff7b72", line=dict(color="#060d1a", width=2)),
        fill="tozeroy", fillcolor="rgba(255,123,114,0.07)",
        text=trend["NOP"].astype(str),
        textposition="top center", textfont=dict(color="#ff7b72", size=11),
    ))
    fig_nop.update_layout(
        **base("📋 NOP Trend (Monthly)", h=350),
        hovermode="x unified",
    )
    fig_nop.update_layout(legend=dict(orientation="h", y=-0.22, font=dict(color=TXT, size=10), bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_nop, use_container_width=True)


# ─────────────────────────────────────────────
#  RM PERFORMANCE TABLE (sorted by MTD Ach%)
# ─────────────────────────────────────────────
st.markdown("<div class='sec-head'>📋 RM Performance Table</div>", unsafe_allow_html=True)

rm_table = (
    df.groupby("RM Name")
    .agg(
        MTD_Target =("MTD Target",       "sum"),
        WGST       =("W/GST",            "sum"),
        NOP        =("Policy Status",    "count"),
        CP_Target  =("CP Target",        "sum"),
        CP_WGST    =("CP Premium W/GST", "sum"),
    )
    .reset_index()
)

rm_table["MTD Ach%"]  = rm_table.apply(lambda r: 0.0 if r["MTD_Target"] == 0 else round(r["WGST"] / r["MTD_Target"] * 100, 1), axis=1)
rm_table["CP Ach%"]   = rm_table.apply(lambda r: 0.0 if r["CP_Target"] == 0  else round(r["CP_WGST"] / r["CP_Target"] * 100, 1), axis=1)
rm_table = rm_table.sort_values("MTD Ach%", ascending=False).reset_index(drop=True)
medals_list = ["🥇","🥈","🥉"]
rm_table["Rank"] = [medals_list[i] if i < 3 else str(i+1) for i in range(len(rm_table))]

rm_display = rm_table[[
    "Rank","RM Name","MTD_Target","WGST","MTD Ach%",
    "NOP","CP_Target","CP_WGST","CP Ach%"
]].copy()

# Total row
total_mtd_t   = rm_table["MTD_Target"].sum()
total_wgst_t  = rm_table["WGST"].sum()
total_nop_t   = rm_table["NOP"].sum()
total_cp_t    = rm_table["CP_Target"].sum()
total_cp_w_t  = rm_table["CP_WGST"].sum()
total_mtd_ach = 0.0 if total_mtd_t == 0 else round(total_wgst_t / total_mtd_t * 100, 1)
total_cp_ach  = 0.0 if total_cp_t  == 0 else round(total_cp_w_t  / total_cp_t  * 100, 1)
total_row = pd.DataFrame([{
    "Rank": "📊", "RM Name": "TOTAL",
    "MTD_Target": total_mtd_t, "WGST": total_wgst_t, "MTD Ach%": total_mtd_ach,
    "NOP": total_nop_t, "CP_Target": total_cp_t, "CP_WGST": total_cp_w_t, "CP Ach%": total_cp_ach
}])
rm_display = pd.concat([rm_display, total_row], ignore_index=True)

rm_display.columns = [
    "🏅","RM Name","🎯 MTD Target","🏆 Achievement","✅ MTD Ach%",
    "📋 NOP","🎯 CP Target","🎯 CP Achievement","✅ CP Ach%"
]

# Color format function
def color_ach(val):
    color = "#3fb950" if val >= 100 else "#ff7b72" if val < 70 else "#d29922"
    return f"color: {color}; font-weight: 600"

styled = rm_display.style.map(
    color_ach, subset=["✅ MTD Ach%","✅ CP Ach%"]
).format({
    "🎯 MTD Target": lambda x: fmt(x),
    "🏆 Achievement":      lambda x: fmt(x),
    "🎯 CP Target":  lambda x: fmt(x),
    "🎯 CP Achievement":   lambda x: fmt(x),
    "✅ MTD Ach%":   "{:.1f}%",
    "✅ CP Ach%":    "{:.1f}%",
})

st.dataframe(
    rm_display,
    use_container_width=True,
    hide_index=True,
    height=min(50 + len(rm_display) * 38, 500),
    column_config={
        "🏅":           st.column_config.TextColumn("🏅", width="small"),
        "RM Name":      st.column_config.TextColumn("Relationship Manager"),
        "🎯 MTD Target":st.column_config.NumberColumn("🎯 MTD Target", format="₹%d"),
        "🏆 Achievement":     st.column_config.NumberColumn("🏆 Achievement",      format="₹%d"),
        "✅ MTD Ach%":  st.column_config.NumberColumn("✅ MTD Ach%",   format="%.1f%%"),
        "📋 NOP":       st.column_config.NumberColumn("📋 NOP"),
        "🎯 CP Target": st.column_config.NumberColumn("🎯 CP Target",  format="₹%d"),
        "🎯 CP Achievement":  st.column_config.NumberColumn("🎯 CP Achievement",  format="₹%d"),
        "✅ CP Ach%":   st.column_config.NumberColumn("✅ CP Ach%",    format="%.1f%%"),
    }
)


# ─────────────────────────────────────────────
#  ROW — Product | Leader Contribution%
# ─────────────────────────────────────────────
st.markdown("<div class='sec-head'>📦 Product & Leader Contribution</div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    prod = df.groupby("Product")["W/GST"].sum().reset_index().sort_values("W/GST", ascending=False)
    fig_prod = go.Figure(go.Bar(
        x=prod["Product"], y=prod["W/GST"],
        marker=dict(
            color=prod["W/GST"],
            colorscale=[[0,"#0d2137"],[0.5,"#1f6feb"],[1,"#58a6ff"]],
            showscale=False, line=dict(color="rgba(0,0,0,0)")
        ),
        text=[fmt(v) for v in prod["W/GST"]], textposition="outside",
        textfont=dict(color="#c9d1d9", size=11)
    ))
    fig_prod.update_layout(**base("Achievement by Product", h=320))
    st.plotly_chart(fig_prod, use_container_width=True)

with c2:
    leader_data = df.groupby("Leader Name")["W/GST"].sum().reset_index()
    leader_data["Contribution%"] = (leader_data["W/GST"] / leader_data["W/GST"].sum() * 100).round(1)
    leader_data = leader_data.sort_values("W/GST", ascending=False)
    fig_leader_pie = go.Figure(go.Pie(
        labels=leader_data["Leader Name"],
        values=leader_data["W/GST"],
        hole=0.55,
        marker=dict(colors=PAL[:len(leader_data)], line=dict(color="#060d1a", width=3)),
        textfont=dict(color="white", size=11),
        texttemplate="%{label}<br>%{percent}",
        pull=[0.04] + [0]*(len(leader_data)-1)
    ))
    fig_leader_pie.update_layout(**base("Leader — Achievement Contribution %", h=320), showlegend=True)
    st.plotly_chart(fig_leader_pie, use_container_width=True)


# ─────────────────────────────────────────────
#  ROW — Leader Bar | Single vs Multi
# ─────────────────────────────────────────────
st.markdown("<div class='sec-head'>🏅 Leader & Single/Multi Analysis</div>", unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    leader = df.groupby("Leader Name").agg(
        WGST=("W/GST","sum"), NOP=("Policy Status","count")
    ).reset_index().sort_values("WGST", ascending=False)
    fig_leader = go.Figure()
    fig_leader.add_trace(go.Bar(
        name="W/GST", x=leader["Leader Name"], y=leader["WGST"],
        marker_color="#388bfd", yaxis="y1",
        text=[fmt(v) for v in leader["WGST"]], textposition="outside",
        textfont=dict(color="#c9d1d9", size=11)
    ))
    fig_leader.add_trace(go.Scatter(
        name="NOP", x=leader["Leader Name"], y=leader["NOP"],
        mode="lines+markers", line=dict(color="#3fb950", width=2, dash="dot"),
        marker=dict(size=8), yaxis="y2"
    ))
    fig_leader.update_layout(**base("Leader-wise Achievement & NOP", h=300))
    fig_leader.update_layout(
        yaxis =dict(gridcolor=GRID, tickfont=dict(color=TXT)),
        yaxis2=dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)", tickfont=dict(color=TXT)),
    )
    st.plotly_chart(fig_leader, use_container_width=True)

with c4:
    sm = df.groupby("Single/Multi").agg(
        WGST=("W/GST","sum"), NOP=("Policy Status","count")
    ).reset_index()
    sm["Contribution%"] = (sm["WGST"] / sm["WGST"].sum() * 100).round(1)
    sm["Label"] = sm.apply(lambda r: f"{r['Single/Multi']}<br>NOP: {int(r['NOP'])}<br>{fmt(r['WGST'])}", axis=1)
    fig_sm = go.Figure(go.Pie(
        labels=sm["Single/Multi"],
        values=sm["WGST"],
        hole=0.52,
        marker=dict(colors=["#388bfd","#bc8cff"], line=dict(color="#060d1a", width=3)),
        text=sm["Label"],
        textinfo="label+percent",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{label}</b><br>W/GST: %{value:,.0f}<br>Share: %{percent}<br>NOP: %{customdata}<extra></extra>",
        customdata=sm["NOP"],
        pull=[0.04, 0]
    ))
    fig_sm.update_layout(**base("Single vs Multi — Premium Contribution %", h=300), showlegend=True)
    st.plotly_chart(fig_sm, use_container_width=True)


# ─────────────────────────────────────────────
#  RAW DATA TABLE
# ─────────────────────────────────────────────
st.markdown("<div class='sec-head'>🗃️ Raw Data Table</div>", unsafe_allow_html=True)

show_cols = ["Date","Month","RM Name","Leader Name","Product","Single/Multi",
             "Policy Status","W/GST","CP Premium W/GST","MTD Target","PI Target","CP Target"]
show_cols = [c for c in show_cols if c in df.columns]

st.dataframe(
    df[show_cols].sort_values("Date", ascending=False).reset_index(drop=True),
    use_container_width=True, height=380,
    column_config={
        "Date":             st.column_config.DateColumn("📅 Date", format="DD MMM YYYY"),
        "W/GST":            st.column_config.NumberColumn("🏆 Achievement",            format="₹%d"),
        "CP Premium W/GST": st.column_config.NumberColumn("🛡️ CP Premium W/GST", format="₹%d"),
        "MTD Target":       st.column_config.NumberColumn("🎯 MTD Target",        format="₹%d"),
        "PI Target":        st.column_config.NumberColumn("🎯 PI Target",         format="₹%d"),
        "CP Target":        st.column_config.NumberColumn("🎯 CP Target",         format="₹%d"),
    }
)

dl1, dl2, dl3, _ = st.columns([1.2, 1.4, 1.4, 2])
with dl1:
    csv1 = df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Full CSV", data=csv1, file_name=f"sales_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
with dl2:
    rm_sum = df.groupby("RM Name")[["W/GST","CP Premium W/GST","MTD Target"]].sum().reset_index()
    csv2 = rm_sum.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ RM Summary", data=csv2, file_name=f"rm_summary_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
with dl3:
    leader_sum = df.groupby("Leader Name")[["W/GST","CP Premium W/GST"]].sum().reset_index()
    csv3 = leader_sum.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Leader Summary", data=csv3, file_name=f"leader_summary_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#21262d; font-size:11px; letter-spacing:1px;'>"
    "LIABILITY SALES DASHBOARD  ·  GOOGLE SHEETS + STREAMLIT  ·  AUTO-REFRESH EVERY 5 MIN"
    "</p>",
    unsafe_allow_html=True
)
