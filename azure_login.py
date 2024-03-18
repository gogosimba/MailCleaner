import os
from tkinter import messagebox
import requests
import unicodedata
import tkinter as tk
from tkinter import ttk
import azure_showmails
import customtkinter as ctk
from cleaning_logic import apply_cleaning_logic
from azure_sendtoapi import send_email_to_api
import azure_test as AzureTest

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
list_of_original_messages = []
list_of_cleaned_messages = []


class AzureLogin:
    def __init__(self, master):
        self.master = master
        self.access_token = AzureTest.get_saved_access_token() or None
        self.selected_folders = set()
        self.setup_gui()
        if self.access_token:
            self.populate_tree()

    def setup_gui(self):
        # Your other components...

        self.loginbutton = ctk.CTkButton(
            master=app, text="Login", command=self.handle_login
        )
        self.loginbutton.grid(row=0, column=0, pady=(5, 0), sticky="nsew")

        self.resetbutton = ctk.CTkButton(
            master=app, text="Reset Accesstoken", command=AzureTest.reset_access_token
        )
        self.resetbutton.grid(row=1, column=0, pady=5, sticky="nsew")

        self.getmailsbutton = ctk.CTkButton(
            master=app, text="Get Emails", command=self.handle_getmails
        )
        self.getmailsbutton.grid(row=2, column=0, pady=5, sticky="nsew")

        self.previewemailsbutton = ctk.CTkButton(
            master=app, text="Preview Emails", command=self.preview_emails
        )
        self.previewemailsbutton.grid(row=3, column=0, pady=5, sticky="nsew")

        self.showdifferences = ctk.CTkFrame(self.master)

        self.nocleaningcheckbox = ctk.CTkCheckBox(self.master, text="No cleaning")
        self.nocleaningcheckbox.grid(row=4, column=0, pady=5, sticky="nsew")

        self.saveashtmlcheckbox = ctk.CTkCheckBox(self.master, text="Save as HTML")
        self.saveashtmlcheckbox.grid(row=5, column=0, pady=5, sticky="nsew")

        self.treeview = ttk.Treeview(self.master, height=7, show="tree")
        self.treeview.grid(row=6, column=0, padx=10, pady=5, sticky="nsew")
        self.treeview.column("#0", width=300)
        self.treeview.bind("<Double-1>", self.on_double_click)

        # Configure row and column weights for resizing
        self.master.grid_rowconfigure(6, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def populate_tree(self, parent="", folder_id="me/mailFolders"):
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
                    self.process_folder_messages(
                        folder_name, folder_id, base_url, headers
                    )

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

    def process_folder_messages(self, folder_name, folder_id, base_url, headers):
        messages_endpoint = f"{base_url}me/mailFolders/{folder_id}/messages?$top=100"
        messages_response = requests.get(messages_endpoint, headers=headers)

        if messages_response.status_code == 200:
            messages = messages_response.json().get("value", [])
            folder_path = os.path.join(os.getcwd(), folder_name)
            os.makedirs(folder_path, exist_ok=True)

            for message in messages:
                list_of_original_messages.append(message)
                self.process_message(message, folder_name, folder_path)

            print(f"Messages saved in folder '{folder_name}'")

        else:
            print(
                f"Error fetching messages in folder '{folder_name}'. "
                f"Status code: {messages_response.status_code}"
            )
            print(f"Error message: {messages_response.text}")

    def process_message(self, message, folder_name, folder_path):
        message_subject = message.get("subject", "NoSubject")
        message_body = message.get("body", {}).get("content", "")

        if self.nocleaningcheckbox.get() == 1:
            print("No cleaning")
            cleaned_content = message_body
            cleaned_subject = message_subject
            cleaned_subject = "".join(
                c if c.isalnum() or c in "._-" else "_" for c in cleaned_subject
            )
        else:
            print(f"Cleaning {message_subject}")
            cleaned_message_body = apply_cleaning_logic(message_body, message_subject)

            if cleaned_message_body is None:
                print(f"Error cleaning message with subject '{message_subject}' ")
                return
            else:
                cleaned_content = cleaned_message_body[1]
                cleaned_subject = cleaned_message_body[0]
                print(cleaned_subject)
                list_of_cleaned_messages.append((cleaned_subject, cleaned_content))
                

    def preview_emails(self):
        if list_of_original_messages and list_of_cleaned_messages:
            azure_showmails.ShowMails(
                self.master, list_of_original_messages, list_of_cleaned_messages
            )
        else:
            messagebox.showinfo(
                "No emails",
                "List is empty, select a folder and then press get emails first",
            )


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("320x400")
    app.title("Azure Email Fetcher")
    azure_login = AzureLogin(app)
    app.mainloop()
