import os

CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID") or os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET") or os.environ.get("CLIENT_SECRET", "")
CHANNEL_LOGIN = os.environ.get("TWITCH_CHANNEL_LOGIN") or os.environ.get("CHANNEL_LOGIN", "")
APP_TOKEN = os.environ.get("TWITCH_APP_TOKEN") or os.environ.get("APP_TOKEN", "")
USER_ACCESS_TOKEN = os.environ.get("TWITCH_USER_TOKEN") or os.environ.get("USER_ACCESS_TOKEN", "")
ENDPOINT_PASSWORD = os.environ.get("TWITCH_ENDPOINT_PASSWORD") or os.environ.get("ENDPOINT_PASSWORD", "")
