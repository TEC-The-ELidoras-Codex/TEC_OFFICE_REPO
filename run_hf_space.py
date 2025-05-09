#!/usr/bin/env python3
"""
Script to launch the TEC Office Hugging Face Space.
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join('config', '.env'))

# Import the Gradio app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import demo

def main():
    """Launch the Hugging Face Space app."""
    parser = argparse.ArgumentParser(description='Launch the TEC Office Hugging Face Space')
    parser.add_argument('--share', action='store_true', help='Create a public link')
    parser.add_argument('--port', type=int, default=7860, help='Port to run the app on')
    args = parser.parse_args()
    
    print(f"Launching TEC Office Gradio app on port {args.port}")
    if args.share:
        print("Creating a public link for sharing")
    
    # Launch the app
    demo.launch(server_name="0.0.0.0", server_port=args.port, share=args.share)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
