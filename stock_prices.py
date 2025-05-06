import pandas as pd
import requests

# Input your Polygon.io API key here
API_KEY = "4tSHWspzMP5cotx5fmZpD37b4CWsNm8G"


# Function to fetch historical stock price data
def fetch_historical_stock_data(ticker, start_date, end_date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
    params = {
        "apiKey": API_KEY,
        "limit": 5000  # Adjust based on expected number of results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", None) if "results" in data else None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching price data for {ticker}: {e}")
        return None


# Function to fetch market cap for a given ticker
def fetch_market_cap(ticker):
    url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract market cap
        return data.get("results", {}).get("market_cap", None)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching market cap for {ticker}: {e}")
        return None


# Convert stock data to DataFrame and add market cap
def convert_to_dataframe(data, ticker):
    if not data:
        print("No stock data to convert.")
        return None

    df = pd.DataFrame(data)
    df['t'] = pd.to_datetime(df['t'], unit='ms')

    # Rename columns
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

    # Fetch market cap and apply it to all rows
    market_cap = fetch_market_cap(ticker)
    df["Market Cap"] = market_cap

    return df


# Example usage
if __name__ == "__main__":
    ticker_symbol = input("Enter the ticker symbol (e.g., AAPL): ")
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")

    raw_data = fetch_historical_stock_data(ticker_symbol, start_date, end_date)
    df = convert_to_dataframe(raw_data, ticker_symbol)

    if df is not None:
        print("✅ DataFrame created successfully!")
        print(df.head())
        df.to_csv("/Users/elvin/Desktop/stock_data.csv", index=False)
        print("📂 Data saved to /Users/elvin/Desktop/stock_data.csv")
