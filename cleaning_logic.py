import re

def clean_volvouppdrag_email(email_body):
    #email_body = email_body.replace("Volvo Group", "Ultra Group")
    #email_body_parts = email_body.split("***")
    #if len(email_body_parts) > 1:
    #    email_body = email_body_parts[0]
    # Remove the compliance sentence
    #compliance_sentence = ("As a supplier to Volvo Cars you agree to comply with our business rules, "
                           #"stating that we do not accept any type of backdoor selling from external parties. "
                           #"Please be aware that you are not allowed to present Candidates, CV’s and/or discuss "
                           #"and negotiate rate and terms directly with managers at Volvo Cars. Applications by "
                           #"e-mail will not be accepted due to GDPR.")
    #email_body = email_body.replace(compliance_sentence, "")
    email_body = re.sub(r"Job Posting ID:\s+VOL[G|V]JP000\d{5}", "", email_body)  
    if "CARS" in email_body:
        note_index = email_body.find("NOTE - Maximum 1 offer per assignment!")
        if note_index != -1:
            return email_body[:note_index]
    elif "AB" in email_body:
        price_index = email_body.find("Price:")
        if price_index != -1:
            return email_body[:price_index]
    return email_body

def clean_combitech_email(email_body):
    index = email_body.find("Beskrivning")
    if index != -1:
        email_body = email_body[index + len("Beskrivning"):]
    takpris_match = re.search(r"Takpris: \d{3} SEK/h", email_body)
    if takpris_match:
        return email_body[:takpris_match.start()]
    id_match = re.search(r"ID: \d{4}", email_body)
    return email_body[:id_match.start()] if id_match else email_body

def clean_polestar_email(email_body):
    email_body = re.sub(r"Levigo ID: LP\d{3}", "", email_body)
    note_index = email_body.find("Please respond to")
    return email_body[:note_index] if note_index != -1 else email_body

def clean_cevt_email(email_body):
    email_body = re.sub(r"RFQ ID:\s+RFQ\d{10}", "", email_body)
    email_body = re.sub(r"RFQ\d{10}", "", email_body)
    note_index = email_body.find("Please respond to")
    return email_body[:note_index] if note_index != -1 else email_body

def clean_AstaZero_email(email_body):
    pris_match = re.search(r"Pris:\s\d{3}-\d{3}kr/h", email_body)
    if pris_match:
        email_body = re.sub(r"Pris:\s\d{3}-\d{3}kr/h", "", email_body)
    kontakt_match = email_body.find("Vid frågor kontakta")
    if kontakt_match != -1:
        email_body = email_body[:kontakt_match]
    #email_body = email_body.replace("AstaZero", "Ultra Group")
    return email_body.strip()

def clean_subject(subject):
    if "Combitech" in subject:
        subject = re.sub(r"^.*söker", "", subject).strip()
        # Remove "(9 random digits)" pattern
        subject = re.sub(r"\b\d{9}\b", "", subject).strip()
    if "Volvouppdrag" in subject:
        #WORKS FOR BOTH CARS AND AB =)
        subject = re.sub(r"^.*VOL[G|V]JP000\d{5}", "", subject).strip()
    if "CEVT" in subject:
        subject = re.sub(r"^.*RFQ\d{10}", "", subject).strip()
    if "Polestar" in subject:
        subject = re.sub(r"^.*RFQ", "", subject).strip()
        subject = re.sub(r"LP\d{3}", "", subject).strip()
    # Additional cleaning for subjects, such as removing dashes
    if "AstaZero" in subject:
        subject = subject.replace("AstaZero", "Ultra Group")
    subject = subject.replace("-", "").strip()
    return subject

def apply_cleaning_logic(email_body, email_subject):
    print("Applying cleaning logic")
    cleaned_subject = clean_subject(email_subject)
    cleaned_content = None
    # Check for specific keywords in the subject or body
    if "Combitech" in email_body or "Combitech" in email_subject:
        cleaned_content = clean_combitech_email(email_body)
    elif "Volvouppdrag" in email_body or "Volvouppdrag" in email_subject:
        cleaned_content = clean_volvouppdrag_email(email_body)
    elif "Polestar" in email_body or "Polestar" in email_subject:
        cleaned_content = clean_polestar_email(email_body)
    elif "CEVT" in email_body or "CEVT" in email_subject:
        cleaned_content = clean_cevt_email(email_body)
    elif "AstaZero" in email_body or "AstaZero" in cleaned_subject:
        cleaned_content = clean_AstaZero_email(email_body)
    if cleaned_content is not None:
        return cleaned_subject, cleaned_content
    else:
        return None  # Indicate that no cleaning was applied 
