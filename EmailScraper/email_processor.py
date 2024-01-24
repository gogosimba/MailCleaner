from pathlib import Path
import os
import dotenv
import tkinter as tk
import win32com.client
from email.header import decode_header
from tkinter import Listbox, scrolledtext, filedialog, messagebox
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from requests.auth import HTTPBasicAuth


class EmailProcessor:
    dotenv.load_dotenv()
    def __init__(self):
        self.removed_text_indices = {}
        self.content_text = {}

    @staticmethod
    def safe_decode(header):
        decoded, encoding = decode_header(header)[0]
        if isinstance(decoded, bytes):
            try:
                decoded = decoded.decode(encoding or "utf-8")
            except UnicodeDecodeError:
                decoded = decoded.decode("latin-1", errors="replace")
        return decoded

    def send_email(self, to_address, subject, body):
        try:
            message = MIMEMultipart()
            message["From"] = "LIA-ultragroup@outlook.com"
            message["To"] = to_address
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
                server.starttls()
                server.login("LIA-ultragroup@outlook.com", "Lia2023EC")
                server.sendmail(
                    "LIA-ultragroup@outlook.com", to_address, message.as_string()
                )

            messagebox.showinfo("Success", "Email sent successfully.")
        except Exception as ex:
            messagebox.showerror(
                "Error", f"An error occurred while sending the email: {ex}"
            )

    def clean_levigo_email(self, email_body):
        # Remove Job Posting IDs
        email_body = re.sub(r"Job Posting ID:\s+VV]OL[G|JP000\d{5}", "", email_body)

        # Remove text after "NOTE - Maximum 1 offer per assignment!"
        note_index = email_body.find("NOTE - Maximum 1 offer per assignment!")
        if note_index != -1:
            return email_body[:note_index]

        return email_body

    def clean_combitech_email(self, email_body):
        # Remove text leading up to and including "Beskrivning"
        index = email_body.find("Beskrivning")
        if index != -1:
            email_body = email_body[index + len("Beskrivning") :]

        # Clean end of email for Combitech
        takpris_match = re.search(r"Takpris: \d{3} SEK/h", email_body)
        if takpris_match:
            return email_body[: takpris_match.start()]

        id_match = re.search(r"ID: \d{4}", email_body)
        if id_match:
            return email_body[: id_match.start()]

        return email_body

    def apply_cleaning_logic(self, email_body):
        print("Applying cleaning logic")
        print(email_body)
        # Check if the email is from Combitech
        if "Combitech" in email_body:
            return self.clean_combitech_email(email_body)

        # Check if the email is from Levigo
        elif "Levigo" in email_body:
            return self.clean_levigo_email(email_body)

        # Return the original body if no keywords are found
        return email_body

    def remove_specific_lines(self, email_body, subject):
        lines_to_remove = ["Från:", "Skickat:", "Till:", "Ämne:"]
        cleaned_body = []
        removed_indices = []
        lines = email_body.splitlines()
        for i, line in enumerate(lines):
            if any(line.lstrip().startswith(phrase) for phrase in lines_to_remove):
                removed_indices.append((i + 1, i + 2))
                continue
            cleaned_body.append(line)
        return "\n".join(cleaned_body), removed_indices

    def send_email_to_api(self, subject, content):
        try:
            # Define your WordPress credentials
            username = os.environ.get("WP_USERNAME")
            password = os.environ.get("WP_PASSWORD")
            print(username, password)

            # Define the WordPress REST API endpoint for creating posts
            url = "https://ultra-group.se/wp-json/wp/v2/awsm_job_openings"

            # Define the post data
            post_data = {
                "title": subject,
                "content": content,
                "status": "publish",
                "type": "awsm_job_openings",
                "author": 1,
                "meta_input": {
                    "job_id": "123456789",
                    "awsm_job_applications": 0,
                    "awsm_job_expiry": "2024-12-31",
                    "awsm_job_post_views": 0,
                    "awsm_job_conversion": 0,
                    "awsm_job_category": "Sigma",  # Add the job category
                    "awsm_job_type": "Heltid",  # Add the job type
                    "awsm_job_location": "Över hela sverige",  # Add the job location
                },
            }

            # Set up headers with basic authentication
            headers = {
                "Content-Type": "application/json",
            }

            # Make the POST request with basic authentication
            response = requests.post(
                url,
                headers=headers,
                json=post_data,
                auth=HTTPBasicAuth(username, password),
            )

            # Check if the post was created successfully
            if response.status_code == 201:
                messagebox.showinfo(
                    "Success",
                    f'Job post created successfully with ID {response.json()["id"]}',
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"Error creating job post. Status code: {response.status_code}\n{response.text}",
                )

        except Exception as ex:
            messagebox.showerror(
                "Error", f"An error occurred while sending data to API: {ex}"
            )

    def save_email_to_file_and_api(
        self, email_obj, output_dir, progress_text, subject_listbox
    ):
        try:
            sanitized_subject = re.sub(r"[^\w\s.-]", "", email_obj.Subject)
            filename = f"{sanitized_subject[:100]}.txt"
            file_path = output_dir / filename
            email_body = email_obj.Body
            cleaned_body = self.apply_cleaning_logic(email_body)

            self.removed_text_indices[
                email_obj.Subject
            ] = []  # No removed indices for cleaned_body
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(f"{email_obj.Subject}\n\n")
                file.write(f"{cleaned_body}")

            progress_text.insert(
                tk.END,
                f"Saved email '{email_obj.Subject}' from {email_obj.Parent.Name}\n",
            )
            progress_text.yview(tk.END)

            subject_listbox.insert(tk.END, email_obj.Subject)
            self.content_text[email_obj.Subject] = cleaned_body

            # Send email data to API
            self.send_email_to_api(email_obj.Subject, cleaned_body)

        except Exception as e:
            print(
                f"Error saving email '{email_obj.Subject}' from {email_obj.Parent.Name}: {e}"
            )
            progress_text.insert(
                tk.END,
                f"Error saving email '{email_obj.Subject}' from {email_obj.Parent.Name}: {e}\n",
            )
            progress_text.yview(tk.END)

    def get_email_content(self, subject):
        return self.content_text.get(subject, ""), self.removed_text_indices.get(
            subject, []
        )

    def get_cleaned_email(self, subject):
        return self.content_text.get(subject, "")

    def retrieve_emails(self, output_dir, progress_text, subject_listbox):
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)

        folder_names = [
            "22. Assignments from Combitech",
            "24. Assignments from Levigo",
        ]

        email_count = 0

        for name in folder_names:
            try:
                folder = inbox.Folders[name]
                for email in folder.Items:
                    email_count += 1
                    self.save_email_to_file_and_api(
                        email, output_dir, progress_text, subject_listbox
                    )
            except Exception as e:
                progress_text.insert(tk.END, f"Error accessing folder {name}: {e}\n")
                progress_text.yview(tk.END)

    def run_script(self, output_folder, progress_text, subject_listbox):
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        progress_text.delete(1.0, tk.END)
        subject_listbox.delete(0, tk.END)
        self.content_text.clear()
        self.removed_text_indices.clear()
        self.retrieve_emails(output_dir, progress_text, subject_listbox)
