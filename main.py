import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from models import db, User

def initialize_database():
    """
    Initialize the database if it doesn't exist.
    Works with both SQLite (file-based) and Postgres (connection-based).
    """
    with app.app_context():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        if uri.startswith('sqlite:///'):
            # Handle SQLite file-based DB
            db_path = uri.replace('sqlite:///', '', 1)
            db_path = os.path.abspath(db_path)
            db_dir = os.path.dirname(db_path)
            
            if not os.path.exists(db_path):
                print(f"🔄 SQLite database not found at {db_path}, initializing...")
                os.makedirs(db_dir, exist_ok=True)
                db.create_all()
                print("✅ SQLite database initialized successfully!")
                print("   - All tables created")
                print("   - Ready for use")
            else:
                print(f"✅ SQLite database already exists at {db_path}, skipping initialization.")
        else:
            # Handle Postgres or any non-SQLite database
            print("🔄 Non-SQLite database detected (likely Postgres). Ensuring tables exist with db.create_all()...")
            db.create_all()
            print("✅ Tables ensured for non-SQLite database.")

def run_database_migrations():
    """
    Run database migrations to ensure schema is up-to-date.
    This is especially important for Postgres where db.create_all() doesn't alter existing columns.
    """
    with app.app_context():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Only run migrations for non-SQLite databases
        if not uri.startswith('sqlite:///'):
            print("🔄 Running database migrations for non-SQLite database...")
            try:
                from utils.db_migrations import upgrade_password_hash_column
                success, message = upgrade_password_hash_column()
                print(f"   {message}")
                if not success:
                    print("   ⚠️  Migration had issues, but continuing startup...")
            except Exception as e:
                print(f"   ⚠️  Error during migration: {e}")
                print("   Continuing startup... (migration may need manual intervention)")


def ensure_admin_user():
    """
    Ensure an admin user exists, creating one from environment variables if needed.
    
    This function is idempotent:
    - Checks if an admin with the specified email already exists
    - Only creates a new admin if none exists with that email
    - Works with both SQLite and Postgres
    
    Logs clearly whether:
    - Admin creation succeeded
    - Admin already existed and was skipped
    - Something failed (with concise error message)
    """
    with app.app_context():
        # Get admin credentials from environment variables
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        # If no environment variables set, check if any admin exists
        if not admin_email or not admin_password:
            existing_admin = User.query.filter_by(is_admin=True).first()
            if existing_admin:
                print(f"✅ Admin user already exists (email: {existing_admin.email}), skipping creation.")
            else:
                print("⚠️  Warning: No admin user found and ADMIN_EMAIL/ADMIN_PASSWORD not set.")
                print("   Skipping admin creation. Set environment variables to auto-create admin.")
            return
        
        # Check if admin with this specific email already exists (idempotent check)
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            if existing_admin.is_admin:
                print(f"✅ Admin user already exists (email: {admin_email}), skipping creation.")
            else:
                # User exists but isn't admin - upgrade them
                print(f"🔄 User {admin_email} exists but isn't admin. Upgrading to admin...")
                try:
                    existing_admin.is_admin = True
                    db.session.commit()
                    print(f"✅ User {admin_email} upgraded to admin.")
                except Exception as e:
                    print(f"❌ Error upgrading user to admin: {e}")
                    print("   App will continue without admin upgrade.")
            return
        
        # No admin with this email exists, try to create one
        # Import the create_admin_user function
        scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        try:
            from manage_users import create_admin_user
            
            # Create the admin user
            user = create_admin_user(email=admin_email, password=admin_password)
            print(f"✅ Admin user created successfully with email: {admin_email}")
        except Exception as e:
            # Provide more detailed error information
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Check for specific error types
            if 'StringDataRightTruncation' in error_msg or 'value too long' in error_msg.lower():
                print(f"❌ Error creating admin user: Password hash too long for database column.")
                print(f"   This suggests the password_hash column needs to be migrated.")
                print(f"   Error details: {error_type}: {error_msg}")
            else:
                print(f"❌ Error creating admin user: {error_type}: {error_msg}")
            
            # Don't raise - allow app to start even if admin creation fails
            print("   App will continue without admin user.")


if __name__ == "__main__":
    # Auto-initialize database if it doesn't exist
    initialize_database()
    
    # Run database migrations (for Postgres schema updates)
    run_database_migrations()
    
    # Ensure admin user exists (from environment variables)
    ensure_admin_user()
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000)
