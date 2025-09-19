import os
import json
import requests
from urllib.parse import urlencode
from flask import Flask, request, redirect
from dotenv import load_dotenv

# Load .env values
load_dotenv()

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID") or "YOUR_CLIENT_ID"
CLIENT_SECRET = os.getenv("SCHWAB_CLIENT_SECRET") or "YOUR_CLIENT_SECRET"
REDIRECT_URI = os.getenv("SCHWAB_REDIRECT_URI") or "https://localhost:5000/callback"
TOKEN_FILE = "token.json"

# Flask app
app = Flask(__name__)

# Start OAuth login flow
@app.route("/")
def login():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "read_accounts"  # Modify if needed
    }
    auth_url = f"https://api.schwabapi.com/v1/oauth2/authorize?{urlencode(params)}"
    return redirect(auth_url)

# Callback route — receives ?code= from Schwab
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Authorization code not found."

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post("https://api.schwabapi.com/v1/oauth2/token", data=data, headers=headers)

    if response.status_code == 200:
        tokens = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f, indent=2)
        return "✅ Token saved to token.json"
    else:
        return f"❌ Error: {response.status_code}<br>{response.text}"

# Token view
@app.route("/token")
def view_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f"<pre>{f.read()}</pre>"
    return "⚠️ No token.json found."

# Run server w/ SSL
if __name__ == "__main__":
    app.run(host="localhost", port=5000, ssl_context=('certs/cert.pem', 'certs/key.pem'))
