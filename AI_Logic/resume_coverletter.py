from openai import OpenAI
from dotenv import load_dotenv
import openai
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv(override=True)
#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_tailored_resume_and_cover_letter(resume_text, jd_text):
    resume_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    resume_prompt = f"""
    You are a professional resume writer.
    Rewrite the following resume to align with the given job description.
    Keep it ATS-friendly and professional.

    Resume:
    {resume_text}

    Job Description:
    {jd_text}
    """

    #For openai
    # tailored_resume = openai.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": resume_prompt}],
    #     temperature=0.7
    # ).choices[0].message.content

    tailored_resume_response = resume_model.generate_content(
        resume_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7
        )
    )

    cover_letter_model = genai.GenerativeModel(model_name='gemini-1.5-flash')

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
    #For openai
    # cover_letter = openai.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role": "user", "content": cover_letter_prompt}],
    #     temperature=0.7
    # ).choices[0].message.content

    cover_letter_response = cover_letter_model.generate_content(
        cover_letter_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7
        )
    )

    cover_letter = cover_letter_response.text

    return tailored_resume_response, cover_letter
 