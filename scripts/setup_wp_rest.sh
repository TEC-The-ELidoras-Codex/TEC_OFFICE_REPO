#!/bin/bash
# Setup script for WordPress REST API configuration
# This script helps create a proper .env file for WordPress REST API access

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory and project paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/config/.env"
LOG_FILE="$PROJECT_ROOT/logs/wp_setup.log"

# Set up logging
log() {
    local message=$1
    local level=${2:-INFO}
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local log_entry="$timestamp - $level - $message"
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Write to log file
    echo "$log_entry" >> "$LOG_FILE"
    
    # Also write to console with color
    case $level in
        ERROR)
            echo -e "${RED}$log_entry${NC}"
            ;;
        WARNING)
            echo -e "${YELLOW}$log_entry${NC}"
            ;;
        SUCCESS)
            echo -e "${GREEN}$log_entry${NC}"
            ;;
        *)
            echo "$log_entry"
            ;;
    esac
}

echo -e "${CYAN}🔄 WordPress REST API Configuration Setup${NC}"
echo -e "${CYAN}=========================================${NC}"
log "Starting WordPress REST API configuration setup"

# Check if .env file exists
if [[ -f "$ENV_FILE" ]]; then
    echo -e "\n${YELLOW}⚠️ An existing .env file was found at $ENV_FILE${NC}"
    read -p "Do you want to update it with REST API configurations? (y/n) " overwrite
    
    if [[ "$overwrite" != "y" ]]; then
        echo -e "\n${RED}❌ Setup cancelled. Your existing .env file was not modified.${NC}"
        exit
    fi
    
    log "User chose to update existing .env file"
    
    # Backup the existing file
    backup_file="$ENV_FILE.bak"
    cp "$ENV_FILE" "$backup_file"
    echo -e "\n${GREEN}✅ Created backup of existing .env file at $backup_file${NC}"
    log "Created backup of existing .env file at $backup_file" "SUCCESS"
fi

# Get WordPress information
echo -e "\n${CYAN}📝 WordPress REST API Configuration${NC}"
echo -e "${CYAN}--------------------------------${NC}"

read -p "Enter your WordPress site URL (e.g., https://yourdomain.com): " wp_url
read -p "Enter your WordPress username: " wp_username
read -sp "Enter your WordPress application password: " wp_password
echo ""
read -p "Enter WordPress API version [wp/v2]: " wp_api_version

# Set default API version if empty
if [[ -z "$wp_api_version" ]]; then
    wp_api_version="wp/v2"
fi

# Clean up URL
if [[ "$wp_url" == */ ]]; then
    wp_url=${wp_url%/}
fi

# Create .env content
cat > "$ENV_FILE" << EOL
# TEC_OFFICE_REPO Environment Variables
# Configured for WordPress REST API

# WordPress REST API Configuration
WP_URL=$wp_url
WP_USERNAME=$wp_username
WP_PASSWORD=$wp_password
WP_API_VERSION=$wp_api_version

# AI Provider Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo

# Logging Configuration
LOG_LEVEL=INFO
DEBUG=false

# Agent-Specific Configuration
AIRTH_PERSONALITY=confident, intelligent, slightly sarcastic
EOL

echo -e "\n${GREEN}✅ WordPress REST API configuration saved to $ENV_FILE${NC}"
log "WordPress REST API configuration saved to $ENV_FILE" "SUCCESS"

# Set restrictive permissions - limit to current user
chmod 600 "$ENV_FILE"
echo -e "${GREEN}✅ Set secure permissions on .env file${NC}"

# Test WordPress connection
echo -e "\n${CYAN}🔄 Would you like to test the WordPress REST API connection now? (y/n)${NC}"
read test_connection

if [[ "$test_connection" == "y" ]]; then
    echo -e "\n${CYAN}🔄 Testing WordPress REST API connection...${NC}"
    log "Testing WordPress REST API connection"
    
    # Run the test script
    python "$SCRIPT_DIR/wp_rest_api_test.py"
    test_result=$?
    
    if [[ $test_result -eq 0 ]]; then
        echo -e "\n${GREEN}✅ WordPress REST API connection test succeeded!${NC}"
        log "WordPress REST API connection test succeeded" "SUCCESS"
        
        echo -e "\n${GREEN}🎉 You're all set to use WordPress with TEC Office Suite!${NC}"
        echo -e "${GREEN}You can now use the Airth agent to post content to WordPress.${NC}"
    else
        echo -e "\n${RED}❌ WordPress REST API connection test failed.${NC}"
        echo -e "${YELLOW}Please check the error messages above for details.${NC}"
        log "WordPress REST API connection test failed" "ERROR"
    fi
else
    echo -e "\n${YELLOW}⚠️ Skipping connection test. You can run it later with:${NC}"
    echo -e "${CYAN}python scripts/wp_rest_api_test.py${NC}"
fi

echo -e "\n${CYAN}👉 Next Steps:${NC}"
echo -e "- Run the WordPress test script: python scripts/test_wordpress.py"
echo -e "- Post a roadmap article: python scripts/post_roadmap_article.py"
echo -e "- Use the Docker container: docker-compose up -d"
