#!/usr/bin/env python3
"""
NFC Networking Assistant - Setup Script
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up NFC Networking Assistant...")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not os.path.exists('.venv'):
        print("📦 Creating virtual environment...")
        if not run_command('python -m venv .venv', 'Virtual environment creation'):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        activate_cmd = '.venv\\Scripts\\activate'
        pip_cmd = '.venv\\Scripts\\pip'
    else:  # Unix/Linux/Mac
        activate_cmd = 'source .venv/bin/activate'
        pip_cmd = '.venv/bin/pip'
    
    print("📦 Installing dependencies...")
    if not run_command(f'{pip_cmd} install -r requirements.txt', 'Dependencies installation'):
        return False
    
    print("🗃️  Database will be initialized when you first run the application")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Run the application:")
    print("   python main.py")
    print("3. Open your browser to: http://127.0.0.1:5000")
    print("\n🔑 Default login credentials:")
    print("   🚀 Super Admin: admin@nfcnetworking.com / admin123")
    print("   👥 Regular users: [email] / password123")

if __name__ == '__main__':
    main()
