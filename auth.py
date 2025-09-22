# auth.py – auto-refresh compatible with schwab_auth.py

import os
import time
import json
import base64
import requests
from dotenv import load_dotenv

# Load credentials from .env if available (optional)
load_dotenv()

# Constants
TOKEN_FILE = "secure/token.json"
APP_KEY = os.getenv("SCHWAB_CLIENT_ID") or "tsTmzjKIa6HveehHUsOeagy2l4Gls2eMSnGHWkbXp5MXAVej"
APP_SECRET = os.getenv("SCHWAB_CLIENT_SECRET") or "HVeGQsBoO7JoCVjEdyHEmb0IdCPHkk0ZGKRTtSxqbOClghdP1Zmw3aC1QAoZLAoh"
REDIRECT_URI = os.getenv("SCHWAB_REDIRECT_URI") or "https://127.0.0.1"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"

def load_token():
    if not os.path.exists(TOKEN_FILE):
        raise Exception("❌ Token file not found.")
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)

def save_token(token_data):
    token_data['timestamp'] = time.time()
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    print("✅ Refreshed token saved.")

def is_expired(token_data):
    expires_in = token_data.get("expires_in", 1800)  # default 30 mins
    return time.time() - token_data.get("timestamp", 0) >= expires_in - 60  # refresh 1 min early

def refresh_token():
    token_data = load_token()
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise Exception("❌ No refresh_token found in token file.")

    print("🔄 Refreshing token...")

    # Encode credentials for Basic Auth
    client_creds = f"{APP_KEY}:{APP_SECRET}"
    encoded_creds = base64.b64encode(client_creds.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_creds}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception(f"❌ Token refresh failed:\n{response.text}")

    new_token_data = response.json()
    new_token_data["refresh_token"] = refresh_token  # Schwab may not return a new one
    save_token(new_token_data)
    return new_token_data

def get_valid_token():
    token_data = load_token()
    if is_expired(token_data):
        token_data = refresh_token()
    return token_data

# Optional test usage
if __name__ == "__main__":
    token = get_valid_token()
    print("✅ Valid access token:", token["access_token"])

