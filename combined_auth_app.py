from flask import Flask, request
import requests
from urllib.parse import urlencode
import webbrowser
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID")
REDIRECT_URI = os.getenv("SCHWAB_REDIRECT_URI")
CERT_PATH = 'certs/cert.pem'
KEY_PATH = 'certs/key.pem'

@app.route("/")
def login():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "read_accounts trade",
    }
    url = f"https://api.schwabapi.com/v1/oauth/authorize?{urlencode(params)}"
    webbrowser.open(url)
    return "Opened Schwab login page. Please complete the login and authorize."

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    response = requests.post("https://api.schwabapi.com/v1/oauth/token", data=data, headers=headers, cert=(CERT_PATH, KEY_PATH))
    tokens = response.json()
    
    # Save tokens locally
    with open("tokens.json", "w") as f:
        f.write(str(tokens))
    
    return f"Tokens received and saved: {tokens}"

if __name__ == "__main__":
    app.run(ssl_context=(CERT_PATH, KEY_PATH), port=8182)
