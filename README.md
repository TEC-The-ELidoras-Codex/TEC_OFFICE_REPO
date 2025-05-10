# ⚡ TEC_OFFICE_REPO: Command Nexus for The Elidoras Codex ⚡

Welcome, **Codex Architects**, to the TEC_OFFICE_REPO—a hub of automation, AI-enhanced workflows, and mythic cyberpunk integrations. This repository powers the inner workings of TEC's development universe, blending **GPT-driven automation**, **WordPress integrations**, **time management tools**, and **cybernetic efficiency**.

---

## 🌌 Vision

The TEC_OFFICE_REPO embodies the **Elidoras Codex philosophy**:  

> *"Unite the mythic with the modular; harness AI to forge digital realms that transcend the mundane."*

This repository is the **nerve center** for TEC's internal operations, designed for:  

1. **AI-Powered Automation**: Craft and deploy TEC-specific GPT workflows.  
2. **WordPress Integration**: Generate cybernetic WordPress content and tools.  
3. **AI Agents**: Host and manage TEC's virtual employees: Airth, Budlee, and Sassafras.
4. **Time Management**: Implement Pomodoro technique and timer functionality for productivity.

---

## 🛠️ Repository Structure

Here's a breakdown of the architecture:

```plaintext
TEC_OFFICE_REPO/
├── config/               # Configuration files (config.yaml, prompts.json, .env)
├── data/                 # Data storage (memories, lore, media)
│   └── storage/          # Persistent storage for timers and other data
├── logs/                 # Log files 
├── scripts/              # Utility scripts for various operations
├── src/                  # Core source code
│   ├── agents/           # AI agent implementations
│   │   ├── airth_agent.py    # Airth - Oracle/Knowledge agent
│   │   ├── budlee_agent.py   # Budlee - Automation agent
│   │   ├── sassafras_agent.py # Sassafras - Creative agent
│   │   ├── wp_poster.py      # WordPress posting capabilities
│   │   └── base_agent.py     # Base agent class
│   ├── utils/            # Utility functions and helpers
│   ├── wordpress/        # WordPress integration modules
│   └── main.py           # Main entry point for CLI usage
├── tests/                # Unit and integration tests
├── app.py                # Gradio web interface
├── Dockerfile            # Container definition for Docker
├── docker-compose.yml    # Docker Compose configuration
├── Makefile              # Common development tasks
└── README.md             # You are here 🚀
```

---

## 🚀 Quickstart Guide

### 1. **Clone the Repository**

```bash
git clone https://github.com/your-organization/TEC_OFFICE_REPO.git
cd TEC_OFFICE_REPO
```

### 2. **Set Up Environment**

Create your configuration file:

```bash
# Create a config directory if it doesn't exist
mkdir -p config

# Copy the example environment file
cp config/env.example config/.env

# Edit with your credentials
nano config/.env
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. **Run Tests**

Verify everything is working:

```bash
# Using make
make test

# Or directly with pytest
python -m pytest tests/
```

### 4. **Start the Application**

Run the Gradio interface:

```bash
python app.py
```

### 5. **Docker Deployment**

For containerized deployment:

```bash
# Build the Docker image
make docker-build

# Start the containers
make docker-up

# Check container status
python scripts/docker_manager.py status
```

---

## 🤖 Agent Features

### Airth - The Oracle

Airth specializes in knowledge retrieval, blog writing, and research:

```python
from src.agents.airth_agent import AirthAgent

# Initialize Airth
airth = AirthAgent('config')

# Get a response from Airth
response = airth.respond("Explain the concept of neural networks")

# Create a blog post
blog_post = airth.create_blog_post(
    "The Future of AI", 
    ["technology", "artificial intelligence"]
)
```

### Budlee - The Automaton

Budlee focuses on task automation and system management:

```python
from src.agents.budlee_agent import BudleeAgent

# Initialize Budlee
budlee = BudleeAgent('config')

# Process a task
result = budlee.process_task("Schedule a weekly backup of our database")
```

### Sassafras - The Creative

Sassafras generates creative content and artistic outputs:

```python
from src.agents.sassafras_agent import SassafrasAgent

# Initialize Sassafras
sassafras = SassafrasAgent('config')

# Generate creative content
creative_text = sassafras.create("A cyberpunk short story about digital consciousness")
```

---

## 🌐 Integration Features

### WordPress Integration

Seamlessly post to WordPress sites:

```python
from src.agents.wp_poster import WordPressAgent

# Initialize the WordPress agent
wp_agent = WordPressAgent('config')

# Create a post
result = wp_agent.create_post(
    title="The Digital Frontier",
    content="<p>Exploring the future of technology...</p>",
    category="Technology",
    tags=["future", "AI", "digital"],
    status="draft"  # or "publish" to go live immediately
)
```

### GitHub Integration

Connect and manage GitHub repositories:

```python
# Run the GitHub connection script
python scripts/github_connection.py status your-repository-name
```

### Hugging Face Integration

Deploy models to Hugging Face Spaces:

```python
# Check if a space exists
python scripts/huggingface_connection.py check your-username your-space-name

# Create a new space
python scripts/huggingface_connection.py create your-username your-space-name --sdk gradio
```

---

## 🧪 Testing

Run tests to ensure everything is working properly:

```bash
# Test utilities
python -m pytest tests/test_utils.py

# Test agents
python -m pytest tests/test_base_agent.py

# Test WordPress connection
python scripts/test_wordpress_connection.py
```

---

## 🐳 Docker Deployment

The repo includes Docker configuration for easy deployment:

```bash
# Build the Docker image
python scripts/docker_manager.py build

# Start the containers
python scripts/docker_manager.py up

# Check status
python scripts/docker_manager.py status

# View logs
python scripts/docker_manager.py logs
```

---

## 📋 Development Tasks

Use the Makefile for common development tasks:

```bash
# Setup the project
make setup

# Install dependencies
make install

# Run tests
make test

# Run linting
make lint

# Build Docker image
make docker-build

# Start Docker containers
make docker-up

# Stop Docker containers
make docker-down

# Test WordPress connection
make wp-test

# Clean up build artifacts
make clean
```

---

## 🔧 Configuration

Create a `config/.env` file with the following variables:

```
# WordPress Configuration
WP_URL=https://your-wordpress-site.com/xmlrpc.php
WP_USERNAME=your_username
WP_PASSWORD=your_application_password

# Hugging Face Configuration
HF_TOKEN=your_huggingface_token

# GitHub Configuration
GITHUB_TOKEN=your_github_token

# AI Provider Configuration
OPENAI_API_KEY=your_openai_api_key
```

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

3. Commit your changes: `git commit -m "Forge: Added my-feature"`.  

4. Push to your branch: `git push origin feature/my-feature`.  

5. Open a pull request.  

---

## 🛡️ License

This repository is licensed under the **Elidoras Codex Open License**, empowering creators to build mythic systems.
