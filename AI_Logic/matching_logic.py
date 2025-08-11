# from flask import Blueprint, request, jsonify
# from models import UploadedResume
# import spacy

# import re
# # import nltk
# # nltk.download('stopwords')

# from nltk.corpus import stopwords

# stop_words = set(stopwords.words('english'))

# def match_resume_to_jd(resume_text: str, jd_text: str):
#     resume_words = {
#         w for w in re.findall(r'\w+', resume_text.lower()) if w not in stop_words
#     }
#     jd_words = {
#         w for w in re.findall(r'\w+', jd_text.lower()) if w not in stop_words
#     }
#     if not resume_words or not jd_words:
#         return 0, []
#     matched_terms = sorted(resume_words.intersection(jd_words))
#     match_score = round((len(matched_terms) / len(jd_words)) * 100, 2)
#     return match_score, matched_terms

# matching_logic.py
import openai
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv("OPENAI_API_KEY")

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def match_resume_to_jd_openai(resume_text, jd_text):
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    resume_emb = get_embedding(resume_text)
    jd_emb = get_embedding(jd_text)

    similarity = cosine_similarity(resume_emb, jd_emb)
    return round(similarity * 100, 2)  # percentage

