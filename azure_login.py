import os
import customtkinter as ctk
import tkinter as tk
import base64
from tkinter import ttk
from cleaning_logic import apply_cleaning_logic
from azure_sendtoapi import send_email_to_api
import requests
import azure_test as AzureTest

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.geometry("320x300")
app.title("Azure Email Fetcher")


class AzureLogin:
    def __init__(self, master):
        self.master = master
        self.access_token = AzureTest.get_saved_access_token() or None
        self.selected_folders = set()

        self.loginbutton = ctk.CTkButton(
            master=app, text="Login", command=self.handle_login
        )
        self.loginbutton.place(relx=0.5, rely=0.5, anchor="ne")
        
        self.resetbutton = ctk.CTkButton(
            master=app, text="Reset Accesstoken", command=AzureTest.reset_access_token
        )
        self.resetbutton.place(relx=0.5, rely=0.6, anchor="ne")

        self.getmailsbutton = ctk.CTkButton(
            master=app, text="Get Emails", command=self.handle_getmails
        )
        self.getmailsbutton.place(relx=0.5, rely=0.7, anchor="ne")
        self.nocleaningcheckbox = ctk.CTkCheckBox(master, text="No cleaning")
        self.nocleaningcheckbox.place(relx=0.9, rely=0.7, anchor="ne")
        self.saveashtmlcheckbox = ctk.CTkCheckBox(master, text="Save as HTML")
        self.saveashtmlcheckbox.place(relx=0.94, rely=0.8, anchor="ne")
        self.sendtoapicheckbox = ctk.CTkCheckBox(master, text="Send to API")
        self.sendtoapicheckbox.place(relx=0.9, rely=0.9, anchor="ne")
        self.treeview = ttk.Treeview(master, height=7, show="tree")
        self.treeview.grid(padx=10)
        self.treeview.column("#0", width=300)
        self.treeview.bind("<Double-1>", self.on_double_click)
        if self.access_token:
            self.populate_tree()

    def populate_tree(self, parent="", folder_id="me/mailFolders"):
        print("Fetching folders...")
        base_url = "https://graph.microsoft.com/v1.0/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        folders_endpoint = base_url + folder_id
        if folder_id != "me/mailFolders":
            folders_endpoint = f"{base_url}me/mailFolders/{folder_id}/childFolders"

        folders_response = requests.get(folders_endpoint, headers=headers)

        if folders_response.status_code != 200:
            print(
                f"Error fetching folders. Status code: {folders_response.status_code}"
            )
            print(f"Error message: {folders_response.text}")
            return

        folders = folders_response.json().get("value", [])

        for folder in folders:
            folder_id = folder.get("id", "")
            folder_name = folder.get("displayName", "")
            item_id = self.treeview.insert(
                parent, "end", text=folder_name, values=(folder_name), tags=(folder_id)
            )
            self.treeview.item(item_id, open=False)

        print("Folders fetched successfully.")

    def handle_login(self):
        self.access_token = AzureTest.get_access_token()
        self.populate_tree()

    def handle_getmails(self):
        self.selected_folders.clear()
        selected_items = self.treeview.selection()
        for item in selected_items:
            folder_name = self.treeview.item(item, "text")
            self.selected_folders.add(folder_name)
        print("Selected Folders:", self.selected_folders)

        if self.access_token and self.selected_folders:
            base_url = "https://graph.microsoft.com/v1.0/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Prefer": (
                    'outlook.body-content-type="html"'
                    if self.saveashtmlcheckbox.get() == 1
                    else 'outlook.body-content-type="text"'
                ),
            }

            for folder_name in self.selected_folders:
                folder_id = self.get_folder_id_by_name(
                    folder_name, base_url, headers, path_components=[folder_name]
                )
                if folder_id:
                    messages_endpoint = (
                        f"{base_url}me/mailFolders/{folder_id}/messages?$top=100"
                    )
                    messages_response = requests.get(messages_endpoint, headers=headers)

                    if messages_response.status_code == 200:
                        messages = messages_response.json().get("value", [])
                        folder_path = os.path.join(os.getcwd(), folder_name)
                        os.makedirs(folder_path, exist_ok=True)

                        for message in messages:
                            message_subject = message.get("subject", "NoSubject")
                            message_body = message.get("body", {}).get("content", "")

                            if self.nocleaningcheckbox.get() == 1:
                                print("No cleaning")
                                cleaned_content = message_body
                                cleaned_subject = message_subject
                                cleaned_subject = "".join(
                                    c if c.isalnum() or c in "._-" else "_"
                                    for c in cleaned_subject
                                )

                            else:
                                print("Cleaning")
                                cleaned_message_body = apply_cleaning_logic(
                                    message_body, message_subject
                                )
                                if cleaned_message_body is None:
                                    print(
                                        f"Error cleaning message with subject '{message_subject}'"
                                        " moved the email to the Review folder"
                                    )
                                    print("Message ID:", message["id"])
                                    self.move_email(message["id"], "I00E")
                                    continue
                                else:
                                    cleaned_content = cleaned_message_body[1]
                                    cleaned_subject = cleaned_message_body[0]
                                    sanitized_subject = "".join(
                                        c if c.isalnum() or c in "._-" else "_"
                                        for c in cleaned_subject
                                    )
                            message_filename = (
                                sanitized_subject
                                if self.saveashtmlcheckbox.get() == 0
                                else f"{sanitized_subject}.html"
                            )
                            message_filepath = os.path.join(
                                folder_path, message_filename
                            )
                            with open(message_filepath, "w", encoding="utf-8") as file:
                                try:
                                    file.write(cleaned_content)
                                except Exception as e:
                                    print(f"Error writing file {message_filepath}: {e}")
                            if self.sendtoapicheckbox.get() == 1:
                                send_email_to_api(cleaned_subject, cleaned_content)
                        print(f"Messages saved in folder '{folder_name}'")

                    else:
                        print(
                            f"Error fetching messages in folder '{folder_name}'. "
                            f"Status code: {messages_response.status_code}"
                        )
                        print(f"Error message: {messages_response.text}")

    def on_double_click(self, event):
        item = self.treeview.selection()[0]
        print(item)
        folder_id = (
            self.treeview.item(item, "tags")[0]
            if self.treeview.item(item, "tags")
            else None
        )
        if not self.treeview.item(item, "open"):
            self.populate_tree(item, folder_id)

    def get_folder_id_by_name(
        self,
        target_folder_name,
        base_url,
        headers,
        parent_folder_id="me/mailFolders",
        path_components=None,
    ):
        if path_components is None:
            path_components = []
        current_path = path_components  # Initialize current_path outside the loop
        if parent_folder_id == "me/mailFolders":
            folders_endpoint = f"{base_url}{parent_folder_id}"
        else:
            folders_endpoint = (
                f"{base_url}me/mailFolders/{parent_folder_id}/childFolders"
            )

        folders_response = requests.get(folders_endpoint, headers=headers)

        if folders_response.status_code == 200:
            folders = folders_response.json().get("value", [])

            for folder in folders:
                folder_id = folder.get("id", "")
                folder_display_name = folder.get("displayName", "")
                current_path = path_components + [folder_display_name]

                if folder_display_name == target_folder_name:
                    return folder_id

                subfolder_id = self.get_folder_id_by_name(
                    target_folder_name, base_url, headers, folder_id, current_path
                )
                if subfolder_id:
                    return subfolder_id

            print(
                f"Folder '{target_folder_name}' not found in path {'/'.join(current_path)}"
            )
            return None
        else:
            print(
                f"Error fetching folders. Status code: {folders_response.status_code}"
            )
            print(f"Error message: {folders_response.text}")
            return None

    def move_email(self, message_id, destination_folder_id):
        base_url = "https://graph.microsoft.com/v1.0/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        try:
            decoded_message_id = base64.urlsafe_b64decode(message_id + "==")
        except Exception as e:
            print(f"Error decoding message ID: {e}")
            return
        
        move_endpoint = f"{base_url}me/messages/{decoded_message_id.decode()}/move"
        move_data = {"destinationId": destination_folder_id}

        move_response = requests.post(
            move_endpoint, headers=headers, json=move_data
        )

        if move_response.status_code == 201:
            print(f"Message moved to '{destination_folder_id}' successfully")
        else:
            print(
                f"Error moving message to '{destination_folder_id}'. "
                f"Status code: {move_response.status_code}"
            )
            print(f"Error message: {move_response.text}")

azure_login = AzureLogin(app)
app.mainloop()
