import requests
import webbrowser
import urllib.parse
import json
import os

# ========== CONFIGURATION ==========
CLIENT_ID = "tsTmzjKIa6HveehHUsOeagy2l4Gls2eMSnGHWkbXp5MXAVej"
CLIENT_SECRET = "HVeGQsBoO7JoCVjEdyHEmb0IdCPHkk0ZGKRTtSxqbOClghdP1Zmw3aC1QAoZLAoh"
REDIRECT_URI = "https://127.0.0.1:5000/callback"
TOKEN_FILE = "schwab_tokens.json"
AUTH_URL = "https://api.schwabapi.com/v1/oauth/authorize"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
# ===================================

def get_authorization_code():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code"
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print("Opening browser for Schwab login...")
    webbrowser.open(url)

    code = input("Paste the 'code' from the redirect URL:\n> ").strip()
    return code

def exchange_code_for_tokens(auth_code):
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = { "Content-Type": "application/x-www-form-urlencoded" }

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code != 200:
        print("ERROR: Failed to retrieve tokens.")
        print(response.text)
        return None

    tokens = response.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)
    print("Tokens saved.")
    return tokens

def refresh_tokens():
    if not os.path.exists(TOKEN_FILE):
        print("No existing token file. Run the login flow first.")
        return None

    with open(TOKEN_FILE, "r") as f:
        old_tokens = json.load(f)

    data = {
        "grant_type": "refresh_token",
        "refresh_token": old_tokens["refresh_token"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = { "Content-Type": "application/x-www-form-urlencoded" }

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code != 200:
        print("ERROR: Failed to refresh tokens.")
        print(response.text)
        return None

    tokens = response.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)
    print("Tokens refreshed.")
    return tokens

if __name__ == "__main__":
    if not os.path.exists(TOKEN_FILE):
        code = get_authorization_code()
        tokens = exchange_code_for_tokens(code)
    else:
        tokens = refresh_tokens()

    if tokens:
        print("Access Token:", tokens["access_token"][:40], "...")
