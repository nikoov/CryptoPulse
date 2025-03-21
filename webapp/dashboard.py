import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import glob
import os
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

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

def load_sentiment_data():
    """Load sentiment analysis data."""
    try:
        with open('data/reddit/sample_posts.json', 'r') as f:
            data = json.load(f)
            return data['posts']
    except Exception:
        return None

# Sidebar
st.sidebar.image("https://img.icons8.com/nolan/64/cryptocurrency.png", width=64)
st.sidebar.title("CryptoPulse")
st.sidebar.markdown("---")
selected_page = st.sidebar.radio(
    "Navigation",
    ["Market Overview", "Price Analysis", "Historical Trends", "Sentiment Analysis"]
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
        price = data.get('usd', 0)
        change = data.get('usd_24h_change', 0)
        market_cap = data.get('usd_market_cap', 0)
        volume = data.get('usd_24h_vol', 0)
        
        price_data.append({
            "Cryptocurrency": crypto_id.title(),
            "Price (USD)": price,
            "24h Change": change,
            "Market Cap": market_cap,
            "24h Volume": volume
        })
    
    df = pd.DataFrame(price_data)
    
    # Create a styled version with formatting
    styled_df = df.copy()
    
    # Keep numerical values for styling
    numerical_changes = df["24h Change"].copy()
    
    # Format display values
    styled_df["Price (USD)"] = styled_df["Price (USD)"].apply(lambda x: f"${x:,.2f}")
    styled_df["24h Change"] = styled_df["24h Change"].apply(lambda x: f"{x:.2f}%")
    styled_df["Market Cap"] = styled_df["Market Cap"].apply(lambda x: f"${x:,.0f}")
    styled_df["24h Volume"] = styled_df["24h Volume"].apply(lambda x: f"${x:,.0f}")
    
    # Apply styling with background gradient on the numerical change column
    st.dataframe(
        styled_df.style.background_gradient(
            subset=["24h Change"],
            cmap='RdYlGn',
            gmap=numerical_changes
        ),
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

# Sentiment Analysis Page
elif selected_page == "Sentiment Analysis":
    st.title("🎭 Sentiment Analysis")
    
    # Load sentiment data
    sentiment_data = load_sentiment_data()
    
    if sentiment_data is None:
        st.error("No sentiment data available. Please run the sentiment analyzer first.")
    else:
        # Group posts by cryptocurrency
        crypto_sentiments = {}
        for post in sentiment_data:
            crypto_id = post['crypto_id']
            if crypto_id not in crypto_sentiments:
                crypto_sentiments[crypto_id] = []
            crypto_sentiments[crypto_id].append(post)
        
        # Overall Sentiment Summary
        st.subheader("📊 Overall Sentiment Distribution")
        
        # Calculate overall sentiment stats
        all_sentiments = []
        for posts in crypto_sentiments.values():
            for post in posts:
                if 'sentiment_analysis' in post:
                    all_sentiments.append(post['sentiment_analysis']['sentiment'])
        
        if all_sentiments:
            sentiment_counts = Counter(all_sentiments)
            
            # Create pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(sentiment_counts.keys()),
                values=list(sentiment_counts.values()),
                hole=.3,
                marker_colors=['#00ff88', '#888888', '#ff4444']
            )])
            
            fig_pie.update_layout(
                title="Overall Sentiment Distribution",
                template="plotly_dark",
                showlegend=True
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Cryptocurrency selector
        selected_crypto = st.selectbox(
            "Select Cryptocurrency",
            options=list(crypto_sentiments.keys()),
            format_func=lambda x: x.title()
        )
        
        if selected_crypto:
            posts = crypto_sentiments[selected_crypto]
            
            # Sentiment Statistics for Selected Crypto
            st.subheader(f"📈 {selected_crypto.title()} Sentiment Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            # Calculate statistics
            crypto_sentiments_list = [
                post['sentiment_analysis']['sentiment'] 
                for post in posts 
                if 'sentiment_analysis' in post
            ]
            
            if crypto_sentiments_list:
                sentiment_counts = Counter(crypto_sentiments_list)
                total_posts = len(crypto_sentiments_list)
                
                with col1:
                    positive_pct = (sentiment_counts.get('positive', 0) / total_posts) * 100
                    st.metric(
                        "Positive Sentiment",
                        f"{positive_pct:.1f}%",
                        delta=f"{positive_pct - 33.33:.1f}%" if positive_pct > 33.33 else None
                    )
                
                with col2:
                    neutral_pct = (sentiment_counts.get('neutral', 0) / total_posts) * 100
                    st.metric(
                        "Neutral Sentiment",
                        f"{neutral_pct:.1f}%",
                        delta=None
                    )
                
                with col3:
                    negative_pct = (sentiment_counts.get('negative', 0) / total_posts) * 100
                    st.metric(
                        "Negative Sentiment",
                        f"{negative_pct:.1f}%",
                        delta=f"{33.33 - negative_pct:.1f}%" if negative_pct < 33.33 else None
                    )
            
            # Word Clouds
            st.subheader("🔤 Word Frequency Analysis")
            
            # Separate texts by sentiment
            positive_texts = " ".join([
                post['text'] for post in posts 
                if 'sentiment_analysis' in post and post['sentiment_analysis']['sentiment'] == 'positive'
            ])
            
            negative_texts = " ".join([
                post['text'] for post in posts 
                if 'sentiment_analysis' in post and post['sentiment_analysis']['sentiment'] == 'negative'
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Positive Sentiment Words**")
                if positive_texts:
                    wordcloud = WordCloud(
                        width=800, height=400,
                        background_color='#0e1117',
                        colormap='YlGn'
                    ).generate(positive_texts)
                    
                    plt.figure(figsize=(10, 5))
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis('off')
                    st.pyplot(plt)
                else:
                    st.info("No positive sentiment texts available")
            
            with col2:
                st.write("**Negative Sentiment Words**")
                if negative_texts:
                    wordcloud = WordCloud(
                        width=800, height=400,
                        background_color='#0e1117',
                        colormap='RdGy'
                    ).generate(negative_texts)
                    
                    plt.figure(figsize=(10, 5))
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis('off')
                    st.pyplot(plt)
                else:
                    st.info("No negative sentiment texts available")
            
            # Recent Posts with Sentiment
            st.subheader("📝 Recent Posts and Sentiments")
            
            for post in posts:
                with st.expander(f"{post['title']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write("**Content:**")
                        st.write(post['text'])
                        st.write(f"**Posted in:** r/{post['subreddit']}")
                        st.write(f"**Score:** {post['score']}")
                    
                    with col2:
                        if 'sentiment_analysis' in post:
                            sentiment = post['sentiment_analysis']
                            sentiment_color = {
                                'positive': 'green',
                                'neutral': 'gray',
                                'negative': 'red'
                            }.get(sentiment['sentiment'], 'gray')
                            
                            st.markdown(f"""
                                <div style='background-color: {sentiment_color}20; padding: 10px; border-radius: 5px;'>
                                    <h4 style='color: {sentiment_color}; margin: 0;'>
                                        {sentiment['sentiment'].title()}
                                    </h4>
                                    <p style='margin: 5px 0;'>
                                        Confidence: {sentiment['confidence']:.2%}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("Sentiment analysis not available")
                    
                    st.markdown("---")

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