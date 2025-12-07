"""
Database migration utilities for schema updates.

This module provides helper functions to safely upgrade database schemas,
particularly for production deployments where manual migrations may not be feasible.
"""

from sqlalchemy import inspect, text
from flask import current_app


def upgrade_password_hash_column():
    """
    Upgrade the password_hash column in the User table from VARCHAR(128) to VARCHAR(255).
    
    This migration is needed because Werkzeug's scrypt password hashes can exceed 128 characters,
    causing StringDataRightTruncation errors in Postgres (which enforces VARCHAR length limits).
    SQLite doesn't enforce these limits, so the issue only appears in Postgres.
    
    This function:
    1. Detects if the database is Postgres (or another non-SQLite DB)
    2. Checks the current column type
    3. If it's VARCHAR(128) or smaller, upgrades it to VARCHAR(255)
    4. If it's already VARCHAR(255) or larger, skips the migration
    
    Returns:
        tuple: (success: bool, message: str)
    
    Raises:
        Exception: If migration fails unexpectedly
    """
    from models import db
    
    try:
        # Get database URI
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Skip migration for SQLite (it doesn't enforce VARCHAR length limits)
        if db_uri.startswith('sqlite:///'):
            return True, "SQLite database detected - no migration needed (SQLite doesn't enforce VARCHAR length limits)"
        
        # For Postgres and other databases, check and upgrade if needed
        inspector = inspect(db.engine)
        
        # Check if user table exists
        if 'user' not in inspector.get_table_names():
            return True, "User table doesn't exist yet - will be created with correct schema"
        
        # Get column info for password_hash
        columns = inspector.get_columns('user')
        password_hash_col = next((col for col in columns if col['name'] == 'password_hash'), None)
        
        if not password_hash_col:
            return True, "password_hash column doesn't exist yet - will be created with correct schema"
        
        # Check current column type
        # Postgres returns type as a SQLAlchemy type object, so we need to handle it properly
        current_type = str(password_hash_col['type']).upper()
        
        # Also check the actual type name from the database
        # For Postgres, we can query information_schema for the exact type
        db_engine_name = db.engine.dialect.name
        
        current_length = None
        if db_engine_name == 'postgresql':
            # For Postgres, query information_schema for accurate column info
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT character_maximum_length 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND column_name = 'password_hash'
                """))
                row = result.fetchone()
                if row and row[0] is not None:
                    current_length = int(row[0])
        else:
            # For other databases, parse from type string
            if 'VARCHAR' in current_type or 'CHARACTER VARYING' in current_type:
                # Extract length from type string
                import re
                match = re.search(r'\((\d+)\)', current_type)
                if match:
                    current_length = int(match.group(1))
        
        # If already VARCHAR(255) or larger, or if it's TEXT (unlimited), skip
        if current_length is None:  # TEXT or other unlimited type
            return True, f"password_hash column is already {current_type} (unlimited) - no migration needed"
        
        if current_length >= 255:
            return True, f"password_hash column is already VARCHAR({current_length}) - no migration needed"
        
        # Need to upgrade: current_length < 255
        # Execute ALTER TABLE to change column type
        # Note: This is safe to run multiple times (idempotent) because we check the current type first
        with db.engine.begin() as conn:
            # Use text() to safely execute raw SQL
            # For Postgres, we use ALTER TABLE ... ALTER COLUMN ... TYPE
            if 'postgresql' in db_uri.lower():
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255)'))
            else:
                # For other databases, use a generic ALTER TABLE (may need adjustment per DB)
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash VARCHAR(255)'))
        
        return True, f"✅ Successfully upgraded password_hash column from VARCHAR({current_length}) to VARCHAR(255)"
    
    except Exception as e:
        # Log the error but don't crash the app
        error_msg = f"❌ Error during password_hash migration: {e}"
        current_app.logger.error(error_msg, exc_info=True)
        return False, error_msg


def upgrade_resume_embedding_fields():
    """
    Add extracted_text and embedding columns to the Resume table for caching.
    
    This migration enables memory-efficient matching by storing pre-computed
    document text and embeddings, avoiding re-extraction and re-embedding on every match.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from models import db
    
    try:
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Skip migration for SQLite (it's more flexible with schema changes)
        if db_uri.startswith('sqlite:///'):
            return True, "SQLite database detected - columns will be added automatically on next schema update"
        
        inspector = inspect(db.engine)
        
        # Check if resume table exists
        if 'resume' not in inspector.get_table_names():
            return True, "Resume table doesn't exist yet - will be created with correct schema"
        
        # Get existing columns
        columns = inspector.get_columns('resume')
        column_names = {col['name'] for col in columns}
        
        columns_to_add = []
        if 'extracted_text' not in column_names:
            columns_to_add.append('extracted_text')
        if 'embedding' not in column_names:
            columns_to_add.append('embedding')
        
        if not columns_to_add:
            return True, "Resume embedding fields already exist - no migration needed"
        
        # Execute ALTER TABLE to add columns
        with db.engine.begin() as conn:
            if 'postgresql' in db_uri.lower():
                if 'extracted_text' in columns_to_add:
                    conn.execute(text('ALTER TABLE resume ADD COLUMN IF NOT EXISTS extracted_text TEXT'))
                if 'embedding' in columns_to_add:
                    conn.execute(text('ALTER TABLE resume ADD COLUMN IF NOT EXISTS embedding TEXT'))
            else:
                # For other databases, try generic ALTER TABLE
                if 'extracted_text' in columns_to_add:
                    conn.execute(text('ALTER TABLE resume ADD COLUMN extracted_text TEXT'))
                if 'embedding' in columns_to_add:
                    conn.execute(text('ALTER TABLE resume ADD COLUMN embedding TEXT'))
        
        return True, f"✅ Successfully added columns to resume table: {', '.join(columns_to_add)}"
    
    except Exception as e:
        error_msg = f"❌ Error during resume embedding fields migration: {e}"
        current_app.logger.error(error_msg, exc_info=True)
        return False, error_msg
