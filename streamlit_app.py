from core import StockAnalyzer
import streamlit as st
import pandas as pd
import yfinance as yf

import math

import plotly.graph_objects as go




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

@st.cache_data(ttl=3600)
def analyze_stock_x(ticker="ANTM.JK", period="3mo", interval="1d"):
    """
    Fungsi utama untuk menjalankan analisis lengkap
    
    Parameters:
    -----------
    ticker : str
        Kode saham (contoh: "ANTM.JK", "BMRI.JK")
    period : str
        Periode data (contoh: "1mo", "3mo", "6mo", "1y")
    interval : str
        Interval data (contoh: "1d", "1h", "15m")
    """
    # Inisialisasi analyzer
    analyzer = StockAnalyzer(ticker=ticker, period=period, interval=interval)
    
    # Jalankan semua analisis
    analyzer.info()
    analyzer.technical_analysis()
    analyzer.price_action_analysis()
    analyzer.fundamental_analysis()
    analyzer.valuation_analysis()  # Analisis baru
    analyzer.trading_recommendation()
    
    # Generate laporan
    return analyzer.results

    
# ==============================
# Graphical Rendering
# ==============================
def create_stock_chart(data, title="Stock Price"):
    """
    data: DataFrame dengan kolom ['date', 'open', 'high', 'low', 'close', 'volume']
    """
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data['date'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='Price',
        increasing_line_color='#26a69a',  # Hijau
        decreasing_line_color='#ef5350',   # Merah
    ))
    
    # MA 20
    if len(data) >= 20:
        data['MA20'] = data['close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['MA20'],
            name='MA 20',
            line=dict(color='#FFA726', width=2),
            opacity=0.7
        ))
    
    # MA 50
    if len(data) >= 50:
        data['MA50'] = data['close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['MA50'],
            name='MA 50',
            line=dict(color='#42a5f5', width=2),
            opacity=0.7
        ))
    
    # Layout customization
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        template='plotly_white',
        xaxis=dict(
            title='Date',
            rangeslider=dict(visible=False),
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            title='Price',
            gridcolor='#f0f0f0',
            tickformat='.2f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

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
    df = data.df.copy()


    # ===============================
    # PLOTLY CHARTS
    # ===============================
    fig_price = go.Figure()

    # -------------------------------
    # Candlestick
    # -------------------------------
    fig_price.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))

    # -------------------------------
    # EMA
    # -------------------------------
    fig_price.add_trace(go.Scatter(x=df.index, y=df['EMA_5'],  name='EMA 5'))
    fig_price.add_trace(go.Scatter(x=df.index, y=df['EMA_9'],  name='EMA 9'))
    fig_price.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20'))
    fig_price.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name='EMA 50'))

    # -------------------------------
    # Bollinger Bands
    # -------------------------------
    fig_price.add_trace(go.Scatter(
        x=df.index,
        y=df['BB_UPPER'],
        name='BB Upper',
        line=dict(dash='dot')
    ))
    fig_price.add_trace(go.Scatter(
        x=df.index,
        y=df['BB_LOWER'],
        name='BB Lower',
        line=dict(dash='dot'),
        fill='tonexty'
    ))

    # -------------------------------
    # SUPPORT & RESISTANCE
    # -------------------------------
    support_1 = safe_get(result, "technical.support")[0]
    support_2 = safe_get(result, "technical.support")[1]
    resistance_1 = safe_get(result, "technical.resistance")[0]
    resistance_2 = safe_get(result, "technical.resistance")[1]

    x_range = [df.index.min(), df.index.max()]

    if support_1:
        fig_price.add_trace(go.Scatter(
            x=x_range,
            y=[support_1, support_1],
            mode="lines",
            name="Support 1",
            line=dict(color="green", width=2, dash="dash")
        ))

    if support_2:
        fig_price.add_trace(go.Scatter(
            x=x_range,
            y=[support_2, support_2],
            mode="lines",
            name="Support 2",
            line=dict(color="green", width=1, dash="dot")
        ))

    if resistance_1:
        fig_price.add_trace(go.Scatter(
            x=x_range,
            y=[resistance_1, resistance_1],
            mode="lines",
            name="Resistance",
            line=dict(color="red", width=2, dash="dash")
        ))
    
    if resistance_2:
        fig_price.add_trace(go.Scatter(
            x=x_range,
            y=[resistance_2, resistance_2],
            mode="lines",
            name="Resistance 2",
            line=dict(color="red", width=1, dash="dot")
        ))

    # -------------------------------
    # Layout
    # -------------------------------
    fig_price.update_layout(
        title="📈 Price Chart + EMA + Bollinger Bands + S/R",
        height=500,
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig_price, use_container_width=True)


    #===============================
    # RSI CHART
    #==============================
    fig_rsi = go.Figure()

    fig_rsi.add_trace(go.Scatter(
        x=df.index, y=df['RSI'], name='RSI'
    ))

    # Level reference
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")

    fig_rsi.update_layout(
        title="📊 RSI Indicator",
        height=250,
        yaxis_range=[0,100]
    )

    st.plotly_chart(fig_rsi, use_container_width=True)

    # ===============================
    # MACD CHART (Histogram Merah-Hijau)
    # ===============================
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

    # Warna histogram: hijau jika >0, merah jika <0
    hist_colors = [
        "green" if val >= 0 else "red"
        for val in df["MACD_HIST"]
    ]

    fig_macd = go.Figure()

    # MACD Line (BIRU)
    fig_macd.add_trace(go.Scatter(
        x=df.index,
        y=df["MACD"],
        name="MACD",
        line=dict(color="blue", width=2)
    ))

    # Signal Line (KUNING)
    fig_macd.add_trace(go.Scatter(
        x=df.index,
        y=df["MACD_SIGNAL"],
        name="Signal",
        line=dict(color="gold", width=2, dash="dot")
    ))

    # Histogram Merah-Hijau
    fig_macd.add_trace(go.Bar(
        x=df.index,
        y=df["MACD_HIST"],
        name="Histogram",
        marker=dict(color=hist_colors),
        opacity=0.6
    ))

    fig_macd.update_layout(
        title="📉 MACD Indicator",
        height=300,
        barmode="relative",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.15)",
            zeroline=True,
            zerolinecolor="rgba(0,0,0,0.4)"
        )
    )

    st.plotly_chart(fig_macd, use_container_width=True)

    # ===============================
    # PRICE ACTION
    # ===============================
    fig = go.Figure()

    # ===============================
    # CLOSE PRICE (GARIS BIRU)
    # ===============================
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name="Close",
        line=dict(color="blue", width=2)
    ))

    # ===============================
    # SUPPORT & RESISTANCE
    # ===============================
    supports = safe_get(result, "technical.support", [])
    resistances = safe_get(result, "technical.resistance", [])

    for i, s in enumerate(supports):
        fig.add_hline(
            y=s,
            line=dict(
                color="green",
                width=1,
                dash="dash"
            ),
            annotation_text=f"Support {i+1}",
            annotation_position="left"
        )

    for i, r in enumerate(resistances):
        fig.add_hline(
            y=r,
            line=dict(
                color="red",
                width=1,
                dash="dash"
            ),
            annotation_text=f"Resistance {i+1}",
            annotation_position="left"
        )

    # ===============================
    # PRICE ACTION ZONES
    # ===============================
    zones = result.get("price_action", {}).get("zones", [])

    for zone in zones:
        zone_type = zone.get("type", "").upper()
        low = zone.get("low")
        high = zone.get("high")
        zone_date = pd.to_datetime(zone.get("date"))

        if not all([low, high, zone_date]):
            continue

        color = "rgba(0,180,0,0.25)" if zone_type == "DEMAND" else "rgba(220,0,0,0.2)"
        label = "Demand Zone" if zone_type == "DEMAND" else "Supply Zone"

        fig.add_shape(
            type="rect",
            x0=zone_date,
            x1=df.index.max(),
            y0=low,
            y1=high,
            fillcolor=color,
            line=dict(width=0),
            layer="below"
        )

        fig.add_annotation(
            x=zone_date,
            y=high,
            text=f"{label}<br>{low:.0f} - {high:.0f}",
            showarrow=False,
            font=dict(size=10),
            align="left"
        )

    # ===============================
    # LAYOUT
    # ===============================
    fig.update_layout(
        title="📊 Price Action + Support & Resistance",
        height=450,
        xaxis_title="Tanggal",
        yaxis_title="Harga",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


    # ===============================
    # VOLUME CHART
    # ===============================
    volume_colors = [
        "green" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "red"
        for i in range(len(df))
    ]

    fig_volume = go.Figure()

    fig_volume.add_trace(go.Bar(
        x=df.index,
        y=df["Volume"],
        name="Volume",
        marker=dict(color=volume_colors),
        opacity=0.6
    ))

    fig_volume.update_layout(
        title="📦 Volume Trading",
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            title="Volume",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.15)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig_volume, use_container_width=True)



    fig_price.update_layout(template="plotly_white")
    fig_rsi.update_layout(template="plotly_white")
    fig_macd.update_layout(template="plotly_white")
    fig.update_layout(template="plotly_white")
    fig_volume.update_layout(template="plotly_white")

    

    
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
                            {"".join([f"<li>{zone['type']} : {fmt(zone['low'])} - {fmt(zone['high'])} (Date: {zone['date']})</li>" for zone in safe_get(result, "price_action.zones", [])])}
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

                    <li>Alasan : {safe_get(result, "trading_recommendation.reason")}</li>
                </ul>
            </div>

        </div>
        """
        )

    # Render Auto Recommendation
    st.divider()
    render_auto_recommendation(data.generate_recommendation())

    #st.json(data.results)

    
    
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

    # ==============================
    # RELOAD DATA
    # ==============================
    col_reload, col_space = st.columns([1, 5])
    with col_reload:
        if st.button("🔄 Reload Data"):
            load_data.clear()   # clear cache @st.cache_data
            st.rerun()

    # ==============================
    # LOAD DATA
    # ==============================
    try:
        df_src = load_data()
    except Exception:
        st.error("❌ Gagal memuat data idx_list.csv")
        st.stop()

    # ==============================
    # SAFE COLUMN DEFAULT
    # ==============================
    safe_cols = [
        "Kode",
        "info_sector",
        "info_category",
        "trading_recommendation"
    ]

    for col in safe_cols:
        if col not in df_src.columns:
            df_src[col] = None

    # NULL → aman untuk UI
    df_src["info_sector"] = df_src["info_sector"].fillna("Unknown")
    df_src["info_category"] = df_src["info_category"].fillna("Unknown")
    df_src["trading_recommendation"] = df_src["trading_recommendation"].fillna("Unknown")

    # ==============================
    # FILTER UI
    # ==============================
    with st.container(border=True):
        st.subheader("🔍 Filter Saham")

        col1, col2, col3 = st.columns(3)

        with col1:
            sector = st.selectbox(
                "Sector",
                ["All"] + sorted(df_src["info_sector"].unique())
            )

        with col2:
            category = st.selectbox(
                "Category",
                ["All"] + sorted(df_src["info_category"].unique())
            )

        with col3:
            recommendation = st.selectbox(
                "Recommendation",
                ["All"] + sorted(df_src["trading_recommendation"].unique())
            )

    # ==============================
    # FILTER LOGIC (NULL SAFE)
    # ==============================
    filtered_df = df_src.copy()

    if sector != "All":
        filtered_df = filtered_df[filtered_df["info_sector"] == sector]

    if category != "All":
        filtered_df = filtered_df[filtered_df["info_category"] == category]

    if recommendation != "All":
        filtered_df = filtered_df[
            filtered_df["trading_recommendation"] == recommendation
        ]

    # ==============================
    # METRICS
    # ==============================
    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Total Saham", len(filtered_df))

    col2.metric(
        "🏭 Sector",
        filtered_df["info_sector"].nunique()
        if not filtered_df.empty else 0
    )

    col3.metric(
        "⭐ Rekomendasi",
        filtered_df["trading_recommendation"].nunique()
        if not filtered_df.empty else 0
    )

    st.divider()

    # ==============================
    # TABLE + DETAIL
    # ==============================
    st.subheader("📋 Daftar Saham")

    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data sesuai filter")
    else:
        table_df = filtered_df.copy()
        table_df["🔎 Detail"] = False

        column_order = ["🔎 Detail"] + [
            c for c in table_df.columns if c != "🔎 Detail"
        ]

        edited_df = st.data_editor(
            table_df,
            hide_index=True,
            width="stretch",
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
        # HANDLE CLICK DETAIL (SAFE)
        # ==============================
        clicked = edited_df[edited_df["🔎 Detail"] == True]

        if not clicked.empty:
            ticker = clicked.iloc[0].get("Kode")

            if pd.notna(ticker):
                st.session_state.selected_ticker = ticker
                st.session_state.page = "Detail"
                st.rerun()
            else:
                st.warning("⚠️ Kode saham tidak valid")

    # ==============================
    # DOWNLOAD CSV
    # ==============================
    st.subheader("⬇️ Download Data")

    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            csv,
            "idx_stock_screener.csv",
            "text/csv"
        )
    else:
        st.info("Tidak ada data untuk di-download")



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
    st.caption("Perbarui data saham dari Yahoo Finance")

    with st.container(border=True):
        with st.form("update_form"):
            col0, col1, col2, col3 = st.columns([3,3, 3, 1])
            with col0:
                total_stocks = st.number_input(
                    "Total Saham yang Ingin Diproses",
                    min_value=1,
                    max_value=1000,
                    value=950,
                    step=1
                )
            with col1:
                period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=2)

            with col2:
                interval = st.selectbox("Interval", ["1d", "1wk"], index=0)

            with col3:
                update_btn = st.form_submit_button("🔄 Update")

    if update_btn:
        try:
            with st.spinner("📡 Mengambil & menganalisis data saham..."):
                idx_url = "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/master/List%20Emiten/all.csv"

                idx = pd.read_csv(idx_url).head(total_stocks)
                tickers = idx["code"].dropna().unique()
                tickers = [f"{t}.JK" for t in tickers]

                results = []
                progress = st.progress(0)

                for i, ticker in enumerate(tickers):
                    try:
                        data = analyze_stock_x(
                            ticker=ticker,
                            period=period,
                            interval=interval
                        )
                        results.append({
                            "Kode": ticker,

                            "info_longName": data["info"].get("longName"),
                            "info_sector": data["info"].get("sector"),
                            "info_industry": data["info"].get("industry"),
                            "info_marketCap": data["info"].get("marketCap"),
                            "info_category": data["info"].get("category"),

                            "trading_recommendation": data["trading_recommendation"].get("status"),

                            "technical_trend": data["technical"].get("trend"),
                            "technical_momentum": data["technical"].get("momentum"),
                            "technical_signal": data["technical"].get("signal"),

                            "price_action_market_structure": data["price_action"].get("market_structure"),
                            "price_action_market_total_zones": data["price_action"].get("total_zones"),

                            "fundamental_score": data["fundamental"].get("score"),
                            "fundamental_rating": data["fundamental"].get("rating"),

                            "valuation_score": data["valuation"].get("valuation_score"),
                            "valuation_conclusion": data["valuation"].get("valuation_conclusion"),
                            "valuation_reason": data["valuation"].get("valuation_reason"),
                            "valuation_notes": "|".join(
                                data["valuation"].get("valuation_notes", [])
                            ),

                            "info_website": data["info"].get("website"),
                        })

                    except Exception as e:
                        # Jika error per saham → tetap lanjut
                        results.append({
                            "Kode": ticker,

                            "technical_trend": None,
                            "technical_momentum": None,
                            "technical_signal": None,

                            "price_action_market_structure": None,
                            "price_action_market_total_zones": None,

                            "fundamental_score": None,
                            "fundamental_rating": None,

                            "valuation_score": None,
                            "valuation_conclusion": None,
                            "valuation_reason": None,
                            "valuation_notes": None,
                        })

                        st.warning(f"⚠️ {ticker} gagal diproses")

                    progress.progress((i + 1) / len(tickers))

                screened = pd.DataFrame(results)

                df_sorted = screened.sort_values(
                    by="fundamental_score",
                    ascending=False
                )

                df_sorted.to_csv("idx_list.csv", index=False)

            st.success("✅ Update selesai! Data tersimpan ke idx_list.csv")

            # Preview hasil
            st.subheader("📊 Preview Top 20 Saham")
            st.dataframe(df_sorted.head(20), use_container_width=True)

        except Exception as e:
            st.error("🚦 Terlalu banyak request ke Yahoo Finance. Coba lagi nanti.")
            st.caption(str(e))


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
