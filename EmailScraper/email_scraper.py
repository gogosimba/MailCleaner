import tkinter as tk
import os
from tkinter import ttk, scrolledtext, filedialog, Listbox, messagebox
from email_processor import EmailProcessor


class EmailScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Retrieval GUI")

        self.email_processor = EmailProcessor()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        output_folder_label = ttk.Label(frame, text="Output Folder:")
        output_folder_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.output_folder_entry = ttk.Entry(frame, width=50)
        self.output_folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        choose_folder_button = ttk.Button(
            frame, text="Choose Folder", command=self.choose_folder
        )
        choose_folder_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        recipient_label = ttk.Label(
            frame,
            text="Recipient:",
        )
        recipient_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.recipient_entry = ttk.Entry(frame, width=50)
        self.recipient_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        subject_label = ttk.Label(frame, text="Subject:")
        subject_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.subject_entry = ttk.Entry(frame, width=50)
        self.subject_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        progress_label = ttk.Label(frame, text="Progress:")
        progress_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

        self.progress_text = scrolledtext.ScrolledText(frame, height=5, width=60)
        self.progress_text.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=5,
            pady=5,
            sticky=(tk.W, tk.E, tk.N, tk.S),
        )

        subject_label = ttk.Label(frame, text="Email Subjects:")
        subject_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        self.subject_listbox = Listbox(frame, selectmode=tk.SINGLE, height=10, width=60)
        self.subject_listbox.grid(
            row=6,
            column=0,
            columnspan=3,
            padx=5,
            pady=5,
            sticky=(tk.W, tk.E, tk.N, tk.S),
        )

        self.subject_listbox.bind("<ButtonRelease-1>", self.on_subject_select)

        run_button = ttk.Button(frame, text="Run Script", command=self.run_script)
        run_button.grid(
            row=7, column=0, columnspan=1, pady=10, padx=(0, 2), sticky=tk.E
        )

        send_email_button = ttk.Button(
            frame, text="Send Email", command=self.send_email
        )
        send_email_button.grid(
            row=7, column=1, columnspan=1, pady=10, padx=(2, 0), sticky=tk.W
        )

        test_code_button = ttk.Button(frame, text="Test Code", command=self.test_code)
        test_code_button.grid(row=9, column=0, columnspan=3, pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, folder)

    def on_subject_select(self, event):
        selected_index = self.subject_listbox.curselection()[0]
        subject = self.subject_listbox.get(selected_index)
        original_body, removed_indices = self.email_processor.get_email_content(subject)
        cleaned_body = self.email_processor.get_cleaned_email(subject)

    def run_script(self):
        try:
            output_folder = self.output_folder_entry.get()
            self.email_processor.run_script(
                output_folder, self.progress_text, self.subject_listbox
            )
            messagebox.showinfo("Success", "Email retrieval completed.")
        except Exception as ex:
            messagebox.showerror("Error", f"An error occurred: {ex}")

    def send_email(self):
        try:
            recipient = self.recipient_entry.get()
            selected_index = self.subject_listbox.curselection()[0]
            subject = self.subject_listbox.get(selected_index)
            body = self.email_processor.get_cleaned_email(subject)

            self.email_processor.send_email(recipient, subject, body)
        except Exception as ex:
            messagebox.showerror(
                "Error", f"An error occurred while sending the email: {ex}"
            )

    def test_code(self):
        os.system("cls")
        print("Test code\n")
        selected_index = self.subject_listbox.curselection()[0]
        subject = self.subject_listbox.get(selected_index)
        email_body = self.email_processor.get_email_content(subject)
        print(self.email_processor.apply_cleaning_logic(email_body))
        """
        print("original email:\n\n")
        print(self.email_processor.get_email_content(subject))
        print("cleaned email:\n\n")
        print(self.email_processor.get_cleaned_email(subject))
        """


def main():
    root = tk.Tk()
    app = EmailScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
