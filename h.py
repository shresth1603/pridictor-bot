import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="HiTrade | Market Master", page_icon="🇮🇳", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0b1016; font-family: 'Roboto', sans-serif; }
    .ticker-wrap { background-color: #1a202c; padding: 10px; border-bottom: 2px solid #2d3748; }
    .ticker-item { display: inline-block; padding: 0 2rem; color: #e2e8f0; font-weight: bold; }
    .positive { color: #48bb78; }
    .stock-row { background-color: #1a202c; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #718096; display: flex; justify-content: space-between; }
    .stock-row-buy { border-left: 5px solid #48bb78; }
    .innovation-card { background: linear-gradient(180deg, #161b24 0%, #0e1117 100%); border: 1px solid #4fd1c5; border-radius: 15px; padding: 20px; text-align: center; }
    .edu-card { background-color: #1a202c; border-left: 5px solid #f6e05e; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. THE SMART LOADER (Connects to your CSV) ---
@st.cache_data
def load_market_universe():
    file_path = "EQUITY_L.csv"
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Add .NS for Yahoo Finance
            stock_list = [str(x).strip() + ".NS" for x in df['SYMBOL'].tolist()]
            return stock_list
        except:
            return ["RELIANCE.NS", "TCS.NS", "INFY.NS", "SBIN.NS"] # Fail-safe
    else:
        # BACKUP LIST (If you forget the file)
        return [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", 
            "LT.NS", "KOTAKBANK.NS", "AXISBANK.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "MARUTI.NS", "ASIANPAINT.NS", 
            "HCLTECH.NS", "TITAN.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "NTPC.NS", "M&M.NS", 
            "POWERGRID.NS", "ADANIENT.NS", "TATASTEEL.NS", "COALINDIA.NS", "ONGC.NS" , "PAYTM.NS",
            "SUZLON.NS", "IDEA.NS", "YESBANK.NS", "IRFC.NS", "NHPC.NS", "SJVN.NS"
        ]

MARKET_UNIVERSE = load_market_universe()

# --- 4. CALCULATION ENGINE ---
# Updated to accept 'days' as an argument
def analyze_stock(ticker, days=180):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        
        # Indicators
        df['EMA_9'] = df['Close'].ewm(span=9).mean()
        df['EMA_21'] = df['Close'].ewm(span=21).mean()
        df['TR'] = np.maximum((df['High'] - df['Low']), np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
        df['ATR'] = df['TR'].rolling(14).mean()
        return df
    except:
        return None

# --- 5. EDUCATION PATTERN GENERATOR ---
def plot_educational_pattern(pattern_type):
    fig = go.Figure()
    
    if pattern_type == "Bullish Engulfing":
        # Create Dummy Data: Red candle then Big Green candle
        fig.add_trace(go.Candlestick(
            x=[1, 2], open=[100, 90], high=[102, 115], low=[95, 88], close=[96, 112],
            increasing_line_color='#48bb78', decreasing_line_color='#f56565'
        ))
        title = "Bullish Engulfing (Reversal)"
        
    elif pattern_type == "Doji":
        # Create Dummy Data: Open and Close are same
        fig.add_trace(go.Candlestick(
            x=[1], open=[100], high=[110], low=[90], close=[100.2],
            increasing_line_color='gray', decreasing_line_color='gray'
        ))
        title = "Doji (Indecision)"
    
    fig.update_layout(template="plotly_dark", height=250, title=title, xaxis_visible=False, yaxis_visible=False, margin=dict(l=0,r=0,t=30,b=0))
    return fig

# --- 6. UI HEADER ---
c1, c2 = st.columns([1, 4])
with c1: st.markdown("# 🇮🇳 HiTrade")
with c2: st.markdown(f"""<div class="ticker-wrap"><span class="ticker-item">DATABASE STATUS: <span class="positive">{len(MARKET_UNIVERSE)} COMPANIES LOADED</span></span></div>""", unsafe_allow_html=True)

tabs = st.tabs(["🏠 Safe Scanner", "🔎 Search Everything", "🎓 Academy"])

# =========================================================
# TAB 1: SCANNER
# =========================================================
with tabs[0]:
    st.subheader("🚀 AI Opportunity Scanner")
    st.info("We scan the market in segments to keep the app fast.")
    
    c1, c2 = st.columns(2)
    capital = c1.number_input("Capital (₹)", 100, step=50)
    
    # Safe Slicing
    if len(MARKET_UNIVERSE) > 100:
        segments = {
            "Top 50 (Nifty 50)": MARKET_UNIVERSE[:50],
            "Next 50 (Midcap)": MARKET_UNIVERSE[50:100],
            "Risky / Small": MARKET_UNIVERSE[100:150]
        }
    else:
        segments = {"Backup List": MARKET_UNIVERSE} 
    
    segment_name = c2.selectbox("Select Segment", list(segments.keys()))
    
    if st.button("Start Scan"):
        target_list = segments[segment_name]
        st.write(f"Scanning {len(target_list)} stocks...")
        bar = st.progress(0)
        
        for i, ticker in enumerate(target_list):
            # Scanner uses default 180 days for speed consistency
            df = analyze_stock(ticker, days=180)
            if df is not None:
                price = df['Close'].iloc[-1]
                ema9 = df['EMA_9'].iloc[-1]
                ema21 = df['EMA_21'].iloc[-1]
                atr = df['ATR'].iloc[-1]
                
                if ema9 > ema21 and price <= capital:
                    safe_qty = int((capital * 0.02) / (2 * atr))
                    st.markdown(f"""
                    <div class="stock-row stock-row-buy">
                        <div><b>{ticker}</b><br><small>Positive Momentum</small></div>
                        <div style="text-align:right;"><b>₹{price:.2f}</b><br><span style="color:#48bb78">BUY {safe_qty} Qty</span></div>
                    </div>""", unsafe_allow_html=True)
            
            bar.progress((i + 1) / len(target_list))
        bar.empty()

# =========================================================
# TAB 2: UNIVERSAL SEARCH
# =========================================================
with tabs[1]:
    st.subheader("🔎 Universal Market Search")
    st.caption(f"Search from {len(MARKET_UNIVERSE)} available companies.")
    
    # --- CHANGED: Added Data Analysis (Days) here ---
    c_search, c_days = st.columns([3, 1])
    
    with c_search:
        selected_ticker = st.selectbox("Type Company Name...", MARKET_UNIVERSE)
    
    with c_days:
        days_lookback = st.slider("Analysis (Days)", 100, 730, 180)
    
    if st.button("Analyze Stock"):
        with st.spinner(f"Analyzing {selected_ticker}..."):
            # Pass the slider value to the function
            df = analyze_stock(selected_ticker, days=days_lookback)
            
            if df is not None:
                price = df['Close'].iloc[-1]
                atr = df['ATR'].iloc[-1]
                stop = price - (2 * atr)
                
                # Plot
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
                fig.add_hline(y=stop, line_dash="dash", line_color="red", annotation_text="AI Stop Loss")
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='green'), name='9 EMA'))
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='red'), name='21 EMA'))
                fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Logic
                st.markdown("---")
                c1, c2 = st.columns(2)
                c1.info(f"**Analysis:** {selected_ticker} | Volatility: ₹{atr:.2f}")
                safe_q = int((50000 * 0.02) / (2 * atr))
                c2.markdown(f"""<div class="innovation-card"><h2>{safe_q} Shares</h2><p>Safe Limit</p></div>""", unsafe_allow_html=True)
            else:
                st.error("Could not fetch data. Market might be closed.")

# =========================================================
# TAB 3: ACADEMY (FULL CONTENT)
# =========================================================
with tabs[2]:
    st.header("🎓 HiTrade Academy")
    st.caption("Learn the Logic behind the Markets. No more gambling.")
    st.markdown("---")
    
    # SECTION 1: CANDLESTICK PATTERNS
    st.subheader("1. Essential Candlestick Patterns")
    col_pat1, col_pat2 = st.columns(2)
    
    with col_pat1:
        st.plotly_chart(plot_educational_pattern("Bullish Engulfing"), use_container_width=True)
        st.markdown("""
        <div class="edu-card">
            <b>🐂 Bullish Engulfing</b><br>
            A small red candle followed by a <b>giant green candle</b> that "eats" the previous one.<br>
            <b>Meaning:</b> Buyers have completely overwhelmed sellers. Strong Buy Signal.
        </div>
        """, unsafe_allow_html=True)

    with col_pat2:
        st.plotly_chart(plot_educational_pattern("Doji"), use_container_width=True)
        st.markdown("""
        <div class="edu-card">
            <b>⚖️ The Doji</b><br>
            A candle with almost no body (looks like a cross).<br>
            <b>Meaning:</b> Indecision. Buyers and Sellers are fighting equally. Wait for the next candle to decide direction.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # SECTION 2: INDICATORS EXPLAINED
    st.subheader("2. Indicators Logic")
    
    with st.expander("📉 What is EMA (Exponential Moving Average)?"):
        st.write("""
        * **The Concept:** It is the average price of the stock, but it gives more importance to *recent* days.
        * **Our Algo:** We use the **9 EMA** (Fast) and **21 EMA** (Slow).
        * **The Signal:** When the Fast line crosses ABOVE the Slow line, it's like a Ferrari overtaking a Truck. It means Speed (Momentum) is picking up!
        """)
        
    with st.expander("🛡️ What is ATR (Average True Range)?"):
        st.write("""
        * **The Concept:** It measures the "Weather" of the stock.
        * **High ATR:** Stormy weather (High Volatility). Keep your boat (Trade Size) small.
        * **Low ATR:** Calm weather. You can sail a bigger boat.
        * **Why we use it:** To calculate your **Safe Quantity**.
        """)
        
    st.info("💡 **Pro Tip:** HiTrade automates all these lessons for you in the 'Scanner' tab!")