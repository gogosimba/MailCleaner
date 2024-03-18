import os
import requests
from requests.auth import HTTPBasicAuth
from tkinter import messagebox
from dotenv import load_dotenv

# Skapa .env fil med följande innehåll:
# WP_USERNAME=your_username
# WP_PASSWORD=your_password
# Sätt rätt värden för your_username och your_password





def send_email_to_api(subject, content):
    try:
        load_dotenv()
        username = os.environ.get("WP_USERNAME")
        password = os.environ.get("WP_PASSWORD")
        url = "https://ultra-group.se/wp-json/wp/v2/awsm_job_openings"
        post_data = {
            "title": subject,  # Ändra till subject
            "content": content,
            "status": "publish",
            "type": "awsm_job_openings",
            "author": 1,
            "meta_input": {
                "job_id": "123456789",
                "awsm_job_applications": 0,
                "awsm_job_expiry": "2024-12-31",  # Datum för när jobbet går ut
                "awsm_job_post_views": 0,
                "awsm_job_conversion": 0,
                "awsm_job_category": "IT",  # Jobbkategori om vi någonsin cleanar det
                "awsm_job_type": "Heltid",  # Heltid/deltid om det går att cleana
                "awsm_job_location": "Göteborg",  # Plats om det går att cleana. Ifall detta läggs in kan man filtrera jobb
            },
        }
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(
            url,
            headers=headers,
            json=post_data,
            auth=HTTPBasicAuth(username, password),
        )
        if response.status_code == 201:
            print("Post created successfully")
        else:
            print(f"An error occurred while creating the post: {response.text}")

    except Exception as ex:
        messagebox.showerror(
            "Error", f"An error occurred while sending data to API: {ex}"
        )
