from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Event, Membership, Resume
import os
from datetime import datetime

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/nfc_networking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('../instance', exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello')
def hello():
    return '<h1>Hello World! Flask is working!</h1>'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
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
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Redirect admins to admin dashboard
    if current_user.is_administrator():
        return redirect(url_for('admin_dashboard'))
    
    # Get user's memberships and resumes
    memberships = Membership.query.filter_by(user_id=current_user.id).all()
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard.html', memberships=memberships, resumes=resumes)

@app.route('/join_event', methods=['POST'])
@login_required
def join_event():
    event_code = request.form['event_code'].strip()
    
    # Find event by code
    event = Event.query.filter_by(code=event_code).first()
    
    if not event:
        flash(f'Event code "{event_code}" does not exist. Please check the code and try again.', 'info')
        return redirect(url_for('dashboard'))
    
    # Check if user is already a member
    existing_membership = Membership.query.filter_by(
        user_id=current_user.id, 
        event_id=event.id
    ).first()
    
    if existing_membership:
        flash(f'You are already a member of "{event.name}"!', 'info')
        return redirect(url_for('dashboard'))
    
    # Create new membership
    membership = Membership(
        user_id=current_user.id,
        event_id=event.id
    )
    db.session.add(membership)
    db.session.commit()
    
    flash(f'Successfully joined "{event.name}"!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/upload_resume/<int:event_id>', methods=['GET', 'POST'])
@login_required
def upload_resume(event_id):
    # Check if user is a member of this event
    membership = Membership.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('dashboard'))
    
    event = Event.query.get(event_id)
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('upload_resume', event_id=event_id))
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('upload_resume', event_id=event_id))
        
        # Check file type
        allowed_extensions = {'pdf', 'doc', 'docx'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            flash('Only PDF, DOC, and DOCX files are allowed!', 'error')
            return redirect(url_for('upload_resume', event_id=event_id))
        
        # Check file size (16MB max)
        if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
            flash('File too large! Maximum size is 16MB.', 'error')
            return redirect(url_for('upload_resume', event_id=event_id))
        
        file.seek(0)  # Reset file pointer
        
        # Create secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{current_user.id}_{event_id}_{timestamp}_{filename}"
        
        # Create event-specific upload directory
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(event_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Check if user already has a resume for this event
        existing_resume = Resume.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).first()
        
        if existing_resume:
            # Update existing resume
            existing_resume.filename = unique_filename
            existing_resume.original_name = file.filename
            existing_resume.mime_type = file.content_type
            existing_resume.file_size = len(file.read())
            existing_resume.uploaded_at = datetime.utcnow()
            file.seek(0)
        else:
            # Create new resume record
            resume = Resume(
                user_id=current_user.id,
                event_id=event_id,
                filename=unique_filename,
                original_name=file.filename,
                mime_type=file.content_type,
                file_size=len(file.read())
            )
            db.session.add(resume)
        
        db.session.commit()
        flash(f'Resume uploaded successfully for "{event.name}"!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upload_resume.html', event=event)

@app.route('/view_resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    # Get the resume record
    resume = Resume.query.get(resume_id)
    
    if not resume:
        flash('Resume not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You are not authorized to view this resume!', 'error')
        return redirect(url_for('dashboard'))
    
    # Construct the file path
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(resume.event_id), resume.filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('Resume file not found!', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('view_resume.html', resume=resume, file_path=file_path)

@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    # Extract event_id and user_id from filename
    parts = filename.split('/')
    if len(parts) < 2:
        flash('Invalid file path!', 'error')
        return redirect(url_for('dashboard'))
    
    event_id = parts[0]
    actual_filename = '/'.join(parts[1:])
    
    # Find the resume record
    resume = Resume.query.filter_by(filename=actual_filename, event_id=event_id).first()
    
    if not resume:
        flash('File not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You are not authorized to access this file!', 'error')
        return redirect(url_for('dashboard'))
    
    # Construct the full file path
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('File not found on server!', 'error')
        return redirect(url_for('dashboard'))
    
    # Serve the file
    return send_file(file_path, as_attachment=False)

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('Admin access required!', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Get statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_events = Event.query.count()
    total_memberships = Membership.query.count()
    total_resumes = Resume.query.count()
    
    # Get recent events
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    # Get recent users (excluding admins)
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_events=total_events,
                         total_memberships=total_memberships,
                         total_resumes=total_resumes,
                         recent_events=recent_events,
                         recent_users=recent_users)

@app.route('/admin/events')
@login_required
@admin_required
def admin_events():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/events.html', events=events)

@app.route('/admin/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_event():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        description = request.form.get('description', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Validate description word count
        if description:
            word_count = len(description.split())
            if word_count > 300:
                flash('Description cannot exceed 300 words. Please shorten your description.', 'error')
                return render_template('admin/create_event.html')
        
        # Check if event code already exists
        if Event.query.filter_by(code=code).first():
            flash(f'Event code "{code}" already exists!', 'error')
            return render_template('admin/create_event.html')
        
        # Create new event
        event = Event(
            name=name,
            code=code,
            description=description if description else None,
            start_date=datetime.strptime(start_date, '%Y-%m-%d') if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        )
        db.session.add(event)
        db.session.commit()
        
        flash(f'Event "{name}" created successfully!', 'success')
        return redirect(url_for('admin_events'))
    
    return render_template('admin/create_event.html')

@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.name = request.form['name']
        event.code = request.form['code']
        description = request.form.get('description', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Validate description word count
        if description:
            word_count = len(description.split())
            if word_count > 300:
                flash('Description cannot exceed 300 words. Please shorten your description.', 'error')
                return render_template('admin/edit_event.html', event=event)
        
        # Check if event code already exists (excluding current event)
        existing_event = Event.query.filter_by(code=event.code).first()
        if existing_event and existing_event.id != event.id:
            flash(f'Event code "{event.code}" already exists!', 'error')
            return render_template('admin/edit_event.html', event=event)
        
        event.description = description if description else None
        event.start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        event.end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        db.session.commit()
        flash(f'Event "{event.name}" updated successfully!', 'success')
        return redirect(url_for('admin_events'))
    
    return render_template('admin/edit_event.html', event=event)

@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Delete associated files
    resumes = Resume.query.filter_by(event_id=event_id).all()
    for resume in resumes:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(event_id), resume.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Delete associated records
    Membership.query.filter_by(event_id=event_id).delete()
    Resume.query.filter_by(event_id=event_id).delete()
    
    # Delete event
    db.session.delete(event)
    db.session.commit()
    
    flash(f'Event "{event.name}" deleted successfully!', 'success')
    return redirect(url_for('admin_events'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id:
        flash('You cannot remove admin status from yourself!', 'error')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'removed'
    flash(f'Admin status {status} for {user.name}!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin_users'))
    
    # Store user name for flash message
    user_name = user.name
    
    # Delete associated data first
    # Delete memberships
    Membership.query.filter_by(user_id=user_id).delete()
    
    # Delete resumes and associated files
    resumes = Resume.query.filter_by(user_id=user_id).all()
    for resume in resumes:
        # Delete the file from filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(resume.event_id), resume.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Delete resume records
    Resume.query.filter_by(user_id=user_id).delete()
    
    # Finally delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user_name} has been deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

def create_sample_events():
    """Create sample events for testing"""
    sample_events = [
        {
            'name': 'NYUAD Career Fair 2025', 
            'code': 'NYUAD2025',
            'description': 'Join us for the largest career fair at NYU Abu Dhabi! Connect with top employers from various industries including technology, finance, consulting, and more. This event brings together students, recent graduates, and industry professionals for meaningful networking opportunities and career exploration.'
        },
        {
            'name': 'Tech Conference Dubai', 
            'code': 'TECH2025',
            'description': 'The premier technology conference in the Middle East featuring cutting-edge innovations, AI developments, and digital transformation strategies. Network with tech leaders, entrepreneurs, and developers while exploring the latest trends in software development, cybersecurity, and emerging technologies.'
        },
        {
            'name': 'Startup Networking Event', 
            'code': 'STARTUP2025',
            'description': 'A dynamic networking event designed for entrepreneurs, investors, and startup enthusiasts. Share ideas, find co-founders, connect with potential investors, and learn from successful startup founders. Perfect for anyone looking to launch their next venture or join the startup ecosystem.'
        }
    ]
    
    for event_data in sample_events:
        existing_event = Event.query.filter_by(code=event_data['code']).first()
        if not existing_event:
            event = Event(
                name=event_data['name'],
                code=event_data['code'],
                description=event_data['description']
            )
            db.session.add(event)
    
    # Create a default admin user if no users exist
    if User.query.count() == 0:
        admin_user = User(
            name='Admin User',
            email='admin@nfcnetworking.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
    
    db.session.commit()

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        create_sample_events()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    # For development: initialize database if it doesn't exist
    if not os.path.exists('instance/nfc_networking.db'):
        init_db()
    app.run(debug=True)
