import PyPDF2
from docx import Document
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from googletrans import Translator

nltk.download('punkt')
nltk.download('stopwords')

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

def improve_cv(cv_text, analysis):
    improved_cv = cv_text
    
    # Simple improvements based on analysis
    if 'Your CV seems short' in analysis['suggestions']:
        improved_cv += "\n\nAdditional Details:\nConsider expanding on your experiences and skills to provide a more comprehensive overview of your qualifications."
    
    if 'Try to use a wider variety of words' in analysis['suggestions']:
        improved_cv += "\n\nLanguage Enhancement:\nConsider using more diverse and impactful language to describe your achievements and responsibilities."
    
    if 'Consider adding more information about your work experience' in analysis['suggestions']:
        improved_cv += "\n\nWork Experience:\nEnsure that you have detailed your relevant work experiences, including job titles, companies, dates, and key responsibilities."
    
    if 'Make sure to highlight your skills in the CV' in analysis['suggestions']:
        improved_cv += "\n\nSkills Section:\nAdd a dedicated skills section to highlight your key competencies and technical abilities relevant to your target role."
    
    return improved_cv

def translate_cv(cv_text):
    translator = Translator()
    translated = translator.translate(cv_text, dest='en')
    return translated.text

