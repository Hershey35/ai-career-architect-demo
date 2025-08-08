def match_resume_to_jd(resume_text, jd_text):
    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    common = resume_words.intersection(jd_words)
    score = (len(common) / len(jd_words)) * 100 if jd_words else 0
    return round(score, 2), list(common)