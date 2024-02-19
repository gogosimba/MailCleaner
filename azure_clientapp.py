import requests

# Azure AD application details
client_id = "40abbd7b-c951-473e-8f69-dc10494ee62c"
client_secret = "KSb8Q~VFiqT_2cT~I6ngEID4eKeUdbJC~EFtBaXg"
tenant_id = "f8cdef31-a31e-4b4a-93e4-5f571e91255a"
graph_url = "https://graph.microsoft.com/v1.0/"

def get_access_token():
    # Acquire token using client credentials flow
    token_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }

    token_response = requests.post(token_endpoint, data=token_data)
    access_token = token_response.json().get("access_token")
    print(access_token)
    return access_token

def get_user_inbox(access_token):
    # Endpoint to get user's inbox
    inbox_endpoint = f"{graph_url}users/{user_email}/mailFolders/Inbox/messages"
    
    # Define headers with access token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Make request to retrieve inbox messages
    response = requests.get(inbox_endpoint, headers=headers)

    if response.status_code == 200:
        inbox_messages = response.json().get("value", [])
        for message in inbox_messages:
            print(f"Subject: {message.get('subject')}")
    else:
        print(f"Error fetching inbox. Status code: {response.status_code}")
        print(f"Error message: {response.text}")

# Replace with the user's email address
user_email = "LIA-ultragroup@outlook.com"

# Get access token
access_token = get_access_token()

# Get user's inbox
get_user_inbox(access_token)
