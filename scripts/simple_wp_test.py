#!/usr/bin/env python
"""
Simple WordPress Post Test - Tests WordPress posting functionality

This script creates a simple test post on your WordPress site to verify
that the credentials and connectivity are working properly.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "wp_posting_test.log"))
    ]
)
logger = logging.getLogger("WordPress.PostTest")

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Load environment variables from the .env file
env_path = Path(__file__).parent.parent / "config" / ".env"
if not env_path.exists():
    logger.error(f".env file not found at {env_path}. Please create this file with your WordPress credentials.")
    print(f"\n⚠️ .env file not found. Please create {env_path} with your WordPress credentials.")
    print("You can use the .env.template file as a starting point.\n")
    sys.exit(1)

load_dotenv(dotenv_path=env_path)

def create_test_post():
    """Create a simple test post on WordPress"""
    try:
        # Import here to ensure environment variables are loaded first
        from src.agents.wp_poster import WordPressAgent
        
        wp_agent = WordPressAgent()
        
        # Generate a unique test post
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        random_id = random.randint(1000, 9999)
        
        test_title = f"Test Post {random_id} - {timestamp}"
        test_content = f"""
        <p>This is an automated test post created at {timestamp}.</p>
        <p>If you're seeing this post, your WordPress integration is working correctly!</p>
        <p>Test ID: {random_id}</p>
        <hr/>
        <p><em>Posted from TEC Office Suite test script</em></p>
        """
        
        # Set categories and tags
        categories = wp_agent.get_categories()
        if not categories:
            logger.warning("No categories found. Using default category.")
            category_ids = [1]  # Default "Uncategorized" category
        else:
            # Try to use "Technology" category if it exists, otherwise use the first category
            tech_category_id = None
            for cat_id, cat_name in categories.items():
                if "tech" in cat_name.lower():
                    tech_category_id = cat_id
                    break
            
            category_ids = [tech_category_id] if tech_category_id else [list(categories.keys())[0]]
          # Create the post - using the correct method signature
        print(f"Creating test post: {test_title}")
        result = wp_agent.create_post(
            title=test_title,
            content=test_content,
            status="draft",  # Always create as draft for testing
            category="uncategorized",
            tags=['test', 'automated-test', 'tec-office']
        )
        
        if result.get('success'):
            print(f"\n✅ Test post created successfully!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Title: {result.get('title')}")
            print(f"   Status: {result.get('status', 'draft')}")
            print("\n   Your WordPress integration is working correctly!")
            return True
        else:
            print(f"\n❌ Failed to create test post: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.exception("Failed to create test post")
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("==== Simple WordPress Post Test ====\n")
    
    # Check environment variables
    wp_url = os.getenv("WP_URL")
    wp_username = os.getenv("WP_USERNAME")
    wp_password = os.getenv("WP_PASSWORD")
    
    if not all([wp_url, wp_username, wp_password]):
        print("❌ Missing WordPress credentials in environment variables.")
        print("Please set WP_URL, WP_USERNAME, and WP_PASSWORD in your .env file.")
        sys.exit(1)
    
    print(f"WordPress URL: {wp_url}")
    print(f"WordPress Username: {wp_username}")
    print(f"WordPress Password: {'*' * len(wp_password) if wp_password else 'NOT SET'}")
    print("\nCreating a test post as a draft...")
    
    success = create_test_post()
    
    if success:
        print("\n✅ WordPress posting test completed successfully.")
        print("You can now run the Airth agent to post more complex content.")
    else:
        print("\n❌ WordPress posting test failed. Please check the error messages and your configuration.")
        sys.exit(1)
