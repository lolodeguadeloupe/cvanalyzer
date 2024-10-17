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
        "Profile": "",
        "Personal Information": "",
        "Education": "",
        "Work Experience": "",
        "Skills": ""
    }
    
    current_section = "Personal Information"
    lines = cv_text.split('\n')
    
    for line in lines:
        if re.match(r'profile|summary|objective', line.lower()):
            current_section = "Profile"
        elif re.match(r'education|qualifications', line.lower()):
            current_section = "Education"
        elif re.match(r'work experience|employment|professional experience', line.lower()):
            current_section = "Work Experience"
        elif re.match(r'skills|abilities|competencies', line.lower()):
            current_section = "Skills"
        
        sections[current_section] += line + "\n"
    
    return sections

def improve_cv(cv_text, analysis):
    sections = split_cv_into_sections(cv_text)
    improved_sections = {}

    section_prompts = {
        "Profile": "Improve the following profile section of a CV. Make it more concise, impactful, and highlight key strengths:",
        "Personal Information": "Organize and format the following personal information section of a CV:",
        "Education": "Enhance the following education section of a CV. Highlight key achievements and relevant coursework:",
        "Work Experience": "Improve the following work experience section of a CV. Use action verbs, quantify achievements, and focus on relevant responsibilities:",
        "Skills": "Refine the following skills section of a CV. Organize skills into categories and highlight the most relevant ones:"
    }

    for section_name, section_content in sections.items():
        if section_content.strip():
            prompt = (
                f"{section_prompts.get(section_name, 'Improve the following section of a CV:')}\n\n"
                f"{section_content}\n\n"
                "Improved version:"
            )
            try:
                response = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=prompt,
                    max_tokens=300,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                if isinstance(response, dict) and 'choices' in response:
                    improved_content = response['choices'][0]['text'].strip()
                else:
                    improved_content = section_content
                improved_sections[section_name] = improved_content
            except Exception as e:
                print(f"Error improving {section_name} section: {str(e)}")
                improved_sections[section_name] = section_content
        else:
            improved_sections[section_name] = section_content

    return improved_sections

def translate_cv(cv_text, target_language):
    translator = Translator()
    try:
        translated = translator.translate(cv_text, dest=target_language)
        if hasattr(translated, 'text'):
            return translated.text
        else:
            return cv_text
    except Exception as e:
        print(f"Error translating CV: {str(e)}")
        return cv_text
