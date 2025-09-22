import json
import time
import base64
import requests
from loguru import logger

def refresh_tokens():
    logger.info("🔁 Starting token refresh...")

    # Load token file
    try:
        with open("secure/token.json", "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        logger.error("❌ secure/token.json not found.")
        return

    refresh_token_value = tokens.get("refresh_token")
    if not refresh_token_value:
        logger.error("❌ No refresh_token found in token.json.")
        return

    # Schwab app credentials
    client_id = 'tsTmzjKIa6HveehHUsOeagy2l4Gls2eMSnGHWkbXp5MXAVej'
    client_secret = 'HVeGQsBoO7JoCVjEdyHEmb0IdCPHkk0ZGKRTtSxqbOClghdP1Zmw3aC1QAoZLAoh'

    # Encode for Basic Auth
    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    # POST data
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value
    }
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Correct refresh token URL
    response = requests.post(
        url="https://api.schwabapi.com/v1/oauth/token",
        headers=headers,
        data=payload
    )

    # Handle response
    if response.status_code == 200:
        logger.info("✅ Token refreshed successfully.")
        new_tokens = response.json()
        new_tokens["timestamp"] = int(time.time())

        with open("secure/token.json", "w") as f:
            json.dump(new_tokens, f, indent=2)

        logger.success("💾 Updated secure/token.json with new tokens.")
        logger.debug(f"Access token: {new_tokens.get('access_token')}")
        return new_tokens.get("access_token")
    else:
        logger.error(f"❌ Refresh failed: {response.status_code} {response.text}")
        return None

# Call it manually if testing:
if __name__ == "__main__":
    refresh_tokens()
