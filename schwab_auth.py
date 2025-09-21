import base64
import requests
import webbrowser
from loguru import logger


def construct_init_auth_url():
    app_key = "tsTmzjKIa6HveehHUsOeagy21l4Gls2eMSnGHWkbXp5MXAVej"
    app_secret = "HVeGQsBoO7JoCVjEdyHEmb0IdCPHkk0ZGKRTtSxqbOClghdP1Zmw3aC1QAoZLAoh"
    redirect = "https://127.0.0.1"

    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}"

    logger.info("Click the link to authenticate and copy the FULL returned URL:")
    logger.info(auth_url)

    return app_key, app_secret, redirect


def construct_headers_and_payload(returned_url, app_key, app_secret, redirect):
    # Extract just the code from the returned URL
    response_code = f"{returned_url.split('code=')[1].split('%40')[0]}@"

    # Base64 encode the app_key + app_secret
    combined = f"{app_key}:{app_secret}"
    encoded = base64.b64encode(combined.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "grant_type": "authorization_code",
        "code": response_code,
        "redirect_uri": redirect,
    }

    return headers, payload


def retrieve_tokens(headers, payload):
    token_url = "https://api.schwabapi.com/v1/oauth/token"
    response = requests.post(token_url, headers=headers, data=payload)
    return response.json()


def main():
    app_key, app_secret, redirect = construct_init_auth_url()
    webbrowser.open(f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}")

    returned_url = input("Paste the full redirect URL from the browser: ")

    headers, payload = construct_headers_and_payload(returned_url, app_key, app_secret, redirect)
    tokens = retrieve_tokens(headers, payload)

    logger.debug(tokens)
    return "Done!"


if __name__ == "__main__":
    main()
