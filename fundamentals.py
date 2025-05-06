import pandas as pd
import requests

# Your Polygon.io API key
API_KEY = "U7HWXx__jVzv4pz7p_wQKavhoXMoNshK"

# Function to fetch fundamental data for a given ticker
def fetch_fundamentals_data(ticker):
    url = f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&timeframe=quarterly&apiKey={API_KEY}"  # Use vX

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        print("\n🔹 **DEBUG: API Request Sent** 🔹")
        print(f"Request URL: {url}")
        print(f"Status Code: {response.status_code}")

        # Print raw response (for debugging)
        print("\n🔹 **DEBUG: Raw API Response** 🔹")
        print(response.text)

        response.raise_for_status()  # Raise HTTPError for bad responses

        # Parse JSON response
        data = response.json()

        if "results" in data and data["results"]:
            print(f"✅ Successfully fetched fundamentals data for {ticker}")
            return data["results"]
        else:
            print(f"⚠️ No fundamentals data found for {ticker}.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")
        return None

# Convert the response to a DataFrame
def convert_fundamentals_to_dataframe(data):
    if not data:
        print("No data to convert.")
        return None

    # Extract relevant fields from the response
    records = []
    for item in data:
        financials = item.get("financials", {})

        # Income Statement
        income_statement = financials.get("income_statement", {})
        balance_sheet = financials.get("balance_sheet", {})
        cash_flow_statement = financials.get("cash_flow_statement", {})

        records.append({
            "Start Date": item.get("start_date"),
            "End Date": item.get("end_date"),
            "Revenue": income_statement.get("revenues", {}).get("value"),
            "Net Income": income_statement.get("net_income_loss", {}).get("value"),
            "Operating Income": income_statement.get("operating_income_loss", {}).get("value"),
            "EPS": income_statement.get("basic_earnings_per_share", {}).get("value"),
            "Total Assets": balance_sheet.get("assets", {}).get("value"),
            "Total Liabilities": balance_sheet.get("liabilities", {}).get("value"),
            "Equity": balance_sheet.get("equity", {}).get("value"),
            "Operating Cash Flow": cash_flow_statement.get("net_cash_flow_from_operating_activities", {}).get("value"),
            "Total Net Cash Flow": cash_flow_statement.get("net_cash_flow", {}).get("value")
        })

    # Convert to a DataFrame
    df = pd.DataFrame(records)
    return df

# Example usage
if __name__ == "__main__":
    ticker_symbol = input("Enter the ticker symbol (e.g., AAPL): ")

    raw_data = fetch_fundamentals_data(ticker_symbol)
    df = convert_fundamentals_to_dataframe(raw_data)

    if df is not None:
        print("✅ DataFrame created successfully!")
        print(df.head())  # Display the first few rows of the DataFrame

df.to_csv("/Users/elvin/Desktop/fundamentals_data.csv", index=False)  # Save as CSV