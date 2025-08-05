import openai
from dotenv import load_dotenv

load_dotenv(override=True)

def generate_resume_and_cover_letter(profile, job_description):
    prompt = f"""
You are a professional career coach and resume writer. Based on the user's profile and the job description, generate a highly tailored resume and cover letter.

USER PROFILE:
Full Name: {profile.full_name}
Email: {profile.email}
Phone: {profile.phone}
Education: {profile.education}
Experience: {profile.experience}
Skills: {profile.skills}
Achievements: {profile.achievements}

JOB DESCRIPTION:
{job_description}

Please respond in the following format:

[RESUME]
<Custom resume text>

[COVER LETTER]
<Custom cover letter text>
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",      
        messages=[
            {"role": "system", "content": "You are an expert career assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1800
    )

    output = response.choices[0].message.content

    try:
        resume = output.split("[COVER LETTER]")[0].replace("[RESUME]", "").strip()
        cover_letter = output.split("[COVER LETTER]")[1].strip()
    except IndexError:
        resume = output
        cover_letter = "Could not extract cover letter from output."

    return resume, cover_letter
