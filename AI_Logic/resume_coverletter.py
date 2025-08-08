from openai import OpenAI
from dotenv import load_dotenv
import openai

load_dotenv(override=True)

def generate_tailored_resume_and_cover_letter(resume_text, jd_text):
    resume_prompt = f"""
    You are a professional resume writer.
    Rewrite the following resume to align with the given job description.
    Keep it ATS-friendly and professional.

    Resume:
    {resume_text}

    Job Description:
    {jd_text}
    """
    tailored_resume = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": resume_prompt}],
        temperature=0.7
    ).choices[0].message.content

    # Cover Letter
    cover_letter_prompt = f"""
    You are an expert career consultant.
    Write a personalized, professional cover letter for the job description below,
    using the candidate's experience from the given resume.

    Resume:
    {resume_text}

    Job Description:
    {jd_text}
    """
    cover_letter = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": cover_letter_prompt}],
        temperature=0.7
    ).choices[0].message.content

    return tailored_resume, cover_letter