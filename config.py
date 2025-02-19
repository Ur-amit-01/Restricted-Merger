import os
from os import environ

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "22012880"))
API_HASH = os.environ.get("API_HASH", "5b0e07f5a96d48b704eb9850d274fe1d")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL_ID", "-1002027394591"))

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
