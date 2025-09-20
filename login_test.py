from schwab.auth import easy_client

client = easy_client(
    api_key="your_client_id_here",
    app_secret="your_client_secret_here",
    callback_url="https://127.0.0.1:8182",
    token_path="token.json"
)

# This triggers auth + token flow automatically
resp = client.get_user_preferences()
print(resp.status_code)
print(resp.json())
