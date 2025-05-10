#!/usr/bin/env python
"""
Test WordPress posting with both calling styles.
This script tests both the dictionary and parameter-based styles for create_post.
"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / "logs" / "wp_test_styles.log")
    ]
)
logger = logging.getLogger("WP.Test.Styles")

# Load environment variables from the .env file
env_path = Path(__file__).parent.parent / "config" / ".env"
if not env_path.exists():
    logger.error(f".env file not found at {env_path}")
    print(f"\n⚠️ .env file not found. Please create {env_path} with your WordPress credentials.")
    print("You can use the .env.template file as a starting point.\n")
    sys.exit(1)

load_dotenv(dotenv_path=env_path)

def test_parameter_style():
    """Test the WordPress posting with separate parameters style."""
    from src.agents.wp_poster import WordPressAgent
    
    print("\n🔄 Testing WordPress posting (Parameter Style)...")
    try:
        wp_agent = WordPressAgent()
        
        test_title = "Test Post - Parameter Style"
        test_content = """
        <p>This is a test post created using the parameter style of the create_post method.</p>
        <p>If you see this post in your WordPress drafts, the parameter style is working correctly!</p>
        """
        
        result = wp_agent.create_post(
            title_or_data=test_title,
            content=test_content,
            category="uncategorized",
            tags=["test", "parameter-style"],
            status="draft"
        )
        
        if result.get('success'):
            print(f"✅ Parameter style test passed!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Title: {result.get('title')}")
            print(f"   Status: {result.get('status', 'draft')}")
            return True
        else:
            print(f"❌ Parameter style test failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        logger.exception("Parameter style test failed")
        print(f"❌ Parameter style test failed: {str(e)}")
        return False

def test_dictionary_style():
    """Test the WordPress posting with dictionary style."""
    from src.agents.wp_poster import WordPressAgent
    
    print("\n🔄 Testing WordPress posting (Dictionary Style)...")
    try:
        wp_agent = WordPressAgent()
        
        post_data = {
            'title': 'Test Post - Dictionary Style',
            'content': '<p>This is a test post created using the dictionary style of the create_post method.</p>'
                      '<p>If you see this post in your WordPress drafts, the dictionary style is working correctly!</p>',
            'status': 'draft',
            'tags': ['test', 'dictionary-style']
        }
        
        result = wp_agent.create_post(post_data)
        
        if result.get('success'):
            print(f"✅ Dictionary style test passed!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Title: {result.get('title')}")
            print(f"   Status: {result.get('status', 'draft')}")
            return True
        else:
            print(f"❌ Dictionary style test failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        logger.exception("Dictionary style test failed")
        print(f"❌ Dictionary style test failed: {str(e)}")
        return False

def main():
    print("==== WordPress Integration Test - Both Calling Styles ====")
    
    # Test parameter style
    param_success = test_parameter_style()
    
    # Test dictionary style
    dict_success = test_dictionary_style()
    
    # Output results summary
    print("\n==== Test Results Summary ====")
    print(f"Parameter Style: {'✅ PASSED' if param_success else '❌ FAILED'}")
    print(f"Dictionary Style: {'✅ PASSED' if dict_success else '❌ FAILED'}")
    
    if param_success and dict_success:
        print("\n✅ All tests passed! Both WordPress posting styles are working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
