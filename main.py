import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import pytz

# --- UPDATED DATA ---
SHARES = 435_666_174
CASH = 1_000_000_000
BTC_HELD = 193
ETH_HELD = 4_110_525 
EIGHT_STOCK_VALUE = 23_000_000
ETH_STAKED = 408_627  
ANNUAL_STAKING_APR = 0.03

st.set_page_config(page_title="BMNR NAV Tracker", page_icon="📈", layout="wide")

# --- CUSTOM UI STYLING ---
st.markdown("""
    <style>
    [data-testid="stMetricLabel"] p { color: #ADD8E6 !important; font-size: 1.1rem !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] div { color: #ADD8E6 !important; font-size: 2.2rem !important; }
    .timestamp { color: #888888; font-size: 0.9rem; margin-top: -20px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)
def fetch_prices():
    try:
        bmnr = yf.Ticker("BMNR").fast_info.last_price
        eth = yf.Ticker("ETH-USD").fast_info.last_price
        btc = yf.Ticker("BTC-USD").fast_info.last_price
        return bmnr, eth, btc
    except:
        return 0.0, 0.0, 0.0

bmnr_p, eth_p, btc_p = fetch_prices()

# --- CALCULATIONS ---
if bmnr_p > 0 and eth_p > 0:
    val_eth = ETH_HELD * eth_p
    val_btc = BTC_HELD * btc_p
    total_nav = val_eth + val_btc + CASH + EIGHT_STOCK_VALUE
    nav_per_share = total_nav / SHARES
    mnav = (bmnr_p * SHARES) / total_nav
    
    total_annual_usd_yield = (ETH_STAKED * ANNUAL_STAKING_APR) * eth_p
    yield_per_share = total_annual_usd_yield / SHARES
    eth_per_share = ETH_HELD / SHARES
    
    # Bottom calculations
    pct_eth_staked = (ETH_STAKED / ETH_HELD) * 100

    # --- HEADER SECTION ---
    st.title("BMNR mNAV Tracker")
    
    est_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %I:%M:%S %p')
    st.markdown(f'<p class="timestamp">Last Updated: {est_time} EST</p>', unsafe_allow_html=True)

    # TOP METRICS ROW
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("BMNR Price", f"${bmnr_p:,.2f}")    
    with m2: st.metric("NAV/Share", f"${nav_per_share:,.2f}")
    with m3: st.metric("mNAV (Total)", f"{mnav:.3f}x")
    with m4: st.metric("ETH/Share", f"{eth_per_share:.6f}")
    with m5: st.metric("Yield/Share", f"${yield_per_share:,.4f}")
    
    st.divider()

    # --- TREASURY BREAKDOWN ---
    st.subheader("Treasury & Staking Breakdown")
    assets_data = {
        "Asset": ["Ethereum (ETH)", "Bitcoin (BTC)", "Cash", "Eightco Stake"],
        "Total Quantity": [ETH_HELD, BTC_HELD, 0, 0],
        "Live Price": [eth_p, btc_p, 0, 0],
        "Staked Amount": [ETH_STAKED, 0, 0, 0],
        "Est. Annual Yield": [total_annual_usd_yield, 0, 0, 0],
        "Total Value": [val_eth, val_btc, CASH, EIGHT_STOCK_VALUE]
    }

    st.dataframe(
        pd.DataFrame(assets_data),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Total Quantity": st.column_config.NumberColumn("Total Quantity", format="%,.0f"),
            "Live Price": st.column_config.NumberColumn("Live Price", format="$%,.0f"),
            "Staked Amount": st.column_config.NumberColumn("Staked Amount (ETH)", format="%,.0f"),
            "Est. Annual Yield": st.column_config.NumberColumn("Est. Annual Yield", format="$%,.0f"),
            "Total Value": st.column_config.NumberColumn("Total Value", format="$%,.0f"),
        }
    )

    # --- FOOTER METRICS ---
    st.markdown("### Portfolio Statistics")
    f1, f2 = st.columns(2)
    with f1:
        st.metric("Shares Outstanding", f"{SHARES:,.0f}")
    with f2:
        st.metric("% of ETH Staked", f"{pct_eth_staked:.2f}%")
    
    # Auto-refresh loop
    time.sleep(30)
    st.rerun()
else:
    st.warning("🔄 Fetching live market data... Please wait.")
    time.sleep(5)
    st.rerun()
