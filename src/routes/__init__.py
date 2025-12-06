"""
Blueprint initialization for Prophere routes.
"""
from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('user', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
matching_bp = Blueprint('matching', __name__)
scheduling_bp = Blueprint('scheduling', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes to register them with blueprints
from . import auth, user, admin, matching, scheduling, api
