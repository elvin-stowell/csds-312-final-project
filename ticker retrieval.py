import requests
import pandas as pd

API_KEY = "4tSHWspzMP5cotx5fmZpD37b4CWsNm8G"
URL = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&limit=1000&apiKey={API_KEY}"

response = requests.get(URL)
data = response.json()

# Extract tickers
tickers = [item["ticker"] for item in data.get("results", [])]

print(tickers)