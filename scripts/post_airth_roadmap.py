#!/usr/bin/env python
"""
Airth Roadmap Article Test

This script tests Airth's ability to post a roadmap article through the WordPress agent.
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import agent modules
from src.agents.airth_agent import AirthAgent
from src.agents.wp_poster import WordPressAgent
from src.utils.logging_utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger("Airth.RoadmapTest")

def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if not env_path.exists():
        print(f"❌ Environment file not found at {env_path}")
        sys.exit(1)
    
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded environment variables from {env_path}")

def main():
    """Main function to run the Airth roadmap article test"""
    load_environment()
    
    print("==== Airth Roadmap Article Posting Test ====")
    
    try:
        # Initialize Airth agent
        print("🔄 Initializing Airth agent...")
        airth = AirthAgent()
        
        # Initialize WordPress agent
        print("🔄 Initializing WordPress agent...")
        wp = WordPressAgent()
        
        # Check if WordPress credentials are properly configured
        if wp.wp_user == "your_wordpress_username" or \
           wp.wp_app_pass == "your_wordpress_app_password":
            print("❌ WordPress credentials not configured.")
            print("Please update the .env file with proper WordPress credentials.")
            sys.exit(1)
        
        # Generate a roadmap article
        print("🔄 Generating roadmap article through Airth...")
        roadmap_topic = "Future of AI in Content Marketing"
        
        article_content = airth.generate_roadmap_article(
            topic=roadmap_topic, 
            word_count=800,
            include_headings=True,
            include_conclusion=True
        )
        
        if not article_content:
            print("❌ Failed to generate article content.")
            sys.exit(1)
        
        print(f"✅ Successfully generated '{roadmap_topic}' roadmap article!")
        print(f"   Length: ~{len(article_content.split())} words")
        
        # Prepare the post data
        current_date = datetime.now().strftime("%Y-%m-%d")
        post_data = {
            "title": f"{roadmap_topic} - Airth's Roadmap ({current_date})",
            "content": article_content,
            "status": "draft",
            "categories": ["Roadmap", "AI"],
            "tags": ["roadmap", "artificial intelligence", "content marketing", "airth"]
        }
        
        # Post to WordPress
        print("\n🔄 Posting article to WordPress...")
        try:
            result = wp.create_post(post_data)
            
            if result and 'id' in result:
                post_id = result['id']
                post_url = result.get('link', f"ID: {post_id}")
                
                print(f"✅ Successfully posted article to WordPress!")
                print(f"   Post ID: {post_id}")
                print(f"   Post URL: {post_url}")
                print(f"   Status: {result.get('status', 'Unknown')}")
                
                print("\n🎉 Test complete! Airth can successfully post roadmap articles to WordPress.")
                return True
            else:
                print(f"❌ Failed to post article. WordPress API returned: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to WordPress: {str(e)}")
            logger.exception("Error posting to WordPress")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        logger.exception("Unexpected error occurred")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
