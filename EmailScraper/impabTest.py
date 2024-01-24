import imaplib
import email
from email.header import decode_header

def safe_decode(header):
    decoded, encoding = decode_header(header)[0]
    if isinstance(decoded, bytes):
        try:
            decoded = decoded.decode(encoding or "utf-8")
        except UnicodeDecodeError:
            decoded = decoded.decode("latin-1", errors="replace")
    return decoded

def fetch_emails(folder):
    outlook_server = imaplib.IMAP4_SSL('imap-mail.outlook.com', 993)
    outlook_server.login('LIA-ultragroup@outlook.com', 'Lia2023EC')
    typ, folders = outlook_server.list()
    typ, data = outlook_server.select(folder)
    if typ == 'OK':
        print(f'Fetching emails from folder: {folder}')
        typ, msg_nums = outlook_server.search(None, 'ALL')
        if typ == 'OK':
            for num in msg_nums[0].split():
                typ, msg_data = outlook_server.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                # Extract subject
                subject = safe_decode(msg["Subject"])

                # Extract plaintext body
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True)
                            print(f'Subject: {subject}\nMessage:\n{body.decode("utf-8", "replace")}')
                else:
                    body = msg.get_payload(decode=True)
                    print(f'Subject: {subject}\nMessage:\n{body.decode("utf-8", "replace")}')
        else:
            print(f'Error fetching emails from folder {folder}')
    else:
        print(f'Error selecting folder {folder}')
    outlook_server.logout()







