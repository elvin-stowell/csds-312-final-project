import pandas as pd
import requests
import time
import random

# Your Polygon.io API key
API_KEY = "4tSHWspzMP5cotx5fmZpD37b4CWsNm8G"
URL = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&limit=1000&apiKey={API_KEY}"


def fetch_all_tickers():
    all_tickers = []
    url = "https://api.polygon.io/v3/reference/tickers"
    params = {
        "market": "stocks",
        "active": "true",
        "limit": 1000,
        "apiKey": API_KEY
    }

    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract tickers
        tickers = [item["ticker"] for item in data.get("results", [])]
        all_tickers.extend(tickers)

        # Check for next page
        url = data.get("next_url")  # Polygon provides a `next_url` for pagination

    return all_tickers


# Fetch list of tickers
# response = requests.get(URL)
# data = response.json()
# TICKERS = [item["ticker"] for item in data.get("results", [])][1000:]

all_tickers = fetch_all_tickers()  # Fetch all available tickers
TICKERS = all_tickers[2000:30000]  # Get tickers from ____

# # Shuffle tickers to change processing order
# random.shuffle(TICKERS)

# Define time range for stock price data
START_DATE = "2020-03-02"
END_DATE = "2025-02-28"

# Function to split tickers into batches of 100
def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# # Function to fetch fundamental data
# def fetch_fundamentals_data(ticker):
#     url = f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&timeframe=quarterly&apiKey={API_KEY}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         return data.get("results", None)
#     except requests.exceptions.RequestException:
#         return None

def fetch_fundamentals_data(ticker):
    # Fetch market cap separately to filter companies under $1B
    market_cap = fetch_market_cap(ticker)
    if market_cap is None or market_cap < 500_000_000:
        print(f"⚠️ {ticker} market cap under $500M. Skipping data collection.")
        return None
    url = f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&timeframe=quarterly&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("results", None)
    except requests.exceptions.RequestException:
        return None

# Function to fetch historical stock price data
def fetch_market_cap(ticker):
    url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("results", {}).get("market_cap", None)
    except requests.exceptions.RequestException:
        return None

# Function to fetch historical stock price data
def fetch_stock_price_data(ticker, start_date, end_date):
    market_cap = fetch_market_cap(ticker)
    if market_cap is None or market_cap < 500_000_000:
        print(f"⚠️ {ticker} market cap under $500M. Skipping data collection.")
        return None
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?limit=5000&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("results", None)
    except requests.exceptions.RequestException:
        return None

# Convert fundamentals data to DataFrame
def convert_fundamentals_to_dataframe(data, ticker):
    if not data:
        return None
    market_cap = fetch_market_cap(ticker)
    records = []
    for item in data:
        financials = item.get("financials", {})

        records.append({
            "Ticker": ticker,
            "Start Date": item.get("start_date"),
            "End Date": item.get("end_date"),
            "Filing Date": item.get("filing_date"),
            "Revenue": financials.get("income_statement", {}).get("revenues", {}).get("value"),
            "Net Income": financials.get("income_statement", {}).get("net_income_loss", {}).get("value"),
            "Operating Income": financials.get("income_statement", {}).get("operating_income_loss", {}).get("value"),
            "EPS": financials.get("income_statement", {}).get("basic_earnings_per_share", {}).get("value"),
            "Total Assets": financials.get("balance_sheet", {}).get("assets", {}).get("value"),
            "Total Liabilities": financials.get("balance_sheet", {}).get("liabilities", {}).get("value"),
            "Equity": financials.get("balance_sheet", {}).get("equity", {}).get("value"),
            "Market Cap": market_cap,
            "Operating Cash Flow": financials.get("cash_flow_statement", {}).get(
                "net_cash_flow_from_operating_activities", {}).get("value"),
            "Total Net Cash Flow": financials.get("cash_flow_statement", {}).get("net_cash_flow", {}).get("value")
        })

    return pd.DataFrame(records)

# Convert stock price data to DataFrame
def convert_price_to_dataframe(data, ticker):
    if not data:
        return None

    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['t'], unit='ms')  # Convert Unix timestamp to datetime

    df.rename(columns={
        'v': 'Volume',
        'vw': 'Volume Weighted Price',
        'o': 'Open Price',
        'c': 'Close Price',
        'h': 'High Price',
        'l': 'Low Price',
        't': 'Date',
        'n': 'Number of Trades'
    }, inplace=True)

    df["Ticker"] = ticker  # Add ticker column

    return df

# Loop through ticker batches of 100
batch_number = 21
for batch in chunk_list(TICKERS, 100):
    print(f"🚀 Processing Batch {batch_number} ({len(batch)} tickers)...")

    # Initialize empty DataFrames for each batch
    batch_price_data = pd.DataFrame()
    batch_fundamentals_data = pd.DataFrame()

    # Process each ticker in the batch
    for ticker in batch:
        print(f"Fetching data for {ticker}...")

        # Fetch fundamentals data
        raw_fundamentals = fetch_fundamentals_data(ticker)
        df_fundamentals = convert_fundamentals_to_dataframe(raw_fundamentals, ticker)

        if df_fundamentals is not None:
            batch_fundamentals_data = pd.concat([batch_fundamentals_data, df_fundamentals], ignore_index=True)
            print(f"✅ {ticker} Fundamentals added!")

        # Fetch stock price data
        raw_price_data = fetch_stock_price_data(ticker, START_DATE, END_DATE)
        df_price = convert_price_to_dataframe(raw_price_data, ticker)

        try:
            if df_price is not None:
                df_price = df_price.reset_index(drop=True)  # Ensure unique index before merging
                batch_price_data = pd.concat([batch_price_data, df_price], ignore_index=True)
                print(f"✅ {ticker} Price data added!")
        except Exception as e:
            print(f"❌ Skipping {ticker} due to error during concatenation: {e}")
            continue  # Skip the ticker and move to the next one

        # if df_price is not None:
        #     # df_price = df_price.reset_index(drop=True)  # Ensure unique index before merging
        #     batch_price_data = pd.concat([batch_price_data, df_price], ignore_index=True)
        #     print(f"✅ {ticker} Price data added!")

        # Pause to avoid rate limits
        time.sleep(1)

    # Save batch data after every 100 tickers
    if not batch_fundamentals_data.empty:
        batch_fundamentals_data.to_csv(f"/Users/elvin/Desktop/Data/fundamentals_batch_{batch_number}.csv", index=False)
        print(f"📂 Batch {batch_number} Fundamentals data saved!")

    if not batch_price_data.empty:
        batch_price_data.to_csv(f"/Users/elvin/Desktop/Data/price_batch_{batch_number}.csv", index=False)
        print(f"📂 Batch {batch_number} Price data saved!")

    print(f"✅ Batch {batch_number} processing complete!\n")
    batch_number += 1
    time.sleep(5)

print("🎉 All data collection complete!")
