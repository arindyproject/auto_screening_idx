from core import StockAnalyzer
import streamlit as st
import pandas as pd
import yfinance as yf

import math



# ===============================
# LOAD TAILWIND CDN
# ===============================
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Tambahkan custom CSS jika diperlukan */
    </style>
""", unsafe_allow_html=True)

# ==============================
# Hellper Functions
# ==============================
def fmt(value, suffix="", digits=2):
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return "-"
        return f"{round(value, digits)}{suffix}"
    except Exception:
        return "-"
    
def safe_get(d, path, default="-"):
    """
    Ambil value nested dict dengan aman
    path contoh: "info.longName"
    """
    try:
        for p in path.split("."):
            d = d[p]
        if d is None:
            return default
        return d
    except Exception:
        return default

def render_auto_recommendation(text: str):
    if not text:
        st.html("<p>-</p>")
        return

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    final_reco = ""
    normal_lines = []

    for line in lines:
        if line.startswith("🎯"):
            final_reco = line
        else:
            normal_lines.append(line)

    st.html(
        f"""
        <h2>🧠 Auto Trading Recommendation</h2>

        <ul style="font-size:14px; line-height:1.6;">
            {
                "".join([
                    f"<li>{line}</li>"
                    for line in normal_lines
                ])
            }
        </ul>

        {
            f'''
            <div style="
                margin-top:16px;
                padding:12px;
                border-radius:10px;
                background:#609BF3;
                border-left:6px solid #2ecc71;
                font-size:15px;
                font-weight:bold;
            ">
                {final_reco}
            </div>
            ''' if final_reco else ""
        }
        """
    )

def render_stock_result(result: dict | None, data: StockAnalyzer):

    st.html("""
        <style>
        /* ==============================
        THEME VARIABLES (LIGHT DEFAULT)
        ============================== */
        :root {
            --bg-card: #ffffff;
            --text-main: #111827;
            --text-muted: #6b7280;
            --border-color: #e5e7eb;
            --shadow: 0 8px 24px rgba(0,0,0,0.06);
        }

        /* ==============================
        AUTO DARK MODE (OS BASED)
        ============================== */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-card: #020617;
                --text-main: #e5e7eb;
                --text-muted: #94a3b8;
                --border-color: #1e293b;
                --shadow: 0 10px 30px rgba(0,0,0,0.4);
            }
        }

        /* ==============================
        GRID UTAMA
        ============================== */
        .grid-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            margin-top: 10px;
        }

        /* ==============================
        CARD
        ============================== */
        .card {
            background: var(--bg-card);
            color: var(--text-main);
            padding: 18px;
            border-radius: 14px;
            box-shadow: var(--shadow);
            font-size: 14px;
            border: 1px solid var(--border-color);
        }

        /* ==============================
        JUDUL CARD
        ============================== */
        .card h2 {
            font-size: 17px;
            margin-bottom: 10px;
        }

        /* ==============================
        LIST
        ============================== */
        .card ul {
            padding-left: 18px;
        }

        /* ==============================
        TABLE
        ============================== */
        .card table {
            width: 100%;
            border-collapse: collapse;
        }

        .card table th,
        .card table td {
            padding: 6px 8px;
            border-bottom: 1px solid var(--border-color);
            text-align: left;
            font-size: 13px;
        }

        /* ==============================
        MOBILE
        ============================== */
        @media (max-width: 900px) {
            .grid-container {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """)



    st.subheader(f"📊 {safe_get(result,'info.longName')} ({safe_get(result,'code')})")

    st.html(
        f"""
        <div class="grid-container">

            <!-- INFORMASI DASAR -->
            <div class="card">
                <h2>📋 Informasi Dasar</h2>
                <ul>
                    <li>Nama : {safe_get(result,'info.longName')}</li>
                    <li>Sector : {safe_get(result,"info.sector")}</li>
                    <li>Industry : {safe_get(result,"info.industry")}</li>
                    <li>Market Cap : {f"{safe_get(result,'info.marketCap'):,}"}</li>
                    <li>Kategori : {safe_get(result,"info.category")}</li>
                    <li>Website :
                        <a href="{safe_get(result,'info.website')}" target="_blank">
                            {safe_get(result,'info.website')}
                        </a>
                    </li>
                </ul>
            </div>

            <!-- TEKNIKAL -->
            <div class="card">
                    <h2>📈 Analisis Teknikal</h2>
                    <ul>
                        <li>Trend : {safe_get(result, "technical.trend")}</li>
                        <li>Momentum : {safe_get(result, "technical.momentum")}</li>
                        <li>RSI : {round(safe_get(result, "technical.rsi", 0), 2)}</li>
                        <li>Support : 
                            <ol>
                                <li>-> {safe_get(result, "technical.support")[0]}</li>
                                <li>-> {safe_get(result, "technical.support")[1]}</li>
                            </ol>
                        </li>
                        <li>Resistance : 
                            <ol>
                                <li>-> {safe_get(result, "technical.resistance")[0]}</li>
                                <li>-> {safe_get(result, "technical.resistance")[1]}</li>
                            </ol>
                        </li>
                        <li>Signal : {safe_get(result, "technical.signal")}</li>
                        <li>Trading Plan : 
                            <ul>
                                <li>Take Profit 2 : {safe_get(result, "technical.trading_plan.tp2")}</li>
                                <li>Take Profit 1 : {safe_get(result, "technical.trading_plan.tp1")}</li>
                                <li>Entry : {safe_get(result, "technical.trading_plan.entry")}</li>
                                <li>Stop Loss : {safe_get(result, "technical.trading_plan.sl")}</li>
                            </ul>
                        </li>
                    </ul>
            </div>

            <!-- PRICE ACTION -->
            <div class="card">
                <h2>📊 Price Action</h2>   
                <ul>
                    <li>Market Structure : {safe_get(result, "price_action.market_structure")}</li>
                    <li>Zones : 
                        <ol>
                            {"".join([f"<li>{zone['type']} : {zone['low']} - {zone['high']} (Date: {zone['date']})</li>" for zone in safe_get(result, "price_action.zones", [])])}
                        </ol>
                    </li>
                    <li>Total Zones : {safe_get(result, "price_action.total_zones")}</li>
                </ul>
            </div>

            <!-- FUNDAMENTAL -->
            <div class="card">
                <h2>🏦 Fundamental</h2>
                <ul>
                    <li>ROE : {fmt(safe_get(result, "fundamental.roe"), " %")}</li>
                    <li>ROA : {fmt(safe_get(result, "fundamental.roa"), " %")}</li>
                    <li>NPM : {fmt(safe_get(result, "fundamental.npm"), " %")}</li>
                    <li>DER : {fmt(safe_get(result, "fundamental.der"))}</li>
                    <li>PE  : {fmt(safe_get(result, "fundamental.pe"))}</li>
                    <li>PB  : {fmt(safe_get(result, "fundamental.pb"))}</li>

                    <li>Revenue Growth :
                        <ul>
                            <li>QoQ : {fmt(safe_get(result, "fundamental.revenue_growth.qoq"), " %")}</li>
                            <li>YoY : {fmt(safe_get(result, "fundamental.revenue_growth.yoy"), " %")}</li>
                        </ul>
                    </li>

                    <li>Net Income Growth :
                        <ul>
                            <li>QoQ : {fmt(safe_get(result, "fundamental.netincome_growth.qoq"), " %")}</li>
                            <li>YoY : {fmt(safe_get(result, "fundamental.netincome_growth.yoy"), " %")}</li>
                        </ul>
                    </li>

                    <li>Operating Cash Flow : {fmt(safe_get(result, "fundamental.operating_cf"))}</li>
                    <li>Fundamental Score : {safe_get(result, "fundamental.score") or "-"} / 100</li>
                    <li>Rating : {safe_get(result, "fundamental.rating") or "-"}</li>
                </ul>
            </div>

            <!-- VALUATION -->
            <div class="card">
                <h2>💰 Valuation</h2>
                <ul>
                    <li>Current Price : {fmt(safe_get(result, "valuation.current_price"))}</li>
                    <li>PE Ratio : {fmt(safe_get(result, "valuation.pe_ratio"))}</li>
                    <li>PB Ratio : {fmt(safe_get(result, "valuation.pb_ratio"))}</li>
                    <li>Dividend Yield : {fmt(safe_get(result, "valuation.dividend_yield"), " %")}</li>
                    <li>EV / EBITDA : {fmt(safe_get(result, "valuation.ev_ebitda"))}</li>
                    <li>PEG Ratio : {fmt(safe_get(result, "valuation.peg_ratio"))}</li>
                    <li>PS Ratio : {fmt(safe_get(result, "valuation.ps_ratio"))}</li>
                    <li>Industry PE : {fmt(safe_get(result, "valuation.industry_pe"))}</li>

                    <li>Intrinsic Value : {fmt(safe_get(result, "valuation.intrinsic_value"))}</li>
                    <li>Margin of Safety : {fmt(safe_get(result, "valuation.margin_of_safety"), " %")}</li>

                    <li>Valuation Score : {safe_get(result, "valuation.valuation_score") or "-"} / 100</li>

                    <li><strong>Conclusion :</strong> 
                        {safe_get(result, "valuation.valuation_conclusion") or "-"}
                    </li>

                    <li>Reason :
                        {safe_get(result, "valuation.valuation_reason") or "-"}
                    </li>

                    <li>Notes :
                        <ul>
                            {
                                "".join([
                                    f"<li>{note}</li>"
                                    for note in safe_get(result, "valuation.valuation_notes", [])
                                ]) or "<li>-</li>"
                            }
                        </ul>
                    </li>
                </ul>
            </div>

            <!-- TRADING PLAN -->
            <div class="card">
                <h2>📈 Trading Recommendation</h2>
                <ul>
                    <li><strong>Status :</strong> {safe_get(result, "trading_recommendation.status") or "-"}</li>
                    <li><strong>Signal :</strong> {safe_get(result, "trading_recommendation.signal") or "-"}</li>
                    <li><strong>Trend :</strong> {safe_get(result, "trading_recommendation.trend") or "-"}</li>

                    <li>Entry Price : {fmt(safe_get(result, "trading_recommendation.entry_price"))}</li>
                    <li>Stop Loss : {fmt(safe_get(result, "trading_recommendation.stop_loss"))}</li>

                    <li>Take Profit :
                        <ul>
                            <li>TP 1 : {fmt(safe_get(result, "trading_recommendation.take_profit.tp1"))}</li>
                            <li>TP 2 : {fmt(safe_get(result, "trading_recommendation.take_profit.tp2"))}</li>
                        </ul>
                    </li>

                    <li>Risk per Share : {fmt(safe_get(result, "trading_recommendation.risk_per_share"))}</li>

                    <li>Reward Ratio :
                        <ul>
                            <li>RR TP1 : {fmt(safe_get(result, "trading_recommendation.reward.rr_tp1"))}</li>
                            <li>RR TP2 : {fmt(safe_get(result, "trading_recommendation.reward.rr_tp2"))}</li>
                        </ul>
                    </li>

                    <li>Risk Management :
                        <ul>
                            <li>Max Risk : {fmt(safe_get(result, "trading_recommendation.risk_management.max_risk_pct"), " %")}</li>
                            <li>Rule : {safe_get(result, "trading_recommendation.risk_management.rule") or "-"}</li>
                        </ul>
                    </li>

                    <li>Notes :
                        <ul>
                            {
                                "".join([
                                    f"<li>{note}</li>"
                                    for note in safe_get(result, "trading_recommendation.notes", [])
                                ]) or "<li>-</li>"
                            }
                        </ul>
                    </li>
                </ul>
            </div>

        </div>
        """
        )

    # Render Auto Recommendation
    st.divider()
    render_auto_recommendation(data.generate_recommendation())

    






    
    
def render_stock_resultx(result: dict):
    # ==============================
    # HEADER
    # ==============================
    st.markdown(
        f"""
        ## 📌 {safe_get(result, 'code')}
        **{safe_get(result, 'info.longName')}**
        """
    )

    # ==============================
    # BASIC INFO
    # ==============================
    with st.container(border=True):
        st.subheader("ℹ️ Informasi Perusahaan")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sector", safe_get(result, "info.sector"))
        col2.metric("Industry", safe_get(result, "info.industry"))
        col3.metric("Market Cap", f"{safe_get(result, 'info.marketCap'):,}")
        col4.metric("Kategori", safe_get(result, "info.category"))

        st.markdown(f"🌐 Website: {safe_get(result, 'info.website')}")

    # ==============================
    # TECHNICAL
    # ==============================
    with st.container(border=True):
        st.subheader("📈 Analisis Teknikal")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trend", safe_get(result, "technical.trend"))
        col2.metric("Momentum", safe_get(result, "technical.momentum"))
        col3.metric("RSI", round(safe_get(result, "technical.rsi", 0), 2))
        col4.metric("Signal", safe_get(result, "technical.signal"))

        st.markdown("**Support**")
        st.write(safe_get(result, "technical.support", []))

        st.markdown("**Resistance**")
        st.write(safe_get(result, "technical.resistance", []))

    # ==============================
    # PRICE ACTION
    # ==============================
    with st.container(border=True):
        st.subheader("📊 Price Action")

        st.metric(
            "Market Structure",
            safe_get(result, "price_action.market_structure")
        )

        zones = safe_get(result, "price_action.zones", [])
        if zones and isinstance(zones, list):
            zone_df = pd.DataFrame(zones)
            st.dataframe(zone_df, use_container_width=True)
        else:
            st.info("Tidak ada zona supply / demand")

    # ==============================
    # FUNDAMENTAL
    # ==============================
    with st.container(border=True):
        st.subheader("🏦 Fundamental")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("ROE", safe_get(result, "fundamental.roe"))
        col2.metric("ROA", safe_get(result, "fundamental.roa"))
        col3.metric("NPM", safe_get(result, "fundamental.npm"))
        col4.metric("DER", safe_get(result, "fundamental.der"))

        col1, col2 = st.columns(2)
        col1.metric("Fundamental Score", safe_get(result, "fundamental.score"))
        col2.metric("Rating", safe_get(result, "fundamental.rating"))

    # ==============================
    # VALUATION
    # ==============================
    with st.container(border=True):
        st.subheader("💰 Valuation")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Harga Saat Ini", safe_get(result, "valuation.current_price"))
        col2.metric("PER", safe_get(result, "valuation.pe_ratio"))
        col3.metric("PBV", safe_get(result, "valuation.pb_ratio"))
        col4.metric("EV/EBITDA", safe_get(result, "valuation.ev_ebitda"))

        st.metric(
            "Kesimpulan Valuasi",
            safe_get(result, "valuation.valuation_conclusion")
        )

        notes = safe_get(result, "valuation.valuation_notes", [])
        if notes:
            st.markdown("**Catatan Valuasi:**")
            for n in notes:
                st.write(n)

    # ==============================
    # FINAL RECOMMENDATION
    # ==============================
    with st.container(border=True):
        st.subheader("🎯 Trading Recommendation")

        st.metric(
            "Status",
            safe_get(result, "trading_recommendation.status")
        )

        st.write(
            "📌 Alasan:",
            safe_get(result, "trading_recommendation.reason")
        )

def render_stock_result_compact(r: dict):
    # =========================
    # HEADER
    # =========================
    st.markdown(
        f"### 📌 {safe_get(r,'code')} — {safe_get(r,'info.longName')}"
    )

    # =========================
    # BASIC INFO (1 BARIS)
    # =========================
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Sector", safe_get(r, "info.sector"))
    c2.metric("Industry", safe_get(r, "info.industry"))
    c3.metric("Category", safe_get(r, "info.category"))
    c4.metric("Market Cap", f"{safe_get(r,'info.marketCap'):,}")
    c5.metric("Exchange", safe_get(r, "info.exchange"))

    st.divider()

    # =========================
    # TECHNICAL (PADAT)
    # =========================
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Trend", safe_get(r, "technical.trend"))
    c2.metric("Momentum", safe_get(r, "technical.momentum"))
    c3.metric("RSI", round(safe_get(r, "technical.rsi", 0), 2))
    c4.metric("Close", safe_get(r, "technical.close"))
    c5.metric("Signal", safe_get(r, "technical.signal"))

    # Support / Resistance (inline)
    st.caption(
        f"🟢 Support: {safe_get(r,'technical.support')} | "
        f"🔴 Resistance: {safe_get(r,'technical.resistance')}"
    )

    st.divider()

    # =========================
    # PRICE ACTION (MINI)
    # =========================
    c1, c2 = st.columns([1, 4])
    c1.metric(
        "Market Structure",
        safe_get(r, "price_action.market_structure")
    )
    c2.caption(
        f"Zones: {safe_get(r,'price_action.total_zones',0)}"
    )

    zones = safe_get(r, "price_action.zones", [])
    if zones:
        st.dataframe(
            pd.DataFrame(zones)[["type", "low", "high", "date"]],
            use_container_width=True,
            height=150
        )

    st.divider()

    # =========================
    # FUNDAMENTAL (INTI SAJA)
    # =========================
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("ROE", safe_get(r, "fundamental.roe"))
    c2.metric("ROA", safe_get(r, "fundamental.roa"))
    c3.metric("NPM", safe_get(r, "fundamental.npm"))
    c4.metric("DER", safe_get(r, "fundamental.der"))
    c5.metric("Score", safe_get(r, "fundamental.score"))

    st.caption(f"Rating: {safe_get(r,'fundamental.rating')}")

    st.divider()

    # =========================
    # VALUATION (PADAT)
    # =========================
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Price", safe_get(r, "valuation.current_price"))
    c2.metric("PER", safe_get(r, "valuation.pe_ratio"))
    c3.metric("PBV", safe_get(r, "valuation.pb_ratio"))
    c4.metric("EV/EBITDA", safe_get(r, "valuation.ev_ebitda"))
    c5.metric("Score", safe_get(r, "valuation.valuation_score"))

    st.caption(
        f"💡 {safe_get(r,'valuation.valuation_conclusion')} | "
        f"Intrinsic: {round(safe_get(r,'valuation.intrinsic_value',0),2)}"
    )

    # =========================
    # FINAL DECISION (HIGHLIGHT)
    # =========================
    st.markdown(
        f"### 🎯 RECOMMENDATION: **{safe_get(r,'trading_recommendation.status')}**"
    )
    st.caption(safe_get(r, "trading_recommendation.reason"))


# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="IDX Stock Screener",
    page_icon="📊",
    layout="wide",
)

# ==============================
# SESSION STATE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    return pd.read_csv("idx_list.csv")

df = load_data()


# ==============================
# YFINANCE CACHE
# ==============================
#@st.cache_data(ttl=3600)
def get_stock_data(ticker, period, interval):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    info = stock.fast_info  # lebih aman dari rate limit
    return hist, info

# ===========================================
# MAIN EXECUTION (DIPERBARUI)
# ===========================================
def analyze_stock(ticker="ANTM.JK", period="3mo", interval="1d"):

    # Inisialisasi analyzer
    analyzer = StockAnalyzer(ticker=ticker, period=period, interval=interval)
    
    # Jalankan semua analisis
    analyzer.info()
    analyzer.technical_analysis()
    analyzer.price_action_analysis()
    analyzer.fundamental_analysis()
    analyzer.valuation_analysis()  # Analisis baru
    
    
    # Generate laporan
    #analyzer.print_info()
    #analyzer.generate_report()
    #analyzer.generate_recommendation()

    analyzer.trading_recommendation()
    #analyzer.print_trading_recommendation()
    
    #analyzer.visualize()
    
    return analyzer

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.markdown("## 📊 IDX Stock Screener")
    st.caption("Stock Screener & Analysis")
    st.divider()

    menu = st.radio(
        "Navigation",
        ["🏠 Home", "📌 Detail", "🔄 Update", "ℹ️ About"],
        index=["Home", "Detail", "Update", "About"].index(st.session_state.page)
    )

    st.divider()
    st.caption("📈 Powered by YFinance")

# Sinkronisasi sidebar → state
st.session_state.page = menu.replace("🏠 ", "").replace("📌 ", "").replace("🔄 ", "").replace("ℹ️ ", "")


# ==============================
# HOME
# ==============================
if st.session_state.page == "Home":
    st.markdown("# 📈 IDX Stock Screener")
    st.caption("Filter & eksplorasi saham IDX")

    # FILTER
    with st.container(border=True):
        st.subheader("🔍 Filter Saham")

        col1, col2, col3 = st.columns(3)

        with col1:
            sector = st.selectbox(
                "Sector",
                ["All"] + sorted(df["info_sector"].dropna().unique())
            )

        with col2:
            category = st.selectbox(
                "Category",
                ["All"] + sorted(df["info_category"].dropna().unique())
            )

        with col3:
            recommendation = st.selectbox(
                "Recommendation",
                ["All"] + sorted(df["trading_recommendation"].dropna().unique())
            )

    # FILTER LOGIC
    filtered_df = df.copy()

    if sector != "All":
        filtered_df = filtered_df[filtered_df["info_sector"] == sector]
    if category != "All":
        filtered_df = filtered_df[filtered_df["info_category"] == category]
    if recommendation != "All":
        filtered_df = filtered_df[filtered_df["trading_recommendation"] == recommendation]

    # METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Total Saham", len(filtered_df))
    col2.metric("🏭 Sector", filtered_df["info_sector"].nunique())
    col3.metric("⭐ Rekomendasi", filtered_df["trading_recommendation"].nunique())

    st.divider()

    # ==============================
    # TABLE + FIXED DETAIL COLUMN
    # ==============================
    st.subheader("📋 Daftar Saham")

    table_df = filtered_df.copy()

    # Tambahkan kolom Detail
    table_df["🔎 Detail"] = False

    # Urutan kolom: Detail di depan
    column_order = ["🔎 Detail"] + [c for c in table_df.columns if c != "🔎 Detail"]

    edited_df = st.data_editor(
        table_df,
        hide_index=True,
        use_container_width=True,
        height=500,
        column_order=column_order,
        column_config={
            "🔎 Detail": st.column_config.CheckboxColumn(
                "Detail",
                help="Klik untuk melihat detail saham",
                width="small"
            )
        },
        disabled=[c for c in table_df.columns if c != "🔎 Detail"],
    )

    # ==============================
    # HANDLE CLICK
    # ==============================
    clicked = edited_df[edited_df["🔎 Detail"] == True]

    if not clicked.empty:
        ticker = clicked.iloc[0]["Kode"]  # pastikan nama kolom benar
        st.session_state.selected_ticker = ticker
        st.session_state.page = "Detail"
        st.rerun()


    # DOWNLOAD
    st.subheader("⬇️ Download Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download CSV",
        csv,
        "idx_stock_screener.csv",
        "text/csv"
    )

# ==============================
# DETAIL
# ==============================
elif st.session_state.page == "Detail":
    st.markdown("# 📌 Detail Saham")
    st.caption("Data historis & informasi saham")

    default_ticker = (
        st.session_state.selected_ticker
        if st.session_state.selected_ticker
        else "BBRI.JK"
    )

    with st.container(border=True):
        with st.form("detail_form"):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                ticker = st.text_input("Ticker", default_ticker)

            with col2:
                period = st.selectbox("Period", ["6mo","3mo","1mo",   "1y", "5y"])

            with col3:
                interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])

            with col4:
                submit = st.form_submit_button("🔍 Load")

    if submit or st.session_state.selected_ticker:
        st.session_state.selected_ticker = None

        try:
            with st.spinner("📡 Memproses Data....."):
                data = analyze_stock(ticker, period, interval)

            render_stock_result(data.results, data)
        except Exception:
            st.error("🚦 Terlalu banyak request ke Yahoo Finance. Coba lagi nanti.")

# ==============================
# UPDATE
# ==============================
elif menu == "🔄 Update":
    st.markdown("# 🔄 Update Data")
    st.caption("Perbarui data saham dari sumber eksternal")

    with st.container(border=True):
        with st.form("update_form"):
            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])

            with col2:
                interval = st.selectbox("Interval", ["1d", "1wk"])

            with col3:
                update_btn = st.form_submit_button("🔄 Update")

    if update_btn:
        st.success("✅ Data berhasil diperbarui (simulasi)")

# ==============================
# ABOUT
# ==============================
elif menu == "ℹ️ About":
    st.markdown("# ℹ️ About")
    st.info(
        """
        **IDX Stock Screener**  
        
        Aplikasi ini digunakan untuk:
        - Menyaring saham IDX  
        - Analisis data teknikal & fundamental ringan  
        - Mengambil data real-time dari YFinance  

        📌 Dibangun dengan **Streamlit & Python**
        """
    )
