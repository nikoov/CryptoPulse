import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import glob
import os

# Set page configuration
st.set_page_config(
    page_title="CryptoPulse Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c23;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: #fafafa;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper functions
def load_latest_current_prices():
    """Load the most recent current prices data."""
    files = glob.glob('data/prices_current_*.json')
    if not files:
        return None
    
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def load_historical_prices(crypto_id):
    """Load the most recent historical prices for a cryptocurrency."""
    files = glob.glob(f'data/prices_historical_{crypto_id}_*.csv')
    if not files:
        return None
    
    latest_file = max(files, key=os.path.getctime)
    return pd.read_csv(latest_file)

# Sidebar
st.sidebar.image("https://img.icons8.com/nolan/64/cryptocurrency.png", width=64)
st.sidebar.title("CryptoPulse")
st.sidebar.markdown("---")
selected_page = st.sidebar.radio(
    "Navigation",
    ["Market Overview", "Price Analysis", "Historical Trends"]
)

# Load data
current_prices = load_latest_current_prices()
if current_prices is None:
    st.error("No price data available. Please run the data collector first.")
    st.stop()

# Market Overview Page
if selected_page == "Market Overview":
    st.title("📊 Cryptocurrency Market Overview")
    
    # Market Statistics Cards
    col1, col2, col3 = st.columns(3)
    
    total_market_cap = sum(data.get('usd_market_cap', 0) for data in current_prices.values())
    total_volume = sum(data.get('usd_24h_vol', 0) for data in current_prices.values())
    avg_change = sum(data.get('usd_24h_change', 0) for data in current_prices.values()) / len(current_prices)
    
    with col1:
        st.metric(
            "Total Market Cap",
            f"${total_market_cap:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "24h Trading Volume",
            f"${total_volume:,.0f}",
            delta=None
        )
    
    with col3:
        st.metric(
            "Average 24h Change",
            f"{avg_change:.2f}%",
            delta=f"{avg_change:.2f}%"
        )
    
    # Price Overview Table
    st.subheader("Price Overview")
    
    price_data = []
    for crypto_id, data in current_prices.items():
        price_data.append({
            "Cryptocurrency": crypto_id.title(),
            "Price (USD)": f"${data.get('usd', 0):,.2f}",
            "24h Change": f"{data.get('usd_24h_change', 0):.2f}%",
            "Market Cap": f"${data.get('usd_market_cap', 0):,.0f}",
            "24h Volume": f"${data.get('usd_24h_vol', 0):,.0f}"
        })
    
    df = pd.DataFrame(price_data)
    st.dataframe(
        df.style.background_gradient(subset=['24h Change'], cmap='RdYlGn'),
        use_container_width=True
    )

# Price Analysis Page
elif selected_page == "Price Analysis":
    st.title("💹 Price Analysis")
    
    # Cryptocurrency selector
    selected_crypto = st.selectbox(
        "Select Cryptocurrency",
        options=list(current_prices.keys()),
        format_func=lambda x: x.title()
    )
    
    # Load historical data
    historical_data = load_historical_prices(selected_crypto)
    if historical_data is not None:
        # Price chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=historical_data.index,
            y=historical_data['price'],
            name='Price',
            line=dict(color='#00ff88', width=2)
        ))
        
        fig.update_layout(
            title=f"{selected_crypto.title()} Price History",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        fig_volume = px.bar(
            historical_data,
            x=historical_data.index,
            y='volume',
            title=f"{selected_crypto.title()} Trading Volume"
        )
        
        fig_volume.update_layout(
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)

# Historical Trends Page
elif selected_page == "Historical Trends":
    st.title("📈 Historical Trends")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now()
        )
    
    # Multi-cryptocurrency comparison
    selected_cryptos = st.multiselect(
        "Select Cryptocurrencies to Compare",
        options=list(current_prices.keys()),
        default=list(current_prices.keys())[:3],
        format_func=lambda x: x.title()
    )
    
    if selected_cryptos:
        fig = go.Figure()
        
        for crypto in selected_cryptos:
            historical_data = load_historical_prices(crypto)
            if historical_data is not None:
                # Normalize prices to percentage change
                first_price = historical_data['price'].iloc[0]
                normalized_prices = (historical_data['price'] - first_price) / first_price * 100
                
                fig.add_trace(go.Scatter(
                    x=historical_data.index,
                    y=normalized_prices,
                    name=crypto.title(),
                    mode='lines'
                ))
        
        fig.update_layout(
            title="Comparative Price Performance (%)",
            xaxis_title="Date",
            yaxis_title="Price Change (%)",
            template="plotly_dark",
            height=600,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>CryptoPulse Dashboard • Built with Streamlit • Data from CoinGecko</p>
    </div>
    """,
    unsafe_allow_html=True
) 