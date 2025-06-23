import fitz
import re

def extract_text_and_info(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()

    email_match = re.findall(r'[\\w\\.-]+@[\\w\\.-]+', text)
    phone_match = re.findall(r'\\+?\\d[\\d\\s().-]{8,}\\d', text)

    return {
        'text': text,
        'email': email_match[0] if email_match else "N/A",
        'phone': phone_match[0] if phone_match else "N/A"
    }
