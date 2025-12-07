"""
Prophere Configuration Management
Environment-specific configurations for the Flask application
"""
import os

# Get the base directory (src/)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration with common settings"""
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@prophere.com')
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'false').lower() in ['true', 'on', '1']  # Set to true to disable emails in dev)
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # Session
    SESSION_COOKIE_SECURE = False  # Should be True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application
    APP_NAME = 'Prophere'
    APP_VERSION = '1.0.0'
    
    # Matching Configuration
    # Maximum number of attendees to process in a single matching request
    # This prevents OOM errors on Render for very large events
    # Set via environment variable MAX_MATCH_ATTENDEES (default: 500)
    MAX_MATCH_ATTENDEES = int(os.environ.get('MAX_MATCH_ATTENDEES', 500))

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development, with optional override via DEV_DATABASE_URI
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URI',
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'nfc_networking.db')
    )
    
    # Development settings
    SQLALCHEMY_ECHO = False  # Set to True to log SQL queries

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Production database: prefer DATABASE_URL (Postgres on Render), fallback to SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'nfc_networking.db')
    )
    
    # Production security
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """
    Get configuration based on environment
    
    Args:
        env: Environment name ('development', 'testing', 'production')
             If None, uses FLASK_ENV environment variable or defaults to 'development'
    
    Returns:
        Configuration class
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
