import PyPDF2
from docx import Document
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from googletrans import Translator
import openai
import os
import re

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def extract_text(file_path, file_type):
    if file_type == 'pdf':
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
    elif file_type == 'docx':
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type")
    
    return text

def analyze_cv(cv_text):
    words = word_tokenize(cv_text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    word_freq = nltk.FreqDist(filtered_words)
    
    analysis = {
        'word_count': len(words),
        'unique_words': len(set(filtered_words)),
        'most_common': word_freq.most_common(5)
    }
    
    # Simple improvement suggestions
    suggestions = []
    if analysis['word_count'] < 300:
        suggestions.append("Your CV seems short. Consider adding more details about your experiences and skills.")
    if analysis['unique_words'] < 100:
        suggestions.append("Try to use a wider variety of words to make your CV more engaging.")
    if 'experience' not in filtered_words:
        suggestions.append("Consider adding more information about your work experience.")
    if 'skills' not in filtered_words:
        suggestions.append("Make sure to highlight your skills in the CV.")
    
    analysis['suggestions'] = suggestions
    
    return analysis

def split_cv_into_sections(cv_text):
    sections = {
        "Personal Information": "",
        "Education": "",
        "Work Experience": "",
        "Skills": ""
    }
    
    current_section = "Personal Information"
    lines = cv_text.split('\n')
    
    for line in lines:
        if re.match(r'education|qualifications', line.lower()):
            current_section = "Education"
        elif re.match(r'work experience|employment|professional experience', line.lower()):
            current_section = "Work Experience"
        elif re.match(r'skills|abilities|competencies', line.lower()):
            current_section = "Skills"
        
        sections[current_section] += line + "\n"
    
    return sections

def improve_cv(cv_text, analysis):
    sections = split_cv_into_sections(cv_text)
    improved_sections = []

    for section_name, section_content in sections.items():
        prompt = f"""Improve the following {section_name} section of a CV. Make it more professional, concise, and impactful:

{section_content}

Improved version:"""
        
        try:
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.7,
            )
            improved_section = response.choices[0].text.strip()
            improved_sections.append(f"{section_name}:\n{improved_section}")
        except Exception as e:
            print(f"Error improving {section_name} section: {str(e)}")
            improved_sections.append(f"{section_name}:\n{section_content}")

    return "\n\n".join(improved_sections)

def translate_cv(cv_text):
    translator = Translator()
    translated = translator.translate(cv_text, dest='en')
    return translated.text
