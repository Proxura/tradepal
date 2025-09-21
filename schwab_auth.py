import requests
import webbrowser
import urllib.parse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# ───────────────────────────────
# 🔧 INSERT YOUR CREDENTIALS HERE
# ───────────────────────────────
CLIENT_ID = 'tsTmzjKIa6HveehHUsOeagy2l4Gls2eMSnGHWkbXp5MXAVej'
CLIENT_SECRET = 'HVeGQsBoO7JoCVjEdyHEmb0IdCPHkk0ZGKRTtSxqbOClghdP1Zmw3aC1QAoZLAoh'
REDIRECT_URI = 'https://127.0.0.1'
TOKEN_FILE = 'tokens.json'

# ───────────────────────────────
# OAuth2 SETTINGS
# ───────────────────────────────
AUTH_URL = 'https://api.schwabapi.com/v1/oauth/authorize'
TOKEN_URL = 'https://api.schwabapi.com/v1/oauth/token'
SCOPE = 'read_account trade order options'  # adjust if needed

# ───────────────────────────────
# Simple server to catch redirect with auth code
# ───────────────────────────────
class SchwabRedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if 'code' in params:
            auth_code = params['code'][0]
            self.server.auth_code = auth_code
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'✅ Authorization successful. You can close this window.')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'❌ Authorization code not found.')

def get_auth_code():
    # Build the URL for user authorization
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
    }
    full_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    webbrowser.open(full_url)

    print(f"📡 Waiting for Schwab login at {REDIRECT_URI}...")

    # Start local server to catch redirect
    server_address = ('', 443)  # Port 443 for HTTPS (match your localhost setup)
    httpd = HTTPServer(server_address, SchwabRedirectHandler)

    try:
        httpd.handle_request()
        return httpd.auth_code
    except Exception as e:
        print("❌ Failed to capture code:", str(e))
        return None

def get_tokens(auth_code):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers)

    if response.status_code == 200:
        tokens = response.json()
        print("✅ Access token retrieved.")
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        print("💾 Tokens saved to", TOKEN_FILE)
    else:
        print("❌ Failed to retrieve tokens:")
        print(response.status_code, response.text)

if __name__ == '__main__':
    code = get_auth_code()
    if code:
        get_tokens(code)
