#!/usr/bin/env python
"""
Deploy TEC Office Suite to Hugging Face Space

This script prepares and deploys the TEC Office Suite to a Hugging Face Space
using the Hugging Face CLI.
"""
import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
import tempfile
import json

def run_command(command, cwd=None):
    """Run a shell command and return the output"""
    result = subprocess.run(
        command, 
        shell=True, 
        check=False, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True
    )
    return result

def check_huggingface_cli():
    """Check if the Hugging Face CLI is installed and the user is logged in"""
    print("Checking Hugging Face CLI...")
    result = run_command("huggingface-cli --version")
    
    if result.returncode != 0:
        print("❌ Hugging Face CLI not found. Installing...")
        install_result = run_command("pip install huggingface_hub")
        
        if install_result.returncode != 0:
            print("❌ Failed to install Hugging Face CLI.")
            print(install_result.stderr)
            return False
        else:
            print("✅ Hugging Face CLI installed.")
    else:
        print(f"✅ Hugging Face CLI found: {result.stdout.strip()}")
    
    # Check if the user is logged in
    login_check = run_command("huggingface-cli whoami")
    if "not logged in" in login_check.stdout.lower() or login_check.returncode != 0:
        print("❌ Not logged in to Hugging Face.")
        print("Please log in with: huggingface-cli login")
        return False
    
    print(f"✅ Logged in as: {login_check.stdout.strip()}")
    return True

def prepare_deployment(temp_dir, space_name):
    """Prepare the deployment files in a temporary directory"""
    # Create necessary directories
    os.makedirs(os.path.join(temp_dir, "config"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "scripts"), exist_ok=True)
    
    # Copy essential files
    shutil.copy("Dockerfile.huggingface", os.path.join(temp_dir, "Dockerfile"))
    shutil.copy("requirements.txt", os.path.join(temp_dir, "requirements.txt"))
    shutil.copy("hf_app.py", os.path.join(temp_dir, "app.py"))
    
    # Copy src directory
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, ".")
                dst_file = os.path.join(temp_dir, rel_path)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy(src_file, dst_file)
    
    # Copy scripts directory (only essential scripts)
    essential_scripts = ["post_roadmap_article.py", "simple_wp_test.py", "test_wordpress.py"]
    for script in essential_scripts:
        src_file = os.path.join("scripts", script)
        dst_file = os.path.join(temp_dir, "scripts", script)
        if os.path.exists(src_file):
            shutil.copy(src_file, dst_file)
    
    # Copy config files (without sensitive data)
    config_files = ["airth_profile.json", "config.yaml", "env.example", "prompts.json"]
    for config_file in config_files:
        src_file = os.path.join("config", config_file)
        dst_file = os.path.join(temp_dir, "config", config_file)
        if os.path.exists(src_file):
            shutil.copy(src_file, dst_file)
    
    # Create README.md for the Space
    with open(os.path.join(temp_dir, "README.md"), "w") as f:
        f.write(f"""---
title: TEC Office Suite
emoji: ⚡
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# TEC Office Suite

This is the TEC Office Suite, a hub for The Elidoras Codex's AI-powered tools and integrations.

## Features

- **AI Agents**: Chat with Airth, the Machine Goddess AI
- **WordPress Integration**: Post content directly to your WordPress site
- **Time Management**: Productivity tools including Pomodoro timers

## Configuration

To enable WordPress functionality, set the following secrets in your Space:

- `WP_URL`: Your WordPress site URL (with xmlrpc.php)
- `WP_USERNAME`: Your WordPress username
- `WP_PASSWORD`: Your WordPress application password

To enable AI functionality, set the following secrets:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)

""")
    
    print(f"✅ Deployment prepared in: {temp_dir}")
    return temp_dir

def deploy_to_huggingface(repo_path, space_name):
    """Deploy to Hugging Face Space"""
    print(f"Deploying to Hugging Face Space: {space_name}")
    
    # Check if the repository exists
    check_result = run_command(f"huggingface-cli repo info {space_name}")
    
    if check_result.returncode != 0:
        # Create the repository
        print(f"Creating new Space: {space_name}")
        create_result = run_command(f"huggingface-cli repo create {space_name} --type space --space-sdk docker")
        
        if create_result.returncode != 0:
            print(f"❌ Failed to create Space: {space_name}")
            print(create_result.stderr)
            return False
    
    # Initialize git repository in the temporary directory
    git_init = run_command("git init", cwd=repo_path)
    if git_init.returncode != 0:
        print("❌ Failed to initialize git repository.")
        print(git_init.stderr)
        return False
    
    # Add all files
    git_add = run_command("git add .", cwd=repo_path)
    if git_add.returncode != 0:
        print("❌ Failed to add files to git repository.")
        print(git_add.stderr)
        return False
    
    # Configure git user
    git_config_name = run_command("git config user.name \"TEC Office Deployer\"", cwd=repo_path)
    git_config_email = run_command("git config user.email \"deployment@example.com\"", cwd=repo_path)
    
    # Commit changes
    git_commit = run_command("git commit -m \"Update TEC Office Suite\"", cwd=repo_path)
    if git_commit.returncode != 0:
        print("❌ Failed to commit changes.")
        print(git_commit.stderr)
        return False
    
    # Push to Hugging Face
    git_push = run_command(f"git push https://huggingface.co/spaces/{space_name} main -f", cwd=repo_path)
    if git_push.returncode != 0:
        print("❌ Failed to push to Hugging Face.")
        print(git_push.stderr)
        return False
    
    print(f"✅ Successfully deployed to Hugging Face Space: {space_name}")
    print(f"View your Space at: https://huggingface.co/spaces/{space_name}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Deploy TEC Office Suite to Hugging Face Space")
    parser.add_argument("--space", type=str, default="TECHF/TEC_Office_REPO", help="Hugging Face Space name (username/space-name)")
    parser.add_argument("--debug", action="store_true", help="Keep temporary directory for debugging")
    
    args = parser.parse_args()
    
    # Check if Hugging Face CLI is installed and user is logged in
    if not check_huggingface_cli():
        sys.exit(1)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="tec_office_deploy_")
    print(f"Created temporary directory: {temp_dir}")
    
    try:
        # Prepare deployment files
        prepare_deployment(temp_dir, args.space)
        
        # Deploy to Hugging Face
        deploy_to_huggingface(temp_dir, args.space)
        
    finally:
        # Clean up temporary directory
        if not args.debug:
            print(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir)
        else:
            print(f"Temporary directory kept for debugging: {temp_dir}")

if __name__ == "__main__":
    main()
