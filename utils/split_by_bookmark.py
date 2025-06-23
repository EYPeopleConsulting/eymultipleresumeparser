import fitz
import os
import re

def split_pdf_by_bookmarks(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    bookmarks = [(entry[1], entry[2] - 1) for entry in toc] + [("END", len(doc))]
    os.makedirs(output_folder, exist_ok=True)

    resume_info = []

    for i in range(len(bookmarks) - 1):
        name, start = bookmarks[i]
        _, end = bookmarks[i + 1]
        safe_name = re.sub(r'[^\\w\\-_. ]', '', name).strip().replace(" ", "_")
        filename = f"{i+1:02d}_{safe_name}.pdf"
        filepath = os.path.join(output_folder, filename)

        sub_doc = fitz.open()
        for page in range(start, end):
            sub_doc.insert_pdf(doc, from_page=page, to_page=page)
        sub_doc.save(filepath)
        sub_doc.close()

        resume_info.append({
            'name': name,
            'filepath': filepath,
            'filename': filename
        })

    return resume_info
