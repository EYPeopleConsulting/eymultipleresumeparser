from flask import Flask, render_template, request
import os
import socket
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
from utils.split_by_bookmark import split_pdf_by_bookmarks
from utils.extract_text import extract_text_and_info
from utils.semantic_matcher import match_skills
from utils.generate_report import save_results_to_excel, prepare_result_table
from utils.jd_reader import extract_text_from_jd

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "static/reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    jd_file = request.files['jd_file']
    resume_pdf = request.files['resume_pdf']
    mandatory_skills = [s.strip() for s in request.form['mandatory_skills'].split(',') if s.strip()]
    optional_skills = [s.strip() for s in request.form['optional_skills'].split(',') if s.strip()]

    jd_ext = os.path.splitext(jd_file.filename)[1].lower()
    jd_filename = f"jd{jd_ext}"
    jd_path = os.path.join(UPLOAD_FOLDER, jd_filename)
    resume_path = os.path.join(UPLOAD_FOLDER, "resumes.pdf")
    jd_file.save(jd_path)
    resume_pdf.save(resume_path)

    if os.path.getsize(jd_path) == 0:
        return "<h3 style='color:red'>❌ JD file is empty or corrupted. Please upload a valid PDF or Word file.</h3>"

    try:
        jd_text = extract_text_from_jd(jd_path)
    except Exception as e:
        return f"<h3 style='color:red'>❌ Failed to read JD file: {e}</h3>"

    try:
        resumes = split_pdf_by_bookmarks(resume_path, REPORT_FOLDER)
    except Exception as e:
        return f"<h3 style='color:red'>❌ Failed to split resume PDF: {e}</h3>"

    results = []
    for r in resumes:
        extracted = extract_text_and_info(r['filepath'])
        resume_text = extracted['text']
        email = extracted['email'] if extracted['email'] != "N/A" else next((w for w in resume_text.split() if "@" in w and "." in w), "N/A")
        phone = extracted['phone'] if extracted['phone'] != "N/A" else next((p for p in resume_text.split() if any(d.isdigit() for d in p) and len(p) >= 10), "N/A")

        skill_match = match_skills(resume_text, mandatory_skills, optional_skills)
        found_mandatory = skill_match['found_mandatory']
        found_optional = skill_match['found_optional']
        missing_must = skill_match['missing_mandatory']
        missing_opt = skill_match['missing_optional']

        mandatory_score = round((len(found_mandatory) / len(mandatory_skills)) * 100, 2) if mandatory_skills else 0.0
        optional_score = round((len(found_optional) / len(optional_skills)) * 100, 2) if optional_skills else 0.0
        total_score = round(0.7 * mandatory_score + 0.3 * optional_score, 2)

        tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = tfidf.fit_transform([jd_text, resume_text])
        jd_features = tfidf.get_feature_names_out()

        jd_words = set(tfidf_matrix[0].nonzero()[1])
        resume_words = set(tfidf_matrix[1].nonzero()[1])
        missing_keywords = [jd_features[i] for i in jd_words - resume_words]
        top_missing = ", ".join(missing_keywords[:30]) if missing_keywords else "None"

        results.append({
            'name': r['name'],
            'email': email,
            'phone': phone,
            'score': total_score,
            'mandatory_score': mandatory_score,
            'optional_score': optional_score,
            'missing_must': ", ".join(missing_must) if missing_must else "None",
            'missing_opt': ", ".join(missing_opt) if missing_opt else "None",
            'missing_jd': top_missing,
            'filename': r['filename'],
            'resume_link': f"/static/reports/{r['filename']}"
        })

    excel_path = os.path.join(REPORT_FOLDER, f"resume_report_{timestamp}.xlsx")
    save_results_to_excel(results, excel_path)

    return render_template('results.html', results=results, timestamp=timestamp)


@app.route('/results')
def results():
    return "<h3>Please analyze data before viewing results directly.</h3>"

# For Jupyter Notebook Launcher
def run_app_in_notebook():
    import nest_asyncio
    import threading

    nest_asyncio.apply()
    port = get_free_port()
    print(f"✅ Flask app running at: http://127.0.0.1:{port}")

    def run():
        app.run(port=port, debug=False, use_reloader=False)

    threading.Thread(target=run).start()
