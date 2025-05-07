import requests

API_KEY = "API_KEY"
ticker = "GM"

url = f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&apiKey={API_KEY}"
response = requests.get(url)

print("Status Code:", response.status_code)
print("Response Content:", response.text)  # Print raw response
