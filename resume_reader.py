import os
import json
import re
import pdfplumber
from docx import Document
from meta_ai_api import MetaAI

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format"

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def analyze_resume_with_meta_ai(resume_text):
    try:
        ai = MetaAI()
        prompt = (
            "You are a resume evaluation expert. Analyze the resume provided below and return a structured JSON object "
            "containing:\n\n"
            "1. 'overall_score': integer (0–100)\n"
            "2. 'section_scores': an object with:\n"
            "    - 'skills': integer (0–100)\n"
            "    - 'education': integer (0–100)\n"
            "    - 'experience': integer (0–100)\n"
            "    - 'formatting': integer (0–100)\n"
            "    - 'impact': integer (0–100)\n"
            "3. 'strengths': list of strings summarizing what the resume does well\n"
            "4. 'weaknesses': list of strings summarizing areas that need improvement\n"
            "5. 'recommendations': list of suggested improvements\n\n"
            "Resume:\n"
            f"{resume_text}"
        )

        response = ai.prompt(message=prompt)

        # If the response is wrapped in a "message" field, extract the JSON part
        if isinstance(response, dict) and "message" in response:
            # Try to extract the JSON portion from the message using regex
            match = re.search(r'\{[\s\S]*\}', response["message"])
            if match:
                clean_json = json.loads(match.group())
                return json.dumps(clean_json, indent=4)
            else:
                return json.dumps({"error": "Could not extract JSON from response"}, indent=4)

        # If it's already JSON or a stringified JSON
        if isinstance(response, str):
            response = json.loads(response)

        return json.dumps(response, indent=4)
        
    except Exception as e:
        print(f"[Meta AI ERROR] {e}")
        return json.dumps({"error": "Meta AI processing failed"}, indent=4)

# Example usage
if __name__ == "__main__":
    file_path = "resume1.pdf"  # or "resume.docx"
    resume_text = extract_text_from_file(file_path)
    
    if resume_text and "Unsupported file format" not in resume_text:
        result = analyze_resume_with_meta_ai(resume_text)
        print(result)
    else:
        print("Failed to extract text or unsupported file format.")
