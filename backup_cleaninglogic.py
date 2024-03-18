import re
def clean_volvouppdrag_email(email_body):
    email_body = re.sub(r"[_*]+", "", email_body)
    # Test with line removal for Levigo volvouppdrag to get rid of all the VB nonsense at the start...
    # Potential problem if "Ämne" or something is longer than 1 line...
    email_body = re.sub(r"Job Posting ID:\s+VOL[G|V]JP000\d{5}", "", email_body)
    lines_to_remove = ["From:", "Sent:", "To:", "Subject:", "Från:", "Skickat:", "Till:", "Ämne:"]
    for line_start in lines_to_remove:
        email_body = re.sub(rf"{line_start}.*\n?", "", email_body)
    if "Cars" in email_body:
        note_index = email_body.find("NOTE - Maximum 1 offer per assignment!")
        if note_index != -1:
            return email_body[:note_index]
    elif "SE_" in email_body:
        price_index = email_body.find("Price:")
        if price_index != -1:
            return email_body[:price_index]
    return email_body

def clean_combitech_email(email_body):
    email_body = re.sub(r"[_*]+", "", email_body)
    # Remove content leading up to and including "Beskrivning"
    # This is good, but does remove a titel as well, if thats a problem,
    # just change this to remove "Ni finns med på Combitechs distributionslista
    #för partner/konsultuppdrag och får därför denna förfrågan." I think...
    index = email_body.find("Beskrivning")
    if index != -1:
        email_body = email_body[index + len("Beskrivning"):]
    # Remove "Takpris" information, ensuring it matches 3 to 4 digits for the price
    takpris_match = re.search(r"Takpris: \d{3,4} SEK/h", email_body)
    if takpris_match:
        email_body = email_body[:takpris_match.start()]
    # Remove any ID that is between 3 and 6 digits long
    # Currenlty the "Takpris" removal is sufficient for nonsense like
    # 2 ID:s (0123, 0124). If a new ID variant is discovered UPDATE this... 
    id_match = re.search(r"ID: \d{3,6}", email_body)
    if id_match:
        email_body = email_body[:id_match.start()]
    # Remove content after "För ytterligare frågor kontakta"
    kontakt_match = email_body.find("För ytterligare frågor kontakta")
    if kontakt_match != -1:
        email_body = email_body[:kontakt_match]
    return email_body

def clean_polestar_email(email_body):
    email_body = re.sub(r"[_*]+", "", email_body)
    email_body = re.sub(r"Levigo ID: LP\d{3}", "", email_body)
    note_index = email_body.find("Please respond to")
    return email_body[:note_index] if note_index != -1 else email_body

def clean_cevt_email(email_body):
    email_body = re.sub(r"[_*]+", "", email_body)
    email_body = re.sub(r"RFQ ID:\s+RFQ\d{10}", "", email_body)
    email_body = re.sub(r"RFQ\d{10}", "", email_body)
    note_index = email_body.find("Please respond to")
    return email_body[:note_index] if note_index != -1 else email_body

def clean_AstaZero_email(email_body):
    email_body = re.sub(r"[_*]+", "", email_body)
    # Locate and keep everything from "AstaZero är världens första fullskaliga" onwards
    # intended to get rid of the nonsense in the beginning from VB, insted of line removal...
    astazero_index = email_body.find("AstaZero är världens första fullskaliga")
    if astazero_index != -1:
        email_body = email_body[astazero_index:]  # Keep from this phrase onwards
    # Remove "Pris" information
    pris_match = re.search(r"Pris:\s\d{2,4}-\d{2,4}kr/h", email_body)
    if pris_match:
        email_body = re.sub(r"Pris:\s\d{2,4}-\d{2,4}kr/h", "", email_body)
    # Remove content after "Vid frågor kontakta"
    kontakt_match = email_body.find("Vid frågor kontakta")
    if kontakt_match != -1:
        email_body = email_body[:kontakt_match]
    return email_body.strip()


def clean_subject(subject):
    if "Combitech" in subject:
        subject = re.sub(r"^.*söker", "", subject).strip()
        # Remove "(9 random digits)" pattern
        subject = re.sub(r"\(\d{9}\)", "", subject).strip()
    if "Volvouppdrag" in subject:
        # WORKS FOR BOTH CARS AND AB =)
        # Remove everything up to and including the job posting ID, then clean "SE_" if it appears
        subject = re.sub(r"^.*VOL[G|V]JP000\d{5}\s*", "", subject).strip()
        subject = re.sub(r"^SE_", "", subject).strip()
        # Replace underscores with spaces
        subject = subject.replace("_", " ")
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
    # Check for specific keywords in the subject or body
    if "Combitech" in email_body or "Combitech" in email_subject:
        return cleaned_subject, clean_combitech_email(email_body)
    elif "Volvouppdrag" in email_body or "Volvouppdrag" in email_subject:
        return cleaned_subject, clean_volvouppdrag_email(email_body)
    elif "Polestar" in email_body or "Polestar" in email_subject:
        return cleaned_subject, clean_polestar_email(email_body)
    elif "CEVT" in email_body or "CEVT" in email_subject:
        return cleaned_subject, clean_cevt_email(email_body)
    elif "AstaZero" in email_body or "AstaZero" in cleaned_subject:
        return cleaned_subject, clean_AstaZero_email(email_body)
        email_body = start_tag + email_body + end_tag
    return cleaned_subject, email_body

'''<!-- wp:html {"blockVisibility":{"controlSets":[{"id":1,"enable":true,"controls":{"userRole":{"visibilityByRole":"user-role","restrictedRoles":["administrator","contributor"]}}}]}} -->

KÄNSLIG INFO

<!-- /wp:html -->'''

'''AB Volvouppdrag: volvouppdrag@levigo.se
CARS Volvouppdrag: vccuppdrag@levigo.se
Combitech ex_1: För ytterligare frågor kontakta
Therese Bärås, therese.baras@combitech.com
Combitech ex_2: För ytterligare frågor kontakta
Mats Olofsson, mats.olofsson@combitech.se 
+46 734 37 41 07
Combitech ex_3:
For further information, please contact
Mats Olofsson, mats.olofsson@combitech.se  
+46 734 37 41 07
'''