#!/usr/bin/env python3
"""
Setup script for AI Fashion Stylist
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ['uploads', 'static/images']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("🔧 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# OpenAI API Key (get from https://platform.openai.com/api-keys)\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n\n")
            f.write("# Flask Configuration\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=True\n")
        print("✅ Created .env file. Please add your OpenAI API key if you have one.")
    else:
        print("📄 .env file already exists")

def main():
    """Main setup function"""
    print("👗 AI Fashion Stylist Setup")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Add your OpenAI API key to .env file (optional)")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("\n✨ Happy styling!")
    
    return True

if __name__ == "__main__":
    main()
