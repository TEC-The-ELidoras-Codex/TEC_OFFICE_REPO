#!/usr/bin/env python
"""
Simple WordPress REST API Test

This script tests direct REST API connectivity with WordPress,
bypassing the WordPressAgent class to debug connectivity issues.
"""
import os
import sys
import requests
import base64
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / "logs" / "wp_direct_api_test.log")
    ]
)
logger = logging.getLogger("WP.DirectAPI.Test")

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / "config" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded environment variables from {env_path}")
else:
    print(f"❌ Environment file not found at {env_path}")
    sys.exit(1)

def test_wordpress_connection():
    """Test direct WordPress REST API connectivity"""
    # Get credentials from environment variables
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USERNAME")
    wp_pass = os.getenv("WP_PASSWORD")
    
    if not all([wp_url, wp_user, wp_pass]):
        print("❌ WordPress credentials not fully configured in .env file")
        missing = []
        if not wp_url: missing.append("WP_URL")
        if not wp_user: missing.append("WP_USERNAME")
        if not wp_pass: missing.append("WP_PASSWORD")
        print(f"Missing: {', '.join(missing)}")
        return False
    
    # Clean up URL to ensure proper API base
    if wp_url.endswith('xmlrpc.php'):
        print("⚠️ URL points to XML-RPC endpoint, adjusting to REST API")
        wp_url = wp_url.replace('xmlrpc.php', '')
        if not wp_url.endswith('/'):
            wp_url += '/'
    
    # Ensure URL doesn't end with 'wp-json/'
    if wp_url.endswith('wp-json/'):
        pass  # This is good
    elif wp_url.endswith('/'):
        wp_url += 'wp-json/'
    else:
        wp_url += '/wp-json/'
    
    # Basic authentication token
    credentials = f"{wp_user}:{wp_pass}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔄 Testing connection to WordPress REST API...")
    print(f"URL: {wp_url}")
    print(f"User: {wp_user}")
    
    try:
        # First test - Get site info
        info_url = f"{wp_url}"
        print(f"\n📡 Requesting site info from: {info_url}")
        
        response = requests.get(info_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully connected to {data.get('name', 'WordPress site')}")
            print(f"   Description: {data.get('description', 'No description')}")
            print(f"   URL: {data.get('url', 'Unknown URL')}")
        else:
            print(f"❌ Failed to connect to site: Status code {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
        
        # Second test - List posts
        posts_url = f"{wp_url}wp/v2/posts?status=draft,publish&per_page=1"
        print(f"\n📡 Requesting posts from: {posts_url}")
        
        response = requests.get(posts_url, headers=headers)
        
        if response.status_code == 200:
            posts = response.json()
            print(f"✅ Successfully retrieved {len(posts)} post(s)")
            if posts:
                post = posts[0]
                print(f"   Latest post: {post.get('title', {}).get('rendered', 'No title')}")
                print(f"   Status: {post.get('status', 'Unknown')}")
        else:
            print(f"❌ Failed to get posts: Status code {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
        
        # Third test - Create a test draft post
        create_url = f"{wp_url}wp/v2/posts"
        test_post = {
            'title': 'REST API Test Post',
            'content': '<p>This is a test post created via the WordPress REST API.</p>',
            'status': 'draft',
            'categories': [1]  # Default uncategorized category
        }
        
        print(f"\n📡 Creating test post at: {create_url}")
        
        response = requests.post(create_url, headers=headers, json=test_post)
        
        if response.status_code in [200, 201]:
            post_data = response.json()
            post_id = post_data.get('id')
            print(f"✅ Successfully created test post!")
            print(f"   Post ID: {post_id}")
            print(f"   Title: {post_data.get('title', {}).get('rendered', 'No title')}")
            print(f"   Status: {post_data.get('status', 'Unknown')}")
            
            # Clean up - delete the test post
            delete_url = f"{wp_url}wp/v2/posts/{post_id}?force=true"
            print(f"\n🧹 Cleaning up test post: {delete_url}")
            
            del_response = requests.delete(delete_url, headers=headers)
            
            if del_response.status_code in [200, 204]:
                print(f"✅ Successfully deleted test post!")
            else:
                print(f"⚠️ Failed to delete test post: Status code {del_response.status_code}")
        else:
            print(f"❌ Failed to create test post: Status code {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
        
        print("\n✅ All WordPress REST API tests passed successfully!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection error: {str(e)}")
        logger.exception("Request failed")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        logger.exception("Unexpected error")
        return False

def main():
    print("==== WordPress REST API Direct Connection Test ====")
    success = test_wordpress_connection()
    
    if success:
        print("\n✅ WordPress connectivity test passed!")
        print("Your WordPress REST API connection is working properly.")
        sys.exit(0)
    else:
        print("\n❌ WordPress connectivity test failed.")
        print("Please check your WordPress credentials and API endpoints.")
        sys.exit(1)

if __name__ == "__main__":
    main()
