"""
Authentication routes for Prophere.
Handles user registration, login, and logout.
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from . import auth_bp


@auth_bp.route('/')
def index():
    return render_template('index.html')


@auth_bp.route('/hello')
def hello():
    return '<h1>Hello World! Flask is working!</h1>'


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validate inputs
        if not name or len(name) < 2 or len(name) > 100:
            flash('Name must be 2-100 characters long.', 'error')
            return render_template('register.html')
        
        if not email or '@' not in email or len(email) > 120:
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user_role = request.form.get('user_role', 'attendee')
        
        # Validate inputs
        if not email or '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('login.html')
        
        if not password:
            flash('Please enter your password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Check if user role matches the selected login role
            is_admin = user.is_admin
            
            if user_role == 'manager' and not is_admin:
                flash('Access denied! You are not authorized to log in as an Event Manager.', 'error')
                return render_template('login.html')
            elif user_role == 'attendee' and is_admin:
                flash('Access denied! Administrators must log in as Event Manager.', 'error')
                return render_template('login.html')
            
            login_user(user)
            
            if is_admin:
                flash('Login successful! Welcome, Event Manager.', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Login successful! Welcome, Event Attendee.', 'success')
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))
