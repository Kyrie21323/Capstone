#!/usr/bin/env python3
"""
User Management Script

This script consolidates all user management operations:
- Create/update admin users
- Create/update event managers
- List users
- Reset passwords

Replaces: create_admin.py, create_manager.py
"""

import argparse
import getpass
from script_helpers import setup_python_path, print_section, print_success, print_error, print_info

# Setup Python path to import from src
setup_python_path()

from app import app, db
from models import User
from werkzeug.security import generate_password_hash


def create_admin_user(email: str, password: str, name: str = None) -> User:
    """
    Create an admin user with the specified credentials.
    
    This function is designed to be called from other modules (e.g., main.py)
    and requires an active Flask application context.
    
    Args:
        email: Admin email address
        password: Admin password (will be hashed)
        name: Admin display name (defaults to "Admin" if not provided)
    
    Returns:
        User: The created or existing User instance
    
    Raises:
        ValueError: If email or password is missing
        RuntimeError: If called outside Flask application context
    """
    if not email:
        raise ValueError("Email is required")
    if not password:
        raise ValueError("Password is required")
    
    # Default name if not provided
    if not name:
        name = "Admin"
    
    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    
    if user:
        # User exists, update if needed
        if not user.is_admin:
            user.is_admin = True
        if user.name != name:
            user.name = name
        # Update password
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        return user
    
    # Create new admin user
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_or_update_user(email: str, password: str, name: str, is_admin: bool, force_password_reset: bool = False):
    """
    Create a new user or update an existing one.
    
    Args:
        email: User email address
        password: User password (will be hashed)
        name: User display name
        is_admin: Whether user should be an admin/manager
        force_password_reset: Reset password even if user exists
    """
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update existing user
            print_info(f"User {email} already exists")
            
            # Update admin status
            if user.is_admin != is_admin:
                user.is_admin = is_admin
                role = "Event Manager" if is_admin else "Attendee"
                print_success(f"Updated role to: {role}")
            
            # Update password if provided
            if password and (force_password_reset or not user.password_hash):
                user.password_hash = generate_password_hash(password)
                print_success("Password updated")
            
            # Update name if provided and different
            if name and user.name != name:
                old_name = user.name
                user.name = name
                print_success(f"Updated name: {old_name} → {name}")
        
        else:
            # Create new user
            if not password:
                print_error("Password is required for new users")
                return False
            
            if not name:
                name = "Event Manager" if is_admin else "User"
            
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=is_admin
            )
            db.session.add(user)
            
            role = "Event Manager" if is_admin else "Attendee"
            print_success(f"Created new {role}: {name} ({email})")
        
        db.session.commit()
        return True


def list_users(show_admins: bool = True, show_attendees: bool = True):
    """
    List all users in the database.
    
    Args:
        show_admins: Include admin users
        show_attendees: Include regular attendees
    """
    with app.app_context():
        users = User.query.order_by(User.created_at.desc()).all()
        
        if not users:
            print_info("No users found in database")
            return
        
        admins = [u for u in users if u.is_admin]
        attendees = [u for u in users if not u.is_admin]
        
        if show_admins and admins:
            print_section("Event Managers", "👑")
            for user in admins:
                print(f"   • {user.name:<30} {user.email:<35} (ID: {user.id})")
        
        if show_attendees and attendees:
            print_section("Attendees", "👥")
            for user in attendees:
                print(f"   • {user.name:<30} {user.email:<35} (ID: {user.id})")
        
        print(f"\n📊 Total: {len(admins)} managers, {len(attendees)} attendees")


def create_default_admin():
    """Create the default super admin account."""
    print_section("Creating Default Admin", "🚀")
    with app.app_context():
        user = create_admin_user(
            email='admin@nfcnetworking.com',
            password='admin123',
            name='Super Admin'
        )
        print_success(f"Default admin created: {user.email}")
        return True


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Manage users in Prophere',
        epilog='Examples:\n'
               '  %(prog)s --admin                    Create default admin\n'
               '  %(prog)s --manager user@example.com Create manager\n'
               '  %(prog)s --list                     List all users\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Action flags
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('--admin', action='store_true',
                             help='Create/update default admin account (admin@nfcnetworking.com)')
    action_group.add_argument('--manager', metavar='EMAIL',
                             help='Create/update an event manager account')
    action_group.add_argument('--attendee', metavar='EMAIL',
                             help='Create/update an attendee account')
    action_group.add_argument('--list', action='store_true',
                             help='List all users')
    
    # Optional arguments
    parser.add_argument('--password', '-p',
                       help='Password for the user')
    parser.add_argument('--name', '-n',
                       help='Display name for the user')
    parser.add_argument('--reset-password', action='store_true',
                       help='Force password reset for existing user')
    parser.add_argument('--admins-only', action='store_true',
                       help='When listing, show only admins')
    parser.add_argument('--attendees-only', action='store_true',
                       help='When listing, show only attendees')
    
    args = parser.parse_args()
    
    # Handle actions
    if args.admin:
        # Create default admin
        create_default_admin()
    
    elif args.manager:
        # Create/update manager
        email = args.manager
        password = args.password
        name = args.name
        
        # Interactive password prompt if not provided
        if not password:
            with app.app_context():
                existing_user = User.query.filter_by(email=email).first()
                if not existing_user or args.reset_password:
                    password = getpass.getpass(f'Enter password for {email}: ')
        
        create_or_update_user(email, password, name, is_admin=True, force_password_reset=args.reset_password)
    
    elif args.attendee:
        # Create/update attendee
        email = args.attendee
        password = args.password
        name = args.name
        
        # Interactive password prompt if not provided
        if not password:
            with app.app_context():
                existing_user = User.query.filter_by(email=email).first()
                if not existing_user or args.reset_password:
                    password = getpass.getpass(f'Enter password for {email}: ')
        
        create_or_update_user(email, password, name, is_admin=False, force_password_reset=args.reset_password)
    
    elif args.list:
        # List users
        show_admins = not args.attendees_only
        show_attendees = not args.admins_only
        list_users(show_admins=show_admins, show_attendees=show_attendees)
    
    else:
        # No action specified, show help
        parser.print_help()


if __name__ == '__main__':
    main()
