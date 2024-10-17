import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from cv_analyzer import extract_text, analyze_cv, improve_cv, split_cv_into_sections
from pdf_generator import generate_pdf_with_same_design
import tempfile
from flask_sqlalchemy import SQLAlchemy
from models import db, User, CV
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_cvs = CV.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', cvs=user_cvs)

@app.route('/view_cv/<int:cv_id>')
@login_required
def view_cv(cv_id):
    cv = CV.query.get_or_404(cv_id)
    if cv.user_id != current_user.id:
        flash('You do not have permission to view this CV.')
        return redirect(url_for('dashboard'))
    return render_template('view_cv.html', cv=cv)

@app.route('/delete_cv/<int:cv_id>', methods=['POST'])
@login_required
def delete_cv(cv_id):
    cv = CV.query.get_or_404(cv_id)
    if cv.user_id != current_user.id:
        flash('You do not have permission to delete this CV.')
        return redirect(url_for('dashboard'))
    
    db.session.delete(cv)
    db.session.commit()
    flash('CV deleted successfully.')
    return redirect(url_for('dashboard'))

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
            original_sections = split_cv_into_sections(cv_text)
            improved_sections = improve_cv(cv_text, analysis)
            
            pdf_path = generate_pdf_with_same_design(improved_sections, filename)
            
            if current_user.is_authenticated:
                new_cv = CV(filename=filename, content=cv_text, analysis=analysis, improved_content=str(improved_sections), user_id=current_user.id, created_at=datetime.utcnow())
                db.session.add(new_cv)
                db.session.commit()
            
            return render_template('index.html', analysis=analysis, original_sections=original_sections, improved_sections=improved_sections, pdf_path=pdf_path)
        
        return render_template('index.html', error="Invalid file format")
    
    return render_template('index.html')

@app.route('/download_pdf/<path:filename>')
def download_pdf(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
