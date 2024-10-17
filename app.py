import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from cv_analyzer import extract_text, analyze_cv, improve_cv, translate_cv
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
            improved_cv = improve_cv(cv_text, analysis)
            translated_cv = translate_cv(improved_cv)
            
            return render_template('index.html', analysis=analysis, improved_cv=improved_cv, translated_cv=translated_cv)
        
        return render_template('index.html', error="Invalid file format")
    
    return render_template('index.html')

@app.route('/download/<cv_type>')
def download(cv_type):
    if cv_type not in ['improved', 'translated']:
        return "Invalid CV type", 400
    
    cv_content = request.args.get(cv_type + '_cv', '')
    if not cv_content:
        return "No CV content available", 400
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write(cv_content)
    
    return send_file(temp_file.name, as_attachment=True, download_name=f"{cv_type}_cv.txt")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
