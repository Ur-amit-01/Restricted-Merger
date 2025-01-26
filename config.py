import os
from os import environ

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

API_ID = int(os.environ.get("API_ID", "22012880"))

API_HASH = os.environ.get("API_HASH", "5b0e07f5a96d48b704eb9850d274fe1d")

SESSION_STRING = os.environ.get("SESSION_STRING", "")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "2031106491"))


# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://uramit0001:EZ1u5bfKYZ52XeGT@cluster0.qnbzn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "restrictedsaver")

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
