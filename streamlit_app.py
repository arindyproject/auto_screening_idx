import streamlit as st
import pandas as pd
import yfinance as yf

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
@st.cache_data(ttl=3600)
def get_stock_data(ticker, period, interval):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    info = stock.fast_info  # lebih aman dari rate limit
    return hist, info

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
                period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "5y"])

            with col3:
                interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])

            with col4:
                submit = st.form_submit_button("🔍 Load")

    if submit or st.session_state.selected_ticker:
        st.session_state.selected_ticker = None

        try:
            with st.spinner("📡 Mengambil data dari Yahoo Finance..."):
                hist, info = get_stock_data(ticker, period, interval)

            st.subheader("📈 Harga Penutupan")
            st.line_chart(hist["Close"])

            st.subheader("ℹ️ Informasi Saham")
            info_df = pd.DataFrame(info.items(), columns=["Key", "Value"])
            st.dataframe(info_df, use_container_width=True)

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
