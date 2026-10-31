import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# resolve paths relative to this file
HERE = os.path.dirname(__file__)
CREDS_FILE = os.path.join(HERE, 'credentials.json')
TOKEN_FILE = os.path.join(HERE, 'token.json')


def get_gmail_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # persist for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds