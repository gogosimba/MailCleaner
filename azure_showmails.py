from tkinter import messagebox
import customtkinter as ctk
from CTkListbox import *
import tkinter as tk
import subprocess
from azure_sendtoapi import send_email_to_api
from email_rewriter import rewrite_with_gpt2

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
multistring = """<!-- wp:html {"blockVisibility":{"controlSets":[{"id":1,"enable":true,"controls":{"userRole":{"visibilityByRole":"user-role","restrictedRoles":["administrator","contributor"]}}}]}} -->
        lägg till känslig info mellan dessa två taggar, t.ex.
        kontaktperson@företag.se
        jobbid: 123456789
        lön: 100-200kr/h
<!-- /wp:html -->"""

start_tag = """
<!-- wp:html {"blockVisibility":{"controlSets":[{"id":1,"enable":true,"controls":{"userRole":{"visibilityByRole":"user-role","restrictedRoles":["administrator","contributor"]}}}]}} -->
"""
end_tag = """
<!-- /wp:html -->
"""


class ShowMails:
    def __init__(self, master, original_messages, cleaned_messages):
        self.master = master
        self.window = ctk.CTkToplevel(self.master)
        self.window.title("Show Mails")
        self.window.geometry("800x600")
        self.window.state("zoomed")

        self.subject_listbox = tk.Listbox(
            self.window, selectmode=tk.SINGLE, background="gray10", foreground="white"
        )
        for cleaned_subject, _ in cleaned_messages:
            self.subject_listbox.insert(tk.END, cleaned_subject)
        self.subject_listbox.pack(side=tk.TOP, fill=tk.X)

        self.text_area_original = ctk.CTkTextbox(
            self.window, wrap=tk.WORD, width=40, height=20
        )
        self.text_area_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_area_cleaned = ctk.CTkTextbox(
            self.window, wrap=tk.WORD, width=40, height=20
        )
        self.text_area_cleaned.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.button_publish = ctk.CTkButton(
            self.window, text="Publish", command=self.publish
        )
        self.button_publish.place(relx=1.0, rely=0.9, anchor="se")

        self.button_hidetext = ctk.CTkButton(
            self.window, text="Hide Text", command=self.hide_text
        )
        self.button_hidetext.place(relx=1.0, rely=1.0, anchor="se")
        
        self.button_rewrite = ctk.CTkButton(
            self.window, text="Rewrite", command=self.rewrite
        )
        self.button_rewrite.place(relx=1.0, rely=0.8, anchor="se")

        self.subject_listbox.bind(
            "<<ListboxSelect>>",
            lambda event: self.show_selected_message(
                event, original_messages, cleaned_messages
            ),
        )

    def show_selected_message(
        self, event, original_messages, cleaned_messages
    ):  # Corrected this line
        selected_index = self.subject_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            original_message = (
                original_messages[selected_index]  # Adjusted this line
                .get("body", {})
                .get("content", "")
            )
            cleaned_message = cleaned_messages[selected_index]  # Adjusted this line

            self.text_area_original.delete(1.0, tk.END)
            self.text_area_original.insert(tk.END, multistring)
            self.text_area_original.insert(tk.END, original_message)

            _, cleaned_content = cleaned_message

            self.text_area_cleaned.delete(1.0, tk.END)
            self.text_area_cleaned.insert(tk.END, cleaned_content)

    def publish(self):
        send_email_to_api(
            self.subject_listbox.get(tk.ACTIVE),
            self.text_area_cleaned.get(1.0, tk.END),
        )
        messagebox.showinfo(
            "Published to the job page", "Email published through the API"
        )

    def hide_text(self):
        start_index = self.text_area_cleaned.index(tk.SEL_FIRST)
        end_index = self.text_area_cleaned.index(tk.SEL_LAST)
        if start_index and end_index:
            self.text_area_cleaned.insert(start_index, start_tag)
            end_index = self.text_area_cleaned.index(tk.SEL_LAST + " +1c")
            self.text_area_cleaned.insert(end_index, end_tag)
    
    
    def rewrite(self):
        cleaned_email = self.text_area_cleaned.get(1.0, tk.END)
        # Create a new window for displaying the rewritten email
        rewrite_window = tk.Toplevel(self.master)
        rewrite_window.title("Rewritten Email")

        # Add a text widget to display the rewritten email
        text_widget = ctk.CTkTextbox(rewrite_window, wrap=tk.WORD, width=40, height=20)
        text_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        rewritten_email = rewrite_with_gpt2(cleaned_email)
        text_widget.insert(tk.END, rewritten_email)
        
        rewrite_window.state("zoomed")

        # Add a button to close the window
        close_button = ctk.CTkButton(rewrite_window, text="Close", command=rewrite_window.destroy)
        close_button.pack(side=tk.BOTTOM)
     

    
  
        
