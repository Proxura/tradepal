import json
import time
import requests

# Update this path if needed
with open('secure/token.json', 'r') as f:
    token_data = json.load(f)

access_token = token_data.get('access_token')
timestamp = token_data.get('timestamp')
expires_in = token_data.get('expires_in', 1800)  # default: 1800 seconds (30 min)

is_expired = (time.time() - timestamp) >= expires_in

if is_expired:
    print("❌ Token is expired. Ready for refresh.")
else:
    print("✅ Access token is still valid based on timestamp.")

# Optional: make a test API call to confirm
response = requests.get(
    "https://api.schwabapi.com/trader/v1/accounts",
    headers={"Authorization": f"Bearer {access_token}"}
)

if response.status_code == 200:
    print("✅ API call succeeded. Token is working.")
else:
    print(f"❌ API call failed: {response.status_code}")
    print(response.text)
