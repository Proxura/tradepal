import os
import requests
import webbrowser
from flask import Flask, request

oapp = Flask(__name__)

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID")
REDIRECT_URI = "http://127.0.0.1:5000/callback"
AUTH_URL = "https://api.schwabapi.com/v1/oauth/authorize"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
ACCESS_TOKEN_FILE = "access_token.txt"

@app.route("/")
def authorize():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
    }
    url = requests.Request("GET", AUTH_URL, params=params).prepare().url
    webbrowser.open(url)
    return "Opening Schwab login page..."

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        with open(ACCESS_TOKEN_FILE, "w") as f:
            f.write(tokens["access_token"])
        return "✅ Authentication successful. Access token saved."
    else:
        return f"❌ Error retrieving token: {response.text}"

if __name__ == "__main__":
    app.run(port=5000)

