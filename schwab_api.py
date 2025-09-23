import requests
import json
import os
import time
from auth import get_tokens
from dotenv import load_dotenv

# Load .env vars
load_dotenv()

MEMORY_FILE = "memory.json"
BASE_URL = "https://api.schwabapi.com/trader/v1"

# === Memory Helpers ===
def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === Auth ===
def load_access_token():
    tokens = get_tokens()
    return tokens['access_token']

# === Account Info ===
def get_account_info():
    token = load_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    account_id = os.getenv("SCHWAB_ACCOUNT_ID")
    url = f"{BASE_URL}/accounts/{account_id}"
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# === Quote ===
def get_quote(symbol):
    token = load_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/marketdata/quotes/{symbol}"
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# === Place Equity Order w/ Memory Logging ===
def place_equity_order(symbol, quantity, instruction="Buy", order_type="Market", price=None):
    memory = load_memory()

    # Check blacklist
    if symbol in memory.get("blacklist_commands", []):
        print(f"⛔ Blocked: {symbol} is blacklisted.")
        return {"status": "blocked", "symbol": symbol}

    # Check risk limits
    max_loss = memory["risk_profile"].get("max_loss_per_trade", 100)
    if order_type == "Limit" and price and quantity * price > max_loss * 2:
        print(f"⚠️ Trade too large: would exceed max loss per trade.")
        return {"status": "too_large", "symbol": symbol}

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
        "orderLegCollection": [{
            "instruction": instruction,
            "quantity": quantity,
            "instrument": {
                "symbol": symbol,
                "assetType": "EQUITY"
            }
        }]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f"✅ Order placed for {symbol}")

        # Log to memory
        memory["last_trade"] = {
            "symbol": symbol,
            "instruction": instruction,
            "quantity": quantity,
            "order_type": order_type,
            "timestamp": time.time()
        }
        memory["trade_history"].append(memory["last_trade"])
        save_memory(memory)

        return {"status": "success", "symbol": symbol}

    else:
        print(f"❌ Order failed: {response.status_code} — {response.text}")
        return {"status": "error", "symbol": symbol, "details": response.text}

# === Option Chain ===
def get_option_chain(symbol):
    token = load_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/marketdata/chains?symbol={symbol}"
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# === Main Test ===
if __name__ == "__main__":
    print("[TEST] TSLA Quote:")
    quote = get_quote("TSLA")
    print(json.dumps(quote, indent=2))

    print("\n[TEST] Memory-aware order:")
    result = place_equity_order("TSLA", 1)
    print(result)
