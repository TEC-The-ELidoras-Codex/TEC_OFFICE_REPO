"""
WordPress Posting Agent for The Elidoras Codex.
Handles interactions with WordPress for publishing content.
"""
import os
import logging
import json
import requests
from typing import Dict, Any, List, Optional
from base64 import b64encode

from .base_agent import BaseAgent

class WordPressAgent(BaseAgent):
    """
    WordPressAgent handles interactions with the WordPress API.
    It creates posts, updates content, and manages media uploads.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("WordPressAgent", config_path)
        self.logger.info("WordPressAgent initialized")
        
        # Initialize WordPress API credentials
        # Support both naming conventions for compatibility
        self.wp_site_url = os.getenv("WP_SITE_URL") or os.getenv("WP_URL", "https://elidorascodex.com")
        self.wp_user = os.getenv("WP_USER") or os.getenv("WP_USERNAME")
        self.wp_app_pass = os.getenv("WP_APP_PASS") or os.getenv("WP_PASSWORD")
        
        # Check for required environment variables
        if not self.wp_site_url or not self.wp_user or not self.wp_app_pass:
            self.logger.warning("WordPress credentials not fully configured in environment variables.")
        
        # WordPress REST API endpoints
        self.api_base_url = f"{self.wp_site_url.rstrip('/')}/wp-json/wp/v2" if self.wp_site_url else None
        
        # Predefined categories and tags for TEC content
        self.categories = {
            "airths_codex": None,  # Will be populated during get_categories
            "technology_ai": None,
            "reviews_deepdives": None,
            "uncategorized": None
        }
        
        # Common tags for AI content
        self.common_ai_tags = [
            "ai-ethics", "ai-storytelling", "ai-assisted-writing", 
            "ai-driven-creativity", "ai-generated-content", "ai-human-collaboration",
            "creative-ai-tools"
        ]
        
        # Cache categories on initialization
        if self.api_base_url:
            self.get_categories()
    
    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get the authorization header for WordPress API requests.
        Uses Basic Authentication that works with WordPress.com sites.
        
        Returns:
            Dictionary containing the Authorization header
        """
        if not self.wp_user or not self.wp_app_pass:
            self.logger.error("Cannot create auth header: WordPress credentials not configured")
            return {}
            
        # Convert username to lowercase for consistency
        username = self.wp_user.lower()
        
        # Use Basic Authentication with username and password with spaces
        credentials = f"{username}:{self.wp_app_pass}"
        token = b64encode(credentials.encode()).decode()
        
        self.logger.debug(f"Generated Basic Auth token for WordPress API")
        return {"Authorization": f"Basic {token}"}
    
    def _try_multiple_auth_methods(self, method: str, url: str, data: Dict = None) -> requests.Response:
        """
        Try multiple authentication methods for WordPress API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: API URL to request
            data: Data to send (for POST/PUT)
            
        Returns:
            Response from the successful authentication method or the last attempted response
        """
        # Authentication methods to try in order
        auth_methods = [
            {
                "name": "Bearer token",
                "headers": {
                    **self._get_auth_header(),
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Basic auth with spaces",
                "auth": (self.wp_user.lower(), self.wp_app_pass)
            }
        ]
        
        last_response = None
        errors = []
        
        # Try each authentication method
        for auth_method in auth_methods:
            try:
                self.logger.debug(f"Trying {auth_method['name']} authentication")
                
                if "headers" in auth_method:
                    # Use headers authentication
                    response = requests.request(
                        method=method,
                        url=url,
                        headers=auth_method["headers"],
                        json=data
                    )
                else:
                    # Use basic auth
                    response = requests.request(
                        method=method,
                        url=url,
                        auth=auth_method["auth"],
                        json=data,
                        headers={"Content-Type": "application/json"}
                    )
                
                last_response = response
                
                # If successful, return the response
                if response.status_code < 400:
                    self.logger.debug(f"Authentication successful with {auth_method['name']}")
                    return response
                else:
                    error = f"{auth_method['name']} failed with status {response.status_code}: {response.text}"
                    self.logger.debug(error)
                    errors.append(error)
                    
            except Exception as e:
                error = f"{auth_method['name']} failed with exception: {e}"
                self.logger.debug(error)
                errors.append(error)
        
        # If all methods failed, log the errors
        self.logger.error(f"All authentication methods failed: {errors}")
        return last_response
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get the categories from WordPress.
        Populates the self.categories dictionary with category IDs.
        
        Returns:
            List of categories from the WordPress site
        """
        if not self.api_base_url:
            self.logger.error("Cannot get categories: API base URL not set")
            return []
        
        try:
            url = f"{self.api_base_url}/categories"
            response = self._try_multiple_auth_methods("GET", url)
            
            if response and response.status_code == 200:
                categories = response.json()
                
                # Update the category IDs
                for category in categories:
                    slug = category.get("slug")
                    if slug in self.categories:
                        self.categories[slug] = category.get("id")
                
                self.logger.debug(f"Retrieved {len(categories)} categories")
                return categories
            else:
                status_code = response.status_code if response else "No response"
                self.logger.error(f"Failed to get categories: Status {status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error retrieving categories: {e}")
            return []
    
    def create_post(self, title: str, content: str, 
                   category: str = "uncategorized", 
                   tags: List[str] = None,
                   status: str = "draft") -> Dict[str, Any]:
        """
        Create a post on WordPress.
        
        Args:
            title: The post title
            content: The post content HTML
            category: The category slug to post to
            tags: The tags to apply to the post
            status: Publication status (draft, publish, etc.)
            
        Returns:
            Dictionary with post status and details
        """
        if not self.api_base_url:
            self.logger.error("Cannot create post: API base URL not set")
            return {"success": False, "error": "WordPress API URL not configured"}
            
        if not self.wp_user or not self.wp_app_pass:
            self.logger.error("Cannot create post: WordPress credentials not configured")
            return {"success": False, "error": "WordPress credentials not configured"}
            
        # Get category ID
        category_id = self.categories.get(category)
        if category_id is None:
            # Try refreshing categories
            self.get_categories()
            category_id = self.categories.get(category)
            
            # Fall back to uncategorized
            if category_id is None:
                category_id = self.categories.get("uncategorized")
                
        # Prepare tag IDs (first create them if they don't exist)
        tag_ids = []
        if tags:
            for tag in tags:
                tag_id = self._create_or_get_tag(tag)
                if tag_id:
                    tag_ids.append(tag_id)
        
        # Prepare the post data
        post_data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        # Add categories if available
        if category_id:
            post_data["categories"] = [category_id]
            
        # Add tags if available
        if tag_ids:
            post_data["tags"] = tag_ids
            
        try:
            # Create the post
            url = f"{self.api_base_url}/posts"
            response = self._try_multiple_auth_methods("POST", url, post_data)
            
            if response and response.status_code in [200, 201]:
                post_data = response.json()
                post_id = post_data.get("id")
                post_url = post_data.get("link")
                
                self.logger.info(f"Created post with ID {post_id}: {title}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "title": title,
                    "url": post_url,
                    "status": status
                }
            else:
                status_code = response.status_code if response else "No response"
                error_message = response.text if response else "No response"
                self.logger.error(f"Failed to create post: Status {status_code}, {error_message}")
                return {
                    "success": False,
                    "error": f"API error: {error_message}",
                    "status_code": status_code
                }
                
        except Exception as e:
            self.logger.error(f"Error creating post: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_or_get_tag(self, tag: str) -> Optional[int]:
        """
        Create a tag if it doesn't exist, or get its ID if it does.
        
        Args:
            tag: The tag name/slug
            
        Returns:
            The tag ID if successful, None otherwise
        """
        if not self.api_base_url:
            self.logger.error("Cannot create tag: API base URL not set")
            return None
            
        try:
            # First check if the tag exists
            search_url = f"{self.api_base_url}/tags?search={tag}"
            search_response = self._try_multiple_auth_methods("GET", search_url)
            
            if search_response and search_response.status_code == 200:
                tags = search_response.json()
                if tags:
                    # Check for exact match
                    for tag_data in tags:
                        if tag_data.get("name").lower() == tag.lower():
                            return tag_data.get("id")
                    
            # Tag doesn't exist, create it
            create_url = f"{self.api_base_url}/tags"
            create_data = {
                "name": tag
            }
            create_response = self._try_multiple_auth_methods("POST", create_url, create_data)
            
            if create_response and create_response.status_code in [200, 201]:
                tag_data = create_response.json()
                return tag_data.get("id")
            else:
                self.logger.error(f"Failed to create tag: {tag}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error working with tag {tag}: {e}")
            return None
    
    def upload_media(self, file_path: str, title: str = None) -> Dict[str, Any]:
        """
        Upload media to WordPress.
        
        Args:
            file_path: Path to the media file
            title: Optional title for the media
            
        Returns:
            Dictionary with media status and details
        """
        # This is a placeholder for media upload functionality
        # WordPress media upload requires a different approach with multipart/form-data
        self.logger.warning("Media upload not yet implemented")
        return {"success": False, "error": "Media upload not implemented"}
    
    def run(self) -> Dict[str, Any]:
        """
        Run a test post to verify WordPress connectivity.
        
        Returns:
            Dictionary with the result of the test
        """
        test_title = "TEC WordPress Connection Test"
        test_content = "<p>This is an automated test post from the WordPressAgent.</p>"
        
        return self.create_post(test_title, test_content, status="draft")


# For testing the agent standalone
if __name__ == "__main__":
    wp_agent = WordPressAgent()
    result = wp_agent.run()
    print(json.dumps(result, indent=2))
