# ===========================================
# IMPORT LIBRARY
# ===========================================
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# ===========================================
# SETUP UTAMA
# ===========================================
class StockAnalyzer:
    def __init__(self, ticker="ANTM.JK", period="3mo", interval="1d"):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.df = None
        self.stock_info = None
        self.results = {
            "code": "...",
            "info": {
                "longName": ...,
                "sector": ...,
                "industry": ...,
                "marketCap": ...,
                "exchange": ...,
                "website": ...,
                "category": ...
            }
        }

        self.financials = None
        self.balance = None
        self.cashflow = None

    # ===========================================
    # 0. INFO
    # ===========================================
    def classify_market_cap(self,market_cap):
        """
        Mengklasifikasikan saham berdasarkan market cap (dalam IDR).
        Bluechip : >= 100 triliun
        Menengah : 10 triliun - <100 triliun
        Kecil    : <10 triliun
        """
        if not market_cap:
            return "Unknown"
    
        try:
            mc = float(market_cap)
        except:
            return "Unknown"
    
        TRILLION = 1_000_000_000_000
    
        if mc >= 100 * TRILLION:
            return "Bluechip"
        elif mc >= 10 * TRILLION:
            return "Menengah"
        else:
            return "Kecil"
            
    def info(self):
        # pastikan struktur dasar ada
        self.results.setdefault("info", {})
    
        ticker = yf.Ticker(self.ticker)
        info = ticker.info or {}
    
        self.results["code"] = info.get("symbol", self.ticker)
    
        self.results["info"]["longName"]  = info.get("longName")
        self.results["info"]["sector"]    = info.get("sector")
        self.results["info"]["industry"]  = info.get("industry")
        self.results["info"]["marketCap"] = info.get("marketCap")
        self.results["info"]["exchange"]  = info.get("exchange")
        self.results["info"]["website"]   = info.get("website")
    
        # =========== KATEGORI ===========
        mc = self.results["info"].get("marketCap")
        self.results["info"]["category"] = self.classify_market_cap(mc)
        

    def print_info(self):
        print("\n" + "=" * 50)
        print("📊 INFORMASI SAHAM")
        print("=" * 50)
    
        print(f"{'Kode Saham':<18}: {self.results.get('code', '-')}")
        print("-" * 50)
    
        labels = {
            "longName": "Nama Perusahaan",
            "sector": "Sektor",
            "industry": "Industri",
            "marketCap": "Market Cap",
            "category": "Kategori",
            "exchange": "Bursa",
            "website": "Website"
        }
    
        info = self.results.get("info", {})
    
        for key, label in labels.items():
            value = info.get(key) or "-"
    
            if key == "marketCap" and value != "-":
                value = f"Rp {value:,.0f}"
    
            print(f"{label:<18}: {value}")
    
        print("=" * 50 + "\n")

        
    # ===========================================
    # 1. TEKNIKAL ANALYSIS
    # ===========================================
    def technical_analysis(self):
        """Analisis teknikal dengan indikator tradisional"""
        #print("📊 MENGAMBIL DATA TEKNIKAL...")
        
        # Download data
        self.df = yf.download(
            self.ticker,
            period=self.period,
            interval=self.interval,
            progress=False
        )
        
        # Fix column names if MultiIndex
        if isinstance(self.df.columns, pd.MultiIndex):
            self.df.columns = self.df.columns.get_level_values(0)
        
        self.df.dropna(inplace=True)
        
        # Pastikan data 1 dimensi
        def to_series(col):
            if isinstance(col, pd.DataFrame):
                return col.iloc[:, 0]
            return col
        
        close = to_series(self.df["Close"])
        high = to_series(self.df["High"])
        low = to_series(self.df["Low"])
        
        # Indikator Teknikal
        self.df["EMA_5"] = EMAIndicator(close, window=5).ema_indicator()
        self.df["EMA_9"] = EMAIndicator(close, window=9).ema_indicator()
        self.df["EMA_20"] = EMAIndicator(close, window=20).ema_indicator()
        self.df["EMA_50"] = EMAIndicator(close, window=50).ema_indicator()
        
        self.df["RSI"] = RSIIndicator(close, window=14).rsi()
        
        macd = MACD(close)
        self.df["MACD"] = macd.macd()
        self.df["MACD_SIGNAL"] = macd.macd_signal()
        
        bb = BollingerBands(close)
        self.df["BB_UPPER"] = bb.bollinger_hband()
        self.df["BB_LOWER"] = bb.bollinger_lband()
        
        # Analisis
        latest = self.df.iloc[-1]
        close_price = float(latest["Close"])
        ema20 = float(latest["EMA_20"])
        ema50 = float(latest["EMA_50"])
        rsi = float(latest["RSI"])
        macd_val = float(latest["MACD"])
        macd_signal = float(latest["MACD_SIGNAL"])
        
        # Trend
        if close_price > ema20 > ema50:
            trend = "BULLISH"
        elif close_price < ema20 < ema50:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"
        
        # Momentum
        if rsi > 60:
            momentum = "KUAT (BULLISH)"
        elif rsi < 40:
            momentum = "LEMAH (BEARISH)"
        else:
            momentum = "NETRAL"
        
        # Support & Resistance
        support_1 = low.rolling(window=10).min().iloc[-1]
        resistance_1 = high.rolling(window=10).max().iloc[-1]
        support_2 = low.rolling(window=30).min().iloc[-1]
        resistance_2 = high.rolling(window=30).max().iloc[-1]
        
        # Entry Signal
        signal = "NO TRADE"
        if trend == "BULLISH" and close_price > ema20 and rsi > 50 and macd_val > macd_signal:
            signal = "BUY"
        elif trend == "BEARISH" and close_price < ema20 and rsi < 50 and macd_val < macd_signal:
            signal = "SELL"
        
        # Trading Plan
        trading_plan = {}
        if signal == "BUY":
            trading_plan = {
                "entry": close_price,
                "sl": support_2,
                "tp1": resistance_1,
                "tp2": resistance_2
            }
        elif signal == "SELL":
            trading_plan = {
                "entry": close_price,
                "sl": resistance_2,
                "tp1": support_1,
                "tp2": support_2
            }
        
        # Simpan hasil
        self.results['technical'] = {
            'trend': trend,
            'momentum': momentum,
            'close': close_price,
            'rsi': rsi,
            'support': [support_1, support_2],
            'resistance': [resistance_1, resistance_2],
            'signal': signal,
            'trading_plan': trading_plan
        }
        
        return self.results['technical']
    
    # ===========================================
    # 2. PRICE ACTION ANALYSIS
    # ===========================================
    def price_action_analysis(self, swing_window=3, impulse_factor=1.5):
        """Analisis struktur pasar dan supply/demand zones"""
        #print("📈 ANALISIS PRICE ACTION...")
        
        if self.df is None:
            print("Data belum diambil. Jalankan technical_analysis() terlebih dahulu.")
            return None
        
        df = self.df.copy()
        
        # Deteksi Swing High/Low
        df["SWING_HIGH"] = (
            df["High"]
            .rolling(swing_window*2+1, center=True)
            .apply(lambda x: x[swing_window] == max(x), raw=True)
        )
        
        df["SWING_LOW"] = (
            df["Low"]
            .rolling(swing_window*2+1, center=True)
            .apply(lambda x: x[swing_window] == min(x), raw=True)
        )
        
        # Market Structure
        structure = []
        last_high = None
        last_low = None
        
        for i in range(len(df)):
            if df["SWING_HIGH"].iloc[i]:
                high = df["High"].iloc[i]
                if last_high is not None:
                    structure.append(("HH" if high > last_high else "LH", df.index[i], high))
                last_high = high
            
            if df["SWING_LOW"].iloc[i]:
                low = df["Low"].iloc[i]
                if last_low is not None:
                    structure.append(("HL" if low > last_low else "LL", df.index[i], low))
                last_low = low
        
        # Supply/Demand Zones
        zones = []
        for i in range(1, len(df)):
            body = abs(df["Close"].iloc[i] - df["Open"].iloc[i])
            prev_body = abs(df["Close"].iloc[i-1] - df["Open"].iloc[i-1])
            
            if prev_body == 0:
                continue
            
            # Impulse Up → Demand Zone
            if body > impulse_factor * prev_body and df["Close"].iloc[i] > df["Open"].iloc[i]:
                zones.append({
                    "type": "DEMAND",
                    "low": df["Low"].iloc[i-1],
                    "high": df["Open"].iloc[i-1],
                    "date": df.index[i]
                })
            
            # Impulse Down → Supply Zone
            if body > impulse_factor * prev_body and df["Close"].iloc[i] < df["Open"].iloc[i]:
                zones.append({
                    "type": "SUPPLY",
                    "low": df["Open"].iloc[i-1],
                    "high": df["High"].iloc[i-1],
                    "date": df.index[i]
                })
        
        # Simpan hasil
        market_structure = structure[-1][0] if structure else "TIDAK TERDETEKSI"
        
        self.results['price_action'] = {
            'market_structure': market_structure,
            'zones': zones[-5:],  # 5 zone terakhir
            'total_zones': len(zones)
        }
        
        return self.results['price_action']
    
    # ===========================================
    # 3. FUNDAMENTAL ANALYSIS (FIXED)
    # ===========================================
    def fundamental_analysis(self):
        """Analisis fundamental dengan berbagai metrik"""
        #print("📋 ANALISIS FUNDAMENTAL...")
        
        try:
            stock = yf.Ticker(self.ticker)
            self.stock_info = stock.info
            
            # Data keuangan
            self.financials = stock.financials
            self.balance = stock.balance_sheet
            self.cashflow = stock.cashflow
            
            # Helper function
            def safe_get(df, key):
                try:
                    if isinstance(df, pd.DataFrame) and key in df.index:
                        # Ambil nilai terbaru (index pertama adalah terbaru)
                        value = df.loc[key]
                        if isinstance(value, pd.Series):
                            return value.iloc[0] if len(value) > 0 else None
                        return value
                    elif isinstance(df, dict):
                        return df.get(key)
                    return None
                except:
                    return None
            
            # Extract data - gunakan try-except untuk setiap nilai
            net_income = safe_get(self.financials, "Net Income") if self.financials is not None else None
            total_assets = safe_get(self.balance, "Total Assets") if self.balance is not None else None
            total_equity = safe_get(self.balance, "Total Stockholder Equity") if self.balance is not None else None
            total_debt = safe_get(self.balance, "Total Debt") if self.balance is not None else None
            operating_cf = safe_get(self.cashflow, "Total Cash From Operating Activities") if self.cashflow is not None else None
            revenue = safe_get(self.financials, "Total Revenue") if self.financials is not None else None
            
            # Konversi ke float jika ada
            def to_float(value):
                if value is None:
                    return None
                try:
                    return float(value)
                except:
                    return None
            
            net_income_f = to_float(net_income)
            total_assets_f = to_float(total_assets)
            total_equity_f = to_float(total_equity)
            total_debt_f = to_float(total_debt)
            operating_cf_f = to_float(operating_cf)
            revenue_f = to_float(revenue)
            
            # Rasio (dengan pengecekan division by zero)
            roe = (net_income_f / total_equity_f * 100) if net_income_f and total_equity_f and total_equity_f != 0 else None
            roa = (net_income_f / total_assets_f * 100) if net_income_f and total_assets_f and total_assets_f != 0 else None
            npm = (net_income_f / revenue_f * 100) if net_income_f and revenue_f and revenue_f != 0 else None
            der = (total_debt_f / total_equity_f) if total_debt_f and total_equity_f and total_equity_f != 0 else None
            
            # Valuation
            pe = to_float(self.stock_info.get("trailingPE"))
            pb = to_float(self.stock_info.get("priceToBook"))
            
            # Growth (Quarterly) - FIXED: handle series properly
            quarterly_income = stock.quarterly_financials
            quarterly_cf = stock.quarterly_cashflow
            
            # Helper untuk mendapatkan series dengan benar
            def get_quarterly_series(data, key):
                if data is None or key not in data.index:
                    return None
                series = data.loc[key]
                if isinstance(series, pd.Series):
                    # Sort dari yang terlama ke terbaru
                    return series.sort_index(ascending=True)
                return None
            
            # Get series untuk growth calculation
            rev_series = get_quarterly_series(quarterly_income, "Total Revenue")
            ni_series = get_quarterly_series(quarterly_income, "Net Income")
            
            # Helper untuk calculate growth - FIXED: tidak pakai len() di float
            def calculate_growth(series):
                if series is None or not isinstance(series, pd.Series):
                    return None, None
                
                if len(series) < 2:
                    return None, None
                
                try:
                    # QoQ growth (quarter to quarter)
                    last_val = series.iloc[-1]
                    prev_val = series.iloc[-2]
                    qoq = ((last_val - prev_val) / abs(prev_val) * 100) if prev_val != 0 else None
                    
                    # YoY growth (year over year)
                    yoy = None
                    if len(series) >= 4:
                        year_ago_val = series.iloc[-4]
                        yoy = ((last_val - year_ago_val) / abs(year_ago_val) * 100) if year_ago_val != 0 else None
                    
                    return yoy, qoq
                except:
                    return None, None
            
            rev_yoy, rev_qoq = calculate_growth(rev_series)
            ni_yoy, ni_qoq = calculate_growth(ni_series)
            
            # Fundamental Score
            score = 0
            
            # Profitability (50 points)
            if roe and roe > 15: score += 20
            if roa and roa > 5: score += 15
            if npm and npm > 10: score += 15
            
            # Leverage (20 points)
            if der and der < 1.5: score += 10
            if der and der < 1: score += 10
            
            # Growth (20 points)
            if rev_yoy and rev_yoy > 10: score += 10
            if ni_yoy and ni_yoy > 10: score += 10
            
            # Valuation (10 points)
            if pb and pb < 2: score += 10
            
            # Cap score maksimal 100
            score = min(score, 100)
            
            # Interpretasi Score
            if score >= 80:
                rating = "SANGAT KUAT 🟢"
            elif score >= 60:
                rating = "CUKUP KUAT 🟡"
            elif score >= 40:
                rating = "LEMAH 🟠"
            else:
                rating = "BURUK 🔴"
            
            # Simpan hasil
            self.results['fundamental'] = {
                'roe': roe,
                'roa': roa,
                'npm': npm,
                'der': der,
                'pe': pe,
                'pb': pb,
                'revenue_growth': {'yoy': rev_yoy, 'qoq': rev_qoq},
                'netincome_growth': {'yoy': ni_yoy, 'qoq': ni_qoq},
                'operating_cf': operating_cf_f,
                'score': score,
                'rating': rating
            }
            
            return self.results['fundamental']
            
        except Exception as e:
            print(f"⚠️ Warning dalam analisis fundamental: {e}")
            print("Melanjutkan dengan data yang tersedia...")
            
            # Return minimal data jika error
            self.results['fundamental'] = {
                'roe': None,
                'roa': None,
                'npm': None,
                'der': None,
                'pe': None,
                'pb': None,
                'revenue_growth': {'yoy': None, 'qoq': None},
                'netincome_growth': {'yoy': None, 'qoq': None},
                'operating_cf': None,
                'score': 0,
                'rating': "DATA TIDAK TERSEDIA ⚠️"
            }
            
            return self.results['fundamental']
    
    # ===========================================
    # 4. ANALISIS VALUASI (BARU)
    # ===========================================
    def valuation_analysis(self):
        """Analisis apakah harga saham mahal atau murah relatif terhadap nilai aset dan kinerja"""
        #print("💰 ANALISIS VALUASI...")
        
        if self.stock_info is None:
            try:
                stock = yf.Ticker(self.ticker)
                self.stock_info = stock.info
            except:
                print("⚠️ Tidak bisa mendapatkan data valuasi")
                return None
        
        try:
            # Ambil data harga dari technical analysis
            if 'technical' in self.results:
                current_price = self.results['technical']['close']
            else:
                current_price = self.df['Close'].iloc[-1] if self.df is not None else None
            
            # Ambil data fundamental
            fund = self.results.get('fundamental', {})
            
            # Data dari yfinance
            info = self.stock_info
            
            # Helper function
            def safe_get(key, default=None):
                value = info.get(key, default)
                if value is None or value == 0:
                    return default
                return float(value)
            
            # 1. PER Analysis
            trailing_pe = safe_get('trailingPE')
            forward_pe = safe_get('forwardPE')
            pe_ratio = trailing_pe if trailing_pe else forward_pe
            
            # 2. PBV Analysis
            pb_ratio = safe_get('priceToBook')
            
            # 3. Dividend Yield
            dividend_yield = safe_get('dividendYield')
            if dividend_yield:
                dividend_yield = dividend_yield * 100  # Convert to percentage
            
            # 4. EV/EBITDA
            ev_to_ebitda = safe_get('enterpriseToEbitda')
            
            # 5. PEG Ratio (Price/Earnings to Growth)
            peg_ratio = safe_get('pegRatio')
            
            # 6. Price/Sales
            ps_ratio = safe_get('priceToSalesTrailing12Months')
            
            # 7. Historical Price Analysis
            historical_analysis = {}
            if self.df is not None:
                # Rentang harga 52 minggu
                week_52_high = self.df['High'].rolling(window=252).max().iloc[-1] if len(self.df) >= 252 else None
                week_52_low = self.df['Low'].rolling(window=252).min().iloc[-1] if len(self.df) >= 252 else None
                
                if week_52_high and week_52_low and current_price:
                    # Posisi relatif dalam rentang 52 minggu
                    position_52_week = (current_price - week_52_low) / (week_52_high - week_52_low) * 100
                    historical_analysis['week_52_position'] = position_52_week
                    historical_analysis['week_52_high'] = week_52_high
                    historical_analysis['week_52_low'] = week_52_low
                
                # Analisis rata-rata bergerak
                ma_200 = self.df['Close'].rolling(window=200).mean().iloc[-1] if len(self.df) >= 200 else None
                if ma_200 and current_price:
                    price_vs_ma200 = (current_price / ma_200 - 1) * 100
                    historical_analysis['ma_200'] = ma_200
                    historical_analysis['price_vs_ma200_pct'] = price_vs_ma200
            
            # 8. Industry Comparison (estimasi sederhana)
            industry_pe = safe_get('industryPE', 15)  # Default 15 jika tidak ada data
            
            # 9. Intrinsic Value Estimation (simplified)
            intrinsic_value = None
            if pe_ratio and fund.get('netincome_growth', {}).get('yoy'):
                # Simple Graham Formula: V = EPS * (8.5 + 2g)
                eps = current_price / pe_ratio if pe_ratio and pe_ratio > 0 else None
                growth_rate = fund['netincome_growth']['yoy']
                if eps and growth_rate:
                    intrinsic_value = eps * (8.5 + 2 * min(growth_rate/100, 0.2))  # Growth max 20%
            
            # 10. Valuation Score
            valuation_score = 0
            valuation_notes = []
            
            # PER Score
            if pe_ratio:
                if pe_ratio < 10:
                    valuation_score += 20
                    valuation_notes.append("✅ PER sangat rendah (murah)")
                elif pe_ratio < 15:
                    valuation_score += 15
                    valuation_notes.append("✅ PER rendah")
                elif pe_ratio < industry_pe:
                    valuation_score += 10
                    valuation_notes.append("✅ PER di bawah rata-rata industri")
                elif pe_ratio < 25:
                    valuation_score += 5
                    valuation_notes.append("⚠️ PER sedang")
                else:
                    valuation_score += 0
                    valuation_notes.append("❌ PER tinggi (mahal)")
            
            # PBV Score
            if pb_ratio:
                if pb_ratio < 1:
                    valuation_score += 20
                    valuation_notes.append("✅ Harga di bawah nilai buku (murah)")
                elif pb_ratio < 1.5:
                    valuation_score += 15
                    valuation_notes.append("✅ PBV rendah")
                elif pb_ratio < 2:
                    valuation_score += 10
                    valuation_notes.append("✅ PBV wajar")
                elif pb_ratio < 3:
                    valuation_score += 5
                    valuation_notes.append("⚠️ PBV agak tinggi")
                else:
                    valuation_score += 0
                    valuation_notes.append("❌ PBV sangat tinggi")
            
            # Dividend Yield Score
            if dividend_yield:
                if dividend_yield > 5:
                    valuation_score += 15
                    valuation_notes.append("✅ Dividend yield tinggi")
                elif dividend_yield > 3:
                    valuation_score += 10
                    valuation_notes.append("✅ Dividend yield baik")
                elif dividend_yield > 1.5:
                    valuation_score += 5
                    valuation_notes.append("⚠️ Dividend yield cukup")
            
            # PEG Ratio Score
            if peg_ratio:
                if peg_ratio < 0.5:
                    valuation_score += 15
                    valuation_notes.append("✅ PEG sangat rendah (sangat murah)")
                elif peg_ratio < 1:
                    valuation_score += 10
                    valuation_notes.append("✅ PEG rendah (murah)")
                elif peg_ratio < 1.5:
                    valuation_score += 5
                    valuation_notes.append("⚠️ PEG wajar")
                else:
                    valuation_score += 0
                    valuation_notes.append("❌ PEG tinggi (mahal)")
            
            # Historical Price Score
            if 'week_52_position' in historical_analysis:
                position = historical_analysis['week_52_position']
                if position < 30:
                    valuation_score += 15
                    valuation_notes.append("✅ Posisi di bawah 30% rentang 52 minggu (murah)")
                elif position < 50:
                    valuation_score += 10
                    valuation_notes.append("✅ Posisi di bawah tengah rentang 52 minggu")
                elif position > 70:
                    valuation_score += 0
                    valuation_notes.append("❌ Posisi di atas 70% rentang 52 minggu (mahal)")
            
            # Cap maksimal score
            valuation_score = min(valuation_score, 100)
            
            # Kesimpulan Valuasi
            if valuation_score >= 60:
                valuation_conclusion = "SAHAM MURAH 🟢"
                valuation_reason = "Berbagai indikator valuasi menunjukkan harga relatif murah"
            elif valuation_score >= 40:
                valuation_conclusion = "SAHAM WAJAR 🟡"
                valuation_reason = "Harga dalam kisaran wajar berdasarkan valuasi"
            else:
                valuation_conclusion = "SAHAM MAHAL 🔴"
                valuation_reason = "Berbagai indikator valuasi menunjukkan harga relatif mahal"
            
            # Margin of Safety
            margin_of_safety = None
            if intrinsic_value and current_price:
                margin_of_safety = (intrinsic_value - current_price) / intrinsic_value * 100
            
            # Simpan hasil
            self.results['valuation'] = {
                'current_price': current_price,
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'dividend_yield': dividend_yield,
                'ev_ebitda': ev_to_ebitda,
                'peg_ratio': peg_ratio,
                'ps_ratio': ps_ratio,
                'industry_pe': industry_pe,
                'historical_analysis': historical_analysis,
                'intrinsic_value': intrinsic_value,
                'margin_of_safety': margin_of_safety,
                'valuation_score': valuation_score,
                'valuation_conclusion': valuation_conclusion,
                'valuation_reason': valuation_reason,
                'valuation_notes': valuation_notes
            }
            
            return self.results['valuation']
            
        except Exception as e:
            print(f"⚠️ Error dalam analisis valuasi: {e}")
            
            self.results['valuation'] = {
                'current_price': None,
                'pe_ratio': None,
                'pb_ratio': None,
                'dividend_yield': None,
                'ev_ebitda': None,
                'peg_ratio': None,
                'ps_ratio': None,
                'industry_pe': None,
                'historical_analysis': {},
                'intrinsic_value': None,
                'margin_of_safety': None,
                'valuation_score': 0,
                'valuation_conclusion': "DATA TIDAK TERSEDIA",
                'valuation_reason': "Tidak dapat menganalisis valuasi",
                'valuation_notes': []
            }
            
            return self.results['valuation']
    
    # ===========================================
    # 5. VISUALISASI (DIPERBARUI)
    # ===========================================
    def visualize(self):
        """Visualisasi komprehensif"""
        if self.df is None:
            print("Data belum tersedia. Jalankan analisis terlebih dahulu.")
            return
        
        fig = plt.figure(figsize=(18, 14))
        gs = GridSpec(5, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # Subplot 1: Price dengan EMA dan Support/Resistance
        ax1 = fig.add_subplot(gs[0:2, :])
        ax1.plot(self.df.index, self.df['Close'], label='Close', linewidth=2, color='black')
        ax1.plot(self.df.index, self.df['EMA_20'], label='EMA 20', linewidth=1, alpha=0.7, color='blue')
        ax1.plot(self.df.index, self.df['EMA_50'], label='EMA 50', linewidth=1, alpha=0.7, color='orange')
        
        # Bollinger Bands
        ax1.fill_between(self.df.index, self.df['BB_LOWER'], self.df['BB_UPPER'], 
                        alpha=0.1, color='blue', label='Bollinger Bands')
        
        # Support/Resistance
        if 'technical' in self.results:
            tech = self.results['technical']
            for i, (s, r) in enumerate(zip(tech['support'], tech['resistance'])):
                style = '--' if i == 0 else '-.'
                alpha = 0.7 if i == 0 else 0.9
                ax1.axhline(s, linestyle=style, alpha=alpha, color='green', 
                           label=f'Support {i+1}' if i == 0 else "")
                ax1.axhline(r, linestyle=style, alpha=alpha, color='red', 
                           label=f'Resistance {i+1}' if i == 0 else "")
        
        # Tambah garis MA200 jika ada
        if 'valuation' in self.results and 'ma_200' in self.results['valuation']['historical_analysis']:
            ma_200 = self.results['valuation']['historical_analysis']['ma_200']
            ax1.axhline(ma_200, linestyle='--', alpha=0.5, color='purple', 
                       label='MA 200')
        
        ax1.set_title(f'{self.ticker} - Price Chart dengan Indikator', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: RSI
        ax2 = fig.add_subplot(gs[2, 0])
        ax2.plot(self.df.index, self.df['RSI'], label='RSI', color='purple', linewidth=1.5)
        ax2.axhline(70, linestyle='--', alpha=0.5, color='red', label='Overbought (70)')
        ax2.axhline(30, linestyle='--', alpha=0.5, color='green', label='Oversold (30)')
        ax2.axhline(50, linestyle='-', alpha=0.3, color='gray')
        ax2.fill_between(self.df.index, 30, 70, alpha=0.1, color='gray')
        ax2.set_title('RSI (14)', fontsize=12)
        ax2.set_ylabel('RSI')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper right')
        
        # Subplot 3: MACD
        ax3 = fig.add_subplot(gs[2, 1])
        ax3.plot(self.df.index, self.df['MACD'], label='MACD', color='blue', linewidth=1.5)
        ax3.plot(self.df.index, self.df['MACD_SIGNAL'], label='Signal', color='red', linewidth=1)
        
        # MACD histogram
        macd_diff = self.df['MACD'] - self.df['MACD_SIGNAL']
        colors = ['green' if val >= 0 else 'red' for val in macd_diff]
        ax3.bar(self.df.index, macd_diff, alpha=0.3, color=colors, width=0.8)
        
        ax3.axhline(0, linestyle='-', alpha=0.3, color='black')
        ax3.set_title('MACD', fontsize=12)
        ax3.set_ylabel('MACD')
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper right')
        
        # Subplot 4: Price Action dengan Swing Points
        ax4 = fig.add_subplot(gs[3, :])
        ax4.plot(self.df.index, self.df['Close'], label='Close', color='black', linewidth=1.5)
        
        # Swing Points (jika ada)
        if 'SWING_HIGH' in self.df.columns and 'SWING_LOW' in self.df.columns:
            swing_high_idx = self.df[self.df['SWING_HIGH'] == 1].index
            swing_low_idx = self.df[self.df['SWING_LOW'] == 1].index
            
            if len(swing_high_idx) > 0:
                ax4.scatter(swing_high_idx, self.df.loc[swing_high_idx, 'High'], 
                           color='red', s=50, label='Swing High', zorder=5, marker='v')
            if len(swing_low_idx) > 0:
                ax4.scatter(swing_low_idx, self.df.loc[swing_low_idx, 'Low'], 
                           color='green', s=50, label='Swing Low', zorder=5, marker='^')
        
        # Supply/Demand Zones
        if 'price_action' in self.results:
            pa = self.results['price_action']
            zones = pa.get('zones', [])
            
            # Plot zones (maksimal 3 terakhir untuk menghindari clutter)
            for i, zone in enumerate(zones[-3:]):
                color = 'green' if zone['type'] == 'DEMAND' else 'red'
                alpha = 0.2 if zone['type'] == 'DEMAND' else 0.1
                label = f'{zone["type"]} Zone' if i == 0 else ""
                
                ax4.axhspan(zone['low'], zone['high'], alpha=alpha, color=color, 
                           label=label)
        
        market_structure = self.results.get('price_action', {}).get('market_structure', 'N/A')
        ax4.set_title(f'Price Action Analysis - Market Structure: {market_structure}', 
                     fontsize=12, fontweight='bold')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Price')
        ax4.legend(loc='upper left')
        ax4.grid(True, alpha=0.3)
        
        # Subplot 5: Valuation Metrics (BARU)
        ax5 = fig.add_subplot(gs[4, 0])
        if 'valuation' in self.results:
            val = self.results['valuation']
            
            # Buat data untuk bar chart
            metrics = []
            values = []
            colors = []
            
            if val['pe_ratio']:
                metrics.append('PER')
                values.append(val['pe_ratio'])
                colors.append('green' if val['pe_ratio'] < 15 else 'red' if val['pe_ratio'] > 25 else 'orange')
            
            if val['pb_ratio']:
                metrics.append('PBV')
                values.append(val['pb_ratio'])
                colors.append('green' if val['pb_ratio'] < 1.5 else 'red' if val['pb_ratio'] > 3 else 'orange')
            
            if val['dividend_yield']:
                metrics.append('DY (%)')
                values.append(val['dividend_yield'])
                colors.append('green' if val['dividend_yield'] > 3 else 'orange')
            
            if val['peg_ratio']:
                metrics.append('PEG')
                values.append(val['peg_ratio'])
                colors.append('green' if val['peg_ratio'] < 1 else 'red' if val['peg_ratio'] > 1.5 else 'orange')
            
            if metrics:
                bars = ax5.bar(metrics, values, color=colors, alpha=0.7)
                ax5.set_title('Valuation Metrics', fontsize=12, fontweight='bold')
                ax5.set_ylabel('Value')
                ax5.grid(True, alpha=0.3, axis='y')
                
                # Tambah nilai di atas bar
                for bar in bars:
                    height = bar.get_height()
                    ax5.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        # Subplot 6: Valuation Score (BARU)
        ax6 = fig.add_subplot(gs[4, 1])
        if 'valuation' in self.results:
            score = val['valuation_score']
            
            # Buat gauge chart sederhana
            ax6.set_xlim(0, 100)
            ax6.set_ylim(0, 1)
            
            # Warna berdasarkan score
            if score >= 60:
                facecolor = 'green'
                status = "MURAH"
            elif score >= 40:
                facecolor = 'orange'
                status = "WAJAR"
            else:
                facecolor = 'red'
                status = "MAHAL"
            
            # Gauge
            ax6.barh(0.5, score, height=0.3, color=facecolor, alpha=0.7)
            ax6.axvline(40, color='red', linestyle='--', alpha=0.5)
            ax6.axvline(60, color='green', linestyle='--', alpha=0.5)
            
            ax6.set_title(f'Valuation Score: {score}/100\nStatus: {status}', 
                         fontsize=12, fontweight='bold')
            ax6.set_xlabel('Score')
            ax6.set_yticks([])
            ax6.grid(True, alpha=0.3)
            
            # Tambah teks score
            ax6.text(score/2, 0.5, f'{score}', ha='center', va='center', 
                    color='white', fontweight='bold', fontsize=14)
        
        # Subplot 7: Historical Position (BARU)
        ax7 = fig.add_subplot(gs[4, 2])
        if 'valuation' in self.results and 'week_52_position' in val['historical_analysis']:
            position = val['historical_analysis']['week_52_position']
            low_52 = val['historical_analysis']['week_52_low']
            high_52 = val['historical_analysis']['week_52_high']
            current = val['current_price']
            
            # Buat visualisasi rentang 52 minggu
            ax7.plot([0, 100], [low_52, high_52], 'k-', alpha=0.3)
            ax7.scatter([position], [current], s=100, color='blue', zorder=5)
            
            # Tambah garis bantu
            ax7.axhline(current, color='blue', linestyle='--', alpha=0.3)
            ax7.axvline(position, color='blue', linestyle='--', alpha=0.3)
            
            ax7.set_title('52-Week Range Position', fontsize=12, fontweight='bold')
            ax7.set_xlabel('Position (%)')
            ax7.set_ylabel('Price')
            ax7.grid(True, alpha=0.3)
            
            # Tambah anotasi
            ax7.text(position, current, f'  {position:.1f}%', 
                    verticalalignment='center', fontsize=10)
        
        plt.suptitle(f'COMPREHENSIVE STOCK ANALYSIS - {self.ticker}', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.show()
    
    # ===========================================
    # 6. REPORT SUMMARY (DIPERBARUI)
    # ===========================================
    def generate_report(self):
        """Generate laporan analisis lengkap"""
        print("=" * 60)
        print(f"📈 LAPORAN ANALISIS SAHAM: {self.ticker}")
        print("=" * 60)
        
        # Technical Analysis Summary
        if 'technical' in self.results:
            tech = self.results['technical']
            print("\n1. 📊 ANALISIS TEKNIKAL")
            print("-" * 40)
            print(f"   Trend           : {tech['trend']}")
            print(f"   Momentum        : {tech['momentum']}")
            print(f"   Harga Close     : {tech['close']:.2f}")
            print(f"   RSI (14)        : {tech['rsi']:.2f}")
            print(f"   Support (S1/S2) : {tech['support'][0]:.2f} / {tech['support'][1]:.2f}")
            print(f"   Resistance(R1/R2): {tech['resistance'][0]:.2f} / {tech['resistance'][1]:.2f}")
            print(f"   Sinyal Trading  : {tech['signal']}")
            
            if tech['trading_plan']:
                tp = tech['trading_plan']
                print(f"\n   🎯 RENCANA TRADING:")
                print(f"   Entry          : {tp['entry']:.2f}")
                print(f"   Stop Loss      : {tp['sl']:.2f}")
                print(f"   Take Profit 1  : {tp['tp1']:.2f}")
                print(f"   Take Profit 2  : {tp['tp2']:.2f}")
        
        # Price Action Summary
        if 'price_action' in self.results:
            pa = self.results['price_action']
            print("\n2. 📈 ANALISIS PRICE ACTION")
            print("-" * 40)
            print(f"   Market Structure : {pa['market_structure']}")
            print(f"   Total Zones      : {pa['total_zones']}")
            print(f"   Active Zones     : {len(pa['zones'])}")
            
            # Hitung zone per tipe
            if pa['zones']:
                demand_zones = [z for z in pa['zones'] if z['type'] == 'DEMAND']
                supply_zones = [z for z in pa['zones'] if z['type'] == 'SUPPLY']
                
                if demand_zones:
                    print(f"   Demand Zones     : {len(demand_zones)}")
                if supply_zones:
                    print(f"   Supply Zones     : {len(supply_zones)}")
        
        # Fundamental Summary
        if 'fundamental' in self.results:
            fund = self.results['fundamental']
            print("\n3. 📋 ANALISIS FUNDAMENTAL")
            print("-" * 40)
            
            # Format output dengan pengecekan None
            def format_value(val, fmt=".2f", suffix=""):
                if val is None:
                    return "N/A"
                if fmt:
                    return f"{val:{fmt}}{suffix}"
                return f"{val}{suffix}"
            
            print(f"   ROE              : {format_value(fund['roe'], '.2f', '%')}")
            print(f"   ROA              : {format_value(fund['roa'], '.2f', '%')}")
            print(f"   NPM              : {format_value(fund['npm'], '.2f', '%')}")
            print(f"   DER              : {format_value(fund['der'], '.2f', 'x')}")
            
            print(f"   PER              : {format_value(fund['pe'], '.2f')}")
            print(f"   PBV              : {format_value(fund['pb'], '.2f')}")
            
            print(f"   Revenue YoY      : {format_value(fund['revenue_growth']['yoy'], '.2f', '%')}")
            print(f"   Net Income YoY   : {format_value(fund['netincome_growth']['yoy'], '.2f', '%')}")
            
            if fund['operating_cf']:
                print(f"   Operating CF     : {fund['operating_cf']:,.0f}")
            
            print(f"\n   📊 FUNDAMENTAL SCORE: {fund['score']}/100")
            print(f"   RATING           : {fund['rating']}")
        
        # Valuation Summary (BARU)
        if 'valuation' in self.results:
            val = self.results['valuation']
            print("\n4. 💰 ANALISIS VALUASI")
            print("-" * 40)
            
            # Format helper
            def fmt(val, fmt=".2f"):
                if val is None:
                    return "N/A"
                return f"{val:{fmt}}"
            
            print(f"   Harga Saat Ini   : {fmt(val['current_price'])}")
            print(f"   PER Ratio        : {fmt(val['pe_ratio'])}")
            print(f"   PBV Ratio        : {fmt(val['pb_ratio'])}")
            print(f"   Dividend Yield   : {fmt(val['dividend_yield'], '.2f')}%")
            print(f"   PEG Ratio        : {fmt(val['peg_ratio'])}")
            print(f"   EV/EBITDA        : {fmt(val['ev_ebitda'])}")
            print(f"   Industry PER     : {fmt(val['industry_pe'])}")
            
            # Historical Analysis
            hist = val.get('historical_analysis', {})
            if 'week_52_position' in hist:
                print(f"\n   📅 ANALISIS HISTORIS:")
                print(f"   Rentang 52 Mgg   : {fmt(hist['week_52_low'])} - {fmt(hist['week_52_high'])}")
                print(f"   Posisi          : {fmt(hist['week_52_position'], '.1f')}% dari rendah")
                
                if 'price_vs_ma200_pct' in hist:
                    status = "DI ATAS" if hist['price_vs_ma200_pct'] > 0 else "DI BAWAH"
                    print(f"   vs MA200         : {status} {abs(hist['price_vs_ma200_pct']):.1f}%")
            
            # Intrinsic Value
            if val['intrinsic_value']:
                print(f"\n   🎯 NILAI INTRINSIK:")
                print(f"   Estimasi        : {fmt(val['intrinsic_value'])}")
                print(f"   Harga Saat Ini  : {fmt(val['current_price'])}")
                
                if val['margin_of_safety']:
                    mos = val['margin_of_safety']
                    if mos > 0:
                        print(f"   Margin of Safety: +{mos:.1f}% (DISKON)")
                    else:
                        print(f"   Margin of Safety: {mos:.1f}% (PREMIUM)")
            
            print(f"\n   📊 VALUATION SCORE: {val['valuation_score']}/100")
            print(f"   KESIMPULAN      : {val['valuation_conclusion']}")
            print(f"   ALASAN          : {val['valuation_reason']}")
            
            # Tampilkan catatan penting
            if val['valuation_notes']:
                print(f"\n   📝 CATATAN PENTING:")
                for note in val['valuation_notes'][:3]:  # Tampilkan 3 catatan terpenting
                    print(f"   • {note}")
        
        print("\n" + "=" * 60)
        print("📌 REKOMENDASI:")
        
        # Generate rekomendasi
        recommendation = self.generate_recommendation()
        print(recommendation)
        print("=" * 60)
    
    # ===========================================
    # 7. REKOMENDASI OTOMATIS (DIPERBARUI)
    # ===========================================
    def generate_recommendation(self):
        """Generate rekomendasi trading otomatis"""
        # Cek apakah semua data tersedia
        tech_available = 'technical' in self.results
        fund_available = 'fundamental' in self.results and self.results['fundamental']['score'] > 0
        pa_available = 'price_action' in self.results
        val_available = 'valuation' in self.results and self.results['valuation']['valuation_score'] > 0
        
        if not tech_available:
            return "⚠️ Data teknikal tidak tersedia"
        
        tech = self.results['technical']
        signal = tech['signal']
        trend = tech['trend']
        
        recommendations = []
        
        # Analisis Teknikal
        if signal == "BUY":
            recommendations.append("✅ SIGNAL BUY DARI TEKNIKAL")
            
            if trend == "BULLISH":
                recommendations.append("✅ TREN BULLISH")
            elif trend == "BEARISH":
                recommendations.append("⚠️ PERHATIAN: Meski signal BUY, tren BEARISH")
        
        elif signal == "SELL":
            recommendations.append("🔻 SIGNAL SELL DARI TEKNIKAL")
            
            if trend == "BEARISH":
                recommendations.append("🔻 TREN BEARISH")
            elif trend == "BULLISH":
                recommendations.append("⚠️ PERHATIAN: Meski signal SELL, tren BULLISH")
        
        else:
            recommendations.append("⏸️ NO TRADE SIGNAL")
            recommendations.append("⚠️ TUNGGU KONFIRMASI LEBIH LANJUT")
            
            if trend == "SIDEWAYS":
                recommendations.append("📊 PASAR SIDEWAYS - Pertimbangkan range trading")
        
        # Analisis Fundamental
        if fund_available:
            fund = self.results['fundamental']
            fund_score = fund['score']
            
            if signal == "BUY":
                if fund_score >= 60:
                    recommendations.append("✅ FUNDAMENTAL KUAT - Mendukung BUY")
                elif fund_score >= 40:
                    recommendations.append("⚠️ FUNDAMENTAL CUKUP")
                else:
                    recommendations.append("❌ FUNDAMENTAL LEMAH - Hati-hati dengan BUY")
            
            elif signal == "SELL":
                if fund_score < 40:
                    recommendations.append("🔻 FUNDAMENTAL LEMAH - Mendukung SELL")
                elif fund_score >= 60:
                    recommendations.append("⚠️ PERHATIAN: Fundamental kuat, pertimbangkan ulang SELL")
        
        # Analisis Valuasi (BARU)
        if val_available:
            val = self.results['valuation']
            val_score = val['valuation_score']
            conclusion = val['valuation_conclusion']
            
            if "MURAH" in conclusion:
                if signal == "BUY":
                    recommendations.append("💰 HARGA MURAH - Peluang bagus untuk BUY")
                elif signal == "SELL":
                    recommendations.append("⚠️ PERHATIAN: Harga murah, pertimbangkan hold atau akumulasi")
                else:
                    recommendations.append("💰 HARGA MURAH - Pertimbangkan akumulasi")
            
            elif "MAHAL" in conclusion:
                if signal == "BUY":
                    recommendations.append("⚠️ PERHATIAN: Harga mahal, tunggu koreksi")
                elif signal == "SELL":
                    recommendations.append("💰 HARGA MAHAL - Peluang bagus untuk SELL")
                else:
                    recommendations.append("💰 HARGA MAHAL - Pertimbangkan profit taking")
            
            # Tambah catatan valuasi spesifik
            for note in val.get('valuation_notes', [])[:2]:
                if "sangat rendah" in note.lower() or "di bawah nilai buku" in note.lower():
                    recommendations.append(f"💎 {note}")
        
        # Price Action
        if pa_available:
            pa = self.results['price_action']
            market_structure = pa.get('market_structure', '')
            
            if market_structure in ["HH", "HL"]:
                recommendations.append("✅ STRUKTUR PASAR POSITIF")
            elif market_structure in ["LL", "LH"]:
                recommendations.append("🔻 STRUKTUR PASAR NEGATIF")
        
        # Risk Management
        if signal in ["BUY", "SELL"] and tech.get('trading_plan'):
            tp = tech['trading_plan']
            try:
                risk_reward = abs(tp['tp1'] - tp['entry']) / abs(tp['sl'] - tp['entry'])
                recommendations.append(f"📊 Risk-Reward Ratio: {risk_reward:.2f}")
                
                if risk_reward >= 2:
                    recommendations.append("✅ RISK-REWARD BAIK")
                elif risk_reward >= 1.5:
                    recommendations.append("⚠️ RISK-REWARD CUKUP")
                else:
                    recommendations.append("❌ RISK-REWARD BURUK - Pertimbangkan ulang")
            except:
                recommendations.append("⚠️ Tidak dapat menghitung risk-reward ratio")
        
        # Rekomendasi Akhir
        if signal == "BUY" and val_available and "MURAH" in val['valuation_conclusion']:
            recommendations.append("\n🎯 REKOMENDASI AKHIR: STRONG BUY - Harga menarik dengan fundamental baik")
        elif signal == "BUY":
            recommendations.append("\n🎯 REKOMENDASI AKHIR: BUY dengan pengelolaan risiko ketat")
        elif signal == "SELL" and val_available and "MAHAL" in val['valuation_conclusion']:
            recommendations.append("\n🎯 REKOMENDASI AKHIR: STRONG SELL - Harga overvalued")
        elif signal == "SELL":
            recommendations.append("\n🎯 REKOMENDASI AKHIR: SELL dengan hati-hati")
        else:
            recommendations.append("\n🎯 REKOMENDASI AKHIR: HOLD / TUNGGU KONFIRMASI")
        
        return "\n".join(recommendations)

    # ===========================================
    # 8. REKOMENDASI OTOMATIS (DIPERBARUI)
    # ===========================================
    def trading_recommendation(self, risk_per_trade_pct=2):
        """
        Membuat rencana & rekomendasi trading lengkap
        risk_per_trade_pct : % maksimal risiko per trade (default 2%)
        """
    
        # ======================================================
        # HELPER FINALIZER (SATU PINTU KELUAR)
        # ======================================================
        def finalize(recommendation):
            self.results["trading_recommendation"] = recommendation
            return recommendation
    
        # ======================================================
        # AMBIL DATA
        # ======================================================
        tech = self.results.get("technical")
        pa = self.results.get("price_action")
        info = self.results.get("info", {})
        valuation = self.results.get("valuation", {})
    
        # ======================================================
        # VALIDASI DATA WAJIB
        # ======================================================
        if not tech or not pa:
            return finalize({
                "status": "TIDAK LAYAK",
                "reason": "Data teknikal atau price action belum tersedia"
            })
    
        signal = tech.get("signal")
        trend = tech.get("trend")
        close = tech.get("close")
    
        if signal == "NO TRADE":
            return finalize({
                "status": "WAIT",
                "reason": "Tidak ada sinyal teknikal yang valid"
            })
    
        # ======================================================
        # ENTRY, SL, TP
        # ======================================================
        plan = tech.get("trading_plan", {})
    
        entry = plan.get("entry")
        sl = plan.get("sl")
        tp1 = plan.get("tp1")
        tp2 = plan.get("tp2")
    
        if not all([entry, sl, tp1]):
            return finalize({
                "status": "WAIT",
                "reason": "Trading plan tidak lengkap"
            })
    
        # ======================================================
        # RISK & REWARD
        # ======================================================
        risk = abs(entry - sl)
    
        if risk == 0:
            return finalize({
                "status": "WAIT",
                "reason": "Risk per share = 0 (entry & SL sama)"
            })
    
        reward_1 = abs(tp1 - entry)
        reward_2 = abs(tp2 - entry) if tp2 else None
    
        rr1 = reward_1 / risk
        rr2 = reward_2 / risk if reward_2 else None
    
        # ======================================================
        # FILTER KUALITAS
        # ======================================================
        category = info.get("category")
    
        quality_note = (
            "⚠️ Saham kategori kecil, risiko likuiditas lebih tinggi"
            if category == "Kecil"
            else "Likuiditas relatif aman"
        )
    
        if rr1 < 2:
            return finalize({
                "status": "WAIT",
                "reason": f"Risk reward tidak ideal (RR {rr1:.2f})"
            })
    
        # ======================================================
        # KONTEKS VALUASI
        # ======================================================
        valuation_view = valuation.get("valuation_conclusion", "TIDAK DINILAI")
    
        bias_note = (
            "⚠️ Secara valuasi saham tergolong mahal"
            if valuation_view == "SAHAM MAHAL 🔴" and signal == "BUY"
            else "Valuasi tidak menjadi hambatan utama"
        )
    
        # ======================================================
        # REKOMENDASI FINAL
        # ======================================================
        recommendation = {
            "status": "LAYAK DITRADINGKAN",
            "signal": signal,
            "trend": trend,
            "entry_price": entry,
            "stop_loss": sl,
            "take_profit": {
                "tp1": tp1,
                "tp2": tp2
            },
            "risk_per_share": round(risk, 2),
            "reward": {
                "rr_tp1": round(rr1, 2),
                "rr_tp2": round(rr2, 2) if rr2 else None
            },
            "risk_management": {
                "max_risk_pct": risk_per_trade_pct,
                "rule": f"Maksimal risiko {risk_per_trade_pct}% dari modal"
            },
            "notes": [
                quality_note,
                bias_note,
                f"Market Structure: {pa.get('market_structure')}"
            ]
        }
    
        return finalize(recommendation)


    # ===========================================
    # 9. REKOMENDASI OTOMATIS (DIPERBARUI)
    # ===========================================
    def print_trading_recommendation(self):
        rec = self.results.get("trading_recommendation")
        
        print("\n" + "=" * 60)
        print("📌 RENCANA & REKOMENDASI TRADING")
        print("=" * 60)
    
        if rec is None:
            print("❌ Rekomendasi trading belum tersedia.")
            print("Jalankan trading_recommendation() terlebih dahulu.")
            print("=" * 60 + "\n")
            return
    
        status = rec.get("status", "UNKNOWN")
        signal = rec.get("signal", "-")
    
        print(f"{'Status Trading':<25}: {status}")
        print(f"{'Sinyal':<25}: {signal}")
        print(f"{'Trend':<25}: {rec.get('trend', '-')}")
    
        if status != "LAYAK DITRADINGKAN":
            print(f"{'Alasan':<25}: {rec.get('reason', '-')}")
            print("=" * 60 + "\n")
            return
    
        print("-" * 60)
    
        # Harga
        entry = rec.get("entry_price")
        sl = rec.get("stop_loss")
        tp = rec.get("take_profit", {})
    
        print("📍 LEVEL HARGA")
        print(f"{'Entry Price':<25}: Rp {entry:,.0f}")
        print(f"{'Stop Loss':<25}: Rp {sl:,.0f}")
        print(f"{'Take Profit 1':<25}: Rp {tp.get('tp1'):,.0f}")
        if tp.get("tp2"):
            print(f"{'Take Profit 2':<25}: Rp {tp.get('tp2'):,.0f}")
    
        print("-" * 60)
    
        # Risk & Reward
        reward = rec.get("reward", {})
        print("⚖️ RISK & REWARD")
        print(f"{'Risk per Share':<25}: Rp {rec.get('risk_per_share'):,.0f}")
        print(f"{'RR ke TP1':<25}: 1 : {reward.get('rr_tp1')}")
        if reward.get("rr_tp2"):
            print(f"{'RR ke TP2':<25}: 1 : {reward.get('rr_tp2')}")
    
        print("-" * 60)
    
        # Risk Management
        rm = rec.get("risk_management", {})
        print("🛡️ MANAJEMEN RISIKO")
        print(f"{'Maks Risiko / Trade':<25}: {rm.get('max_risk_pct')}%")
        print(f"{'Aturan':<25}: {rm.get('rule')}")
    
        print("-" * 60)
    
        # Catatan
        print("🧠 CATATAN ANALISIS")
        for note in rec.get("notes", []):
            print(f"- {note}")
    
        print("=" * 60 + "\n")


    



