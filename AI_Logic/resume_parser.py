import pdfplumber
import docx
from typing import Dict,Set
from io import BytesIO
import spacy
from typing import List

nlp = spacy.load("en_core_web_sm")

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


SECTION_HEADINGS = {
    "education": ["education", "certifications"],
    "experience": ["experience", "internship", "intern", "work", "project"],
    "achievements": ["achievements", "awards", "certificates", "honors", "key achievements"],
    "skills":["skills"]
}

def extract_section_blocks(lines: List[str]) -> Dict[str, str]:
    section_blocks = {key: [] for key in SECTION_HEADINGS}
    current_section = None

    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        for section, keywords in SECTION_HEADINGS.items():
            if any(kw in line_lower for kw in keywords):
                current_section = section
                break
        if current_section:
            section_blocks[current_section].append(line)

    for section in section_blocks:
        # section_blocks[section] = "\n".join(section_blocks[section]).strip("•o- \n")
        section_blocks[section] = " ".join(section_blocks[section]).strip("•o- \n")

    return section_blocks

def extract_resume_fields(text: str) -> Dict[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    blocks = extract_section_blocks(lines)
    
    fields = {
        "education": blocks.get("education", ""),
        "skills":blocks.get("skills",""),
        "experience": blocks.get("experience", ""),
        "achievements": blocks.get("achievements", "")
    }

    return fields


def resume_combine_parser(file: BytesIO, filename: str) -> Dict:
    file.seek(0)  # Rewind file pointer to start
    
    if filename.endswith(".pdf"):
        raw_text = parse_pdf(file)
    elif filename.endswith(".docx"):
        raw_text = parse_docx(file)
    else:
        raise ValueError("Unsupported file format")

    if not raw_text.strip():
        raise ValueError("Failed to extract raw text from resume.")

    fields = extract_resume_fields(raw_text)
    fields["raw_text"] = raw_text  

    return fields