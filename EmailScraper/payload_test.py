import requests
from requests.auth import HTTPBasicAuth

# Define your WordPress credentials
username = 'LIA-ultragroup@outlook.com'
password = '1JMO FwfG cl4E 9Iej pEM2 vobp'

# Define the WordPress REST API endpoint for creating posts
url = 'https://ultra-group.se/wp-json/wp/v2/awsm_job_openings'

# Define the post data
post_data = {
    'title': 'Nytt jobb',
    'content': '',
    'status': 'publish',
    'type': 'awsm_job_openings',
    'author': 1,
    'meta_input': {
        'job_id': '123456789',
        'awsm_job_applications': 0,
        'awsm_job_expiry': '2024-12-31',
        'awsm_job_post_views': 0,
        'awsm_job_conversion': 0,
        'awsm_job_category': 'Sigma',  # Add the job category
        'awsm_job_type': 'Heltid',  # Add the job type
        'awsm_job_location': 'Över hela sverige',  # Add the job location
    },
}

# Set up headers with basic authentication
headers = {
    'Content-Type': 'application/json',
}

# Make the POST request with basic authentication
response = requests.post(url, headers=headers, json=post_data, auth=HTTPBasicAuth(username, password))

# Check if the post was created successfully
if response.status_code == 201:
    print(f'Job post created successfully with ID {response.json()["id"]}')
else:
    print(f'Error creating job post. Status code: {response.status_code}')
    print(response.text)
