from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_session import Session
from config import Config
from utils.auth import create_user, verify_user, login_required
from utils.blob_manager import BlobManager
import io

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

blob_manager = BlobManager()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('browse'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('register'))
        
        # Create user
        success, message = create_user(username, password)
        
        if not success:
            flash(message, 'danger')
            return redirect(url_for('register'))
        
        # Create blob container for user
        success, message = blob_manager.create_user_container(username)
        
        if not success:
            flash(f'User created but container failed: {message}', 'warning')
        else:
            flash('Account created successfully! Please login.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_user(username, password):
            session['username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('browse'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload'))
        
        # Check if file is PDF
        if not file.filename.lower().endswith('.pdf'):
            flash('Only PDF files are allowed', 'danger')
            return redirect(url_for('upload'))
        
        # Upload to blob storage
        username = session['username']
        success, message = blob_manager.upload_file(username, file, file.filename)
        
        if success:
            flash('File uploaded successfully!', 'success')
        else:
            flash(f'Upload failed: {message}', 'danger')
        
        return redirect(url_for('upload'))
    
    # GET request - show user's files
    username = session['username']
    files = blob_manager.list_user_files(username)
    
    return render_template('upload.html', files=files)

@app.route('/delete/<filename>')
@login_required
def delete_file(filename):
    username = session['username']
    success, message = blob_manager.delete_file(username, filename)
    
    if success:
        flash('File deleted successfully!', 'success')
    else:
        flash(f'Delete failed: {message}', 'danger')
    
    return redirect(url_for('upload'))

@app.route('/browse')
@login_required
def browse():
    all_files = blob_manager.list_all_files()
    return render_template('browse.html', files=all_files)

@app.route('/download/<container>/<filename>')
@login_required
def download_file(container, filename):
    file_data = blob_manager.download_file(container, filename)
    
    if file_data:
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    else:
        flash('File not found', 'danger')
        return redirect(url_for('browse'))

@app.route('/search')
@login_required
def search():
    # We'll implement AI search later
    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
