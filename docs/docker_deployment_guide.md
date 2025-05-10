# Deploying TEC Office Suite with Docker

This guide covers Docker deployment options for TEC Office Suite including local Docker deployments and Hugging Face Space deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Docker Deployment](#local-docker-deployment)
3. [Hugging Face Space Deployment](#hugging-face-space-deployment)
4. [Environment Variables](#environment-variables)
5. [Testing WordPress Integration](#testing-wordpress-integration)

## Prerequisites

- Docker and Docker Compose installed for local deployment
- Git installed
- A Hugging Face account (for Hugging Face Space deployment)
- WordPress site with REST API enabled (for WordPress integration)

## Local Docker Deployment

### 1. Configure Environment Variables

First, set up your environment variables. You have two options:

**Option A:** Use the setup script (recommended):

```bash
# Windows (PowerShell)
cd scripts
.\setup_wp_rest.ps1

# Linux/macOS
cd scripts
bash ./setup_wp_rest.sh
```

**Option B:** Manually create your `.env` file:

```bash
# Copy the template
cp config/env.example config/.env

# Edit with your favorite editor
nano config/.env
```

### 2. Build the Docker Image

```bash
docker build -t tec_office:latest .
```

### 3. Start the Container

```bash
docker-compose up -d
```

### 4. Verify the Container is Running

```bash
docker ps
```

You should see output showing the `tec_office` container running on port 7860.

### 5. Access the Application

Open your browser and navigate to:

```
http://localhost:7860
```

## Hugging Face Space Deployment

### 1. Clone Your Space Repository

Replace `your-username` with your Hugging Face username:

```bash
git clone https://huggingface.co/spaces/your-username/TEC_Office_REPO
cd TEC_Office_REPO
```

### 2. Add TEC Office Files

Copy the TEC Office files to your Space repository:

```bash
# Copy all files from your local TEC_OFFICE_REPO
cp -r /path/to/your/TEC_CODE/TEC_OFFICE_REPO/* .
```

### 3. Create Secrets for Environment Variables

In the Hugging Face Space dashboard:

1. Go to Settings > Repository Secrets
2. Add the following secrets:
   - `WP_URL`: Your WordPress site URL
   - `WP_USERNAME`: Your WordPress username
   - `WP_PASSWORD`: Your WordPress application password
   - `OPENAI_API_KEY`: Your OpenAI API key

### 4. Use the Hugging Face Dockerfile

Ensure you're using the Hugging Face-specific Dockerfile:

```bash
mv Dockerfile.huggingface Dockerfile
```

### 5. Commit and Push

```bash
git add .
git commit -m "Deploy TEC Office Suite to Hugging Face"
git push
```

### 6. Check Deployment

Visit your Hugging Face Space at `https://huggingface.co/spaces/your-username/TEC_Office_REPO` to see your deployment.

## Environment Variables

TEC Office Suite requires the following environment variables for proper operation:

### WordPress Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| WP_URL | WordPress site URL | https://yourdomain.com |
| WP_USERNAME | WordPress username | admin |
| WP_PASSWORD | WordPress app password | xxxx xxxx xxxx xxxx |
| WP_API_VERSION | WordPress API version | wp/v2 |

### AI Provider Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| OPENAI_API_KEY | OpenAI API key | sk-... |
| OPENAI_MODEL | OpenAI model to use | gpt-4-turbo |
| ANTHROPIC_API_KEY | Anthropic API key (optional) | sk-ant-... |

### Logging Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| LOG_LEVEL | Logging verbosity | INFO |
| DEBUG | Debug mode flag | false |

## Testing WordPress Integration

You can verify that WordPress integration is working correctly:

### 1. Test WordPress Connectivity

```bash
# From inside the container
docker exec -it tec_office python scripts/wp_rest_api_test.py

# Or from your local environment
python scripts/wp_rest_api_test.py
```

### 2. Post a Test Article

```bash
# From inside the container
docker exec -it tec_office python scripts/post_roadmap_article.py

# Or from your local environment
python scripts/post_roadmap_article.py
```

### 3. Check for Errors

Examine the logs for any WordPress-related errors:

```bash
# View container logs
docker logs tec_office

# Check specific log files
cat logs/wp_posting_test.log
```

If you encounter issues, ensure your WordPress site has REST API enabled and your credentials are correct.

## Troubleshooting

- **REST API Errors**: If you get JSON parsing errors, make sure your WordPress URL is the site root URL, not the xmlrpc.php endpoint
- **Authentication Failures**: Verify your WordPress username and application password
- **Container Won't Start**: Check Docker logs with `docker logs tec_office`
