import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Page configuration
st.set_page_config(
    page_title="MTWB Stock & ETF Evaluator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme
st.markdown("""
<style>
    :root {
        --primary-color: #000000;
        --background-color: #ffffff;
        --secondary-background-color: #ffffff;
        --text-color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Professional CSS styling
st.markdown("""
<style>
    /* Professional color scheme */
    .main-header {
        background: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        color: #000000;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    .main-header h1 {
        color: #000000 !important;
    }
    
    .main-header h3 {
        color: #000000 !important;
    }
    
    .main-header p {
        color: #000000 !important;
    }
    
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #000000;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #000000 !important;
        border: 1px solid #ecf0f1;
    }
    
    .metric-card h1, .metric-card h2, .metric-card h3, .metric-card h4, .metric-card h5, .metric-card h6 {
        color: #000000 !important;
    }
    
    .metric-card p {
        color: #000000 !important;
    }
    
    .esg-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #000000 !important;
        border: 1px solid #e9ecef;
    }
    
    .esg-card h1, .esg-card h2, .esg-card h3, .esg-card h4, .esg-card h5, .esg-card h6 {
        color: #000000 !important;
    }
    
    .esg-card p {
        color: #000000 !important;
    }
    
    .community-highlight {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #f39c12;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #000000 !important;
        border: 1px solid #e9ecef;
    }
    
    .community-highlight h1, .community-highlight h2, .community-highlight h3, .community-highlight h4, .community-highlight h5, .community-highlight h6 {
        color: #000000 !important;
    }
    
    .community-highlight p {
        color: #000000 !important;
    }
    
    .ranking-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #000000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    
    .ranking-card h1, .ranking-card h2, .ranking-card h3, .ranking-card h4, .ranking-card h5, .ranking-card h6 {
        color: #000000 !important;
        margin: 0.5rem 0;
    }
    
    .ranking-card p {
        color: #000000 !important;
    }
    
    .ranking-card small {
        color: #000000 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #ecf0f1;
        border-radius: 6px;
        padding: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 4px;
        padding: 12px 20px;
        border: 1px solid #000000;
        color: #000000;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #000000;
        border-color: #000000;
        font-weight: 600;
        border-bottom: 3px solid #2c3e50;
    }
    
    .stSelectbox > div > div {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
    }
    
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        border-radius: 4px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #000000;
        box-shadow: 0 0 0 2px rgba(31, 78, 121, 0.2);
    }
    
    /* Ensure all text on white backgrounds is dark */
    .main .block-container {
        color: #000000;
    }
    
    .stMarkdown {
        color: #000000;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #000000 !important;
    }
    
    .stMarkdown p {
        color: #000000 !important;
    }
    
    .stMarkdown strong {
        color: #000000 !important;
    }
    
    /* Fix Streamlit default dark theme text */
    .stApp {
        background-color: #ffffff;
    }
    
    .main .block-container {
        background-color: #ffffff;
        color: #000000 !important;
    }
    
    /* Fix sidebar text */
    .css-1d391kg {
        color: #000000 !important;
    }
    
    /* Fix all Streamlit text elements */
    .stText, .stMarkdown, .stSelectbox label, .stTextInput label {
        color: #000000 !important;
    }
    
    /* Fix section headings */
    .element-container h1, .element-container h2, .element-container h3, 
    .element-container h4, .element-container h5, .element-container h6 {
        color: #000000 !important;
    }
    
    /* Fix paragraph text */
    .element-container p {
        color: #000000 !important;
    }
    
    /* Fix form labels */
    .stTextInput > label, .stSelectbox > label, .stNumberInput > label {
        color: #000000 !important;
    }
    
    /* Force light theme and fix all text colors */
    .stApp > header {
        background-color: #ffffff;
    }
    
    .stApp > div > div {
        background-color: #ffffff;
    }
    
    /* Fix all possible text elements */
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    div[data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    
    /* Override Streamlit's default text colors */
    .stApp [data-testid="stMarkdownContainer"] {
        color: #000000 !important;
    }
    
    .stApp [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }
    
    .stApp [data-testid="stMarkdownContainer"] h1,
    .stApp [data-testid="stMarkdownContainer"] h2,
    .stApp [data-testid="stMarkdownContainer"] h3,
    .stApp [data-testid="stMarkdownContainer"] h4,
    .stApp [data-testid="stMarkdownContainer"] h5,
    .stApp [data-testid="stMarkdownContainer"] h6 {
        color: #000000 !important;
    }
    
    /* Fix sidebar content */
    .css-1d391kg, .css-1d391kg p, .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Updated MTWB Scoring System
MTWB_WEIGHTS = {
    "pe_score": 0.10,              # 15% - Valuation
    "volatility_score": 0.20,      # 15% - Risk management  
    "dividend_score": 0.20,        # 15% - Income generation
    "profit_score": 0.10,          # 15% - Profitability
    "roe_score": 0.10,             # 15% - Efficiency
    "growth_score": 0.10,          # 15% - Growth potential
    "esg_score": 0.20             # 10% - ESG (reduced from 25% to fit 100%)
}

# ESG weights (25% of total score)
ESG_WEIGHTS = {
    "esg_rating": 0.40,      # 40% of ESG score
    "carbon_targets": 0.35,  # 35% of ESG score
    "community": 0.25        # 25% of ESG score
}

ESG_RATING_SCORES = {
    "AAA": 100, "AA": 90, "A": 80, "BBB": 70, "BB": 60, "B": 50, "CCC": 30, "CC": 20, "C": 10
}

# Enhanced company data with more stocks and ETFs
COMPANIES = [
    "AAPL","MSFT","AMZN","GOOGL","META","TSLA","BRK-B","JNJ","V","JPM","PG","NVDA","HD","MA","DIS","UNH","VZ","NFLX",
    "PFE","KO","PEP","INTC","MRK","WMT","CSCO","NKE","XOM","BA","ABBV","CVX","COST","T","LLY","ORCL","MCD","ADBE","WFC",
    "IBM","MDT","HON","BMY","QCOM","C","TXN","ABT","CRM","UNP","GS","AMGN","CAT","GILD","AXP","LMT","MS","BKNG","ISRG",
    "CVS","DE","BLK","TMO","GE","UPS","LOW","AMAT","SPGI","PLD","USB","NOW","SCHW","VRTX","MO","NEE","RTX","PYPL","ADI",
    "COP","PM","MU","SO","DHR","MMC","SBUX","CI","BDX","MDLZ","ICE","ZTS","PNC","APD","DUK","REGN","CME","GM","F","TGT",
    "CL","EW","ETN","NSC","FDX","MRNA","ILMN","KMB","LRCX","EOG","MMM","CSX"
]

ETFS = [
    "ARKK","GRID","FAN","PAVE","TAN","PHO","PBW","IBB","DGRO","ESGU","ICLN","INDA","EWW","EWT","ITA","BBCA","XLU",
    "ESGV","VWO","VHT","VNQ","VTI","VT","VSS","VNQI","MSOS","IPO","JEPI","COWZ","LCTU","XLC","XLP","XLE","XLF","XLV",
    "XLI","RSP","ESGE","EWA","EWZ","MCHI","DSI","USMV","QUAL","ESGD","MOAT","VEU","VEA","VGK","VOO","VXUS","XLB","XLY",
    "QQQ","MTUM","IWF","XLK","SMH","VUG","VGT","IWD","NOBL","SCHD","VIG","VYM","VTV","IJH","VO","IJR","IWM","AVUV",
    "AGG","JPST","BSV","BND","BNDX","FTSL","HYLS","IGSB","FALN","HYG","LQD","JNK","VCIT","VCSH","SHY","TLT","IEF","EMB",
    "SHV","GOVT","BIL","VGSH","USFR","EMLC","VTIP","TIP","MBB","MUB","VTEB"
]

# Enhanced ESG data
ESG_DATA = {
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

# Add ESG data for ETFs (different scoring)
ETF_ESG_DATA = {
    "ESGU": {"esg_rating": "AA", "carbon_targets": 90, "community": 85, "community_initiatives": "ESG-focused investment, sustainable growth"},
    "ICLN": {"esg_rating": "AAA", "carbon_targets": 95, "community": 80, "community_initiatives": "Clean energy investment, environmental impact"},
    "ESGV": {"esg_rating": "AA", "carbon_targets": 85, "community": 80, "community_initiatives": "ESG value investing, responsible growth"},
    "VTI": {"esg_rating": "A", "carbon_targets": 70, "community": 75, "community_initiatives": "Broad market exposure, diversified impact"},
    "QQQ": {"esg_rating": "A", "carbon_targets": 75, "community": 70, "community_initiatives": "Technology sector focus, innovation"},
    "SCHD": {"esg_rating": "A", "carbon_targets": 60, "community": 80, "community_initiatives": "Dividend focus, income generation"},
    "VIG": {"esg_rating": "A", "carbon_targets": 65, "community": 85, "community_initiatives": "Dividend growth, sustainable income"},
    "AGG": {"esg_rating": "AA", "carbon_targets": 70, "community": 80, "community_initiatives": "Fixed income, stability focus"}
}

def get_esg_data(ticker, is_etf=False):
    """Get ESG data for a company or ETF"""
    if is_etf:
        if ticker in ETF_ESG_DATA:
            return ETF_ESG_DATA[ticker]
        else:
            return {
                "esg_rating": "A",
                "carbon_targets": 70,
                "community": 75,
                "community_initiatives": "Diversified investment approach"
            }
    else:
        if ticker in ESG_DATA:
            return ESG_DATA[ticker]
        else:
            return {
                "esg_rating": "BBB",
                "carbon_targets": 65,
                "community": 70,
                "community_initiatives": "Standard community engagement programs"
            }


def calculate_esg_score(ticker, is_etf=False):
    """Calculate ESG Score (0-25 points)"""
    esg_data = get_esg_data(ticker, is_etf)
    
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

def get_financial_data(ticker, is_etf=False):
    """Get comprehensive financial data"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Basic data
        pe_ratio = info.get("trailingPE", np.nan)
        beta = info.get("beta", np.nan)
        dividend_yield = (info.get("dividendYield", 0) or 0)  # Keep as decimal (0.04 = 4%)
        sector = info.get("sector", "ETF" if is_etf else "Unknown")
        profit_margin = (info.get("profitMargins", np.nan) or 0)  # Keep as decimal (0.15 = 15%)
        roe = (info.get("returnOnEquity", np.nan) or 0)  # Keep as decimal (0.12 = 12%)
        fiftytwo_wk_change = (info.get("52WeekChange", np.nan) or 0)  # Keep as decimal (0.25 = 25%)
        market_cap = info.get("marketCap", np.nan)
        current_price = info.get("currentPrice", np.nan)
        
        # ESG data
        esg_data = calculate_esg_score(ticker, is_etf)
        
        return {
            "ticker": ticker,
            "sector": sector,
            "current_price": current_price,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "beta": beta,
            "dividend_yield": dividend_yield,
            "profit_margin": profit_margin,
            "roe": roe,
            "fiftytwo_wk_change": fiftytwo_wk_change,
            "is_etf": is_etf,
            **esg_data
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

def calculate_mtwb_score(data):
    """Calculate comprehensive MTWB score"""
    if not data:
        return None
    
    # Extract values
    pe_ratio = data.get("pe_ratio", 0) or 0
    beta = data.get("beta", 1) or 1
    dividend_yield = data.get("dividend_yield", 0) or 0
    profit_margin = data.get("profit_margin", 0) or 0
    roe = data.get("roe", 0) or 0
    fiftytwo_wk_change = data.get("fiftytwo_wk_change", 0) or 0
    esg_score = data.get("esg_score", 12.5)
    
    # Calculate individual scores (0-100 scale)
    pe_score = max(0, min(100, 100 - (pe_ratio - 15) * 2)) if pe_ratio > 0 else 50
    volatility_score = max(0, min(100, 100 - beta * 40)) if beta > 0 else 50
    dividend_score = min(100, dividend_yield * 1500) if dividend_yield >= 0 else 50  # Scale for decimal (0.04 -> 60 points)
    profit_score = max(0, min(100, profit_margin * 100)) if profit_margin >= 0 else 50  # Scale for decimal (0.15 -> 15 points)
    roe_score = max(0, min(100, roe * 100)) if roe >= 0 else 50  # Scale for decimal (0.12 -> 12 points)
    growth_score = max(0, min(100, 50 + fiftytwo_wk_change * 100)) if fiftytwo_wk_change >= -0.5 else 50  # Scale for decimal (0.25 -> 25 points)
    
    # ESG score (0-25 points scaled to 0-100)
    esg_score_normalized = min(100, max(0, esg_score * 4))
    
    # Calculate weighted MTWB score
    mtwb_score = (
        pe_score * MTWB_WEIGHTS["pe_score"] +
        volatility_score * MTWB_WEIGHTS["volatility_score"] +
        dividend_score * MTWB_WEIGHTS["dividend_score"] +
        profit_score * MTWB_WEIGHTS["profit_score"] +
        roe_score * MTWB_WEIGHTS["roe_score"] +
        growth_score * MTWB_WEIGHTS["growth_score"] +
        esg_score_normalized * MTWB_WEIGHTS["esg_score"]
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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_top_rankings():
    """Get top 50 stocks and ETFs by MTWB score"""
    all_data = []
    
    # Get stock data
    for ticker in COMPANIES[:50]:  # Limit to first 50 for performance
        data = get_financial_data(ticker, False)
        if data:
            scores = calculate_mtwb_score(data)
            if scores:
                all_data.append({**data, **scores})
    
    # Get ETF data
    for ticker in ETFS[:30]:  # Limit to first 30 for performance
        data = get_financial_data(ticker, True)
        if data:
            scores = calculate_mtwb_score(data)
            if scores:
                all_data.append({**data, **scores})
    
    # Sort by MTWB score
    all_data.sort(key=lambda x: x['mtwb_score'], reverse=True)
    return all_data[:50]

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>MTWB Stock & ETF Evaluator</h1>
        <h3>Making the World Better Through Investment</h3>
        <p>Comprehensive analysis combining financial performance with ESG and community impact</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## MTWB Mission")
        st.markdown("""
        **Making the World Better** invests in Philadelphia communities through:
        - **$30M+ in capital improvements** to public spaces
        - **Multi-purpose parks and athletic fields**
        - **Community centers** with creative programs
        - **Deep community engagement** in every project
        """)
        
        st.markdown("---")
        st.markdown("## Strategic Vision")
        st.markdown("""
        *"Wharton made me think more about the sustainability of a nonprofit, and the importance of building strong partnerships to keep the work going."*
        
        - **NFL Veteran** → **Wharton MBA** (2023)
        - **Strategic Leadership** with systems-level thinking
        - **Emphasis on Sustainability** and lasting partnerships
        """)
        
        st.markdown("---")
        st.markdown("## MTWB Scoring System")
        st.markdown("""
        **Financial Metrics (90%)**
        - Growth Potential (15%)
        - Risk Management (15%)
        - Dividend Stability (15%)
        - Profitability (15%)
        - ROE Efficiency (15%)
        - Valuation (15%)
        
        **ESG & Community (10%)**
        - ESG Rating (4%)
        - Carbon Targets (3.5%)
        - Community Engagement (2.5%)
        """)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Individual Analysis", "Top 50 Rankings", "Market Overview"])
    
    with tab1:
        st.markdown("## Individual Stock & ETF Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input section
            st.markdown("### Enter Ticker Symbol")
            ticker_input = st.text_input(
                "Stock or ETF Ticker",
                placeholder="e.g., AAPL, MSFT, ESGU, VTI",
                help="Enter any valid stock or ETF ticker symbol"
            ).upper().strip()
            
            if ticker_input:
                with st.spinner(f"Analyzing {ticker_input}..."):
                    # Determine if it's an ETF
                    is_etf = ticker_input in ETFS
                    
                    # Get data
                    data = get_financial_data(ticker_input, is_etf)
                    
                    if data:
                        scores = calculate_mtwb_score(data)
                        
                        if scores:
                            # Main score display
                            st.markdown(f"""
                            <div class="metric-card">
                                <h2 style="color: #000000 !important;">MTWB Score: {scores['mtwb_score']}/100</h2>
                                <p style="color: #000000 !important;"><strong>{ticker_input}</strong> - {data['sector']} {'(ETF)' if is_etf else '(Stock)'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Detailed metrics
                            col_m1, col_m2 = st.columns(2)
                            
                            with col_m1:
                                st.metric("Current Price", f"${data['current_price']:.2f}" if not pd.isna(data['current_price']) else "N/A")
                                st.metric("Market Cap", f"${data['market_cap']/1e9:.1f}B" if not pd.isna(data['market_cap']) else "N/A")
                                st.metric("P/E Ratio", f"{data['pe_ratio']:.2f}" if not pd.isna(data['pe_ratio']) else "N/A")
                                st.metric("Beta (Risk)", f"{data['beta']:.2f}" if not pd.isna(data['beta']) else "N/A")
                            
                            with col_m2:
                                st.metric("Dividend Yield", f"{data['dividend_yield']:.4f}" if not pd.isna(data['dividend_yield']) else "N/A")
                                st.metric("Profit Margin", f"{data['profit_margin']:.4f}" if not pd.isna(data['profit_margin']) else "N/A")
                                st.metric("ROE", f"{data['roe']:.4f}" if not pd.isna(data['roe']) else "N/A")
                                st.metric("52W Change", f"{data['fiftytwo_wk_change']:.4f}" if not pd.isna(data['fiftytwo_wk_change']) else "N/A")
                            
                            # Score breakdown chart
                            score_data = {
                                'Metric': ['Growth', 'Risk Mgmt', 'Dividend', 'Profit', 'ROE', 'Valuation', 'ESG'],
                                'Score': [
                                    scores['growth_score'],
                                    scores['volatility_score'],
                                    scores['dividend_score'],
                                    scores['profit_score'],
                                    scores['roe_score'],
                                    scores['pe_score'],
                                    scores['esg_score_normalized']
                                ],
                                'Weight': [15, 15, 15, 15, 15, 15, 10]
                            }
                            
                            df_scores = pd.DataFrame(score_data)
                            
                            fig = px.bar(
                                df_scores,
                                x='Metric',
                                y='Score',
                                color='Score',
                                color_continuous_scale='RdYlGn',
                                title=f"MTWB Score Breakdown for {ticker_input}",
                                text='Score'
                            )
                            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                            fig.update_layout(height=500, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # ESG details
                            if not is_etf:
                                st.markdown(f"""
                                <div class="esg-card">
                                    <h3 style="color: #000000 !important;">ESG & Community Impact</h3>
                                    <p style="color: #000000 !important;"><strong>ESG Rating:</strong> {data['esg_rating']} | <strong>ESG Score:</strong> {data['esg_score']:.1f}/25</p>
                                    <p style="color: #000000 !important;"><strong>Carbon Targets:</strong> {data['carbon_targets']}/100 | <strong>Community Engagement:</strong> {data['community']}/100</p>
                                    <p style="color: #000000 !important;"><strong>Community Initiatives:</strong> {data['community_initiatives']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Investment recommendation
                            st.markdown("## MTWB Investment Perspective")
                            
                            if scores['mtwb_score'] >= 80:
                                st.success(f"**Excellent Match for MTWB**: {ticker_input} demonstrates exceptional alignment with MTWB's values of financial performance and community impact.")
                            elif scores['mtwb_score'] >= 65:
                                st.info(f"**Good Fit for MTWB**: {ticker_input} shows solid fundamentals with meaningful community engagement.")
                            elif scores['mtwb_score'] >= 50:
                                st.warning(f"**Moderate Fit**: {ticker_input} has mixed performance. Consider deeper ESG analysis.")
                            else:
                                st.error(f"**Poor Fit for MTWB**: {ticker_input} may not align with MTWB's mission of community impact.")
        
        with col2:
            st.markdown("## Top MTWB Aligned")
            
            # Quick top 10
            top_data = get_top_rankings()[:10]
            for i, item in enumerate(top_data):
                st.markdown(f"""
                <div class="ranking-card">
                    <strong>#{i+1} {item['ticker']}</strong><br>
                    <span style="color: #000000; font-size: 1.2em;">{item['mtwb_score']}/100</span><br>
                    <small>{item['sector']} {'(ETF)' if item['is_etf'] else '(Stock)'}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## Top 50 MTWB Rankings")
        
        # Get rankings
        rankings = get_top_rankings()
        
        if rankings:
            # Create DataFrame for display
            df_rankings = pd.DataFrame(rankings)
            
            # Display options
            col1, col2 = st.columns([1, 1])
            with col1:
                show_type = st.selectbox("Show", ["All", "Stocks Only", "ETFs Only"])
            with col2:
                num_display = st.slider("Number to display", 10, 50, 25)
            
            # Filter data
            if show_type == "Stocks Only":
                df_filtered = df_rankings[~df_rankings['is_etf']]
            elif show_type == "ETFs Only":
                df_filtered = df_rankings[df_rankings['is_etf']]
            else:
                df_filtered = df_rankings
            
            df_filtered = df_filtered.head(num_display)
            
            # Initialize session state for selected ticker
            if 'selected_ticker' not in st.session_state:
                st.session_state.selected_ticker = None
            
            # Display rankings with clickable functionality
            for idx, row in df_filtered.iterrows():
                rank = list(df_filtered.index).index(idx) + 1
                
                # Create clickable button for each ranking
                if st.button(f"#{rank} {row['ticker']} - {row['mtwb_score']}/100", 
                           key=f"rank_{rank}_{row['ticker']}", 
                           help=f"Click to view detailed analysis of {row['ticker']}",
                           use_container_width=True):
                    st.session_state.selected_ticker = row['ticker']
                
                # Show basic info
                st.markdown(f"""
                <div class="ranking-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>#{rank} {row['ticker']}</strong> - {row['sector']} {'(ETF)' if row['is_etf'] else '(Stock)'}<br>
                            <small>ESG: {row['esg_rating']} | Community: {row['community']}/100</small>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #000000; font-size: 1.5em; font-weight: bold;">{row['mtwb_score']}</span><br>
                            <small>/100</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Show detailed breakdown for selected ticker
            if st.session_state.selected_ticker:
                st.markdown("---")
                st.markdown(f"## Detailed Analysis: {st.session_state.selected_ticker}")
                
                # Find the selected ticker data
                selected_data = None
                for item in rankings:
                    if item['ticker'] == st.session_state.selected_ticker:
                        selected_data = item
                        break
                
                if selected_data:
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("### 📈 Financial Metrics")
                        # Format values properly
                        current_price = f"${selected_data.get('current_price', 0):.2f}" if selected_data.get('current_price') and not pd.isna(selected_data.get('current_price')) else "N/A"
                        market_cap = f"${selected_data.get('market_cap', 0)/1e9:.1f}B" if selected_data.get('market_cap') and not pd.isna(selected_data.get('market_cap')) else "N/A"
                        pe_ratio = f"{selected_data.get('pe_ratio', 0):.2f}" if selected_data.get('pe_ratio') and not pd.isna(selected_data.get('pe_ratio')) else "N/A"
                        beta = f"{selected_data.get('beta', 0):.2f}" if selected_data.get('beta') and not pd.isna(selected_data.get('beta')) else "N/A"
                        dividend_yield = f"{selected_data.get('dividend_yield', 0):.4f}"
                        profit_margin = f"{selected_data.get('profit_margin', 0):.4f}"
                        roe = f"{selected_data.get('roe', 0):.4f}"
                        fiftytwo_wk_change = f"{selected_data.get('fiftytwo_wk_change', 0):.4f}"
                        
                        st.markdown(f"""
                        <div class="metric-card" style="color: #000000 !important;">
                            <h4 style="color: #000000 !important;">Current Price: {current_price}</h4>
                            <h4 style="color: #000000 !important;">Market Cap: {market_cap}</h4>
                            <h4 style="color: #000000 !important;">P/E Ratio: {pe_ratio}</h4>
                            <h4 style="color: #000000 !important;">Beta (Risk): {beta}</h4>
                            <h4 style="color: #000000 !important;">Dividend Yield: {dividend_yield}</h4>
                            <h4 style="color: #000000 !important;">Profit Margin: {profit_margin}</h4>
                            <h4 style="color: #000000 !important;">ROE: {roe}</h4>
                            <h4 style="color: #000000 !important;">52W Change: {fiftytwo_wk_change}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if not selected_data.get('is_etf', False):
                            st.markdown("### ESG & Community")
                            st.markdown(f"""
                            <div class="esg-card" style="color: #000000 !important;">
                                <h4 style="color: #000000 !important;">ESG Rating: {selected_data.get('esg_rating', 'N/A')}</h4>
                                <h4 style="color: #000000 !important;">ESG Score: {selected_data.get('esg_score', 0):.1f}/25</h4>
                                <h4 style="color: #000000 !important;">Carbon Targets: {selected_data.get('carbon_targets', 0)}/100</h4>
                                <h4 style="color: #000000 !important;">Community: {selected_data.get('community', 0)}/100</h4>
                                <p style="color: #000000 !important;"><strong>Initiatives:</strong> {selected_data.get('community_initiatives', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("### MTWB Score Breakdown")
                        
                        # Create detailed breakdown
                        breakdown_data = {
                            'Metric': ['Growth Potential', 'Risk Management', 'Dividend Stability', 'Profitability', 'ROE Efficiency', 'Valuation', 'ESG & Community'],
                            'Weight (%)': [15, 15, 15, 15, 15, 15, 10],
                            'Score': [
                                selected_data.get('growth_score', 0),
                                selected_data.get('volatility_score', 0),
                                selected_data.get('dividend_score', 0),
                                selected_data.get('profit_score', 0),
                                selected_data.get('roe_score', 0),
                                selected_data.get('pe_score', 0),
                                selected_data.get('esg_score_normalized', 0)
                            ],
                            'Weighted Contribution': [
                                round(selected_data.get('growth_score', 0) * 0.15, 1),
                                round(selected_data.get('volatility_score', 0) * 0.15, 1),
                                round(selected_data.get('dividend_score', 0) * 0.15, 1),
                                round(selected_data.get('profit_score', 0) * 0.15, 1),
                                round(selected_data.get('roe_score', 0) * 0.15, 1),
                                round(selected_data.get('pe_score', 0) * 0.15, 1),
                                round(selected_data.get('esg_score_normalized', 0) * 0.10, 1)
                            ]
                        }
                        
                        df_breakdown = pd.DataFrame(breakdown_data)
                        
                        # Display breakdown table
                        st.dataframe(df_breakdown, use_container_width=True)
                        
                        # Create visualization
                        fig_breakdown = px.bar(
                            df_breakdown,
                            x='Metric',
                            y='Score',
                            color='Weight (%)',
                            color_continuous_scale='RdYlGn',
                            title=f"MTWB Score Components for {st.session_state.selected_ticker}",
                            text='Score',
                            hover_data=['Weight (%)', 'Weighted Contribution']
                        )
                        fig_breakdown.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                        fig_breakdown.update_layout(height=500, showlegend=False)
                        st.plotly_chart(fig_breakdown, use_container_width=True)
                        
                        # Summary
                        total_score = sum(breakdown_data['Weighted Contribution'])
                        st.markdown(f"""
                        <div class="metric-card" style="color: #000000 !important;">
                            <h3 style="color: #000000 !important;">Total MTWB Score: {total_score:.1f}/100</h3>
                            <p style="color: #000000 !important;"><strong>Rank:</strong> #{rank} out of 50</p>
                            <p style="color: #000000 !important;"><strong>Category:</strong> {selected_data['sector']} {'(ETF)' if selected_data.get('is_etf', False) else '(Stock)'}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Summary statistics
            st.markdown("## Ranking Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average MTWB Score", f"{df_filtered['mtwb_score'].mean():.1f}")
            with col2:
                st.metric("Top Score", f"{df_filtered['mtwb_score'].max():.1f}")
            with col3:
                st.metric("ESG Leaders (AA+)", f"{len(df_filtered[df_filtered['esg_rating'].isin(['AAA', 'AA'])])}")
    
    with tab3:
        st.markdown("## Market Overview")
        
        # Sector analysis
        rankings = get_top_rankings()
        if rankings:
            df = pd.DataFrame(rankings)
            
            # Sector distribution
            sector_counts = df['sector'].value_counts().head(10)
            
            fig_sector = px.pie(
                values=sector_counts.values,
                names=sector_counts.index,
                title="Top 50 Distribution by Sector"
            )
            st.plotly_chart(fig_sector, use_container_width=True)
            
            # Score distribution
            fig_dist = px.histogram(
                df,
                x='mtwb_score',
                nbins=20,
                title="MTWB Score Distribution",
                labels={'mtwb_score': 'MTWB Score', 'count': 'Number of Securities'}
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # ESG vs Performance
            fig_scatter = px.scatter(
                df,
                x='esg_score',
                y='mtwb_score',
                color='is_etf',
                title="ESG Score vs MTWB Score",
                labels={'esg_score': 'ESG Score', 'mtwb_score': 'MTWB Score'},
                hover_data=['ticker', 'sector']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

if __name__ == "__main__":
    main()
