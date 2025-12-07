import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db

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

if __name__ == "__main__":
    # Auto-initialize database if it doesn't exist
    initialize_database()
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000)
