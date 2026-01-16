import streamlit as st
import pandas as pd
import yfinance as yf
from io import BytesIO



# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="IDX Stock Screener",
    layout="wide"
)

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    return pd.read_csv("idx_list.csv")

df = load_data()

# ==============================
# SIDEBAR MENU
# ==============================
st.sidebar.title("📊 IDX Stock Screener")
menu = st.sidebar.radio(
    "Menu",
    ["Home", "Detail", "Update", "About"]
)

# ==============================
# HOME
# ==============================
if menu == "Home":
    st.title("📈 IDX Stock Screener")

    st.subheader("🔍 Filter Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        sector = st.selectbox(
            "Sector",
            ["All"] + sorted(df["info_sector"].dropna().unique().tolist())
        )

    with col2:
        category = st.selectbox(
            "Category",
            ["All"] + sorted(df["info_category"].dropna().unique().tolist())
        )

    with col3:
        recommendation = st.selectbox(
            "Recommendation",
            ["All"] + sorted(df["trading_recommendation"].dropna().unique().tolist())
        )

    filtered_df = df.copy()

    if sector != "All":
        filtered_df = filtered_df[filtered_df["info_sector"] == sector]

    if category != "All":
        filtered_df = filtered_df[filtered_df["info_category"] == category]

    if recommendation != "All":
        filtered_df = filtered_df[filtered_df["trading_recommendation"] == recommendation]

    st.subheader(f"📋 Data Saham ({len(filtered_df)} saham)")
    st.dataframe(filtered_df, use_container_width=True)

    # ==============================
    # DOWNLOAD
    # ==============================
    st.subheader("⬇️ Download Data")

    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(filtered_df)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="idx_stock_screener.csv",
        mime="text/csv"
    )

# ==============================
# DETAIL
# ==============================
elif menu == "Detail":
    st.title("📌 Detail Saham (YFinance)")

    with st.form("detail_form"):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            ticker = st.text_input("Stock Ticker", value="BBRI.JK")

        with col2:
            period = st.selectbox(
                "Period",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
            )

        with col3:
            interval = st.selectbox(
                "Interval",
                ["1d", "1wk", "1mo"]
            )

        with col4:
            submit = st.form_submit_button("🔍 Load")

    if submit:
        with st.spinner("Mengambil data dari YFinance..."):
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            info = stock.info

        st.subheader("📊 Price History")
        st.line_chart(hist["Close"])

        st.subheader("ℹ️ Stock Info")
        info_df = pd.DataFrame.from_dict(info, orient="index", columns=["Value"])
        st.dataframe(info_df, use_container_width=True)

# ==============================
# UPDATE
# ==============================
elif menu == "Update":
    st.title("🔄 Update Data Saham (YFinance)")

    with st.form("update_form"):
        col1, col2, col3 = st.columns([3, 3, 1])

        with col1:
            period = st.selectbox(
                "Period",
                ["1mo", "3mo", "6mo", "1y"]
            )

        with col2:
            interval = st.selectbox(
                "Interval",
                ["1d", "1wk"]
            )

        with col3:
            update_btn = st.form_submit_button("🔄 Update")

    if update_btn:
        st.success("Data berhasil diperbarui (placeholder)")


# ==============================
# ABOUT
# ==============================
elif menu == "About":
    st.title("ℹ️ About")
    st.empty()
