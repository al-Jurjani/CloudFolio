import json
import os
from functools import wraps
from flask import session, redirect, url_for, flash


def load_users():
    """Load users from JSON file"""
    if not os.path.exists('users.json'):
        return {}

    with open('users.json', 'r') as f:
        return json.load(f)


def save_users(users):
    """Save users to JSON file"""
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)


def create_user(username, password):
    """Create a new user"""
    users = load_users()

    if username in users:
        return False, "Username already exists"

    users[username] = password
    save_users(users)
    return True, "User created successfully"


def verify_user(username, password):
    """Verify user credentials"""
    users = load_users()
    return users.get(username) == password


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function