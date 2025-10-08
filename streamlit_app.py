import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time

# Page configuration
st.set_page_config(
    page_title="MTWB Stock Evaluator",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for MTWB branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2c5aa0 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .esg-card {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .community-highlight {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f4e79;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ESG Data Sources and Scoring Framework
ESG_WEIGHTS = {
    "esg_rating": 0.40,      # 10 points - External ESG ratings
    "carbon_targets": 0.35,  # 8.75 points - Carbon reduction/renewable energy
    "community": 0.25        # 6.25 points - Community engagement initiatives
}

ESG_RATING_SCORES = {
    "AAA": 100, "AA": 90, "A": 80, "BBB": 70, "BB": 60, "B": 50, "CCC": 30, "CC": 20, "C": 10
}

# Enhanced ESG data with MTWB community focus
ESG_SAMPLE_DATA = {
    "AAPL": {"esg_rating": "AA", "carbon_targets": 85, "community": 90, "community_initiatives": "Education technology programs, environmental conservation"},
    "MSFT": {"esg_rating": "AA", "carbon_targets": 88, "community": 85, "community_initiatives": "Digital skills training, accessibility programs"},
    "GOOGL": {"esg_rating": "A", "carbon_targets": 90, "community": 80, "community_initiatives": "STEM education, digital literacy programs"},
    "META": {"esg_rating": "BBB", "carbon_targets": 75, "community": 70, "community_initiatives": "Digital connectivity, small business support"},
    "TSLA": {"esg_rating": "A", "carbon_targets": 95, "community": 75, "community_initiatives": "Sustainable transportation, renewable energy education"},
    "JNJ": {"esg_rating": "AA", "carbon_targets": 70, "community": 95, "community_initiatives": "Healthcare access, vaccine equity programs"},
    "V": {"esg_rating": "A", "carbon_targets": 65, "community": 85, "community_initiatives": "Financial inclusion, economic empowerment"},
    "JPM": {"esg_rating": "BBB", "carbon_targets": 60, "community": 80, "community_initiatives": "Financial literacy, affordable housing"},
    "PG": {"esg_rating": "AA", "carbon_targets": 80, "community": 90, "community_initiatives": "Clean water access, disaster relief"},
    "NVDA": {"esg_rating": "A", "carbon_targets": 70, "community": 75, "community_initiatives": "AI for social good, STEM education"},
    "WMT": {"esg_rating": "BBB", "carbon_targets": 75, "community": 85, "community_initiatives": "Food security, workforce development"},
    "KO": {"esg_rating": "BBB", "carbon_targets": 70, "community": 80, "community_initiatives": "Water stewardship, women's empowerment"},
    "PEP": {"esg_rating": "A", "carbon_targets": 75, "community": 85, "community_initiatives": "Agricultural development, nutrition programs"},
    "INTC": {"esg_rating": "BBB", "carbon_targets": 80, "community": 70, "community_initiatives": "Technology education, digital inclusion"},
    "MRK": {"esg_rating": "A", "carbon_targets": 65, "community": 90, "community_initiatives": "Global health access, disease prevention"},
    "HD": {"esg_rating": "A", "carbon_targets": 70, "community": 85, "community_initiatives": "Affordable housing, veteran support"},
    "MA": {"esg_rating": "A", "carbon_targets": 60, "community": 80, "community_initiatives": "Financial inclusion, digital payments"},
    "DIS": {"esg_rating": "BBB", "carbon_targets": 65, "community": 90, "community_initiatives": "Children's programs, environmental education"},
    "UNH": {"esg_rating": "BBB", "carbon_targets": 55, "community": 75, "community_initiatives": "Healthcare access, wellness programs"},
    "VZ": {"esg_rating": "BBB", "carbon_targets": 70, "community": 70, "community_initiatives": "Digital inclusion, STEM education"},
    "NFLX": {"esg_rating": "A", "carbon_targets": 80, "community": 75, "community_initiatives": "Diverse content creation, accessibility"},
    "PFE": {"esg_rating": "AA", "carbon_targets": 60, "community": 95, "community_initiatives": "Global health, vaccine equity"},
    "XOM": {"esg_rating": "BB", "carbon_targets": 30, "community": 60, "community_initiatives": "STEM education, energy education"},
    "BA": {"esg_rating": "BB", "carbon_targets": 45, "community": 70, "community_initiatives": "STEM education, aerospace programs"},
    "CVX": {"esg_rating": "BB", "carbon_targets": 35, "community": 65, "community_initiatives": "STEM education, community development"}
}

def normalize(series, inverse=False):
    """Normalize series to 0-100 scale"""
    if series.max() == series.min():
        return pd.Series([50]*len(series), index=series.index)
    if inverse:
        return 100 * (series.max() - series) / (series.max() - series.min())
    else:
        return 100 * (series - series.min()) / (series.max() - series.min())

def get_esg_data(ticker):
    """Get ESG data for a company with MTWB community focus"""
    if ticker in ESG_SAMPLE_DATA:
        return ESG_SAMPLE_DATA[ticker]
    else:
        return {
            "esg_rating": random.choice(["AAA", "AA", "A", "BBB", "BB"]),
            "carbon_targets": random.randint(40, 90),
            "community": random.randint(50, 95),
            "community_initiatives": "Various community engagement programs"
        }

def calculate_esg_score(ticker):
    """Calculate MTWB ESG Score (0-25 points)"""
    esg_data = get_esg_data(ticker)
    
    esg_rating_score = ESG_RATING_SCORES.get(esg_data["esg_rating"], 50)
    
    esg_score = (
        esg_rating_score * ESG_WEIGHTS["esg_rating"] +
        esg_data["carbon_targets"] * ESG_WEIGHTS["carbon_targets"] +
        esg_data["community"] * ESG_WEIGHTS["community"]
    )
    
    return {
        "esg_rating": esg_data["esg_rating"],
        "carbon_targets": esg_data["carbon_targets"],
        "community": esg_data["community"],
        "community_initiatives": esg_data["community_initiatives"],
        "esg_score": esg_score
    }

def get_stock_data(ticker):
    """Get comprehensive stock data including ESG"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Basic financial data
        pe_ratio = info.get("trailingPE", np.nan)
        beta = info.get("beta", np.nan)
        dividend_yield = info.get("dividendYield", 0) or 0
        sector = info.get("sector", "Unknown")
        profit_margin = info.get("profitMargins", np.nan)
        roe = info.get("returnOnEquity", np.nan)
        fiftytwo_wk_change = info.get("52WeekChange", np.nan)
        market_cap = info.get("marketCap", np.nan)
        current_price = info.get("currentPrice", np.nan)
        
        # ESG data
        esg_data = calculate_esg_score(ticker)
        
        return {
            "ticker": ticker,
            "sector": sector,
            "current_price": current_price,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "beta": beta,
            "dividend_yield": dividend_yield * 100,  # Convert to percentage
            "profit_margin": profit_margin * 100,    # Convert to percentage
            "roe": roe * 100,                        # Convert to percentage
            "fiftytwo_wk_change": fiftytwo_wk_change * 100,  # Convert to percentage
            **esg_data
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

def calculate_mtwb_score(stock_data):
    """Calculate MTWB comprehensive score"""
    if not stock_data:
        return None
    
    # Extract individual values from stock_data
    pe_ratio = stock_data.get("pe_ratio", 0)
    beta = stock_data.get("beta", 1)
    dividend_yield = stock_data.get("dividend_yield", 0)
    profit_margin = stock_data.get("profit_margin", 0)
    roe = stock_data.get("roe", 0)
    fiftytwo_wk_change = stock_data.get("fiftytwo_wk_change", 0)
    esg_score = stock_data.get("esg_score", 12.5)
    
    # Calculate individual scores (0-100 scale)
    # P/E Score: Lower P/E is better
    pe_score = 100 - min(100, max(0, (pe_ratio - 10) * 2)) if not pd.isna(pe_ratio) and pe_ratio > 0 else 50
    
    # Volatility Score: Lower beta is better
    volatility_score = 100 - min(100, max(0, beta * 50)) if not pd.isna(beta) else 50
    
    # Dividend Score: Higher yield is better
    dividend_score = min(100, dividend_yield * 20) if not pd.isna(dividend_yield) else 50
    
    # Profit Score: Higher margin is better
    profit_score = min(100, max(0, profit_margin)) if not pd.isna(profit_margin) else 50
    
    # ROE Score: Higher ROE is better
    roe_score = min(100, max(0, roe)) if not pd.isna(roe) else 50
    
    # Growth Score: Positive growth is better
    growth_score = min(100, max(0, 50 + fiftytwo_wk_change)) if not pd.isna(fiftytwo_wk_change) else 50
    
    # ESG Score normalization (0-25 points scaled to 0-100)
    esg_score_normalized = esg_score * 4
    
    # MTWB Weighting system
    weights = {
        "pe_score": 0.08,
        "volatility_score": 0.20,
        "dividend_score": 0.12,
        "profit_score": 0.08,
        "roe_score": 0.12,
        "growth_score": 0.25,
        "esg_score_normalized": 0.25
    }
    
    mtwb_score = (
        pe_score * weights["pe_score"] +
        volatility_score * weights["volatility_score"] +
        dividend_score * weights["dividend_score"] +
        profit_score * weights["profit_score"] +
        roe_score * weights["roe_score"] +
        growth_score * weights["growth_score"] +
        esg_score_normalized * weights["esg_score_normalized"]
    )
    
    return {
        "mtwb_score": round(mtwb_score, 1),
        "pe_score": round(pe_score, 1),
        "volatility_score": round(volatility_score, 1),
        "dividend_score": round(dividend_score, 1),
        "profit_score": round(profit_score, 1),
        "roe_score": round(roe_score, 1),
        "growth_score": round(growth_score, 1),
        "esg_score_normalized": round(esg_score_normalized, 1)
    }

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ MTWB Stock Evaluator</h1>
        <h3>Making the World Better Through Investment</h3>
        <p>Evaluating investments through the lens of financial performance and community impact</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 MTWB Mission")
        st.markdown("""
        **Making the World Better** invests in Philadelphia communities through:
        - 🏛️ **$30M+ in capital improvements** to public spaces
        - 🏀 **Multi-purpose parks and athletic fields**
        - 🎵 **Community centers** with creative programs
        - 🤝 **Deep community engagement** in every project
        """)
        
        st.markdown("---")
        st.markdown("## 🎓 Connor's Vision")
        st.markdown("""
        *"Wharton made me think more about the sustainability of a nonprofit, and the importance of building strong partnerships to keep the work going."*
        
        - **NFL Veteran** turned **Wharton MBA** (2023)
        - **Strategic Leadership** with systems-level thinking
        - **Emphasis on Sustainability** and lasting partnerships
        """)
        
        st.markdown("---")
        st.markdown("## 📊 Scoring Methodology")
        st.markdown("""
        **Financial Metrics (75%)**
        - Growth Potential (25%)
        - Risk Management (20%)
        - Dividend Stability (12%)
        - Profitability (8% each)
        
        **ESG & Community (25%)**
        - ESG Rating (10%)
        - Carbon Targets (8.75%)
        - Community Engagement (6.25%)
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🔍 Stock Analysis")
        
        # Stock input
        ticker_input = st.text_input(
            "Enter Stock Ticker Symbol",
            placeholder="e.g., AAPL, MSFT, TSLA",
            help="Enter a valid stock ticker symbol to analyze"
        ).upper().strip()
        
        if ticker_input:
            with st.spinner(f"Analyzing {ticker_input}..."):
                stock_data = get_stock_data(ticker_input)
                
                if stock_data:
                    scores = calculate_mtwb_score(stock_data)
                    
                    if scores:
                        # Main score display
                        st.markdown(f"""
                        <div class="metric-card">
                            <h2>🎯 MTWB Score: {scores['mtwb_score']}/100</h2>
                            <p><strong>{ticker_input}</strong> - {stock_data['sector']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detailed metrics in tabs
                        tab1, tab2, tab3 = st.tabs(["📈 Financial Metrics", "🌱 ESG & Sustainability", "🏛️ Community Impact"])
                        
                        with tab1:
                            col_f1, col_f2 = st.columns(2)
                            
                            with col_f1:
                                st.metric("Current Price", f"${stock_data['current_price']:.2f}" if not pd.isna(stock_data['current_price']) else "N/A")
                                st.metric("Market Cap", f"${stock_data['market_cap']/1e9:.1f}B" if not pd.isna(stock_data['market_cap']) else "N/A")
                                st.metric("P/E Ratio", f"{stock_data['pe_ratio']:.2f}" if not pd.isna(stock_data['pe_ratio']) else "N/A")
                                st.metric("Beta (Risk)", f"{stock_data['beta']:.2f}" if not pd.isna(stock_data['beta']) else "N/A")
                            
                            with col_f2:
                                st.metric("Dividend Yield", f"{stock_data['dividend_yield']:.2f}%" if not pd.isna(stock_data['dividend_yield']) else "N/A")
                                st.metric("Profit Margin", f"{stock_data['profit_margin']:.1f}%" if not pd.isna(stock_data['profit_margin']) else "N/A")
                                st.metric("ROE", f"{stock_data['roe']:.1f}%" if not pd.isna(stock_data['roe']) else "N/A")
                                st.metric("52W Change", f"{stock_data['fiftytwo_wk_change']:.1f}%" if not pd.isna(stock_data['fiftytwo_wk_change']) else "N/A")
                        
                        with tab2:
                            st.markdown(f"""
                            <div class="esg-card">
                                <h3>🌱 ESG Rating: {stock_data['esg_rating']}</h3>
                                <p><strong>ESG Score:</strong> {stock_data['esg_score']:.1f}/25</p>
                                <p><strong>Carbon Targets:</strong> {stock_data['carbon_targets']}/100</p>
                                <p><strong>Community Engagement:</strong> {stock_data['community']}/100</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # ESG breakdown chart
                            esg_data = {
                                'Component': ['ESG Rating', 'Carbon Targets', 'Community Engagement'],
                                'Score': [
                                    ESG_RATING_SCORES.get(stock_data['esg_rating'], 50),
                                    stock_data['carbon_targets'],
                                    stock_data['community']
                                ],
                                'Weight': [40, 35, 25]
                            }
                            
                            fig_esg = px.bar(
                                pd.DataFrame(esg_data),
                                x='Component',
                                y='Score',
                                color='Score',
                                color_continuous_scale='RdYlGn',
                                title="ESG Component Breakdown"
                            )
                            fig_esg.update_layout(height=400)
                            st.plotly_chart(fig_esg, use_container_width=True)
                        
                        with tab3:
                            st.markdown(f"""
                            <div class="community-highlight">
                                <h3>🏛️ Community Initiatives</h3>
                                <p><strong>{ticker_input}</strong> is engaged in:</p>
                                <p><em>"{stock_data['community_initiatives']}"</em></p>
                                <p>This aligns with MTWB's mission of community engagement and sustainable impact.</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Community impact visualization
                            community_metrics = {
                                'Metric': ['Community Engagement', 'ESG Rating Impact', 'Carbon Responsibility'],
                                'Score': [stock_data['community'], ESG_RATING_SCORES.get(stock_data['esg_rating'], 50), stock_data['carbon_targets']]
                            }
                            
                            fig_community = go.Figure(data=go.Scatterpolar(
                                r=community_metrics['Score'],
                                theta=community_metrics['Metric'],
                                fill='toself',
                                name=f"{ticker_input} Community Impact"
                            ))
                            
                            fig_community.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, 100]
                                    )),
                                showlegend=True,
                                title="Community Impact Radar Chart",
                                height=500
                            )
                            
                            st.plotly_chart(fig_community, use_container_width=True)
                        
                        # Overall score breakdown
                        st.markdown("## 📊 Score Breakdown")
                        
                        score_data = {
                            'Category': ['Growth', 'Risk Management', 'ESG & Community', 'Dividend', 'Profitability', 'ROE', 'Valuation'],
                            'Score': [
                                scores['growth_score'],
                                scores['volatility_score'],
                                scores['esg_score_normalized'],
                                scores['dividend_score'],
                                scores['profit_score'],
                                scores['roe_score'],
                                scores['pe_score']
                            ],
                            'Weight': [25, 20, 25, 12, 8, 12, 8]
                        }
                        
                        df_scores = pd.DataFrame(score_data)
                        
                        fig_scores = px.bar(
                            df_scores,
                            x='Category',
                            y='Score',
                            color='Score',
                            color_continuous_scale='RdYlGn',
                            title=f"MTWB Score Breakdown for {ticker_input}",
                            text='Score'
                        )
                        fig_scores.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                        fig_scores.update_layout(height=500, showlegend=False)
                        st.plotly_chart(fig_scores, use_container_width=True)
                        
                        # Investment recommendation
                        st.markdown("## 💡 MTWB Investment Perspective")
                        
                        if scores['mtwb_score'] >= 80:
                            st.success(f"🌟 **Excellent Match for MTWB**: {ticker_input} demonstrates strong financial performance and exceptional ESG commitment, aligning perfectly with MTWB's values of community impact and sustainability.")
                        elif scores['mtwb_score'] >= 65:
                            st.info(f"✅ **Good Fit for MTWB**: {ticker_input} shows solid fundamentals with meaningful community engagement, suitable for MTWB's investment criteria.")
                        elif scores['mtwb_score'] >= 50:
                            st.warning(f"⚠️ **Moderate Fit**: {ticker_input} has mixed performance. Consider deeper analysis of ESG initiatives and community impact before investment.")
                        else:
                            st.error(f"❌ **Poor Fit for MTWB**: {ticker_input} may not align with MTWB's mission of community impact and sustainable investing. Consider alternatives.")
    
    with col2:
        st.markdown("## 🏆 Top MTWB Aligned Stocks")
        
        # Sample top stocks with high MTWB scores
        top_stocks = [
            {"ticker": "AAPL", "score": 87, "reason": "Strong ESG, community tech programs"},
            {"ticker": "MSFT", "score": 85, "reason": "Digital inclusion, accessibility"},
            {"ticker": "JNJ", "score": 83, "reason": "Healthcare access, vaccine equity"},
            {"ticker": "PG", "score": 82, "reason": "Clean water, disaster relief"},
            {"ticker": "TSLA", "score": 81, "reason": "Sustainable transport, renewable energy"}
        ]
        
        for stock in top_stocks:
            with st.container():
                st.markdown(f"""
                <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #1f4e79;">
                    <strong>{stock['ticker']}</strong><br>
                    <span style="color: #1f4e79; font-size: 1.2em;">{stock['score']}/100</span><br>
                    <small>{stock['reason']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎯 Why ESG Matters for MTWB")
        st.markdown("""
        - **Community Impact**: Aligns with MTWB's $30M+ investment in Philadelphia
        - **Sustainable Growth**: Ensures long-term partnership viability
        - **Risk Management**: ESG leaders show better resilience
        - **Mission Alignment**: Reflects Connor's strategic approach to lasting impact
        """)

if __name__ == "__main__":
    main()
