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
#  PAGE NAVIGATION
# ─────────────────────────────────────────────
page = st.sidebar.radio(
    "",
    ["📊 Sales Dashboard", "👥 Client Analytics", "📞 Calling Dashboard", "🎯 Leads Utilisation"],
    label_visibility="collapsed"
)
st.sidebar.markdown("---")

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
.kpi-grid  { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 6px; }
.kpi-grid-3{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 20px; }
.kpi-wrap  { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 20px; }
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
.tgt-above { color:#3fb950; font-size:11px; font-weight:600; }
.tgt-below { color:#ff7b72; font-size:11px; font-weight:600; }
.sec-head {
    display:flex; align-items:center; gap:10px;
    margin:22px 0 12px;
    color:#58a6ff; font-size:11px; font-weight:700;
    letter-spacing:2.5px; text-transform:uppercase;
}
.sec-head::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(56,139,253,0.3),transparent); }
section[data-testid="stSidebar"] { background:#0d1117 !important; border-right:1px solid rgba(56,139,253,0.12) !important; }
section[data-testid="stSidebar"] label { color:#8b949e !important; font-size:11px !important; font-weight:600 !important; letter-spacing:1.5px !important; text-transform:uppercase !important; }
.sidebar-brand { text-align:center; padding:10px 0 18px; border-bottom:1px solid rgba(56,139,253,0.12); margin-bottom:18px; }
.sidebar-brand h2 { color:#58a6ff !important; font-size:17px !important; font-weight:800 !important; margin:0 !important; }
.sidebar-brand p  { color:#484f58; font-size:11px; margin:4px 0 0; }
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
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
def fmt(val, prefix="₹"):
    if val >= 1_00_00_000: return f"{prefix}{val/1_00_00_000:.2f} Cr"
    if val >= 1_00_000:    return f"{prefix}{val/1_00_000:.2f} L"
    if val >= 1_000:       return f"{prefix}{val/1_000:.1f}K"
    return f"{prefix}{val:,.0f}"

def target_badge(actual, target):
    if target == 0: return ""
    pct  = actual / target * 100
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

# ═══════════════════════════════════════════════════════
#  CLIENT ANALYTICS PAGE FUNCTION  ← ✅ BAHAR DEFINE HAI
# ═══════════════════════════════════════════════════════
def show_client_page():

    @st.cache_data(ttl=300)
    def load_client_data():
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
            ]
            creds  = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=scopes
            )
            client = gspread.authorize(creds)
            sheet  = client.open_by_key(st.secrets["sheet_id"]).get_worksheet_by_id(1240499347)
            df     = pd.DataFrame(sheet.get_all_records())
            return df, None
        except Exception as e:
            return None, str(e)

    df_client, err = load_client_data()
    if err or df_client is None or df_client.empty:
        st.warning(f"⚠️ Client data load nahi hua: {err}")
        return

    # ── Data Prep ──
    df_client["Transasction Date"] = pd.to_datetime(df_client["Transasction Date"], errors="coerce")
    for col in ["Total Premium (incl. GST)", "Total Premium (excl. GST)", "Total Sum Assured"]:
        if col in df_client.columns:
            df_client[col] = pd.to_numeric(df_client[col], errors="coerce").fillna(0)
    df_client["_MonthPeriod"] = df_client["Transasction Date"].dt.to_period("M")

    # ── SIDEBAR FILTERS ──
    with st.sidebar:
        st.markdown("<div class='sec-head'>🔍 Client Filters</div>", unsafe_allow_html=True)
        st.markdown("📅 &nbsp;Date Range", unsafe_allow_html=True)
        min_d = df_client["Transasction Date"].min().date()
        max_d = df_client["Transasction Date"].max().date()
        d_range = st.date_input("", value=(min_d, max_d), min_value=min_d, max_value=max_d,
                                key="client_date", label_visibility="collapsed")
        sel_months = []
        if "Month" in df_client.columns:
            month_opts = sorted(df_client["Month"].dropna().unique().tolist(), key=str)
            sel_months = st.multiselect("📅 Month", month_opts, default=month_opts, key="client_month")

        client_filters = {
            "Region":             "🌍 Region",
            "State":              "📍 State",
            "City":               "🏙️ City",
            "Association":        "🏢 Association",
            "Specialization":     "🎯 Specialization",
            "Product":            "📦 Product",
            "Latest Visit Source":"🔗 Lead Source",
            "Team Leader":        "🏅 Team Leader",
        }
        client_sel = {}
        for col, label in client_filters.items():
            if col in df_client.columns:
                opts = sorted(df_client[col].dropna().unique().tolist(), key=str)
                client_sel[col] = st.multiselect(label, opts, default=opts, key=f"cf_{col}")

        sa_range = None
        if "Total Sum Assured" in df_client.columns:
            min_sa = int(df_client["Total Sum Assured"].min())
            max_sa = int(df_client["Total Sum Assured"].max())
            if min_sa < max_sa:
                sa_range = st.slider("💰 Total Sum Assured", min_sa, max_sa, (min_sa, max_sa), key="client_sa")

        if st.button("🔄 Refresh Client Data", use_container_width=True, key="client_refresh"):
            st.cache_data.clear()
            st.rerun()

    # ── Apply Filters ──
    dfc = df_client.copy()
    if len(d_range) == 2:
        dfc = dfc[(dfc["Transasction Date"].dt.date >= d_range[0]) &
                  (dfc["Transasction Date"].dt.date <= d_range[1])]
    if "Month" in dfc.columns and sel_months:
        dfc = dfc[dfc["Month"].isin(sel_months)]
    for col, sel in client_sel.items():
        if sel:
            dfc = dfc[dfc[col].isin(sel)]
    if sa_range and "Total Sum Assured" in dfc.columns:
        dfc = dfc[(dfc["Total Sum Assured"] >= sa_range[0]) &
                  (dfc["Total Sum Assured"] <= sa_range[1])]

    # ── HEADER ──
    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown("# 👥 Client Analytics")
        st.markdown(f"<p style='margin-top:-10px;font-size:13px;'>{len(dfc):,} records · Filtered view</p>",
                    unsafe_allow_html=True)
    with h2:
        st.markdown("<br>", unsafe_allow_html=True)
        now = datetime.now().strftime("%d %b %Y, %H:%M")
        st.markdown(f"<div class='live-badge'><span class='dot'></span> LIVE &nbsp;·&nbsp; {now}</div>",
                    unsafe_allow_html=True)
    st.markdown("---")

    # ── KPI CARDS ──
    st.markdown("<div class='sec-head'>📊 Key Performance Indicators</div>", unsafe_allow_html=True)
    total_prem_excl = dfc["Total Premium (excl. GST)"].sum() if "Total Premium (excl. GST)" in dfc.columns else 0
    total_nop       = len(dfc)
    unique_clients  = dfc["Client Name"].nunique() if "Client Name" in dfc.columns else 0
    avg_prem        = total_prem_excl / unique_clients if unique_clients > 0 else 0
    avg_sa          = dfc["Total Sum Assured"].mean() if "Total Sum Assured" in dfc.columns else 0
    st.markdown(f"""
    <div class='kpi-wrap'>
      <div class='kpi-card c1'><div class='kpi-icon'>💰</div>
        <div class='kpi-label'>Total Premium (excl. GST)</div>
        <div class='kpi-value'>{fmt(total_prem_excl)}</div>
        <div class='kpi-sub'>Net Premium</div></div>
      <div class='kpi-card c2'><div class='kpi-icon'>📋</div>
        <div class='kpi-label'>Number of Policies</div>
        <div class='kpi-value'>{total_nop:,}</div>
        <div class='kpi-sub'>Total policies in period</div></div>
      <div class='kpi-card c3'><div class='kpi-icon'>👥</div>
        <div class='kpi-label'>Total Clients</div>
        <div class='kpi-value'>{unique_clients:,}</div>
        <div class='kpi-sub'>Unique clients</div></div>
      <div class='kpi-card c4'><div class='kpi-icon'>📊</div>
        <div class='kpi-label'>Avg Premium / Client</div>
        <div class='kpi-value'>{fmt(avg_prem)}</div>
        <div class='kpi-sub'>Client value</div></div>
      <div class='kpi-card c5'><div class='kpi-icon'>🛡️</div>
        <div class='kpi-label'>Avg Sum Assured</div>
        <div class='kpi-value'>{fmt(avg_sa)}</div>
        <div class='kpi-sub'>Avg coverage per policy</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHART THEME ──
    C_PAL = ["#388bfd","#3fb950","#d29922","#bc8cff","#ff7b72","#79c0ff","#56d364","#e3b341","#f0883e","#58a6ff"]
    def cbase(title="", h=320):
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

    # ── MONTHLY TREND ──
    st.markdown("<div class='sec-head'>📈 Monthly Premium Trend</div>", unsafe_allow_html=True)
    trend = (
        dfc.groupby("_MonthPeriod")
        .agg(
            Prem_Incl=("Total Premium (incl. GST)", "sum"),
            Prem_Excl=("Total Premium (excl. GST)", "sum"),
            NOP=("Client Name", "count"),
        )
        .reset_index().sort_values("_MonthPeriod")
    )
    trend["Month_Str"] = trend["_MonthPeriod"].astype(str)
    fig_trend = go.Figure()
    trend["Month_Label"] = trend["_MonthPeriod"].dt.strftime("%b %Y")
    fig_trend.add_trace(go.Scatter(
        x=trend["Month_Label"], y=trend["Prem_Excl"],
        name="Premium (excl. GST)", mode="lines+markers+text",
        line=dict(color="#388bfd", width=3),
        marker=dict(size=8, color="#388bfd", line=dict(color="#060d1a", width=2)),
        fill="tozeroy", fillcolor="rgba(56,139,253,0.07)",
        text=[fmt(v) for v in trend["Prem_Excl"]],
        textposition="top center", textfont=dict(color="#388bfd", size=10),
    ))
    fig_trend.update_layout(**cbase("Monthly Premium Trend (incl. vs excl. GST)", h=350))
    fig_trend.update_layout(legend=dict(orientation="h", y=-0.2, font=dict(color=TXT, size=10), bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── PRODUCT PIE | REGION DONUT ──
    st.markdown("<div class='sec-head'>📦 Product & Region Analysis</div>", unsafe_allow_html=True)
    cp1, cp2 = st.columns(2)
    with cp1:
        prod = dfc.groupby("Product").agg(
            Premium=("Total Premium (excl. GST)", "sum"),
            NOP=("Client Name", "count")
        ).reset_index().sort_values("Premium", ascending=False)
        fig_prod = go.Figure(go.Pie(
            labels=prod["Product"], values=prod["Premium"],
            hole=0,
            marker=dict(colors=C_PAL[:len(prod)], line=dict(color="#060d1a", width=2)),
            texttemplate="%{label}<br>%{percent}<br>NOP: %{customdata}",
            customdata=prod["NOP"],
            textfont=dict(color="white", size=10),
        ))
        fig_prod.update_layout(**cbase("Product wise Premium % & NOP", h=380), showlegend=False)
        st.plotly_chart(fig_prod, use_container_width=True)
    with cp2:
        region = dfc.groupby("Region").agg(
            Premium=("Total Premium (excl. GST)", "sum"),
            NOP=("Client Name", "count")
        ).reset_index().sort_values("Premium", ascending=False)
        fig_region = go.Figure(go.Pie(
            labels=region["Region"], values=region["Premium"],
            hole=0.55,
            marker=dict(colors=C_PAL[:len(region)], line=dict(color="#060d1a", width=3)),
            texttemplate="%{label}<br>%{percent}<br>NOP: %{customdata}",
            customdata=region["NOP"],
            textfont=dict(color="white", size=10),
            pull=[0.04] + [0]*(len(region)-1)
        ))
        fig_region.update_layout(**cbase("Region wise Premium % & NOP", h=380), showlegend=True)
        st.plotly_chart(fig_region, use_container_width=True)

    # ── TOP 10 CLIENTS ──
    st.markdown("<div class='sec-head'>🏆 Top 10 Clients by Premium</div>", unsafe_allow_html=True)
    top_clients = (
        dfc.groupby("Client Name")["Total Premium (excl. GST)"].sum()
        .nlargest(10).reset_index().sort_values("Total Premium (excl. GST)")
    )
    medals = ["#d29922","#8b949e","#c17c35"] + ["#388bfd"]*7
    fig_top = go.Figure(go.Bar(
        x=top_clients["Total Premium (excl. GST)"],
        y=top_clients["Client Name"],
        orientation="h",
        marker=dict(color=medals[::-1][:len(top_clients)], line=dict(color="rgba(0,0,0,0)")),
        text=[fmt(v) for v in top_clients["Total Premium (excl. GST)"]],
        textposition="outside",
        textfont=dict(color="#c9d1d9", size=11)
    ))
    fig_top.update_layout(**cbase("Top 10 Clients by Premium (excl. GST)", h=380))
    st.plotly_chart(fig_top, use_container_width=True)

    # ── ANALYSIS TABLE HELPER ──
    def analysis_table(df_in, group_col, title, key):
        st.markdown(f"<div class='sec-head'>{title}</div>", unsafe_allow_html=True)
        if group_col not in df_in.columns:
            st.info(f"Column '{group_col}' data mein nahi mila.")
            return
        tbl = df_in.groupby(group_col).agg(
            Premium=("Total Premium (excl. GST)", "sum"),
            NOP=("Client Name", "count"),
        ).reset_index()
        tbl["ATS"]                     = (tbl["Premium"] / tbl["NOP"].replace(0,1)).round(0)
        tbl["Contribution% (Premium)"] = (tbl["Premium"] / tbl["Premium"].sum() * 100).round(1)
        tbl["Contribution% (NOP)"]     = (tbl["NOP"]     / tbl["NOP"].sum()     * 100).round(1)
        tbl = tbl.sort_values("Premium", ascending=False).reset_index(drop=True)
        total_row = pd.DataFrame([{
            group_col: "TOTAL",
            "Premium": tbl["Premium"].sum(),
            "NOP":     tbl["NOP"].sum(),
            "ATS":     (tbl["Premium"].sum() / tbl["NOP"].sum()) if tbl["NOP"].sum() > 0 else 0,
            "Contribution% (Premium)": 100.0,
            "Contribution% (NOP)":     100.0,
        }])
        tbl = pd.concat([tbl, total_row], ignore_index=True)
        tbl_d = tbl.copy()
        tbl_d["Premium"] = tbl_d["Premium"].apply(fmt)
        tbl_d["ATS"]     = tbl_d["ATS"].apply(fmt)
        tbl_d["Contribution% (Premium)"] = tbl_d["Contribution% (Premium)"].apply(lambda x: f"{x:.1f}%")
        tbl_d["Contribution% (NOP)"]     = tbl_d["Contribution% (NOP)"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(tbl_d, use_container_width=True, hide_index=True,
                     height=min(50 + len(tbl_d) * 38, 500),
                     column_config={
                         group_col:                 st.column_config.TextColumn(group_col),
                         "Premium":                 st.column_config.TextColumn("💰 Premium"),
                         "NOP":                     st.column_config.NumberColumn("📋 NOP"),
                         "ATS":                     st.column_config.TextColumn("📊 ATS"),
                         "Contribution% (Premium)": st.column_config.TextColumn("% Premium"),
                         "Contribution% (NOP)":     st.column_config.TextColumn("% NOP"),
                     })

    # ── ANALYSIS TABLES ──
    analysis_table(dfc, "State",              "📍 State wise Analysis",          "state")
    analysis_table(dfc, "Association",         "🏢 Association wise Analysis",     "assoc")
    analysis_table(dfc, "Specialization",      "🎯 Specialization wise Analysis",  "spec")
    analysis_table(dfc, "Latest Visit Source", "🔗 Lead Source wise Analysis",     "lead")



# ─────────────────────────────────────────────
#  SIDEBAR FILTERS  (Sales Dashboard)
# ─────────────────────────────────────────────
if page == "📊 Sales Dashboard":
    with st.sidebar:
        st.markdown("""
        <div class='sidebar-brand'>
            <h2>📊 Liability Sales</h2>
            <p>Sales Analytics Platform</p>
        </div>""", unsafe_allow_html=True)

        if "Month" in df_raw.columns:
            month_opts = sorted(df_raw["Month"].dropna().unique().tolist(), key=str)
            sel_months = st.multiselect("📅  Month", month_opts, default=month_opts)
        else:
            sel_months = []

        st.markdown(" ")
        min_d   = df_raw["Date"].min().date()
        max_d   = df_raw["Date"].max().date()
        d_range = st.date_input("📆  Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        st.markdown(" ")

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
                opts     = sorted(df_raw[col].dropna().unique().tolist(), key=str)
                sel[col] = st.multiselect(label, opts, default=opts)

        st.markdown("---")
        if st.button("🔄  Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        if demo_mode:
            st.warning("⚠️ Demo Mode\nGoogle Sheets nahi mila.")

    # ── Apply Filters ──
    df = df_raw.copy()
    if sel_months:
        df = df[df["Month"].isin(sel_months)]
    if len(d_range) == 2:
        df = df[(df["Date"].dt.date >= d_range[0]) & (df["Date"].dt.date <= d_range[1])]
    for col, chosen in sel.items():
        if chosen:
            df = df[df[col].isin(chosen)]

    # ── HEADER ──
    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown("# 📊 Liability Sales Dashboard")
        st.markdown(f"<p style='margin-top:-10px;font-size:13px;'>{len(df):,} records · Filtered view</p>", unsafe_allow_html=True)
    with h2:
        st.markdown("<br>", unsafe_allow_html=True)
        now = datetime.now().strftime("%d %b %Y, %H:%M")
        st.markdown(f"<div class='live-badge'><span class='dot'></span> LIVE &nbsp;·&nbsp; {now}</div>", unsafe_allow_html=True)
    st.markdown("---")

    # ── KPI ROW 1 ──
    st.markdown("<div class='sec-head'>📊 Key Performance Indicators</div>", unsafe_allow_html=True)
    total_premium   = df["Total Premium"].sum()    if "Total Premium"    in df.columns else 0
    total_wgst      = df["W/GST"].sum()            if "W/GST"            in df.columns else 0
    total_cp_wgst   = df["CP Premium W/GST"].sum() if "CP Premium W/GST" in df.columns else 0
    total_nop       = len(df)
    total_mtd       = df["MTD Target"].sum()       if "MTD Target"       in df.columns else 0
    total_pi_target = df["PI Target"].sum()        if "PI Target"        in df.columns else 0
    total_cp_target = df["CP Target"].sum()        if "CP Target"        in df.columns else 0

    st.markdown(f"""
    <div class='kpi-grid'>
      <div class='kpi-card c1'><div class='kpi-icon'>💰</div>
        <div class='kpi-label'>Total Premium</div>
        <div class='kpi-value'>{fmt(total_premium)}</div>
        <div class='kpi-sub'>Sum of all premiums</div></div>
      <div class='kpi-card c2'><div class='kpi-icon'>🧾</div>
        <div class='kpi-label'>Achievement</div>
        <div class='kpi-value'>{fmt(total_wgst)}</div>
        <div class='kpi-sub'>{target_badge(total_wgst, total_mtd)}</div></div>
      <div class='kpi-card c3'><div class='kpi-icon'>🛡️</div>
        <div class='kpi-label'>CP Premium W/GST</div>
        <div class='kpi-value'>{fmt(total_cp_wgst)}</div>
        <div class='kpi-sub'>{target_badge(total_cp_wgst, total_cp_target)}</div></div>
      <div class='kpi-card c4'><div class='kpi-icon'>📋</div>
        <div class='kpi-label'>Total NOP</div>
        <div class='kpi-value'>{total_nop:,}</div>
        <div class='kpi-sub'>Number of Policies</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='kpi-grid-3'>
      <div class='kpi-card c5'><div class='kpi-icon'>🎯</div>
        <div class='kpi-label'>MTD Target</div>
        <div class='kpi-value'>{fmt(total_mtd)}</div>
        <div class='kpi-sub'>MTD Target for period</div></div>
      <div class='kpi-card c6'><div class='kpi-icon'>🎯</div>
        <div class='kpi-label'>PI Target</div>
        <div class='kpi-value'>{fmt(total_pi_target)}</div>
        <div class='kpi-sub'>PI Target for period</div></div>
      <div class='kpi-card c7'><div class='kpi-icon'>🎯</div>
        <div class='kpi-label'>CP Target</div>
        <div class='kpi-value'>{fmt(total_cp_target)}</div>
        <div class='kpi-sub'>CP Target for period</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── MONTHLY TREND ──
    st.markdown("<div class='sec-head'>📈 Monthly Trend</div>", unsafe_allow_html=True)
    trend = (
        df.groupby("Month")
        .agg(
            WGST      =("W/GST",           "sum"),
            MTD_Target=("MTD Target",       "sum"),
            NOP       =("Policy Status",    "count"),
            CP_WGST   =("CP Premium W/GST", "sum"),
            CP_Target =("CP Target",        "sum"),
        )
        .reset_index()
    )
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
        fig_nop.update_layout(**base("📋 NOP Trend (Monthly)", h=350), hovermode="x unified")
        fig_nop.update_layout(legend=dict(orientation="h", y=-0.22, font=dict(color=TXT, size=10), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_nop, use_container_width=True)

    # ── RM PERFORMANCE TABLE ──
    st.markdown("<div class='sec-head'>📋 RM Performance Table</div>", unsafe_allow_html=True)
    rm_table = (
        df.groupby("RM Name")
        .agg(
            MTD_Target=("MTD Target",       "sum"),
            WGST      =("W/GST",            "sum"),
            NOP       =("Policy Status",    "count"),
            CP_Target =("CP Target",        "sum"),
            CP_WGST   =("CP Premium W/GST", "sum"),
        )
        .reset_index()
    )
    rm_table["MTD Ach%"] = rm_table.apply(lambda r: 0.0 if r["MTD_Target"]==0 else round(r["WGST"]/r["MTD_Target"]*100,1), axis=1)
    rm_table["CP Ach%"]  = rm_table.apply(lambda r: 0.0 if r["CP_Target"]==0  else round(r["CP_WGST"]/r["CP_Target"]*100,1), axis=1)
    rm_table = rm_table.sort_values("MTD Ach%", ascending=False).reset_index(drop=True)
    medals_list = ["🥇","🥈","🥉"]
    rm_table["Rank"] = [medals_list[i] if i < 3 else str(i+1) for i in range(len(rm_table))]

    rm_display = rm_table[["Rank","RM Name","MTD_Target","WGST","MTD Ach%","NOP","CP_Target","CP_WGST","CP Ach%"]].copy()
    total_mtd_t  = rm_table["MTD_Target"].sum()
    total_wgst_t = rm_table["WGST"].sum()
    total_nop_t  = rm_table["NOP"].sum()
    total_cp_t   = rm_table["CP_Target"].sum()
    total_cp_w_t = rm_table["CP_WGST"].sum()
    total_row = pd.DataFrame([{
        "Rank":"📊","RM Name":"TOTAL",
        "MTD_Target":total_mtd_t,"WGST":total_wgst_t,
        "MTD Ach%":0.0 if total_mtd_t==0 else round(total_wgst_t/total_mtd_t*100,1),
        "NOP":total_nop_t,"CP_Target":total_cp_t,"CP_WGST":total_cp_w_t,
        "CP Ach%":0.0 if total_cp_t==0 else round(total_cp_w_t/total_cp_t*100,1)
    }])
    rm_display = pd.concat([rm_display, total_row], ignore_index=True)
    rm_display.columns = ["🏅","RM Name","🎯 MTD Target","🏆 Achievement","✅ MTD Ach%",
                          "📋 NOP","🎯 CP Target","🎯 CP Achievement","✅ CP Ach%"]
    st.dataframe(
        rm_display, use_container_width=True, hide_index=True,
        height=min(50 + len(rm_display) * 38, 500),
        column_config={
            "🏅":             st.column_config.TextColumn("🏅", width="small"),
            "RM Name":        st.column_config.TextColumn("Relationship Manager"),
            "🎯 MTD Target":  st.column_config.NumberColumn("🎯 MTD Target",       format="₹%d"),
            "🏆 Achievement": st.column_config.NumberColumn("🏆 Achievement",       format="₹%d"),
            "✅ MTD Ach%":    st.column_config.NumberColumn("✅ MTD Ach%",          format="%.1f%%"),
            "📋 NOP":         st.column_config.NumberColumn("📋 NOP"),
            "🎯 CP Target":   st.column_config.NumberColumn("🎯 CP Target",         format="₹%d"),
            "🎯 CP Achievement":st.column_config.NumberColumn("🎯 CP Achievement",  format="₹%d"),
            "✅ CP Ach%":     st.column_config.NumberColumn("✅ CP Ach%",           format="%.1f%%"),
        }
    )

    # ── PRODUCT & LEADER ──
    st.markdown("<div class='sec-head'>📦 Product & Leader Contribution</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        prod = df.groupby("Product")["W/GST"].sum().reset_index().sort_values("W/GST", ascending=False)
        fig_prod = go.Figure(go.Bar(
            x=prod["Product"], y=prod["W/GST"],
            marker=dict(color=prod["W/GST"],
                        colorscale=[[0,"#0d2137"],[0.5,"#1f6feb"],[1,"#58a6ff"]],
                        showscale=False, line=dict(color="rgba(0,0,0,0)")),
            text=[fmt(v) for v in prod["W/GST"]], textposition="outside",
            textfont=dict(color="#c9d1d9", size=11)
        ))
        fig_prod.update_layout(**base("Achievement by Product", h=320))
        st.plotly_chart(fig_prod, use_container_width=True)
    with c2:
        leader_data = df.groupby("Leader Name")["W/GST"].sum().reset_index().sort_values("W/GST", ascending=False)
        fig_lp = go.Figure(go.Pie(
            labels=leader_data["Leader Name"], values=leader_data["W/GST"],
            hole=0.55,
            marker=dict(colors=PAL[:len(leader_data)], line=dict(color="#060d1a", width=3)),
            textfont=dict(color="white", size=11),
            texttemplate="%{label}<br>%{percent}",
            pull=[0.04] + [0]*(len(leader_data)-1)
        ))
        fig_lp.update_layout(**base("Leader — Achievement Contribution %", h=320), showlegend=True)
        st.plotly_chart(fig_lp, use_container_width=True)

    # ── LEADER BAR | SINGLE/MULTI ──
    st.markdown("<div class='sec-head'>🏅 Leader & Single/Multi Analysis</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        leader = df.groupby("Leader Name").agg(WGST=("W/GST","sum"), NOP=("Policy Status","count")).reset_index().sort_values("WGST", ascending=False)
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
        sm = df.groupby("Single/Multi").agg(WGST=("W/GST","sum"), NOP=("Policy Status","count")).reset_index()
        sm["Label"] = sm.apply(lambda r: f"{r['Single/Multi']}<br>NOP: {int(r['NOP'])}<br>{fmt(r['WGST'])}", axis=1)
        fig_sm = go.Figure(go.Pie(
            labels=sm["Single/Multi"], values=sm["WGST"],
            hole=0.52,
            marker=dict(colors=["#388bfd","#bc8cff"], line=dict(color="#060d1a", width=3)),
            text=sm["Label"], textinfo="label+percent",
            textfont=dict(color="white", size=12),
            hovertemplate="<b>%{label}</b><br>W/GST: %{value:,.0f}<br>Share: %{percent}<br>NOP: %{customdata}<extra></extra>",
            customdata=sm["NOP"], pull=[0.04, 0]
        ))
        fig_sm.update_layout(**base("Single vs Multi — Premium Contribution %", h=300), showlegend=True)
        st.plotly_chart(fig_sm, use_container_width=True)

    # ── RAW DATA TABLE ──
    st.markdown("<div class='sec-head'>🗃️ Raw Data Table</div>", unsafe_allow_html=True)
    show_cols = ["Date","Month","RM Name","Leader Name","Product","Single/Multi",
                 "Policy Status","W/GST","CP Premium W/GST","MTD Target","PI Target","CP Target"]
    show_cols = [c for c in show_cols if c in df.columns]
    st.dataframe(
        df[show_cols].sort_values("Date", ascending=False).reset_index(drop=True),
        use_container_width=True, height=380,
        column_config={
            "Date":             st.column_config.DateColumn("📅 Date", format="DD MMM YYYY"),
            "W/GST":            st.column_config.NumberColumn("🏆 Achievement",      format="₹%d"),
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
#  PAGE ROUTER — CLIENT ANALYTICS
# ─────────────────────────────────────────────
elif page == "👥 Client Analytics":
    show_client_page()
elif page == "📞 Calling Dashboard":
    # ── Load Calling Data ──
    @st.cache_data(ttl=300)
    def load_calling_data():
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
            ]
            creds  = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=scopes
            )
            client = gspread.authorize(creds)
            sheet  = client.open_by_key(st.secrets["sheet_id"]).get_worksheet_by_id(2102431440)
            df     = pd.DataFrame(sheet.get_all_records())
            return df, None
        except Exception as e:
            return None, str(e)

    df_call, err = load_calling_data()
    if err or df_call is None or df_call.empty:
        st.warning(f"⚠️ Calling data load nahi hua: {err}")
    else:
        # ── Data Prep ──
        df_call["Call Date"] = pd.to_datetime(df_call["Call Date"], errors="coerce")
        for col in ["Unique Dials", "Talktime"]:
            if col in df_call.columns:
                df_call[col] = pd.to_numeric(df_call[col], errors="coerce").fillna(0)

        # ── SIDEBAR FILTERS ──
        with st.sidebar:
            st.markdown("<div class='sec-head'>🔍 Calling Filters</div>", unsafe_allow_html=True)

            # Month filter
            if "Month" in df_call.columns:
                month_opts = sorted(df_call["Month"].dropna().unique().tolist(), key=str)
                sel_months_call = st.multiselect("📅 Month", month_opts, default=month_opts, key="call_month")
            else:
                sel_months_call = []

            # Date Range
            min_d = df_call["Call Date"].min().date()
            max_d = df_call["Call Date"].max().date()
            d_range_call = st.date_input("📆 Date Range", value=(min_d, max_d),
                                          min_value=min_d, max_value=max_d, key="call_date")

            # Categorical filters
            call_filters = {
                "Employee Name":    "👤 Employee Name",
                "Reporting TL":     "🏅 Reporting TL",
                "System Disposition":"📋 System Disposition",
                "Label Disposition": "🏷️ Label Disposition",
            }
            call_sel = {}
            for col, label in call_filters.items():
                if col in df_call.columns:
                    opts = sorted(df_call[col].dropna().unique().tolist(), key=str)
                    call_sel[col] = st.multiselect(label, opts, default=opts, key=f"call_{col}")

            if st.button("🔄 Refresh Calling Data", use_container_width=True, key="call_refresh"):
                st.cache_data.clear()
                st.rerun()

        # ── Apply Filters ──
        dfc = df_call.copy()
        if sel_months_call:
            dfc = dfc[dfc["Month"].isin(sel_months_call)]
        if len(d_range_call) == 2:
            dfc = dfc[(dfc["Call Date"].dt.date >= d_range_call[0]) &
                      (dfc["Call Date"].dt.date <= d_range_call[1])]
        for col, sel in call_sel.items():
            if sel:
                dfc = dfc[dfc[col].isin(sel)]

        # ── HEADER ──
        h1, h2 = st.columns([5, 1])
        with h1:
            st.markdown("# 📞 Calling Dashboard")
            st.markdown(f"<p style='margin-top:-10px;font-size:13px;'>{len(dfc):,} records · Filtered view</p>",
                        unsafe_allow_html=True)
        with h2:
            st.markdown("<br>", unsafe_allow_html=True)
            now = datetime.now().strftime("%d %b %Y, %H:%M")
            st.markdown(f"<div class='live-badge'><span class='dot'></span> LIVE &nbsp;·&nbsp; {now}</div>",
                        unsafe_allow_html=True)
        st.markdown("---")

        # ── KPI CARDS ──
        st.markdown("<div class='sec-head'>📊 Key Performance Indicators</div>", unsafe_allow_html=True)
        total_calls = len(dfc)

        # Unique Dials — sirf 1 wali rows
        total_unique = len(dfc[dfc["Unique Dials"] == 1]) if "Unique Dials" in dfc.columns else 0

        # Talktime — HH:MM:SS to seconds convert
        def parse_talktime(val):
            try:
                val_str = str(val).strip()
                if val_str in ["", "0", "0:00:00", "00:00:00", "0.0"]:
                    return 0
                # HH:MM:SS string format
                if ":" in val_str:
                    parts = val_str.split(":")
                    if len(parts) == 3:
                        return int(parts[0])*3600 + int(parts[1])*60 + int(float(parts[2]))
                    elif len(parts) == 2:
                        return int(parts[0])*60 + int(float(parts[1]))
                # Google Sheets decimal format (fraction of a day)
                val_float = float(val_str)
                if 0 < val_float < 1:
                    return int(val_float * 86400)  # 1 day = 86400 seconds
                return int(val_float)
            except:
                return 0

        if "Talktime" in dfc.columns:
            dfc["_talktime_sec"] = dfc["Talktime"].apply(parse_talktime)
        else:
            dfc["_talktime_sec"] = 0

        total_talktime_sec = dfc["_talktime_sec"].sum()
        avg_talktime_sec   = dfc[dfc["_talktime_sec"] > 0]["_talktime_sec"].mean() if len(dfc[dfc["_talktime_sec"] > 0]) > 0 else 0
        total_tt_str = f"{int(total_talktime_sec//3600)}h {int((total_talktime_sec%3600)//60)}m {int(total_talktime_sec%60)}s"
        avg_tt_str   = f"{int(avg_talktime_sec//60)}m {int(avg_talktime_sec%60)}s"

        # Connection Rate — exact "Connected" match
        connected_calls = len(dfc[dfc["System Disposition"] == "Connected"]) if "System Disposition" in dfc.columns else 0
        connection_rate = round(connected_calls / total_calls * 100, 1) if total_calls > 0 else 0
        st.markdown(f"""
        <div class='kpi-wrap'>
          <div class='kpi-card c1'><div class='kpi-icon'>📞</div>
            <div class='kpi-label'>Total Calls</div>
            <div class='kpi-value'>{total_calls:,}</div>
            <div class='kpi-sub'>Total call records</div></div>
          <div class='kpi-card c2'><div class='kpi-icon'>🔢</div>
            <div class='kpi-label'>Unique Dials</div>
            <div class='kpi-value'>{int(total_unique):,}</div>
            <div class='kpi-sub'>Unique numbers dialed</div></div>
          <div class='kpi-card c3'><div class='kpi-icon'>⏱️</div>
            <div class='kpi-label'>Total Talktime</div>
            <div class='kpi-value'>{total_tt_str}</div>
            <div class='kpi-sub'>Total talk duration</div></div>
          <div class='kpi-card c4'><div class='kpi-icon'>📊</div>
            <div class='kpi-label'>Avg Talktime/Call</div>
            <div class='kpi-value'>{avg_tt_str}</div>
            <div class='kpi-sub'>Average per call</div></div>
          <div class='kpi-card c5'><div class='kpi-icon'>✅</div>
            <div class='kpi-label'>Connection Rate</div>
            <div class='kpi-value'>{connection_rate}%</div>
            <div class='kpi-sub'>Connected / Total calls</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── CHART THEME ──
        C_PAL = ["#388bfd","#3fb950","#d29922","#bc8cff","#ff7b72","#79c0ff","#56d364","#e3b341","#f0883e","#58a6ff"]
        def cbase(title="", h=320):
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

        # ── MONTHLY TREND ──
        st.markdown("<div class='sec-head'>📈 Monthly Call Trend</div>", unsafe_allow_html=True)
        if "Month" in dfc.columns:
            trend = dfc.groupby("Month").agg(
                Total_Calls=("Employee Name", "count"),
                Unique_Dials=("Unique Dials", "sum"),
                Talktime=("Talktime", "sum"),
            ).reset_index()
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=trend["Month"], y=trend["Total_Calls"],
                name="Total Calls", mode="lines+markers+text",
                line=dict(color="#388bfd", width=3),
                marker=dict(size=8, color="#388bfd", line=dict(color="#060d1a", width=2)),
                fill="tozeroy", fillcolor="rgba(56,139,253,0.07)",
                text=trend["Total_Calls"].astype(str),
                textposition="top center", textfont=dict(color="#388bfd", size=10),
            ))
            fig_trend.add_trace(go.Scatter(
                x=trend["Month"], y=trend["Unique_Dials"],
                name="Unique Dials", mode="lines+markers+text",
                line=dict(color="#3fb950", width=2, dash="dash"),
                marker=dict(size=7, color="#3fb950"),
                text=trend["Unique_Dials"].astype(str),
                textposition="bottom center", textfont=dict(color="#3fb950", size=10),
            ))
            fig_trend.update_layout(**cbase("Monthly Call Trend — Total Calls vs Unique Dials", h=350))
            fig_trend.update_layout(legend=dict(orientation="h", y=-0.2, font=dict(color=TXT, size=10), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_trend, use_container_width=True)

        # ── DISPOSITION CHARTS ──
        st.markdown("<div class='sec-head'>📋 Disposition Analysis</div>", unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            if "System Disposition" in dfc.columns:
                sys_disp = dfc["System Disposition"].value_counts().reset_index()
                sys_disp.columns = ["Disposition", "Count"]
                fig_sys = go.Figure(go.Pie(
                    labels=sys_disp["Disposition"], values=sys_disp["Count"],
                    hole=0.55,
                    marker=dict(colors=C_PAL[:len(sys_disp)], line=dict(color="#060d1a", width=3)),
                    texttemplate="%{label}<br>%{percent}",
                    textfont=dict(color="white", size=10),
                    pull=[0.04] + [0]*(len(sys_disp)-1)
                ))
                fig_sys.update_layout(**cbase("System Disposition Breakdown", h=350), showlegend=True)
                st.plotly_chart(fig_sys, use_container_width=True)
        with d2:
            if "Label Disposition" in dfc.columns:
                lbl_disp = dfc["Label Disposition"].value_counts().reset_index()
                lbl_disp.columns = ["Disposition", "Count"]
                fig_lbl = go.Figure(go.Bar(
                    x=lbl_disp["Count"], y=lbl_disp["Disposition"],
                    orientation="h",
                    marker=dict(color=C_PAL[:len(lbl_disp)], line=dict(color="rgba(0,0,0,0)")),
                    text=lbl_disp["Count"].astype(str),
                    textposition="outside",
                    textfont=dict(color="#c9d1d9", size=11)
                ))
                fig_lbl.update_layout(**cbase("Label Disposition Analysis", h=350))
                st.plotly_chart(fig_lbl, use_container_width=True)

        # ── AGENT PERFORMANCE TABLE ──
        st.markdown("<div class='sec-head'>👤 Agent wise Performance</div>", unsafe_allow_html=True)
        if "Employee Name" in dfc.columns:
            agent = dfc.groupby("Employee Name").agg(
                Total_Calls=("Employee Name", "count"),
                Unique_Dials=("Unique Dials", lambda x: (x == 1).sum()),
                Total_Talktime=("_talktime_sec", "sum"),
                Avg_Talktime=("_talktime_sec", lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0),
            ).reset_index()
            connected_df = dfc[dfc["System Disposition"] == "Connected"].groupby("Employee Name").size()
            agent["Connected"] = connected_df.reindex(agent["Employee Name"]).fillna(0).astype(int).values
            agent["Connection Rate%"] = (agent["Connected"] / agent["Total_Calls"] * 100).round(1)
            agent["Total_Talktime"] = agent["Total_Talktime"].apply(lambda x: f"{int(x//3600)}h {int((x%3600)//60)}m {int(x%60)}s")
            agent["Avg_Talktime"]   = agent["Avg_Talktime"].apply(lambda x: f"{int(x//60)}m {int(x%60)}s")
            agent = agent.sort_values("Total_Calls", ascending=False).reset_index(drop=True)
            # Total row
            total_row = pd.DataFrame([{
                "Employee Name": "TOTAL",
                "Total_Calls":   agent["Total_Calls"].sum() if "Total_Calls" in agent.columns else 0,
                "Unique_Dials":  agent["Unique_Dials"].sum() if "Unique_Dials" in agent.columns else 0,
                "Total_Talktime": f"{int(total_talktime_sec//3600)}h {int((total_talktime_sec%3600)//60)}m {int(total_talktime_sec%60)}s",
                "Avg_Talktime":  avg_tt_str,
                "Connected":     agent["Connected"].sum() if "Connected" in agent.columns else 0,
                "Connection Rate%": round(agent["Connected"].sum() / agent["Total_Calls"].sum() * 100, 1) if agent["Total_Calls"].sum() > 0 else 0,
            }])
            agent.columns = ["👤 Agent", "📞 Total Calls", "🔢 Unique Dials",
                             "⏱️ Total Talktime", "📊 Avg Talktime", "✅ Connected", "📈 Connection Rate%"]
            total_row.columns = ["👤 Agent", "📞 Total Calls", "🔢 Unique Dials",
                                 "⏱️ Total Talktime", "📊 Avg Talktime", "✅ Connected", "📈 Connection Rate%"]
            agent = pd.concat([agent, total_row], ignore_index=True)
            st.dataframe(agent, use_container_width=True, hide_index=True,
                         height=min(50 + len(agent) * 38, 500))

        # ── TL PERFORMANCE TABLE ──
        st.markdown("<div class='sec-head'>🏅 TL wise Team Performance</div>", unsafe_allow_html=True)
        if "Reporting TL" in dfc.columns:
            tl = dfc.groupby("Reporting TL").agg(
                Total_Calls=("Employee Name", "count"),
                Unique_Dials=("Unique Dials", lambda x: (x == 1).sum()),
                Total_Talktime=("_talktime_sec", "sum"),
                Agents=("Employee Name", "nunique"),
            ).reset_index()
            connected_tl = dfc[dfc["System Disposition"] == "Connected"].groupby("Reporting TL").size()
            tl["Connected"] = connected_tl.reindex(tl["Reporting TL"]).fillna(0).astype(int).values
            tl["Connection Rate%"] = (tl["Connected"] / tl["Total_Calls"] * 100).round(1)
            tl["Total_Talktime"] = tl["Total_Talktime"].apply(lambda x: f"{int(x//3600)}h {int((x%3600)//60)}m {int(x%60)}s")
            tl = tl.sort_values("Total_Calls", ascending=False).reset_index(drop=True)
            # Total row
            tl_total = pd.DataFrame([{
                "Reporting TL":  "TOTAL",
                "Total_Calls":   tl["Total_Calls"].sum(),
                "Unique_Dials":  tl["Unique_Dials"].sum(),
                "Total_Talktime": f"{int(total_talktime_sec//3600)}h {int((total_talktime_sec%3600)//60)}m {int(total_talktime_sec%60)}s",
                "Agents":        dfc["Employee Name"].nunique(),
                "Connected":     tl["Connected"].sum(),
                "Connection Rate%": round(tl["Connected"].sum() / tl["Total_Calls"].sum() * 100, 1) if tl["Total_Calls"].sum() > 0 else 0,
            }])
            tl.columns = ["🏅 TL Name", "📞 Total Calls", "🔢 Unique Dials",
                          "⏱️ Total Talktime", "👥 Agents", "✅ Connected", "📈 Connection Rate%"]
            tl_total.columns = ["🏅 TL Name", "📞 Total Calls", "🔢 Unique Dials",
                                "⏱️ Total Talktime", "👥 Agents", "✅ Connected", "📈 Connection Rate%"]
            tl = pd.concat([tl, tl_total], ignore_index=True)
            st.dataframe(tl, use_container_width=True, hide_index=True,
                         height=min(50 + len(tl) * 38, 500))
            l = dfc.groupby("Reporting TL").agg(
                Total_Calls=("Employee Name", "count"),
                Unique_Dials=("Unique Dials", "sum"),
                Total_Talktime=("Talktime", "sum"),
                Agents=("Employee Name", "nunique"),
            ).reset_index()
            tl["Connected"] = dfc[dfc["System Disposition"].str.lower().str.contains("connect", na=False)].groupby("Reporting TL").size().reindex(tl["Reporting TL"]).fillna(0).astype(int).values
            tl["Connection Rate%"] = (tl["Connected"] / tl["Total_Calls"] * 100).round(1)
            tl["Total_Talktime"]   = tl["Total_Talktime"].apply(lambda x: f"{int(x//60)}h {int(x%60)}m")
            tl = tl.sort_values("Total_Calls", ascending=False).reset_index(drop=True)
            tl.columns = ["🏅 TL Name", "📞 Total Calls", "🔢 Unique Dials",
                          "⏱️ Total Talktime", "👥 Agents", "✅ Connected", "📈 Connection Rate%"]
            st.dataframe(tl, use_container_width=True, hide_index=True,
                         height=min(50 + len(tl) * 38, 500))
            
elif page == "🎯 Leads Utilisation":
    st.markdown("# 🎯 Leads Utilisation")
    st.markdown("---")
    st.info("🚧 Coming Soon — Leads data yahan show hoga!")

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
