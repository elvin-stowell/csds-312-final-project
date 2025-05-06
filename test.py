import pandas as pd
import requests

# Input your Polygon.io API key here
API_KEY = "U7HWXx__jVzv4pz7p_wQKavhoXMoNshK"

# Function to fetch historical data for a given ticker
def fetch_historical_stock_data(ticker, start_date, end_date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
    params = {
        "apiKey": API_KEY
    }

    try:
        # Make the request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Parse the JSON response
        data = response.json()
        if "results" in data:
            print(f"Successfully fetched data for {ticker}")
            return data["results"]
        else:
            print(f"No data found for {ticker} in the specified date range.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Convert the response to a DataFrame
def convert_to_dataframe(data):
    if not data:
        print("No data to convert.")
        return None

    # Convert to a DataFrame
    df = pd.DataFrame(data)

    # Convert the timestamp to a readable date
    df['t'] = pd.to_datetime(df['t'], unit='ms')  # Convert Unix timestamp to datetime

    # Rename columns for clarity (optional)
    df = df.rename(columns={
        'v': 'Volume',
        'vw': 'Volume Weighted Price',
        'o': 'Open Price',
        'c': 'Close Price',
        'h': 'High Price',
        'l': 'Low Price',
        't': 'Date',
        'n': 'Number of Trades'
    })

    return df

# Example usage
if __name__ == "__main__":
    ticker_symbol = input("Enter the ticker symbol (e.g., AAPL): ")
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")

    raw_data = fetch_historical_stock_data(ticker_symbol, start_date, end_date)
    df = convert_to_dataframe(raw_data)

    if df is not None:
        print("DataFrame created successfully!")
        print(df.head())  # Display the first few rows of the DataFrame
