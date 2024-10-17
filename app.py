import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from cv_analyzer import extract_text, analyze_cv, improve_cv, translate_cv
from pdf_generator import generate_pdf_with_same_design
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error="No selected file")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                cv_text = extract_text(temp_file.name, filename.split('.')[-1])
            
            analysis = analyze_cv(cv_text)
            improved_sections = improve_cv(cv_text, analysis)
            
            # Convert improved sections back to text
            improved_cv_text = "\n\n".join([f"{section}:\n{content}" for section, content in improved_sections.items()])
            
            # Generate PDF with the same design
            pdf_path = generate_pdf_with_same_design(improved_sections, filename)
            
            return render_template('index.html', analysis=analysis, improved_sections=improved_sections, pdf_path=pdf_path)
        
        return render_template('index.html', error="Invalid file format")
    
    return render_template('index.html')

@app.route('/download_pdf/<path:filename>')
def download_pdf(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
