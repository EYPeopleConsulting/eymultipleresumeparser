import fitz
from docx import Document

def extract_text_from_jd(jd_path):
    if jd_path.endswith(".pdf"):
        try:
            with fitz.open(jd_path) as jd_doc:
                return "\n".join([page.get_text() for page in jd_doc])
        except Exception as e:
            raise Exception(f"PDF read error: {e}")

    elif jd_path.endswith(".docx"):
        try:
            doc = Document(jd_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise Exception(f"DOCX read error: {e}")

    else:
        raise Exception("Unsupported JD file type: must be PDF or DOCX")
