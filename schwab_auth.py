import requests
import urllib.parse
import json
import time
import webbrowser

# Schwab app credentials
app_key = 'tsTmzjKIa6HveehHUsOeagy2l4Gls2eMSnGHWkbXp5MXAVej'
app_secret = 'HVeGQsBoO7JoCVjEdyHEmb0IdCPHkk0ZGKRTtSxqbOClghdP1Zmw3aC1QAoZLAoh'
redirect_uri = 'https://127.0.0.1'

# OAuth endpoints
auth_base_url = "https://api.schwabapi.com/v1/oauth/authorize"
token_url = "https://api.schwabapi.com/v1/oauth/token"

# Step 1: Generate auth URL
def construct_init_auth_url():
    url = f"{auth_base_url}?client_id={app_key}&redirect_uri={redirect_uri}"
    print(f"\nOPEN THIS URL IN YOUR BROWSER TO LOG IN:\n\n{url}\n")
    webbrowser.open(url)
    return url

# Step 2: Extract auth code from pasted redirect URL
def extract_code_from_url(returned_url):
    parsed = urllib.parse.urlparse(returned_url)
    query = urllib.parse.parse_qs(parsed.query)
    code = query.get('code', [None])[0]
    if not code:
        raise Exception("No authorization code found in the pasted URL")
    return code

# Step 3: Exchange code for token
def get_access_token(auth_code):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'client_id': app_key,
        'client_secret': app_secret,
        'code': auth_code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"Token exchange failed:\n{response.text}")
    return response.json()

# Step 4: Save token locally
def save_token_to_file(token_data):
    token_data['timestamp'] = time.time()
    with open('token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    print("Token saved to token.json")

# Main flow
def main():
    construct_init_auth_url()
    returned_url = input("Paste the full redirect URL from the browser: ").strip()
    auth_code = extract_code_from_url(returned_url)
    token_data = get_access_token(auth_code)
    save_token_to_file(token_data)

if __name__ == "__main__":
    main()
