import pdfplumber
import docx
from typing import Dict, List
from io import BytesIO
import spacy
from spacy.pipeline import EntityRuler
import pandas as pd
import re

nlp = spacy.load("en_core_web_sm")

# skills_patterns = [
#     {"label": "SKILL", "pattern": [{"LOWER": "python"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "sql"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "power bi"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "machine learning"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "data science"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "excel"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "tableau"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "communication"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "teamwork"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "pandas"}]},
#     {"label": "SKILL", "pattern": [{"LOWER": "numpy"}]},
# ]

def load_skills_from_csv(csv_path):
    df = pd.read_csv(csv_path, header=None)    
    skills = set()
    for row in df.values.flatten():  
        if pd.notna(row):  
            skills.add(str(row).strip().lower())
    return sorted(skills)


SECTION_HEADINGS = {
    "education": ["education", "degree", "academic","high school"],
    "certifications":["certifications"],
    "experience": ["experience", "internship", "intern", "work", "project","organized",],
    "achievements": ["achievements", "awards", "certificates", "honors", "key achievements","sports achievements"],
    "skills": ["skills", "technical skills", "expertise"]
}

def create_skill_patterns(skills_list):
    return [{"label": "SKILL", "pattern": skill} for skill in skills_list]

skills_list = load_skills_from_csv(r"C:\Users\Dell\ai-career-architect-demo\AI_Logic\UpdatedSkills.csv")
skills_patterns = create_skill_patterns(skills_list)

ruler = EntityRuler(nlp)
nlp.add_pipe(ruler, before="ner")
ruler.add_patterns(skills_patterns)

def parse_pdf(file: BytesIO) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def parse_docx(file: BytesIO) -> str:
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def clean_heading_text(text):#remove any non-alphanumeric characters from the beginning of a text string.
    return re.sub(r'^[^a-zA-Z0-9]+', '', text).strip()

def extract_section_blocks(lines: List[str]) -> Dict[str, Dict[str, str]]:
    section_blocks = {key: {"header": None, "raw": [], "cleaned": ""} for key in SECTION_HEADINGS}
    current_section = None

    for line in lines:
        line_stripped = line.strip()
        line_cleaned = clean_heading_text(line_stripped).lower()
        found_section = None
        for section, keywords in SECTION_HEADINGS.items():
            if any(kw in line_cleaned for kw in keywords):
                found_section = section
                break

        if found_section:
            current_section = found_section
            section_blocks[current_section]["header"] = clean_heading_text(line_stripped)
            continue  
        if current_section and line_stripped:
            section_blocks[current_section]["raw"].append(line_stripped)

    for section, content in section_blocks.items():
        raw_joined = " ".join(content["raw"])
        if section == "skills":
            cleaned = raw_joined.strip()
        else:
            section_doc = nlp(raw_joined)
            cleaned_tokens = [token.lemma_ for token in section_doc if not token.is_stop and not token.is_punct]
            cleaned = " ".join(cleaned_tokens).strip()

        section_blocks[section]["cleaned"] = cleaned

    return section_blocks

def extract_skills(section_text) -> List[str]:
    """Extract skills from section text using EntityRuler."""
    if isinstance(section_text, list):
        section_text = " ".join(section_text)
    doc = nlp(section_text)
    return list(set(ent.text for ent in doc.ents if ent.label_ == "SKILL"))

def extract_entities_from_section(section_text: str) -> Dict[str, List[str]]:
    section_doc = nlp(section_text)
    entities = {"ORG": [], "DATE": [], "PERSON": []}
    for ent in section_doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    return entities

def analyze_experience(section_text: str) -> Dict[str, List[str]]:
    doc = nlp(section_text)
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB" and not token.is_stop]
    return {"key_verbs": verbs}

SECTION_HEADERS = [
    "TECHNICAL SKILLS", "SKILLS", "EDUCATION", "CERTIFICATIONS",
    "PROFESSIONAL EXPERIENCE", "PROJECT EXPERIENCE",
    "EXTRACURRICULAR & ORGANIZATIONAL EXPERIENCE", "KEY ACHIEVEMENTS",
    "HIGH SCHOOL EDUCATION"
]

def split_header_and_content(section_list):
    """Splits out the section header from the content."""
    header = None
    content = []
    for item in section_list:
        if item.strip().upper() in SECTION_HEADERS and header is None:
            header = item.strip()
        else:
            content.append(item.strip())
    return header, content

def format_section(header, content_list):
    """Formats the section with the header on top and each content item on a new line."""
    if not header and not content_list:
        return ""
    lines = []
    if header:
        lines.append(header)
    lines.extend(content_list)
    return "\n".join(lines).strip()

def extract_resume_fields(text: str) -> Dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    blocks = extract_section_blocks(lines)

    enhanced_fields = {}
    for section, data in blocks.items():
        header, content = split_header_and_content(data["raw"])
        formatted_text = format_section(header, content)

        enhanced_fields[section] = {
            "header": header,                     
            "content": content,                   
            "formatted": formatted_text,          
            "entities": extract_entities_from_section(data["cleaned"]),
            "parsed_skills": extract_skills(content) if section == "skills" else [],
            "experience_analysis": analyze_experience(data["cleaned"]) if section == "experience" else {}
        }

    return enhanced_fields

def normalize_line(line: str) -> str:
    """
    Normalize text by removing extra spaces inside words
    and converting to lowercase.
    Example: "T E C H N I C A L  S K I L L S" -> "technical skills"
    """
    return re.sub(r'\s+', ' ', re.sub(r'(?<=\w)\s(?=\w)', '', line)).strip().lower()

def resume_combine_parser(file: BytesIO, filename: str) -> dict:
    file.seek(0)
    
    if filename.endswith(".pdf"):
        raw_text = parse_pdf(file)
    elif filename.endswith(".docx"):
        raw_text = parse_docx(file)
    else:
        raise ValueError("Unsupported file format")

    if not raw_text.strip():
        raise ValueError("Failed to extract raw text from resume.")

    pretty_result = {"full_text": raw_text.strip()}

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    section_blocks = {key: [] for key in SECTION_HEADINGS}
    current_section = None

    for line in lines:
        norm_line = normalize_line(line)
        found_section = False

        for section, keywords in SECTION_HEADINGS.items():
            if any(kw in norm_line for kw in keywords):
                current_section = section
                found_section = True
                break

        if not found_section and current_section:
            section_blocks[current_section].append(line)

    for section, content in section_blocks.items():
        if content:
            header = section.replace("_", " ").title()
            pretty_result[header] = content

    if "Skills" not in pretty_result:
        pretty_result["Skills"] = extract_skills(raw_text)

    return pretty_result
