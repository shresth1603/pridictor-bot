import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# 🎨 1. THE FRONTEND ENGINE (The "Beauty" Layer)
# ==============================================================================

st.set_page_config(
    page_title="HiTrade | Future Finance",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with st.sidebar:
    st.markdown("### 🛠️ Global Settings")
    capital = st.number_input("💰 Your Capital (₹)", value=25000, step=5000)
    risk_pct = st.slider("🛡️ Risk Tolerance (%)", 1.0, 5.0, 2.0)
    st.info(f"Total Risk per trade: ₹{(capital * risk_pct / 100):.2f}")

# This CSS makes it look like a "Real App" instead of a script
st.markdown("""
<style>
    /* IMPORT FONT (Inter - used by Stripe, Notion, etc.) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    /* GLOBAL THEME */
    * { font-family: 'Inter', sans-serif; }
    .stApp { 
        background-color: #000000;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 255, 163, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(0, 212, 255, 0.15) 0px, transparent 50%);
    }
    
    /* HERO HEADER */
    .hero-container {
        text-align: center;
        padding: 60px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 40px;
    }
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #FFFFFF 0%, #8899A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
        line-height: 1.1;
    }
    .hero-subtitle {
        color: #00FFA3;
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* GLASS CARDS (The "HUD" Effect) */
    .glass-card {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 25px;
        transition: all 0.3s ease;
        height: 100%;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    .glass-card:hover {
        border-color: #00FFA3;
        transform: translateY(-5px);
        box-shadow: 0 10px 40px -10px rgba(0, 255, 163, 0.2);
    }
    
    /* TYPOGRAPHY */
    .metric-value { font-size: 2rem; font-weight: 800; color: #fff; margin: 10px 0; }
    .metric-label { font-size: 0.8rem; text-transform: uppercase; color: #8899A6; letter-spacing: 1px; }
    .text-glow { text-shadow: 0 0 20px rgba(0, 255, 163, 0.5); }

    /* BADGES */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .badge-buy { background: rgba(0, 255, 163, 0.1); color: #00FFA3; border: 1px solid rgba(0, 255, 163, 0.3); }
    .badge-math { background: rgba(0, 212, 255, 0.1); color: #00D4FF; border: 1px solid rgba(0, 212, 255, 0.3); }

    /* CUSTOM TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        color: #666;
        font-weight: 600;
        font-size: 1rem;
    }
    .stTabs [aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #00FFA3 !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🧠 2. THE DATA ENGINE (Embedded Top 50 Stocks for Zero-Dependency)
# ==============================================================================

file = pd.read_csv('EQUITY_L.csv')
STOCKS = [str(x).strip() + ".NS" for x in file['SYMBOL'].tolist()]

@st.cache_data
def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period="6mo", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        
        # Math: EMA & ATR
        df['EMA_9'] = df['Close'].ewm(span=9).mean()
        df['EMA_21'] = df['Close'].ewm(span=21).mean()
        df['TR'] = np.maximum((df['High'] - df['Low']), np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
        df['ATR'] = df['TR'].rolling(14).mean()
        return df
    except:
        return None

def plot_neon_chart(df):
    fig = go.Figure()
    # Neon Green & Hot Pink Candles
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
                                 increasing_line_color='#00FFA3', decreasing_line_color='#FF0055', name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='#00FFA3', width=1), name='9 EMA'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='#FF0055', width=1), name='21 EMA'))
    
    # Dark Mode Grid
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                      height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222'))
    return fig

# ==============================================================================
# 🖥️ 3. THE UI LAYOUT (The Dashboard)
# ==============================================================================

# --- HERO SECTION ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">HiTrade</div>
    <div class="hero-subtitle">The AI Co-Pilot for Retail Traders</div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
tabs = st.tabs(["🚀 SCANNER", "🔎 ANALYZER", "🎓 ACADEMY"])

# --- TAB 1: SCANNER ---
with tabs[0]:
    # Control Panel
    with st.container():
        c1, c2, c3 = st.columns([1, 1, 2])
        capital = c1.number_input("💰 Your Capital (₹)", value=25000, step=5000)
        risk_pct = c2.slider("🛡️ Risk Tolerance (%)", 1.0, 5.0, 2.0)
        segment = c3.selectbox("📊 Select Segment", ["Top 50 (Bluechip)", "Midcap Growth", "Penny Stocks", "All Stocks"])
    
    st.markdown("---")
    
    if st.button("⚡ INITIATE AI SCAN", type="primary", use_container_width=True):
        st.write("") 
        
        # Logic to fake segments for demo (Splitting the main list)
        if segment == "Top 50 (Bluechip)": target_list = STOCKS[:15]
        elif segment == "Midcap Growth": target_list = STOCKS[15:30]
        elif segment == "Penny Stock": target_list = STOCKS[30:]
        else: target_list = STOCKS
        
        # Grid Layout
        cols = st.columns(3)
        found_count = 0
        
        for i, ticker in enumerate(target_list):
            df = analyze_stock(ticker)
            if df is not None:
                price = df['Close'].iloc[-1]
                ema9 = df['EMA_9'].iloc[-1]
                ema21 = df['EMA_21'].iloc[-1]
                atr = df['ATR'].iloc[-1]
                
                # Buy Logic
                if ema9 > ema21 and price <= capital:
                    risk_amt = capital * (risk_pct/100)
                    stop_loss = price - (2 * atr)
                    qty = int(risk_amt / (2 * atr))
                    if qty < 1: qty = 0
                    
                    # RENDER THE GLASS CARD
                    with cols[found_count % 3]:
                        st.markdown(f"""
                        <div class="glass-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div style="font-weight:700; color:white; font-size:1.1rem;">{ticker.replace('.NS','')}</div>
                                <span class="badge badge-buy">STRONG BUY</span>
                            </div>
                            <div style="margin-top:15px;">
                                <div class="metric-label">Current Price</div>
                                <div class="metric-value">₹{price:.1f}</div>
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-top:10px;">
                                <div>
                                    <div class="metric-label">Safe Qty</div>
                                    <div style="color:#00FFA3; font-weight:800; font-size:1.2rem;">{qty}</div>
                                </div>
                                <div style="text-align:right;">
                                    <div class="metric-label">Stop Loss</div>
                                    <div style="color:#FF0055; font-weight:800; font-size:1.2rem;">₹{stop_loss:.1f}</div>
                                </div>
                            </div>
                            <div style="margin-top:15px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                                <span class="badge badge-math">AI: ₹{risk_amt:.0f} Risk ÷ ₹{(2*atr):.1f} Vol</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write("") # Spacer
                        found_count += 1

# --- TAB 2: ANALYZER ---
with tabs[1]:
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown("### ⚙️ Input")
        selected_stock = st.selectbox("Search Database", STOCKS, key="analyzer_stock")
        analyze_btn = st.button("Analyze", use_container_width=True)
            
    with c2:
        if analyze_btn:
            df = analyze_stock(selected_stock)
            if df is not None:
                price = float(df['Close'].iloc[-1])
                atr = float(df['ATR'].iloc[-1])
                
                # --- CALCULATIONS ---
                risk_amount = capital * (risk_pct / 100)
                # Stop Loss is set at 2x ATR (Volatility) below current price
                stop_loss = price - (2 * atr)
                risk_per_share = price - stop_loss
                
                # Quantity = Total Risk / Risk Per Share
                if risk_per_share > 0:
                    safe_qty = int(risk_amount / risk_per_share)
                else:
                    safe_qty = 0
                
                # --- UI: METRICS ROW ---
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"""<div class="glass-card"><div class="metric-label">Price</div><div class="metric-value">₹{price:.2f}</div></div>""", unsafe_allow_html=True)
                m2.markdown(f"""<div class="glass-card"><div class="metric-label">Stop Loss</div><div class="metric-value" style="color:#FF0055">₹{stop_loss:.2f}</div></div>""", unsafe_allow_html=True)
                m3.markdown(f"""<div class="glass-card"><div class="metric-label">Safe Quantity</div><div class="metric-value" style="color:#00FFA3">{safe_qty} Units</div></div>""", unsafe_allow_html=True)
                
                # --- UI: REASONING BOX ---
                st.write("")
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color:#00D4FF; margin-top:0;">💡 Why only {safe_qty} shares?</h4>
                    <p style="color:#ccc; font-size:0.9rem; line-height:1.6;">
                        This quantity is calculated using <b>Scientific Position Sizing</b>. 
                        Even if the stock price drops to your stop loss of <b>₹{stop_loss:.2f}</b> (based on 2x market volatility), 
                        your total loss will be limited to <b>₹{risk_amount:.2f}</b> ({risk_pct}% of your capital).
                    </p>
                    <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; border-left:3px solid #00FFA3;">
                        <code style="color:#00FFA3; background:transparent;">
                        Qty = (Capital × Risk%) ÷ (Entry - StopLoss) <br>
                        Qty = {risk_amount:.0f} ÷ {risk_per_share:.2f} ≈ {safe_qty}
                        </code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Chart
                st.write("")
                st.markdown("### 📈 Live Technical View")
                st.plotly_chart(plot_neon_chart(df), use_container_width=True)

# --- TAB 3: ACADEMY ---
with tabs[2]:
    st.markdown("### 🎓 Interactive Trading Modules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h2 style="color:#00FFA3">Module 1: The Basics</h2>
            <p style="color:#ccc;">Learn how the stock market works, what shares are, and how to execute your first trade.</p>
            <br>
            <span class="badge badge-math">BEGINNER</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card" style="margin-top:20px;">
             <h2 style="color:#00D4FF">Module 2: Risk Logic</h2>
            <p style="color:#ccc;">Understand the math behind the "Safe Quantity" calculator and why 2% risk is the golden rule.</p>
            <br>
            <span class="badge badge-math">INTERMEDIATE</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
             <h2 style="color:#FF0055">Module 3: Technicals</h2>
            <p style="color:#ccc;">Master the art of reading Candlestick patterns, EMA crossovers, and RSI indicators.</p>
            <br>
            <span class="badge badge-math">ADVANCED</span>
        </div>
        """, unsafe_allow_html=True)
