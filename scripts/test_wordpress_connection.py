#!/usr/bin/env python3
"""
Test WordPress connection for The Elidoras Codex.
This script verifies that the WordPress credentials are configured correctly.
"""
import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(os.path.join('config', '.env'))

# Import the WordPress test function
from src.wordpress import test_wordpress_connection

def main():
    """Test the WordPress connection."""
    print("Testing WordPress connection...")
    
    # Run the test
    result = test_wordpress_connection()
    
    # Display the result
    print(f"\nConnection successful: {result['success']}")
    print(f"Site URL: {result['site_url']}")
    print(f"Message: {result['message']}")
    
    if not result['success']:
        print("\nTroubleshooting tips:")
        print("1. Check that WP_URL, WP_USERNAME, and WP_PASSWORD are set in config/.env")
        print("2. Ensure that the WordPress site has XML-RPC enabled")
        print("3. Verify that the application password has sufficient permissions")
        print("4. Check if the WordPress site is accessible from this machine")
    
    print("\nFull result:")
    print(json.dumps(result, indent=2))
    
    return 0 if result['success'] else 1

if __name__ == "__main__":
    sys.exit(main())
