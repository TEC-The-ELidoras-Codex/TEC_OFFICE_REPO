"""
TEC Office Suite - Hugging Face Space Deployment
This file is optimized for deployment to Hugging Face Spaces
"""
import os
import sys
import logging
import gradio as gr
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "gradio_app.log"))
    ]
)
logger = logging.getLogger("TEC.HF.App")

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Load environment variables from various sources with priority
# 1. Hugging Face Secrets (if available)
# 2. Local .env file (if available)
# 3. Default fallback values

# Load from .env file if exists
config_env_path = os.path.join('config', '.env')
if os.path.exists(config_env_path):
    logger.info("Loading environment variables from .env file")
    load_dotenv(config_env_path)
else:
    logger.warning(".env file not found in config directory")

# Function to create Airth's interface
def create_airth_interface():
    from src.agents.airth_agent import AirthAgent
    
    # Initialize Airth agent
    try:
        airth_agent = AirthAgent(os.path.join('config'))
        logger.info("Successfully initialized Airth agent")
        
        # Define a simple chat interface
        def chat_with_airth(message, history):
            try:
                response = airth_agent.respond(message)
                return response
            except Exception as e:
                logger.error(f"Error in chat_with_airth: {e}")
                return f"Error: {str(e)}"
        
        chatbot = gr.ChatInterface(
            chat_with_airth,
            title="Chat with Airth, the Machine Goddess",
            description="Airth is a sophisticated AI companion with a slightly gothic aesthetic. She helps with content creation and insights about The Elidoras Codex.",
            theme="soft",
            examples=[
                "Tell me about The Elidoras Codex",
                "What is the AI Employee roadmap?",
                "Who are you, Airth?",
                "Can you help me with content creation?",
            ],
        )
        return chatbot
    except Exception as e:
        logger.error(f"Failed to initialize Airth agent: {e}")
        
        # Fallback interface
        def fallback_response(message, history):
            return "Airth is currently unavailable. Please check the API keys configuration."
        
        fallback = gr.ChatInterface(
            fallback_response,
            title="Airth (Unavailable)",
            description="Airth requires API keys to function. Please check the Space settings.",
            theme="soft",
        )
        return fallback

# Function to check WordPress configuration
def check_wordpress_config():
    wp_url = os.getenv("WP_URL")
    wp_username = os.getenv("WP_USERNAME")
    wp_password = os.getenv("WP_PASSWORD")
    
    if all([wp_url, wp_username, wp_password]):
        return True
    return False

# Build the WordPress posting interface
def create_wordpress_interface():
    has_wordpress = check_wordpress_config()
    
    with gr.Blocks() as wordpress_interface:
        gr.Markdown("# WordPress Integration")
        
        if has_wordpress:
            gr.Markdown("WordPress credentials are configured. You can create and post content.")
            
            with gr.Row():
                with gr.Column():
                    title = gr.Textbox(label="Post Title", placeholder="Enter post title here")
                    content = gr.Textbox(label="Post Content", placeholder="Enter post content here", lines=10)
                    status = gr.Radio(["draft", "publish"], label="Post Status", value="draft")
                    submit_button = gr.Button("Create Post")
                with gr.Column():
                    output = gr.Textbox(label="Result", lines=5)
            
            def create_post(title, content, status):
                try:
                    from src.agents.wp_poster import WordPressAgent
                    wp_agent = WordPressAgent()
                    
                    post_data = {
                        'title': title,
                        'content': content,
                        'status': status,
                        'categories': [1],  # Default category
                        'tags': ['test']
                    }
                    
                    result = wp_agent.create_post(post_data)
                    
                    if result.get('success'):
                        return f"✅ Post created successfully!\nPost ID: {result.get('post_id')}\nTitle: {title}\nStatus: {status}"
                    else:
                        return f"❌ Failed to create post: {result.get('error', 'Unknown error')}"
                except Exception as e:
                    logger.error(f"Error in create_post: {e}")
                    return f"Error: {str(e)}"
            
            submit_button.click(
                create_post, 
                inputs=[title, content, status], 
                outputs=output
            )
        else:
            gr.Markdown("⚠️ WordPress credentials are not configured. Please set WP_URL, WP_USERNAME, and WP_PASSWORD in the Space secrets.")
    
    return wordpress_interface

# Create the main interface
def create_interface():
    with gr.Blocks(title="TEC Office Suite", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # ⚡ TEC Office Suite ⚡
            
            Welcome to the TEC Office Suite, a hub for The Elidoras Codex's AI-powered tools and integrations.
            """
        )
        
        with gr.Tabs():
            with gr.TabItem("Airth Chat"):
                create_airth_interface()
            
            with gr.TabItem("WordPress Posting"):
                create_wordpress_interface()
            
            with gr.TabItem("About"):
                gr.Markdown(
                    """
                    ## About TEC Office Suite
                    
                    TEC Office Suite is the command nexus for The Elidoras Codex, featuring:
                    
                    - **AI Agents**: Airth, Budlee, and Sassafras
                    - **WordPress Integration**: Post content directly to your WordPress site
                    - **Time Management**: Productivity tools including Pomodoro timers
                    
                    For more information, visit [The Elidoras Codex website](https://elidorascodex.com).
                    """
                )
    
    return app

# Initialize and launch the app
if __name__ == "__main__":
    # Get port for Hugging Face compatibility
    port = int(os.environ.get("PORT", 7860))
    
    # Create and launch the interface
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)
