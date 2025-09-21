
import requests
import webbrowser
import urllib.parse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# === Insert your credentials here ===
CLIENT_ID = 'tsTmzjKIa6HveehHUsOeagy2l4Gls2eMSnGHWkbXp5MXAVej'
CLIENT_SECRET = 'HVeGQsBoO7JoCVjEdyHEmb0IdCPHkk0ZGKRTtSxqbOClghdP1Zmw3aC1QAoZLAoh'
REDIRECT_URI = 'https://127.0.0.1'
TOKEN_FILE = 'tokens.json'     

# === OAuth URLs and Scope ===
AUTH_URL = 'https://api.schwabapi.com/v1/oauth/authorize'
TOKEN_URL = 'https://api.schwabapi.com/v1/oauth/token'
SCOPE = 'read_account trade order options'

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
            self.wfile.write(b"Authorization successful. You can close this window.")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization code not found.")

def get_auth_code():
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    webbrowser.open(url)

    server = HTTPServer(('localhost', 5000), SchwabRedirectHandler)
    server.handle_request()
    return server.auth_code

def exchange_code_for_token(auth_code):
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(response.json(), f, indent=2)
        print("Token saved to tokens.json")
    else:
        print("Failed to get token")
        print(response.status_code, response.text)

if __name__ == "__main__":
    code = get_auth_code()
    exchange_code_for_token(code)
