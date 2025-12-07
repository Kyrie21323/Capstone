"""
Prophere - Main Application Factory
"""
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from models import db, User, Event
from config import get_config
import os
from datetime import datetime

# Get the project root directory (parent of src)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # For SQLite: ensure the database directory exists and use absolute path
    # For Postgres: don't override DATABASE_URL (it's already set from config/environment)
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        # Extract path and make it absolute relative to PROJECT_ROOT
        db_path = db_uri.replace('sqlite:///', '', 1)
        # If it's a relative path, make it absolute relative to PROJECT_ROOT
        if not os.path.isabs(db_path):
            db_path = os.path.join(PROJECT_ROOT, db_path)
        else:
            # If already absolute, use as-is but ensure directory exists
            pass
        
        # Normalize and ensure directory exists
        db_path = os.path.abspath(db_path)
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        # Update config with absolute path
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Ensure UPLOAD_FOLDER is absolute and consistent
    upload_folder = os.path.join(PROJECT_ROOT, 'uploads')
    upload_folder = os.path.abspath(upload_folder)  # Normalize to absolute path
    os.makedirs(upload_folder, exist_ok=True)  # Ensure uploads/ folder exists
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db, directory=os.path.join(PROJECT_ROOT, 'migrations'))
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register Blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    from routes import auth_bp, user_bp, admin_bp, matching_bp, scheduling_bp, api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)  # Has prefix '/admin' in __init__
    app.register_blueprint(matching_bp, url_prefix='/event')
    app.register_blueprint(scheduling_bp, url_prefix='/event')
    app.register_blueprint(api_bp)  # Has prefix '/api' in __init__

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

# Create default app instance for backward compatibility
app = create_app()

# Compatibility functions for scripts that import from app
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

def check_database_status():
    """Check if database is properly initialized"""
    try:
        with app.app_context():
            # Check if all required tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['user', 'event', 'membership', 'resume', 'match', 'user_interaction']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                return False
            
            # Check if we have any data
            user_count = User.query.count()
            if user_count == 0:
                print("⚠️  Database exists but has no data")
                return False
                
            return True
    except Exception as e:
        print(f"⚠️  Database check failed: {e}")
        return False

if __name__ == '__main__':
    # Check database status
    if not check_database_status():
        print("🔄 Initializing database...")
        init_db()
    
    app.run(debug=True)

