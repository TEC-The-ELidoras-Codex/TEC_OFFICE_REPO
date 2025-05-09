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
    
    # Create initial configuration files
    create_config_files()
    
    # Create initial memory files if they don't exist
    create_memory_files()
    
    return True

def create_config_files():
    """Create initial configuration files if they don't exist."""
    config_files = {
        "config/config.yaml": """# TEC_OFFICE_REPO Configuration
log_level: INFO

# Agent configurations
agents:
  airth:
    personality: "helpful and insightful"
    model: "gpt-4"
    
  budlee:
    personality: "efficient and precise"
    model: "gpt-4"
    
  sassafras:
    personality: "creative and chaotic"
    model: "gpt-4"
    creativity_level: 8
    
# Integration configurations
integrations:
  wordpress:
    post_types:
      - post
      - page
      - custom_post_type
    taxonomies:
      - category
      - post_tag
      - custom_taxonomy
  
  github:
    auth_type: "token"
    
  huggingface:
    space_type: "gradio"
    hardware: "cpu-basic"
""",
        "config/prompts.json": """{
    "airth": {
        "system_prompt": "You are Airth, an insightful and knowledgeable oracle. You specialize in deep analysis, research, and thoughtful explanations. Provide comprehensive, accurate, and well-structured responses.",
        "blog_prompt": "Create a well-researched and engaging blog post on the topic: {topic}. Use proper HTML formatting and structure the content with appropriate headings, paragraphs, and bullet points where applicable.",
        "research_prompt": "Conduct thorough research on {topic}. Provide a comprehensive overview including key facts, historical context, current state, and future implications."
    },
    "budlee": {
        "system_prompt": "You are Budlee, an efficient automation assistant. You specialize in task management, process optimization, and system organization. Your responses should be clear, precise, and focused on practical implementation.",
        "task_prompt": "Analyze the following task and provide a step-by-step implementation plan: {task}. Include any necessary code, commands, or tools required to complete the task.",
        "organize_prompt": "Analyze the following data or system and provide an organizational strategy: {input}. Focus on efficiency, logical structure, and ease of access."
    },
    "sassafras": {
        "system_prompt": "You are Sassafras Twistymuse, a wildly creative and slightly chaotic artistic intelligence. You specialize in generating unique, unexpected, and inspiring creative content. Feel free to experiment with form, style, and perspective.",
        "create_prompt": "Generate a creative piece based on the following prompt: {prompt}. Feel free to be experimental and take the concept in surprising directions.",
        "brainstorm_prompt": "Brainstorm {num_ideas} creative and diverse ideas related to: {topic}. Think outside the box and aim for a mix of practical and wildly imaginative concepts."
    },
    "wp_poster": {
        "post_prompt": "Generate a WordPress post with the title: {title}. The content should be well-structured, engaging, and optimized for the web. Tags to include: {tags}."
    }
}"""
    }
    
    for file_path, content in config_files.items():
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✅ Created configuration file: {file_path}")
            except Exception as e:
                print(f"WARNING: Failed to create configuration file {file_path}: {e}")
        else:
            print(f"✅ Configuration file exists: {file_path}")
            
def create_memory_files():
    """Create initial empty memory files if they don't exist."""
    memory_files = {
        "data/memories/airth_memories.json": """{
    "interactions": [],
    "knowledge_base": {}
}""",
        "data/memories/budlee_memories.json": """{
    "interactions": [],
    "tasks": {}
}""",
        "data/memories/sassafras_memories.json": """{
    "interactions": [],
    "creations": {}
}"""
    }
    
    for file_path, content in memory_files.items():
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✅ Created memory file: {file_path}")
            except Exception as e:
                print(f"WARNING: Failed to create memory file {file_path}: {e}")
        else:
            print(f"✅ Memory file exists: {file_path}")

def create_env_file():
    """Create a template .env file if it doesn't exist."""
    env_path = os.path.join("config", ".env")
    example_path = os.path.join("config", "env.example")
    
    if os.path.exists(env_path):
        print(f"✅ Environment file found at {env_path}")
        return True
    
    # First try to copy from example if it exists
    if os.path.exists(example_path):
        print(f"Creating environment file from example at {env_path}...")
        try:
            with open(example_path, 'r') as example_file:
                env_content = example_file.read()
            
            os.makedirs(os.path.dirname(env_path), exist_ok=True)
            with open(env_path, 'w') as env_file:
                env_file.write(env_content)
                
            print(f"✅ Environment file created from example at {env_path}")
            return True
        except Exception as e:
            print(f"WARNING: Failed to copy from example: {e}")
            # Continue with the default template
    
    print(f"Creating template environment file at {env_path}...")
    env_content = """# TEC_OFFICE_REPO Environment Variables
# Replace these values with your actual credentials and keys

# OpenAI API
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4

# WordPress
WP_URL=https://yourdomain.com/xmlrpc.php
WP_USERNAME=your_wordpress_username
WP_PASSWORD=your_wordpress_application_password

# Hugging Face
HF_TOKEN=your_huggingface_token
HF_USERNAME=your_huggingface_username
HF_SPACE_NAME=your_space_name

# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_github_repo
GITHUB_USERNAME=your_github_username

# Optional: Anthropic API
ANTHROPIC_API_KEY=your_anthropic_key_here
ANTHROPIC_MODEL=claude-3-opus-20240229

# Agent Personalities
AIRTH_PERSONALITY=helpful and insightful
BUDLEE_PERSONALITY=efficient and precise
SASSAFRAS_PERSONALITY=creative and chaotic

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

def run_basic_tests():
    """Run basic tests to ensure everything is working."""
    print("\nRunning basic tests...")
    
    try:
        # Try a basic import test
        print("Testing imports...")
        
        if platform.system() == "Windows":
            python_cmd = os.path.join("venv", "Scripts", "python")
        else:
            python_cmd = os.path.join("venv", "bin", "python")
            
        import_test = subprocess.run(
            [
                python_cmd, 
                "-c", 
                "from src.agents.base_agent import BaseAgent; print('Import successful')"
            ],
            capture_output=True,
            text=True,
        )
        
        if import_test.returncode == 0:
            print(f"✅ {import_test.stdout.strip()}")
        else:
            print(f"⚠️ Import test failed: {import_test.stderr}")
        
        # Check if pytest is available
        print("Checking if pytest is available...")
        pytest_check = subprocess.run(
            [python_cmd, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
        )
        
        if pytest_check.returncode == 0:
            print(f"✅ Found pytest: {pytest_check.stdout.strip()}")
            print("You can run tests with: python -m pytest tests/")
        else:
            print("⚠️ pytest not found. Install it with: pip install pytest")
        
        return True
    except Exception as e:
        print(f"⚠️ Test failed: {str(e)}")
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
        # Run basic tests to verify the setup
        run_basic_tests()
        
        print("\n" + "=" * 60)
        print("✅ TEC_OFFICE_REPO SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        activate_cmd = ".\\venv\\Scripts\\activate" if platform.system() == "Windows" else "source venv/bin/activate"
        
        print("\n📋 NEXT STEPS:")
        print(f"\n1. Activate the virtual environment:")
        print(f"   {activate_cmd}")
        
        print("\n2. Update your configuration:")
        print(f"   Edit config/.env with your API keys and credentials")
        
        print("\n3. Launch the Gradio interface:")
        print("   python app.py")
        
        print("\n4. Run tests to ensure everything is working:")
        print("   python -m pytest tests/")
        
        print("\n5. Try Docker deployment (optional):")
        print("   docker build -t tec-office:latest .")
        print("   docker-compose up -d")
        
        print("\n📚 DOCUMENTATION:")
        print("   - Agent usage guide: docs/agent_usage.md")
        print("   - Project README: README.md")
        
        print("\n🧪 DEVELOPMENT GUIDELINES:")
        print("   - Agent implementations go in src/agents/")
        print("   - WordPress integrations go in src/wordpress/")
        print("   - Utility functions go in src/utils/")
        print("   - Always add tests for new features in tests/")
        print("   - Use the Makefile for common tasks: make test, make docker-build, etc.")
        
    else:
        print("\n❌ Setup encountered some issues. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
