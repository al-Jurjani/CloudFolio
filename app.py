from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
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
    username = session['username']
    
    if request.method == 'POST':
        folder_name = request.form.get('folder_name')
        
        if not folder_name:
            flash('Please select a folder', 'danger')
            return redirect(url_for('upload'))
        
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
        success, message = blob_manager.upload_file_to_folder(username, file, file.filename, folder_name)
        
        if success:
            flash('File uploaded successfully!', 'success')
        else:
            flash(f'Upload failed: {message}', 'danger')
        
        return redirect(url_for('upload'))
    
    # GET request - show user's folders
    folders = blob_manager.list_user_folders(username)
    
    return render_template('upload.html', folders=folders)

@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    username = session['username']
    folder_name = request.form.get('folder_name')
    
    if not folder_name:
        flash('Folder name is required', 'danger')
        return redirect(url_for('upload'))
    
    success, message = blob_manager.create_folder(username, folder_name)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('upload'))

@app.route('/folder/<folder_name>')
@login_required
def view_folder(folder_name):
    username = session['username']
    files = blob_manager.list_files_in_folder(username, folder_name)
    
    return render_template('folder.html', folder_name=folder_name, files=files)

@app.route('/delete/<folder_name>/<filename>')
@login_required
def delete_file(folder_name, filename):
    username = session['username']
    success, message = blob_manager.delete_file_from_folder(username, folder_name, filename)
    
    if success:
        flash('File deleted successfully!', 'success')
    else:
        flash(f'Delete failed: {message}', 'danger')
    
    return redirect(url_for('view_folder', folder_name=folder_name))

@app.route('/browse')
@login_required
def browse():
    # List all users (containers)
    containers = list(blob_manager.blob_service_client.list_containers())
    users = [container.name for container in containers]
    
    return render_template('browse.html', users=users)

@app.route('/browse/<username>')
@login_required
def browse_user(username):
    # Show folders for a specific user
    folders = blob_manager.list_user_folders(username)
    
    return render_template('browse_user.html', username=username, folders=folders)

@app.route('/browse/<username>/<folder_name>')
@login_required
def browse_folder(username, folder_name):
    # Show files in a user's folder
    files = blob_manager.list_files_in_folder(username, folder_name)
    
    return render_template('browse_folder.html', username=username, folder_name=folder_name, files=files)

@app.route('/download/<container>/<path:filepath>')
@login_required
def download_file(container, filepath):
    file_data = blob_manager.download_file(container, filepath)
    
    if file_data:
        filename = filepath.split('/')[-1]  # Get just the filename
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