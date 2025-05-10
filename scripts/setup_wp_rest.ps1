# PowerShell script to setup WordPress REST API configuration
# This script helps create a proper .env file for WordPress REST API access

# Get the script directory and project paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$EnvFile = Join-Path -Path $ProjectRoot -ChildPath "config\.env"
$LogFile = Join-Path -Path $ProjectRoot -ChildPath "logs\wp_setup.log"

# Set up logging
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Level - $Message"
    
    # Create logs directory if it doesn't exist
    $LogDir = Split-Path -Parent $LogFile
    if (-not (Test-Path $LogDir)) {
        New-Item -Path $LogDir -ItemType Directory | Out-Null
    }
    
    # Write to log file
    Add-Content -Path $LogFile -Value $logEntry
    
    # Also write to console with color
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry -ForegroundColor White }
    }
}

Write-Host "🔄 WordPress REST API Configuration Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Log "Starting WordPress REST API configuration setup"

# Check if .env file exists
if (Test-Path $EnvFile) {
    Write-Host "`n⚠️ An existing .env file was found at $EnvFile" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to update it with REST API configurations? (y/n)"
    
    if ($overwrite -ne "y") {
        Write-Host "`n❌ Setup cancelled. Your existing .env file was not modified." -ForegroundColor Red
        exit
    }
    
    Write-Log "User chose to update existing .env file"
    
    # Backup the existing file
    $backupFile = "$EnvFile.bak"
    Copy-Item -Path $EnvFile -Destination $backupFile -Force
    Write-Host "`n✅ Created backup of existing .env file at $backupFile" -ForegroundColor Green
    Write-Log "Created backup of existing .env file at $backupFile" -Level "SUCCESS"
}

# Get WordPress information
Write-Host "`n📝 WordPress REST API Configuration" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan

$wpUrl = Read-Host "Enter your WordPress site URL (e.g., https://yourdomain.com)"
$wpUsername = Read-Host "Enter your WordPress username"
$wpPassword = Read-Host "Enter your WordPress application password" -AsSecureString
$wpApiVersion = Read-Host "Enter WordPress API version [wp/v2]"

# Set default API version if empty
if ([string]::IsNullOrWhiteSpace($wpApiVersion)) {
    $wpApiVersion = "wp/v2"
}

# Convert secure string password to plain text for .env file
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($wpPassword)
$wpPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)

# Clean up URL
if ($wpUrl.EndsWith("/")) {
    $wpUrl = $wpUrl.TrimEnd("/")
}

# Create .env content
$envContent = @"
# TEC_OFFICE_REPO Environment Variables
# Configured for WordPress REST API

# WordPress REST API Configuration
WP_URL=$wpUrl
WP_USERNAME=$wpUsername
WP_PASSWORD=$wpPasswordPlain
WP_API_VERSION=$wpApiVersion

# AI Provider Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo

# Logging Configuration
LOG_LEVEL=INFO
DEBUG=false

# Agent-Specific Configuration
AIRTH_PERSONALITY=confident, intelligent, slightly sarcastic
"@

# Write to .env file
$envContent | Out-File -FilePath $EnvFile -Encoding utf8 -Force
Write-Host "`n✅ WordPress REST API configuration saved to $EnvFile" -ForegroundColor Green
Write-Log "WordPress REST API configuration saved to $EnvFile" -Level "SUCCESS"

# Set restrictive permissions - limit to current user
$acl = Get-Acl -Path $EnvFile
$acl.SetAccessRuleProtection($true, $false)
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$fileSystemRights = [System.Security.AccessControl.FileSystemRights]::FullControl
$inheritanceFlags = [System.Security.AccessControl.InheritanceFlags]::None
$propagationFlags = [System.Security.AccessControl.PropagationFlags]::None
$accessControlType = [System.Security.AccessControl.AccessControlType]::Allow
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($identity, $fileSystemRights, $inheritanceFlags, $propagationFlags, $accessControlType)
$acl.AddAccessRule($rule)
Set-Acl -Path $EnvFile -AclObject $acl
Write-Host "✅ Set secure permissions on .env file" -ForegroundColor Green

# Test WordPress connection
Write-Host "`n🔄 Would you like to test the WordPress REST API connection now? (y/n)" -ForegroundColor Cyan
$testConnection = Read-Host

if ($testConnection -eq "y") {
    Write-Host "`n🔄 Testing WordPress REST API connection..." -ForegroundColor Cyan
    Write-Log "Testing WordPress REST API connection"
    
    try {
        & python "$ScriptDir\wp_rest_api_test.py"
        $testResult = $LASTEXITCODE
        
        if ($testResult -eq 0) {
            Write-Host "`n✅ WordPress REST API connection test succeeded!" -ForegroundColor Green
            Write-Log "WordPress REST API connection test succeeded" -Level "SUCCESS"
            
            Write-Host "`n🎉 You're all set to use WordPress with TEC Office Suite!" -ForegroundColor Green
            Write-Host "You can now use the Airth agent to post content to WordPress." -ForegroundColor Green
        } else {
            Write-Host "`n❌ WordPress REST API connection test failed." -ForegroundColor Red
            Write-Host "Please check the error messages above for details." -ForegroundColor Yellow
            Write-Log "WordPress REST API connection test failed" -Level "ERROR"
        }
    } catch {
        Write-Host "`n❌ Error executing the test script: $_" -ForegroundColor Red
        Write-Log "Error executing the test script: $_" -Level "ERROR"
    }
} else {
    Write-Host "`n⚠️ Skipping connection test. You can run it later with:" -ForegroundColor Yellow
    Write-Host "python scripts\wp_rest_api_test.py" -ForegroundColor Cyan
}

Write-Host "`n👉 Next Steps:" -ForegroundColor Cyan
Write-Host "- Run the WordPress testing menu: scripts\test_wordpress_menu.ps1" -ForegroundColor White
Write-Host "- Post a roadmap article: python scripts\post_roadmap_article.py" -ForegroundColor White
Write-Host "- Use the Docker container: docker-compose up -d" -ForegroundColor White
