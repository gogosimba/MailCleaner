import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication
import requests

load_dotenv()

APPLICATION_ID = os.environ.get("AZURE_APPLICATION_ID")
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
SCOPES = ["https://graph.microsoft.com/.default"]


def get_access_token():
    app = ConfidentialClientApplication(
        APPLICATION_ID,
        authority="https://login.microsoftonline.com/common",
        client_credential=CLIENT_SECRET,
    )

    result = app.acquire_token_for_client(scopes=SCOPES)
    access_token_id = result["access_token"]
    return access_token_id


def show_inbox(access_token):
    graph_url = "https://graph.microsoft.com/v1.0/"
    user_email = "LIA-ultragroup@outlook.com"  # Replace with the user's email address

    inbox_endpoint = f"{graph_url}me/mailFolders/Inbox/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.get(inbox_endpoint, headers=headers)

    if response.status_code == 200:
        inbox_messages = response.json().get("value", [])
        for message in inbox_messages:
            print(f"Subject: {message.get('subject')}")
    else:
        print(f"Error fetching inbox. Status code: {response.status_code}")
        print(f"Error message: {response.text}")


if __name__ == "__main__":
    # Get access token using client credentials
    access_token = get_access_token()

    # Show user's inbox
    show_inbox(access_token)
