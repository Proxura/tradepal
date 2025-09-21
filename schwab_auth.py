import os
import base64
import requests
import webbrowser
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCHWAB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SCHWAB_REDIRECT_URI")


def get_auth_url():
    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    print("Click or paste into browser to authenticate:\n")
    print(auth_url)
    return auth_url


def parse_code_from_url(callback_url):
    parsed_url = urlparse(callback_url)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get("code", [None])[0]
    return code


def get_tokens(auth_code):
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post("https://api.schwabapi.com/v1/oauth/token", headers=headers, data=payload)

    try:
        tokens = response.json()
    except Exception:
        print("Token response not JSON:")
        print(response.text)
        raise

    return tokens


def main():
    webbrowser.open(get_auth_url())
    callback_url = input("\nPaste the FULL callback URL you were redirected to:\n")
    auth_code = parse_code_from_url(callback_url)
    
    if not auth_code:
        print("No auth code found in URL. Make sure you pasted the full redirected link.")
        return

    tokens = get_tokens(auth_code)

    print("\nAccess + Refresh Tokens:\n")
    print(tokens)


if __name__ == "__main__":
    main()
