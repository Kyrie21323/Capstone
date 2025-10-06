from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Event, Membership, Resume, Match, UserInteraction
import os
from datetime import datetime

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/nfc_networking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
print(f"Upload folder set to: {app.config['UPLOAD_FOLDER']}")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db, directory='../migrations')
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
        user_role = request.form.get('user_role', 'attendee')
        
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
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful! Welcome, Event Attendee.', 'success')
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
    keywords = request.form.get('keywords', '').strip()
    
    # Validate event code
    if not event_code:
        flash('Please enter an event code.', 'error')
        return redirect(url_for('dashboard'))
    
    # Validate keywords
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        if len(keyword_list) < 2:
            flash('Please enter at least 2 keywords. Type keywords and press Enter to create tags.', 'error')
            return redirect(url_for('dashboard'))
    else:
        flash('Please enter your areas of interest (at least 2 keywords).', 'error')
        return redirect(url_for('dashboard'))
    
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
    
    # Create new membership with keywords
    membership = Membership(
        user_id=current_user.id,
        event_id=event.id,
        keywords=keywords
    )
    db.session.add(membership)
    db.session.commit()
    
    flash(f'Successfully joined "{event.name}" with interests: {", ".join(keyword_list)}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/leave_event', methods=['POST'])
@login_required
def leave_event():
    event_id = request.form['event_id']
    
    # Find the membership
    membership = Membership.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('dashboard'))
    
    event = Event.query.get(event_id)
    event_name = event.name if event else 'Unknown Event'
    
    try:
        # Delete associated resume and file if exists
        resume = Resume.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).first()
        
        if resume:
            # Delete the resume file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(event_id), resume.filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted resume file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete resume file {file_path}: {str(e)}")
            
            # Delete resume record from database
            db.session.delete(resume)
        
        # Delete the membership
        db.session.delete(membership)
        db.session.commit()
        
        flash(f'Successfully left "{event_name}"! Your resume has been removed.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error leaving event: {str(e)}', 'error')
        print(f"Error in leave_event: {str(e)}")
    
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
        print(f"Creating upload directory: {upload_dir}")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        print(f"Saving file to: {file_path}")
        file.save(file_path)
        print(f"File saved successfully!")
        
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
        flash(f'Document uploaded successfully for "{event.name}"!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upload_resume.html', event=event)

@app.route('/view_resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    # Get the resume record
    resume = Resume.query.get(resume_id)
    
    if not resume:
        flash('Document not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You are not authorized to view this document!', 'error')
        return redirect(url_for('dashboard'))
    
    # Construct the file path
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(resume.event_id), resume.filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('Document file not found!', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('view_resume.html', resume=resume, file_path=file_path)

@app.route('/delete_resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    # Get the resume record
    resume = Resume.query.get(resume_id)
    
    if not resume:
        flash('Document not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You are not authorized to delete this document!', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Delete the resume file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(resume.event_id), resume.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted resume file: {file_path}")
        
        # Delete resume record from database
        db.session.delete(resume)
        db.session.commit()
        
        flash('Document deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Failed to delete resume {resume_id}: {str(e)}")
        flash('Failed to delete document. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/update_keywords', methods=['POST'])
@login_required
def update_keywords():
    event_id = request.form.get('event_id')
    keywords = request.form.get('keywords')
    
    if not event_id:
        flash('Event ID is required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Find the membership
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not membership:
        flash('You are not a member of this event.', 'error')
        return redirect(url_for('dashboard'))
    
    # Validate keywords
    if not keywords or len(keywords.strip()) == 0:
        flash('Please enter at least 2 keywords.', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse keywords (comma-separated)
    keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
    
    if len(keyword_list) < 2:
        flash('Please enter at least 2 keywords.', 'error')
        return redirect(url_for('dashboard'))
    
    # Update keywords
    membership.keywords = keywords.strip()
    db.session.commit()
    
    flash('Keywords updated successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/event/<int:event_id>/matching')
@login_required
def event_matching(event_id):
    # Get the event
    event = Event.query.get(event_id)
    
    if not event:
        flash('Event not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if user is a member of this event
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all other users who are members of this event (excluding current user)
    other_memberships = Membership.query.filter(
        Membership.event_id == event_id,
        Membership.user_id != current_user.id
    ).all()
    
    if not other_memberships:
        # No other members to match with
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=[],
                             no_matches_reason='no_attendees')
    
    # Filter out users that current user has already interacted with
    interacted_user_ids = set()
    interactions = UserInteraction.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).all()
    for interaction in interactions:
        interacted_user_ids.add(interaction.target_user_id)
    
    # Remove already interacted users from potential matches
    available_memberships = [mem for mem in other_memberships if mem.user_id not in interacted_user_ids]
    
    if not available_memberships:
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=[],
                             no_matches_reason='no_similar_interests')
    
    # Import matching engine
    try:
        from matching_engine import matching_engine
        
        # Prepare current user data for matching
        current_user_resume = Resume.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        current_user_doc_text = ""
        
        if current_user_resume:
            # Extract text from current user's document
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(event_id), current_user_resume.filename)
            current_user_doc_text = matching_engine.extract_text_from_document(file_path)
        
        current_user_data = {
            'user_id': current_user.id,
            'keywords': membership.get_keywords_list(),
            'document_text': current_user_doc_text
        }
        
        # Prepare all other users data for matching
        all_users_data = []
        for mem in available_memberships:
            user = mem.user
            user_resume = Resume.query.filter_by(user_id=user.id, event_id=event_id).first()
            user_doc_text = ""
            
            if user_resume:
                # Extract text from user's document
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(event_id), user_resume.filename)
                user_doc_text = matching_engine.extract_text_from_document(file_path)
            
            user_data = {
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'keywords': mem.get_keywords_list(),
                'document_text': user_doc_text,
                'has_resume': user_resume is not None,
                'resume_name': user_resume.original_name if user_resume else None,
                'joined_at': mem.joined_at.strftime('%B %Y') if mem.joined_at else 'Recently'
            }
            all_users_data.append(user_data)
        
        # Find best matches using intelligent algorithm
        best_matches = matching_engine.find_best_matches(current_user_data, all_users_data, top_k=20)
        
        # Debug: Print matching results
        print(f"DEBUG: Found {len(best_matches)} intelligent matches")
        for match_data, score in best_matches:
            print(f"  - {match_data['name']}: {score:.3f} (keywords: {match_data['keywords']})")
        
        # Debug: Print similarity statistics for all users
        print(f"\nDEBUG: Similarity Statistics:")
        print(f"  Current user keywords: {current_user_data['keywords']}")
        print(f"  Current user has document: {bool(current_user_data['document_text'])}")
        
        for user_data in all_users_data:
            print(f"  - {user_data['name']}:")
            print(f"    Keywords: {user_data['keywords']}")
            print(f"    Has document: {bool(user_data.get('document_text', '').strip())}")
            
            # Calculate total score (this will also print the strategy used)
            total_score = matching_engine.calculate_match_score(current_user_data, user_data)
            
            print(f"    Above threshold (0.26): {'YES' if total_score > 0.26 else 'NO'}")
            print()
        
        # Extract just the user data (without scores) for the template
        potential_matches = [match_data for match_data, score in best_matches]
        
        # Only show intelligent matches - no fallback to irrelevant users
        print(f"DEBUG: Showing {len(potential_matches)} intelligent matches only")
        
        # Determine the reason for no matches
        no_matches_reason = None
        if len(potential_matches) == 0:
            no_matches_reason = 'no_similar_interests'
        
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=potential_matches,
                             no_matches_reason=no_matches_reason)
        
    except ImportError as e:
        print(f"Matching engine not available: {e}")
        # Fallback to simple matching if engine fails
        potential_matches = []
        for mem in other_memberships:
            user = mem.user
            user_resume = Resume.query.filter_by(user_id=user.id, event_id=event_id).first()
            
            match_data = {
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'keywords': mem.get_keywords_list(),
                'has_resume': user_resume is not None,
                'resume_name': user_resume.original_name if user_resume else None,
                'joined_at': mem.joined_at.strftime('%B %Y') if mem.joined_at else 'Recently'
            }
            potential_matches.append(match_data)
    
        return render_template('event_matching.html', 
                             event=event, 
                             membership=membership,
                             potential_matches=potential_matches,
                             no_matches_reason=no_matches_reason)

@app.route('/event/<int:event_id>/like/<int:target_user_id>', methods=['POST'])
@login_required
def like_user(event_id, target_user_id):
    """Handle when a user likes another user"""
    try:
        # Verify the user is a member of this event
        membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if not membership:
            return {'success': False, 'message': 'You are not a member of this event'}, 403
        
        # Check if target user is also a member
        target_membership = Membership.query.filter_by(user_id=target_user_id, event_id=event_id).first()
        if not target_membership:
            return {'success': False, 'message': 'Target user is not a member of this event'}, 404
        
        # Check if interaction already exists
        existing_interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id
        ).first()
        
        if existing_interaction:
            return {'success': False, 'message': 'You have already interacted with this user'}, 400
        
        # Create new interaction
        interaction = UserInteraction(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id,
            action='like'
        )
        db.session.add(interaction)
        
        # Check if this creates a mutual match
        mutual_like = UserInteraction.query.filter_by(
            user_id=target_user_id,
            target_user_id=current_user.id,
            event_id=event_id,
            action='like'
        ).first()
        
        is_match = False
        if mutual_like:
            # Create a match
            match = Match(
                user1_id=min(current_user.id, target_user_id),
                user2_id=max(current_user.id, target_user_id),
                event_id=event_id
            )
            db.session.add(match)
            is_match = True
        
        db.session.commit()
        
        return {
            'success': True, 
            'is_match': is_match,
            'message': 'Match!' if is_match else 'Like recorded'
        }
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500

@app.route('/event/<int:event_id>/pass/<int:target_user_id>', methods=['POST'])
@login_required
def pass_user(event_id, target_user_id):
    """Handle when a user passes on another user"""
    try:
        # Verify the user is a member of this event
        membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if not membership:
            return {'success': False, 'message': 'You are not a member of this event'}, 403
        
        # Check if interaction already exists
        existing_interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id
        ).first()
        
        if existing_interaction:
            return {'success': False, 'message': 'You have already interacted with this user'}, 400
        
        # Create new interaction
        interaction = UserInteraction(
            user_id=current_user.id,
            target_user_id=target_user_id,
            event_id=event_id,
            action='pass'
        )
        db.session.add(interaction)
        db.session.commit()
        
        return {'success': True, 'message': 'Pass recorded'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500

@app.route('/event/<int:event_id>/matches')
@login_required
def event_matches(event_id):
    """Show all matches for a user in an event"""
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found!', 'error')
        return redirect(url_for('dashboard'))
    
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all matches for this user in this event
    matches = Match.query.filter(
        db.or_(
            db.and_(Match.user1_id == current_user.id, Match.event_id == event_id),
            db.and_(Match.user2_id == current_user.id, Match.event_id == event_id)
        ),
        Match.is_active == True
    ).all()
    
    # Prepare match data for template
    match_data = []
    for match in matches:
        other_user = match.get_other_user(current_user.id)
        if other_user:
            match_data.append({
                'match': match,
                'other_user': other_user,
                'matched_at': match.matched_at
            })
    
    return render_template('event_matches.html', 
                         event=event, 
                         matches=match_data)

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
    
    try:
        # Delete associated data first
        # Delete memberships
        Membership.query.filter_by(user_id=user_id).delete()
        
        # Delete resumes and associated files
        resumes = Resume.query.filter_by(user_id=user_id).all()
        deleted_files = []
        failed_files = []
        
        for resume in resumes:
            # Construct the file path using the correct upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(resume.event_id), resume.filename)
            
            # Debug: Print the file path being checked
            print(f"Attempting to delete file: {file_path}")
            
            # Check if file exists and delete it
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files.append(resume.filename)
                    print(f"Successfully deleted: {file_path}")
                except Exception as e:
                    failed_files.append(f"{resume.filename}: {str(e)}")
                    print(f"Failed to delete {file_path}: {str(e)}")
            else:
                print(f"File not found: {file_path}")
                failed_files.append(f"{resume.filename}: File not found")
        
        # Delete resume records from database
        Resume.query.filter_by(user_id=user_id).delete()
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        
        # Create success message with file deletion details
        success_msg = f'User {user_name} has been deleted successfully!'
        if deleted_files:
            success_msg += f' Deleted {len(deleted_files)} resume file(s).'
        if failed_files:
            success_msg += f' Warning: {len(failed_files)} file(s) could not be deleted.'
        
        flash(success_msg, 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user {user_name}: {str(e)}', 'error')
        print(f"Error in admin_delete_user: {str(e)}")
    
    return redirect(url_for('admin_users'))

@app.route('/admin/cleanup-files', methods=['POST'])
@login_required
@admin_required
def admin_cleanup_files():
    """Admin route to clean up orphaned files"""
    try:
        orphaned_count = cleanup_orphaned_files()
        if orphaned_count > 0:
            flash(f'Cleaned up {orphaned_count} orphaned file(s)!', 'success')
        else:
            flash('No orphaned files found.', 'info')
    except Exception as e:
        flash(f'Error during cleanup: {str(e)}', 'error')
    
    return redirect(url_for('admin_users'))

def cleanup_orphaned_files():
    """Clean up files that exist in filesystem but not in database"""
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        orphaned_files = []
        
        # Walk through all files in uploads directory
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, upload_folder)
                
                # Extract event_id and filename from path
                path_parts = relative_path.split(os.sep)
                if len(path_parts) >= 2:
                    event_id = path_parts[0]
                    filename = path_parts[1]
                    
                    # Check if this file exists in database
                    resume = Resume.query.filter_by(
                        event_id=int(event_id),
                        filename=filename
                    ).first()
                    
                    if not resume:
                        orphaned_files.append(file_path)
        
        # Delete orphaned files
        for file_path in orphaned_files:
            try:
                os.remove(file_path)
                print(f"Deleted orphaned file: {file_path}")
            except Exception as e:
                print(f"Failed to delete orphaned file {file_path}: {str(e)}")
        
        return len(orphaned_files)
        
    except Exception as e:
        print(f"Error in cleanup_orphaned_files: {str(e)}")
        return 0

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
