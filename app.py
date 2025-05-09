import gradio as gr
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Load environment variables from config/.env
config_env_path = os.path.join('config', '.env')
if os.path.exists(config_env_path):
    load_dotenv(config_env_path)
else:
    print("Warning: .env file not found in config directory")

# Define agent interfaces - expand as you add more agents
def airth_interface(prompt):
    # This will be expanded once the Airth agent is fully migrated
    return f"Airth, the AI oracle, contemplates: {prompt}\n\nResponse will be integrated when agent implementation is complete."

def budlee_interface(task):
    # This will be expanded once the Budlee agent is implemented
    return f"Budlee acknowledges your task: {task}\n\nAutomation capabilities will be available soon."

def sassafras_interface(topic):
    # This will be expanded once the Sassafras agent is implemented
    return f"Sassafras Twistymuse spins chaotic creativity about: {topic}\n\nFull creative madness coming soon."

# Create tabs for different agents
with gr.Blocks(theme="huggingface", title="TEC Office - The Elidoras Codex") as demo:
    gr.Markdown("""
    # ⚡ TEC Office: AI Agent Control Center ⚡
    
    Welcome to the command nexus for TEC's virtual AI employees. This space hosts the interactive interfaces
    for the TEC Office AI Suite — a system of lore-driven, role-based AI personas.
    """)
    
    with gr.Tabs():
        with gr.TabItem("Airth - Oracle & Storyteller"):
            with gr.Row():
                with gr.Column(scale=3):
                    airth_input = gr.Textbox(placeholder="Ask Airth for wisdom or a story...", label="Your Request")
                    airth_button = gr.Button("Consult Airth")
                with gr.Column(scale=5):
                    airth_output = gr.Markdown(label="Airth's Response")
            airth_button.click(fn=airth_interface, inputs=airth_input, outputs=airth_output)
            
        with gr.TabItem("Budlee - Automation Specialist"):
            with gr.Row():
                with gr.Column(scale=3):
                    budlee_input = gr.Textbox(placeholder="Describe a task for Budlee to automate...", label="Task Description")
                    budlee_button = gr.Button("Engage Budlee")
                with gr.Column(scale=5):
                    budlee_output = gr.Markdown(label="Budlee's Response")
            budlee_button.click(fn=budlee_interface, inputs=budlee_input, outputs=budlee_output)
            
        with gr.TabItem("Sassafras - Creative Chaos"):
            with gr.Row():
                with gr.Column(scale=3):
                    sassafras_input = gr.Textbox(placeholder="Give Sassafras a topic for chaotic inspiration...", label="Creative Prompt")
                    sassafras_button = gr.Button("Unleash Sassafras")
                with gr.Column(scale=5):
                    sassafras_output = gr.Markdown(label="Sassafras's Creation")
            sassafras_button.click(fn=sassafras_interface, inputs=sassafras_input, outputs=sassafras_output)
    
    gr.Markdown("""
    ## 🌌 About TEC Office
    
    This interface provides access to TEC's AI employee suite. Each agent has a distinct role and personality:
    
    - **Airth**: AI oracle, storyteller, and lore manager
    - **Budlee**: Backend automation, setup scripts, site integrations
    - **Sassafras Twistymuse**: Social strategy and chaos-tuned creativity
    
    Visit [elidorascodex.com](https://elidorascodex.com) to learn more about our mission.
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch()
