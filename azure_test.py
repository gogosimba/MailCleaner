import os
import pyperclip
import webbrowser
import requests
import tkinter as tk
from tkinter import messagebox, simpledialog
from msal import PublicClientApplication
from keyring import set_password, get_password
from unicodedata import normalize
from datetime import datetime, timedelta

APPLICATION_ID = "40abbd7b-c951-473e-8f69-dc10494ee62c"
CLIENT_SECRET = "KSb8Q~VFiqT_2cT~I6ngEID4eKeUdbJC~EFtBaXg"
authority_url = "https://login.microsoftonline.com/consumers/"
base_url = "https://graph.microsoft.com/v1.0/"
SCOPES = ["Mail.ReadWrite"]


def save_access_token(access_token, expiration_time):
    set_password("azure_email_fetcher", "access_token", access_token)
    set_password("azure_email_fetcher", "expiration_time", expiration_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
    
def reset_access_token():
    set_password("azure_email_fetcher", "access_token", "")
    set_password("azure_email_fetcher", "expiration_time", "")

def get_saved_access_token():
    return get_password("azure_email_fetcher", "access_token")

def get_access_token():
    saved_token = get_saved_access_token()
    saved_expiration_time = get_password("azure_email_fetcher", "expiration_time")
    if saved_token and saved_expiration_time:
        print("Saved token found")
        expiration_time = datetime.strptime(saved_expiration_time, "%Y-%m-%d %H:%M:%S.%f")
        if expiration_time > datetime.now():
            print("Using saved token")
            return saved_token
    app = PublicClientApplication(APPLICATION_ID, authority=authority_url)
    flow = app.initiate_device_flow(scopes=SCOPES)
    app_code = flow["message"].split()[-3]
    pyperclip.copy(app_code)
    print(app_code)
    webbrowser.open(flow["verification_uri"], new=1)
    messagebox.showinfo(
        "Device Flow", f"Go to {flow['verification_uri']} and enter the code {app_code}"
    )
    result = app.acquire_token_by_device_flow(flow)
    access_token_id = result["access_token"]
    expiration_time = datetime.now() + timedelta(seconds=result["expires_in"])
    save_access_token(access_token_id, expiration_time)
    set_password("azure_email_fetcher", "expiration_time", expiration_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
    return access_token_id


