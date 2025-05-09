#!/usr/bin/env python3
"""
Setup script for the TEC_OFFICE_REPO project.
This script initializes the environment and ensures all dependencies are installed.
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        print("ERROR: Python 3.10 or higher is required.")
        print(f"Current Python version: {major}.{minor}")
        return False
    print(f"✅ Python version {major}.{minor} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = "venv"
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment already exists at {venv_path}")
        return True
    
    print(f"Creating virtual environment in {venv_path}...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"✅ Virtual environment created at {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        return False

def install_requirements():
    """Install requirements from requirements.txt."""
    if platform.system() == "Windows":
        pip_cmd = os.path.join("venv", "Scripts", "pip")
        python_cmd = os.path.join("venv", "Scripts", "python")
    else:
        pip_cmd = os.path.join("venv", "bin", "pip")
        python_cmd = os.path.join("venv", "bin", "python")
    
    print("Installing requirements...")
    try:
        # Use python -m pip instead of pip directly for upgrading pip
        subprocess.check_call([python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ Pip upgraded successfully")
        
        # Now install the requirements
        subprocess.check_call([pip_cmd, "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install requirements: {e}")
        return False

def setup_project_structure():
    """Create necessary project directories if they don't exist."""
    dirs = [
        "src/agents",
        "src/wordpress",
        "src/ai",
        "src/utils",
        "data/memories",
        "data/storage",
        "data/lore",
        "config",
        "docs",
        "tests",
        "assets",
        "logs"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def create_env_file():
    """Create a template .env file if it doesn't exist."""
    env_path = os.path.join("config", ".env")
    
    if os.path.exists(env_path):
        print(f"✅ Environment file found at {env_path}")
        return True
    
    print(f"Creating template environment file at {env_path}...")
    env_content = """# TEC_OFFICE_REPO Environment Variables
# Replace these values with your actual credentials and keys

# OpenAI API
OPENAI_API_KEY=your_openai_key_here

# WordPress
WP_URL=https://yourdomain.com
WP_USERNAME=your_wordpress_username
WP_PASSWORD=your_wordpress_application_password
WP_XMLRPC_PATH=/xmlrpc.php

# Hugging Face
HF_TOKEN=your_huggingface_token

# Optional: Anthropic API
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
"""
    try:
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Template environment file created at {env_path}")
        print("NOTE: Please update the values in the .env file with your actual credentials")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create environment file: {e}")
        return False

def main():
    """Main setup function."""
    print("\n⚡ THE ELIDORAS CODEX - TEC_OFFICE_REPO SETUP ⚡\n")
    
    if not check_python_version():
        return False
    
    success = all([
        create_virtual_environment(),
        install_requirements(),
        setup_project_structure(),
        create_env_file()
    ])
    
    if success:
        print("\n✅ Setup completed successfully!")
        
        activate_cmd = ".\\venv\\Scripts\\activate" if platform.system() == "Windows" else "source venv/bin/activate"
        print(f"\nTo activate the virtual environment, run:")
        print(f"  {activate_cmd}")
        
        print("\nTo launch the Gradio interface, run:")
        print("  python app.py")
        
        print("\nDevelopment Guidelines:")
        print("  1. Update configuration in config/.env")
        print("  2. Agent implementations go in src/agents/")
        print("  3. Run tests with: python -m pytest")
        
    else:
        print("\n❌ Setup encountered some issues. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
