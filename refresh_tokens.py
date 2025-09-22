import json
import time
import base64
import requests
from loguru import logger

def refresh_tokens():
    logger.info("Starting token refresh...")

    # Load existing token.json
    try:
        with open("secure/token.json", "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        logger.error("secure/token.json not found.")
        return

    refresh_token_value = tokens.get("refresh_token")
    if not refresh_token_value:
        logger.error("No refresh_token found in token.json.")
        return

    # Fill in your Schwab app credentials
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"

    # Encode client ID and secret in base64 for Authorization header
    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value
    }
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(
        url="https://api.schwabapi.com/v1/oauth2/token",
        headers=headers,
        data=payload
    )

    if response.status_code == 200:
        logger.info("Token refreshed successfully.")
        new_tokens = response.json()
        new_tokens["timestamp"] = int(time.time())

        with open("secure/token.json", "w") as f:
            json.dump(new_tokens, f, indent=2)

        logger.info("Updated secure/token.json with new tokens.")
    else:
        logger.error(f"Refresh failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    refresh_tokens()
