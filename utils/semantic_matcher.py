def match_skills(resume_text, mandatory_skills, optional_skills):
    resume_lower = resume_text.lower()
    found_mandatory = [s.strip() for s in mandatory_skills if s.strip().lower() in resume_lower]
    found_optional = [s.strip() for s in optional_skills if s.strip().lower() in resume_lower]

    missing_must = list(set(mandatory_skills) - set(found_mandatory))
    missing_opt = list(set(optional_skills) - set(found_optional))

    score = round((len(found_mandatory) / len(mandatory_skills)) * 100 if mandatory_skills else 0, 2)

    return {
        'found_mandatory': found_mandatory,
        'found_optional': found_optional,
        'missing_mandatory': missing_must,
        'missing_optional': missing_opt,
        'score': score
    }
