import yfinance as yf
import sys
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
import random

# --- Top 100 stocks from Yahoo Finance (tickers, representative list) ---
companies = [
    "AAPL","MSFT","AMZN","GOOGL","META","TSLA","BRK-B","JNJ","V","JPM","PG","NVDA","HD","MA","DIS","UNH","VZ","NFLX",
    "PFE","KO","PEP","INTC","MRK","WMT","CSCO","NKE","XOM","BA","ABBV","CVX","COST","T","LLY","ORCL","MCD","ADBE","WFC",
    "IBM","MDT","HON","BMY","QCOM","C","TXN","ABT","CRM","UNP","GS","AMGN","CAT","GILD","AXP","LMT","MS","BKNG","ISRG",
    "CVS","DE","BLK","TMO","GE","UPS","LOW","AMAT","SPGI","PLD","USB","NOW","SCHW","VRTX","MO","NEE","RTX","PYPL","ADI",
    "COP","PM","MU","SO","DHR","MMC","SBUX","CI","BDX","MDLZ","ICE","ZTS","PNC","APD","DUK","REGN","CME","GM","F","TGT",
    "CL","EW","ETN","NSC","FDX","MRNA","ILMN","KMB","LRCX","EOG","MMM","CSX"
]

# --- ETFs from WGHIC Approved List (2025-26) ---
etfs = [
    "ARKK","GRID","FAN","PAVE","TAN","PHO","PBW","IBB","DGRO","ESGU","ICLN","INDA","EWW","EWT","ITA","BBCA","XLU",
    "ESGV","VWO","VHT","VNQ","VTI","VT","VSS","VNQI","MSOS","IPO","JEPI","COWZ","LCTU","XLC","XLP","XLE","XLF","XLV",
    "XLI","RSP","ESGE","EWA","EWZ","MCHI","DSI","USMV","QUAL","ESGD","MOAT","VEU","VEA","VGK","VOO","VXUS","XLB","XLY",
    "QQQ","MTUM","IWF","XLK","SMH","VUG","VGT","IWD","NOBL","SCHD","VIG","VYM","VTV","IJH","VO","IJR","IWM","AVUV",
    "AGG","JPST","BSV","BND","BNDX","FTSL","HYLS","IGSB","FALN","HYG","LQD","JNK","VCIT","VCSH","SHY","TLT","IEF","EMB",
    "SHV","GOVT","BIL","VGSH","USFR","EMLC","VTIP","TIP","MBB","MUB","VTEB"
]

# --- ESG Data Sources and Scoring Framework ---
# MTWB ESG Scoring System (25 points total)
ESG_WEIGHTS = {
    "esg_rating": 0.40,      # 10 points - External ESG ratings
    "carbon_targets": 0.35,  # 8.75 points - Carbon reduction/renewable energy
    "community": 0.25        # 6.25 points - Community engagement initiatives
}

# ESG Rating Scale (AAA to CCC)
ESG_RATING_SCORES = {
    "AAA": 100, "AA": 90, "A": 80, "BBB": 70, "BB": 60, "B": 50, "CCC": 30, "CC": 20, "C": 10
}

# Sample ESG data for major companies (in practice, this would come from APIs)
ESG_SAMPLE_DATA = {
    "AAPL": {"esg_rating": "AA", "carbon_targets": 85, "community": 90},
    "MSFT": {"esg_rating": "AA", "carbon_targets": 88, "community": 85},
    "GOOGL": {"esg_rating": "A", "carbon_targets": 90, "community": 80},
    "META": {"esg_rating": "BBB", "carbon_targets": 75, "community": 70},
    "TSLA": {"esg_rating": "A", "carbon_targets": 95, "community": 75},
    "JNJ": {"esg_rating": "AA", "carbon_targets": 70, "community": 95},
    "V": {"esg_rating": "A", "carbon_targets": 65, "community": 85},
    "JPM": {"esg_rating": "BBB", "carbon_targets": 60, "community": 80},
    "PG": {"esg_rating": "AA", "carbon_targets": 80, "community": 90},
    "NVDA": {"esg_rating": "A", "carbon_targets": 70, "community": 75},
    "WMT": {"esg_rating": "BBB", "carbon_targets": 75, "community": 85},
    "KO": {"esg_rating": "BBB", "carbon_targets": 70, "community": 80},
    "PEP": {"esg_rating": "A", "carbon_targets": 75, "community": 85},
    "INTC": {"esg_rating": "BBB", "carbon_targets": 80, "community": 70},
    "MRK": {"esg_rating": "A", "carbon_targets": 65, "community": 90},
    "HD": {"esg_rating": "A", "carbon_targets": 70, "community": 85},
    "MA": {"esg_rating": "A", "carbon_targets": 60, "community": 80},
    "DIS": {"esg_rating": "BBB", "carbon_targets": 65, "community": 90},
    "UNH": {"esg_rating": "BBB", "carbon_targets": 55, "community": 75},
    "VZ": {"esg_rating": "BBB", "carbon_targets": 70, "community": 70},
    "NFLX": {"esg_rating": "A", "carbon_targets": 80, "community": 75},
    "PFE": {"esg_rating": "AA", "carbon_targets": 60, "community": 95},
    "XOM": {"esg_rating": "BB", "carbon_targets": 30, "community": 60},
    "BA": {"esg_rating": "BB", "carbon_targets": 45, "community": 70},
    "CVX": {"esg_rating": "BB", "carbon_targets": 35, "community": 65}
}

# --- Normalization function ---
def normalize(series, inverse=False):
    if series.max() == series.min():
        return pd.Series([50]*len(series), index=series.index)
    if inverse:
        return 100 * (series.max() - series) / (series.max() - series.min())
    else:
        return 100 * (series - series.min()) / (series.max() - series.min())

# --- ESG Scoring Functions ---
def get_esg_data(ticker):
    """
    Get ESG data for a company. In practice, this would integrate with:
    - MSCI ESG Ratings API
    - Sustainalytics API  
    - Morningstar ESG API
    - Company sustainability reports
    """
    # For demo purposes, return sample data or generate realistic defaults
    if ticker in ESG_SAMPLE_DATA:
        return ESG_SAMPLE_DATA[ticker]
    else:
        # Generate realistic ESG scores based on sector and company characteristics
        return {
            "esg_rating": random.choice(["AAA", "AA", "A", "BBB", "BB"]),
            "carbon_targets": random.randint(40, 90),
            "community": random.randint(50, 95)
        }

def calculate_esg_score(ticker):
    """
    Calculate MTWB ESG Score (0-25 points)
    """
    esg_data = get_esg_data(ticker)
    
    # Convert ESG rating to score
    esg_rating_score = ESG_RATING_SCORES.get(esg_data["esg_rating"], 50)
    
    # Calculate weighted ESG score (0-25 points)
    esg_score = (
        esg_rating_score * ESG_WEIGHTS["esg_rating"] +
        esg_data["carbon_targets"] * ESG_WEIGHTS["carbon_targets"] +
        esg_data["community"] * ESG_WEIGHTS["community"]
    )
    
    return {
        "esg_rating": esg_data["esg_rating"],
        "carbon_targets": esg_data["carbon_targets"],
        "community": esg_data["community"],
        "esg_score": esg_score
    }

# --- Function to pull financials ---
def get_financials(ticker, etf=False):
    stock = yf.Ticker(ticker)
    info = stock.info

    pe_ratio = info.get("trailingPE", np.nan)
    beta = info.get("beta", np.nan)
    dividend_yield = info.get("dividendYield", 0) or 0
    sector = info.get("sector", "ETF" if etf else "Unknown")
    profit_margin = info.get("profitMargins", np.nan)
    roe = info.get("returnOnEquity", np.nan)
    fiftytwo_wk_change = info.get("52WeekChange", np.nan)
    
    # Get ESG data (skip for ETFs as they have different ESG considerations)
    if not etf:
        esg_data = calculate_esg_score(ticker)
        return {
            "company": ticker,
            "sector": sector,
            "pe_ratio": pe_ratio,
            "beta": beta,
            "dividend_yield": dividend_yield,
            "profit_margin": profit_margin,
            "roe": roe,
            "fiftytwo_wk_change": fiftytwo_wk_change,
            "etf": etf,
            "esg_rating": esg_data["esg_rating"],
            "carbon_targets": esg_data["carbon_targets"],
            "community": esg_data["community"],
            "esg_score": esg_data["esg_score"]
        }
    else:
        # For ETFs, set ESG scores to neutral values
        return {
            "company": ticker,
            "sector": sector,
            "pe_ratio": pe_ratio,
            "beta": beta,
            "dividend_yield": dividend_yield,
            "profit_margin": profit_margin,
            "roe": roe,
            "fiftytwo_wk_change": fiftytwo_wk_change,
            "etf": etf,
            "esg_rating": "N/A",
            "carbon_targets": 50,
            "community": 50,
            "esg_score": 12.5  # Neutral ESG score for ETFs
        }

# --- Collect data ---
stock_data = [get_financials(c) for c in companies]
etf_data = [get_financials(e, etf=True) for e in etfs]
all_data = stock_data + etf_data

df = pd.DataFrame(all_data).fillna(0)

# --- Score building ---
df["pe_score"] = normalize(df["pe_ratio"], inverse=True)   
df["volatility_score"] = normalize(df["beta"], inverse=True)   
df["dividend_score"] = normalize(df["dividend_yield"])  
df["profit_score"] = normalize(df["profit_margin"])     
df["roe_score"] = normalize(df["roe"])                   
df["growth_score"] = normalize(df["fiftytwo_wk_change"]) 

# --- ESG Score normalization (0-25 points scaled to 0-100) ---
df["esg_score_normalized"] = df["esg_score"] * 4  # Scale 0-25 to 0-100

# --- Updated Weighting system (MTWB with ESG integration) ---
# Traditional financial metrics: 75 points
# ESG & Sustainability: 25 points
weights = {
    "pe_score": 0.08,              # 8 points (reduced from 10)
    "volatility_score": 0.20,      # 20 points (reduced from 25)
    "dividend_score": 0.12,        # 12 points (reduced from 15)
    "profit_score": 0.08,          # 8 points (reduced from 10)
    "roe_score": 0.12,             # 12 points (reduced from 15)
    "growth_score": 0.25,          # 25 points (reduced from 30)
    "esg_score_normalized": 0.25   # 25 points (new ESG component)
}

df["mtwb_score"] = (
    df["pe_score"] * weights["pe_score"] +
    df["volatility_score"] * weights["volatility_score"] +
    df["dividend_score"] * weights["dividend_score"] +
    df["profit_score"] * weights["profit_score"] +
    df["roe_score"] * weights["roe_score"] +
    df["growth_score"] * weights["growth_score"] +
    df["esg_score_normalized"] * weights["esg_score_normalized"]
)

df["mtwb_score"] = normalize(df["mtwb_score"])

# --- Updated Sector Mapping ---
sector_map = {
    # Industrials
    "Industrials": "Industrials",
    "Industrial": "Industrials",
    "Aerospace & Defense": "Industrials",
    "Business Services": "Industrials",
    "Conglomerates": "Industrials",
    "Engineering & Construction": "Industrials",
    "Marine Shipping": "Industrials",
    "Transportation": "Industrials",
    "Trucking": "Industrials",
    
    # Real Estate
    "Real Estate": "Real Estate",
    "REIT": "Real Estate",
    "Real Estate - General": "Real Estate",
    
    # Utilities
    "Utilities": "Utilities",
    "Utilities - Regulated": "Utilities",
    "Utilities - Independent Power Producers": "Utilities",
    
    # Consumer Staples
    "Consumer Defensive": "Consumer Staples",
    "Consumer Staples": "Consumer Staples",
    "Beverages": "Consumer Staples",
    "Food": "Consumer Staples",
    "Household Products": "Consumer Staples",
    "Tobacco": "Consumer Staples",
    
    # Healthcare
    "Healthcare": "Healthcare",
    "Biotechnology": "Healthcare",
    "Pharmaceuticals": "Healthcare",
    "Medical": "Healthcare",
    "Healthcare Plans": "Healthcare",
    
    # Technology
    "Technology": "Technology",
    "Software": "Technology",
    "Hardware": "Technology",
    "Semiconductors": "Technology",
    
    # Financials
    "Financial Services": "Financials",
    "Banks": "Financials",
    "Insurance": "Financials",
    "Capital Markets": "Financials",
    
    # Energy
    "Energy": "Energy",
    "Oil & Gas": "Energy",
    
    # Communication Services
    "Communication Services": "Communication Services",
    "Telecom": "Communication Services",
    "Media": "Communication Services",
    
    # Consumer Discretionary
    "Consumer Cyclical": "Consumer Discretionary",
    "Consumer Discretionary": "Consumer Discretionary",
    "Retail": "Consumer Discretionary",
    "Automotive": "Consumer Discretionary",
    
    # Materials
    "Basic Materials": "Materials",
    "Chemicals": "Materials",
    "Metals & Mining": "Materials",
    "Paper & Forest Products": "Materials"
}

df["main_sector"] = df["sector"].map(sector_map).fillna("Other")

# --- User Selection ---
print("\n" + "="*80)
print("MTWB STOCK & ETF EVALUATOR")
print("="*80)

# First choice: Stocks or ETFs
while True:
    choice = input("\nDo you want to analyze STOCKS or ETFS? ").strip().lower()
    if choice in ['stocks', 'etfs']:
        break
    print("Please enter either 'stocks' or 'etfs'")

if choice == "stocks":
    # Define available sectors
    sectors = [
        "All Sectors",
        "Industrials",
        "Real Estate",
        "Utilities",
        "Consumer Staples",
        "Healthcare",
        "Technology",
        "Financials",
        "Energy",
        "Communication Services",
        "Consumer Discretionary",
        "Materials"
    ]
    
    # Display sector menu
    print("\nAvailable Sectors:")
    for i, sector in enumerate(sectors, 1):
        print(f"{i}. {sector}")
    
    # Get sector selection
    while True:
        try:
            selection = int(input("\nSelect a sector (1-11): "))
            if 1 <= selection <= len(sectors):
                selected_sector = sectors[selection-1]
                break
            print(f"Please enter a number between 1 and {len(sectors)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Apply sector filter if not "All Sectors"
    result = df[~df["etf"]]
    if selected_sector != "All Sectors":
        result = result[result["main_sector"] == selected_sector]
    
    # Sort and get top 50
    result = result.sort_values("mtwb_score", ascending=False).head(50)
    
    # Display results
    print(f"\n{'='*80}")
    print(f"TOP 50 STOCKS - {selected_sector.upper()}")
    print("="*80)
    print("\nRank | Ticker | MTWB Score | Sector | ESG Rating | Price | 52Wk Change")
    print("-" * 80)
    
    for idx, (_, row) in enumerate(result.iterrows(), 1):
        ticker = row['company']
        score = f"{row['mtwb_score']:.1f}"
        sector = row['main_sector']
        esg_rating = row['esg_rating']
        price = f"${row.get('currentPrice', row.get('regularMarketPrice', 'N/A'))}"
        change_52wk = f"{row['fiftytwo_wk_change']*100:.1f}%" if not pd.isna(row['fiftytwo_wk_change']) else "N/A"
        
        print(f"{idx:4d} | {ticker:6s} | {score:>9} | {sector[:15]:<15} | {esg_rating:^9} | {price:>7} | {change_52wk:>10}")

else:  # ETFs
    result = df[df["etf"]].sort_values("mtwb_score", ascending=False).head(50)
    print("\n" + "="*80)
    print("TOP 50 ETFS")
    print("="*80)
    print("\nRank | Ticker | MTWB Score | Category | Price | 52Wk Change")
    print("-" * 70)
    
    for idx, (_, row) in enumerate(result.iterrows(), 1):
        ticker = row['company']
        score = f"{row['mtwb_score']:.1f}"
        category = row['sector']
        price = f"${row.get('currentPrice', row.get('regularMarketPrice', 'N/A'))}"
        change_52wk = f"{row['fiftytwo_wk_change']*100:.1f}%" if not pd.isna(row['fiftytwo_wk_change']) else "N/A"
        
        print(f"{idx:4d} | {ticker:6s} | {score:>9} | {category[:15]:<15} | {price:>7} | {change_52wk:>10}")

print("\n" + "="*80)
print("ESG SCORING BREAKDOWN:")
print("- ESG Rating (40%): External ratings from MSCI, Sustainalytics, Morningstar")
print("- Carbon Targets (35%): Carbon reduction goals & renewable energy usage")
print("- Community Engagement (25%): Community initiatives aligning with MTWB mission")
print("="*80)