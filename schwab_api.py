import requests
import json
import os
import time
from auth import get_tokens

# Load secrets from .env
from dotenv import load_dotenv
load_dotenv()

# Constants
BASE_URL = "https://api.schwabapi.com/trader/v1"

# Auto-refresh token if needed
def load_access_token():
    tokens = get_tokens()
    return tokens['access_token']

# === GET ACCOUNT INFO ===
def get_account_info():
    token = load_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    account_id = os.getenv("SCHWAB_ACCOUNT_ID")
    url = f"{BASE_URL}/accounts/{account_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get account info: {response.status_code}")
        return None

# === GET QUOTE ===
def get_quote(symbol):
    token = load_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"{BASE_URL}/marketdata/quotes/{symbol}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Quote fetch failed: {response.status_code}")
        return None

# === PLACE EQUITY ORDER ===
def place_equity_order(symbol, quantity, instruction="Buy", order_type="Market"):
    token = load_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    account_id = os.getenv("SCHWAB_ACCOUNT_ID")
    url = f"{BASE_URL}/accounts/{account_id}/orders"

    payload = {
        "orderType": order_type,
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": instruction,
                "quantity": quantity,
                "instrument": {
                    "symbol": symbol,
                    "assetType": "EQUITY"
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 201:
        print(f"✅ Order placed successfully for {symbol}")
    else:
        print(f"❌ Order failed: {response.status_code} — {response.text}")

# === GET OPTION CHAIN ===
def get_option_chain(symbol):
    token = load_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"{BASE_URL}/marketdata/chains?symbol={symbol}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch option chain: {response.status_code}")
        return None

# === MAIN TEST ===
if __name__ == "__main__":
    print("[TEST] Quote for TSLA:")
    quote = get_quote("TSLA")
    print(json.dumps(quote, indent=2))
