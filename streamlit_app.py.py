# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="IDX Stock Screener Pro",
    page_icon="📈",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stock-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #3B82F6;
    }
    .positive {
        color: #10B981;
        font-weight: bold;
    }
    .negative {
        color: #EF4444;
        font-weight: bold;
    }
    .neutral {
        color: #6B7280;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📈 IDX Stock Screener Pro</h1>', unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Ticker input
    ticker_input = st.text_input("Enter Stock Ticker", "ANTM.JK")
    
    # Analysis parameters
    period_options = ["1mo", "3mo", "6mo", "1y", "2y"]
    selected_period = st.selectbox("Period", period_options, index=2)
    
    interval_options = ["1d", "1wk", "1mo"]
    selected_interval = st.selectbox("Interval", interval_options)
    
    # Screening controls
    st.header("🔍 Bulk Screening")
    max_stocks = st.slider("Max Stocks to Screen", 1, 100, 20)
    
    if st.button("Start Screening", type="primary"):
        st.session_state.run_screening = True
    
    # Filters
    st.header("📊 Filters")
    
    filter_category = st.selectbox(
        "Category",
        ["All", "Bluechip", "Menengah", "Kecil"]
    )
    
    filter_status = st.selectbox(
        "Trading Status",
        ["All", "LAYAK DITRADINGKAN", "WAIT", "TIDAK LAYAK"]
    )
    
    filter_signal = st.selectbox(
        "Signal",
        ["All", "BUY", "SELL", "NO TRADE"]
    )
    
    min_score = st.slider("Minimum Score", 0, 100, 0)

# Stock Analyzer Class (Simplified)
class StockAnalyzer:
    def __init__(self, ticker, period="6mo", interval="1d"):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.df = None
        self.results = {}
    
    def analyze(self):
        try:
            # Get stock info
            stock = yf.Ticker(self.ticker)
            info = stock.info
            
            # Basic info
            self.results = {
                "ticker": self.ticker,
                "name": info.get("longName", self.ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0)
            }
            
            # Get price data
            self.df = yf.download(
                self.ticker,
                period=self.period,
                interval=self.interval,
                progress=False
            )
            
            if not self.df.empty:
                # Calculate technical indicators
                self.calculate_indicators()
                
                # Get latest values
                latest = self.df.iloc[-1]
                
                # Technical analysis
                close = float(latest["Close"])
                ema20 = float(self.df["EMA_20"].iloc[-1])
                ema50 = float(self.df["EMA_50"].iloc[-1])
                rsi = float(self.df["RSI"].iloc[-1])
                
                # Trend
                if close > ema20 > ema50:
                    trend = "BULLISH"
                elif close < ema20 < ema50:
                    trend = "BEARISH"
                else:
                    trend = "SIDEWAYS"
                
                # Signal
                if rsi > 60 and close > ema20:
                    signal = "BUY"
                elif rsi < 40 and close < ema20:
                    signal = "SELL"
                else:
                    signal = "NO TRADE"
                
                self.results.update({
                    "price": close,
                    "trend": trend,
                    "signal": signal,
                    "rsi": rsi,
                    "ema20": ema20,
                    "ema50": ema50
                })
            
            # Fundamental analysis (simplified)
            pe = info.get("trailingPE", 0)
            pb = info.get("priceToBook", 0)
            roe = info.get("returnOnEquity", 0)
            
            if roe:
                roe = roe * 100
            
            # Calculate scores
            tech_score = 50  # Base score
            if self.results.get("signal") == "BUY":
                tech_score += 25
            elif self.results.get("signal") == "SELL":
                tech_score -= 25
            
            fund_score = 0
            if pe and pe < 20:
                fund_score += 25
            if pb and pb < 2:
                fund_score += 25
            if roe and roe > 15:
                fund_score += 25
            if info.get("dividendYield"):
                fund_score += 25
            
            total_score = (tech_score + fund_score) / 2
            
            self.results.update({
                "pe": pe,
                "pb": pb,
                "roe": roe,
                "tech_score": tech_score,
                "fund_score": fund_score,
                "total_score": total_score
            })
            
            return self.results
            
        except Exception as e:
            st.error(f"Error analyzing {self.ticker}: {str(e)}")
            return None
    
    def calculate_indicators(self):
        """Calculate technical indicators"""
        self.df["EMA_20"] = self.df["Close"].ewm(span=20).mean()
        self.df["EMA_50"] = self.df["Close"].ewm(span=50).mean()
        
        # RSI calculation
        delta = self.df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.df["RSI"] = 100 - (100 / (1 + rs))
    
    def plot_chart(self):
        """Create interactive price chart"""
        if self.df is None or self.df.empty:
            return None
        
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=self.df.index,
            y=self.df['Close'],
            mode='lines',
            name='Close',
            line=dict(color='blue', width=2)
        ))
        
        # Add EMA lines
        fig.add_trace(go.Scatter(
            x=self.df.index,
            y=self.df['EMA_20'],
            mode='lines',
            name='EMA 20',
            line=dict(color='orange', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.df.index,
            y=self.df['EMA_50'],
            mode='lines',
            name='EMA 50',
            line=dict(color='red', width=1, dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{self.ticker} Price Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode='x unified',
            height=500,
            showlegend=True
        )
        
        return fig

# Main content area
tab1, tab2, tab3 = st.tabs(["📊 Single Analysis", "🔍 Bulk Screening", "📈 Dashboard"])

with tab1:
    st.header("Single Stock Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if ticker_input:
            analyzer = StockAnalyzer(ticker_input, selected_period, selected_interval)
            results = analyzer.analyze()
            
            if results:
                # Display basic info
                st.subheader("📋 Company Information")
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.metric("Ticker", results["ticker"])
                    st.metric("Sector", results["sector"])
                
                with info_col2:
                    st.metric("Price", f"Rp {results.get('price', 0):,.0f}")
                    st.metric("P/E Ratio", f"{results.get('pe', 0):.2f}")
                
                with info_col3:
                    # Determine color for trend
                    trend_color = "positive" if results["trend"] == "BULLISH" else "negative" if results["trend"] == "BEARISH" else "neutral"
                    signal_color = "positive" if results["signal"] == "BUY" else "negative" if results["signal"] == "SELL" else "neutral"
                    
                    st.markdown(f"**Trend:** <span class='{trend_color}'>{results['trend']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Signal:** <span class='{signal_color}'>{results['signal']}</span>", unsafe_allow_html=True)
                
                # Technical indicators
                st.subheader("📈 Technical Indicators")
                tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
                
                with tech_col1:
                    st.metric("RSI", f"{results.get('rsi', 0):.2f}")
                
                with tech_col2:
                    st.metric("EMA 20", f"Rp {results.get('ema20', 0):,.0f}")
                
                with tech_col3:
                    st.metric("EMA 50", f"Rp {results.get('ema50', 0):,.0f}")
                
                with tech_col4:
                    st.metric("Tech Score", f"{results.get('tech_score', 0):.0f}/100")
                
                # Fundamental metrics
                st.subheader("💰 Fundamental Metrics")
                fund_col1, fund_col2, fund_col3, fund_col4 = st.columns(4)
                
                with fund_col1:
                    st.metric("P/B Ratio", f"{results.get('pb', 0):.2f}")
                
                with fund_col2:
                    st.metric("ROE", f"{results.get('roe', 0):.2f}%")
                
                with fund_col3:
                    st.metric("Fundamental Score", f"{results.get('fund_score', 0):.0f}/100")
                
                with fund_col4:
                    total_score = results.get('total_score', 0)
                    score_color = "positive" if total_score >= 70 else "negative" if total_score < 40 else "neutral"
                    st.markdown(f"**Total Score:** <span class='{score_color}'>{total_score:.0f}/100</span>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎯 Trading Recommendation")
        
        if results:
            # Create recommendation card
            with st.container():
                st.markdown('<div class="stock-card">', unsafe_allow_html=True)
                
                if results["signal"] == "BUY":
                    st.success("**RECOMMENDATION: BUY**")
                    st.write("**Reason:** Technical indicators show bullish momentum with strong fundamentals")
                    
                    # Trading plan
                    st.write("**Trading Plan:**")
                    entry = results["price"]
                    sl = entry * 0.95  # 5% stop loss
                    tp = entry * 1.10  # 10% take profit
                    
                    st.write(f"- Entry: Rp {entry:,.0f}")
                    st.write(f"- Stop Loss: Rp {sl:,.0f}")
                    st.write(f"- Take Profit: Rp {tp:,.0f}")
                    
                    risk_reward = (tp - entry) / (entry - sl)
                    st.write(f"- Risk/Reward: 1 : {risk_reward:.2f}")
                
                elif results["signal"] == "SELL":
                    st.error("**RECOMMENDATION: SELL**")
                    st.write("**Reason:** Bearish trend detected with weakening fundamentals")
                
                else:
                    st.warning("**RECOMMENDATION: HOLD/NO TRADE**")
                    st.write("**Reason:** Market is sideways, wait for clearer signals")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Price chart
    st.subheader("📉 Price Chart with Indicators")
    if analyzer.df is not None:
        chart_fig = analyzer.plot_chart()
        if chart_fig:
            st.plotly_chart(chart_fig, use_container_width=True)

with tab2:
    st.header("Bulk Stock Screening")
    
    if 'run_screening' in st.session_state and st.session_state.run_screening:
        with st.spinner(f"Screening {max_stocks} stocks..."):
            # Get sample tickers (in real app, load from IDX list)
            sample_tickers = [
                "ANTM.JK", "ASII.JK", "BBCA.JK", "BBRI.JK", "BMRI.JK",
                "BRPT.JK", "BSDE.JK", "EXCL.JK", "ICBP.JK", "INDF.JK",
                "INTP.JK", "ITMG.JK", "JSMR.JK", "KLBF.JK", "MNCN.JK",
                "PGAS.JK", "PTBA.JK", "SMGR.JK", "TLKM.JK", "UNVR.JK"
            ][:max_stocks]
            
            results_list = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ticker in enumerate(sample_tickers):
                status_text.text(f"Analyzing {ticker}...")
                
                analyzer = StockAnalyzer(ticker, selected_period, selected_interval)
                result = analyzer.analyze()
                
                if result:
                    results_list.append({
                        "Ticker": ticker,
                        "Name": result.get("name", "")[:20],
                        "Sector": result.get("sector", ""),
                        "Price": result.get("price", 0),
                        "Trend": result.get("trend", ""),
                        "Signal": result.get("signal", ""),
                        "RSI": result.get("rsi", 0),
                        "P/E": result.get("pe", 0),
                        "Score": result.get("total_score", 0)
                    })
                
                progress_bar.progress((i + 1) / len(sample_tickers))
            
            status_text.text("Analysis complete!")
            progress_bar.empty()
            
            # Create results DataFrame
            if results_list:
                results_df = pd.DataFrame(results_list)
                
                # Apply filters
                if filter_category != "All":
                    # Note: In full version, would filter by actual category
                    pass
                
                if filter_status != "All":
                    # Note: In full version, would filter by status
                    pass
                
                if filter_signal != "All":
                    results_df = results_df[results_df["Signal"] == filter_signal]
                
                results_df = results_df[results_df["Score"] >= min_score]
                
                # Sort by score
                results_df = results_df.sort_values("Score", ascending=False)
                
                # Display results
                st.subheader(f"📊 Screening Results ({len(results_df)} stocks)")
                
                # Color code the table
                def color_signal(val):
                    if val == "BUY":
                        return 'background-color: #d4edda; color: #155724;'
                    elif val == "SELL":
                        return 'background-color: #f8d7da; color: #721c24;'
                    else:
                        return 'background-color: #fff3cd; color: #856404;'
                
                def color_trend(val):
                    if val == "BULLISH":
                        return 'background-color: #d4edda; color: #155724;'
                    elif val == "BEARISH":
                        return 'background-color: #f8d7da; color: #721c24;'
                    else:
                        return 'background-color: #e2e3e5; color: #383d41;'
                
                # Apply styling
                styled_df = results_df.style.applymap(color_signal, subset=['Signal'])
                styled_df = styled_df.applymap(color_trend, subset=['Trend'])
                
                st.dataframe(
                    styled_df.format({
                        "Price": "Rp {:,.0f}",
                        "RSI": "{:.2f}",
                        "P/E": "{:.2f}",
                        "Score": "{:.0f}"
                    }),
                    use_container_width=True,
                    height=400
                )
                
                # Download button
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"stock_screening_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Summary statistics
                st.subheader("📈 Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Analyzed", len(results_list))
                
                with col2:
                    buy_count = len(results_df[results_df["Signal"] == "BUY"])
                    st.metric("BUY Signals", buy_count)
                
                with col3:
                    avg_score = results_df["Score"].mean()
                    st.metric("Average Score", f"{avg_score:.1f}")
                
                with col4:
                    st.metric("High Score", f"{results_df['Score'].max():.0f}")
            
            else:
                st.warning("No results to display")

with tab3:
    st.header("Market Dashboard")
    
    # Placeholder for dashboard
    st.info("Dashboard features coming soon...")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Performers")
        # Would show top scoring stocks
        
    with col2:
        st.subheader("Market Overview")
        # Would show market statistics

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280;'>
    <p>IDX Stock Screener Pro • Data from Yahoo Finance • For educational purposes only</p>
    <p>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
</div>
""", unsafe_allow_html=True)