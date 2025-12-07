import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import User

def get_database_file_path():
    """
    Extract the database file path from SQLALCHEMY_DATABASE_URI.
    Returns None if not SQLite or if path cannot be determined.
    """
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    # Check if it's SQLite
    if not uri.startswith('sqlite:///'):
        return None
    
    # SQLite URI formats:
    # - sqlite:///relative/path (3 slashes, relative)
    # - sqlite:////absolute/path (4 slashes, absolute)
    # - sqlite:///absolute/path (3 slashes with absolute path - SQLAlchemy handles this)
    
    # Remove 'sqlite:///' prefix (3 slashes)
    path = uri.replace('sqlite:///', '', 1)
    
    # Normalize path separators (handle both / and \)
    # Convert forward slashes to OS-specific separators for proper path handling
    path = os.path.normpath(path)
    
    # If it's already an absolute path, return it
    if os.path.isabs(path):
        return path
    
    # Handle relative paths - convert to absolute based on project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(project_root, path))

def initialize_database():
    """
    Initialize the database if it doesn't exist.
    This runs only once on fresh deployments.
    """
    db_path = get_database_file_path()
    
    if db_path is None:
        # Not SQLite, skip initialization
        print("ℹ️  Database is not SQLite, skipping auto-initialization")
        return
    
    if os.path.exists(db_path):
        # Database already exists, skip initialization
        print(f"✅ Database already exists at {db_path}")
        return
    
    # Database doesn't exist, initialize it
    print(f"🔄 Database not found at {db_path}, initializing...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database initialized successfully!")
            print("   - All tables created")
            print("   - Ready for use")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

def ensure_admin_user():
    """
    Ensure an admin user exists, creating one from environment variables if needed.
    This runs on every startup but only creates an admin if none exists.
    """
    with app.app_context():
        # Check if any admin already exists
        existing_admin = User.query.filter_by(is_admin=True).first()
        
        if existing_admin:
            print(f"✅ Admin user already exists (email: {existing_admin.email}), skipping creation.")
            return
        
        # No admin exists, try to create one from environment variables
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if not admin_email or not admin_password:
            print("⚠️  Warning: No admin user found and ADMIN_EMAIL/ADMIN_PASSWORD not set.")
            print("   Skipping admin creation. Set environment variables to auto-create admin.")
            return
        
        # Import the create_admin_user function
        # Add scripts to path temporarily for import
        scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        try:
            from manage_users import create_admin_user
            
            # Create the admin user
            user = create_admin_user(email=admin_email, password=admin_password)
            print(f"✅ Default admin created with email: {admin_email}")
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            # Don't raise - allow app to start even if admin creation fails
            print("   App will continue without admin user.")


if __name__ == "__main__":
    # Auto-initialize database if it doesn't exist
    initialize_database()
    
    # Ensure admin user exists (from environment variables)
    ensure_admin_user()
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000)
