# AgentSpring Tool Configuration Guide

This guide explains how to configure and use all the real implementations in AgentSpring's tool registry.

## Overview

AgentSpring now includes real, working implementations for all tools. Users can:
- Install optional dependencies as needed
- Configure services via environment variables
- Use tools immediately without writing integration code

## Installation

### Core Dependencies
```bash
pip install -r requirements.txt
```

### Optional Dependencies (install as needed)
```bash
# For database operations (PostgreSQL)
pip install psycopg2-binary

# For PDF reading
pip install PyPDF2

# For image processing and OCR
pip install Pillow pytesseract

# For SMS (Twilio)
pip install twilio

# For Google Calendar
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# For audio transcription
pip install openai-whisper

# For document text extraction
pip install textract python-docx

# For OCR (system dependency)
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
```

## Configuration

### Email (SMTP)
Configure SMTP settings for sending emails:

```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587port SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Note:** For Gmail, use an App Password, not your regular password.

### SMS (Twilio)
Configure Twilio for sending SMS messages:

```bash
export TWILIO_ACCOUNT_SID=your-account-sid
export TWILIO_AUTH_TOKEN=your-auth-token
export TWILIO_FROM_NUMBER=+1234567890
```

**Setup:**1Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the dashboard
3. Get a phone number for sending SMS

### Slack Integration
Configure Slack webhook for sending messages:

```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Setup:**
1. Go to your Slack workspace settings
2. Create an incoming webhook
3. Copy the webhook URL

### Discord Integration
Configure Discord webhook for sending messages:

```bash
export DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

**Setup:**
1. Go to your Discord server settings
2. Create a webhook
3. Copy the webhook URL

### Google Calendar
Configure Google Calendar API for creating and listing events:

```bash
export GOOGLE_CALENDAR_CREDENTIALS_JSON=/path/to/your/service-account.json
```

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create a service account
5. Download the JSON credentials file
6. Share your calendar with the service account email

### Database
Configure database connection (optional, defaults to SQLite):

```bash
# For PostgreSQL
export DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# For SQLite (default)
export DATABASE_URL=sqlite:///app.db
```

### CRM Database
Configure CRM database path (optional, defaults to crm.sqlite3):

```bash
export CRM_DB_PATH=/path/to/crm.sqlite3
```

### User Management Database
Configure user database path (optional, defaults to users.sqlite3):

```bash
export USER_DB_PATH=/path/to/users.sqlite3
```

### System Logs
Configure log file path (optional, defaults to {service}.log):

```bash
export LOG_PATH=/path/to/your/logs/app.log
```

## Usage Examples

### Basic Tool Usage
```python
from agentspring.tools import tool_registry

# Send an email
result = tool_registry.execute_tool("send_email", 
                                   to="user@example.com",
                                   subject="Hello",
                                   body="This is a test email)

#Send an SMS
result = tool_registry.execute_tool("send_sms",
                                   to="+1234567890",
                                   message="Hello from AgentSpring!)

# Send a Slack message
result = tool_registry.execute_tool("send_slack_message",
                                   channel="#general",
                                   message="Hello from AgentSpring!")

# Create a calendar event
result = tool_registry.execute_tool("create_event",
                                   title="Team Meeting",
                                   start_time=20241                   end_time=20241                   attendees=["user@example.com"])

# Query database
result = tool_registry.execute_tool("query_db",
                                   query="SELECT * FROM users")

# Read PDF
result = tool_registry.execute_tool("read_pdf",
                                   file_path=document.pdf)

# Extract text from image (OCR)
result = tool_registry.execute_tool("ocr_text",
                                   image_path="image.png")

# Transcribe audio
result = tool_registry.execute_tool("transcribe_audio",
                                   audio_path="audio.mp3")

# Search the web
result = tool_registry.execute_tool("search_web",
                                   query="Python programming",
                                   max_results=5)
```

### CRM Operations
```python
# Create a contact
result = tool_registry.execute_tool(create_contact                   name="John Doe",
                                   email="john@example.com",
                                   phone="+1234567890)

# Update a lead
result = tool_registry.execute_tool("update_lead",
                                   lead_id="1",
                                   updates={"status": "qualified"})
```

### User Management
```python
# Create a user
result = tool_registry.execute_tool("create_user",
                                   username="john_doe",
                                   email="john@example.com",
                                   password="secure_password")

# Update permissions
result = tool_registry.execute_tool("update_permissions",
                                   username="john_doe",
                                   permissions=[read, write,admin"])
```

## Tool Categories

### Communication Tools
- **Email (SMTP):** Send emails via SMTP
- **SMS (Twilio):** Send SMS messages
- **Slack (Webhook):** Send messages to Slack
- **Discord (Webhook):** Send messages to Discord

### Calendar Tools
- **Google Calendar:** Create and list calendar events

### Database Tools
- **SQLite/PostgreSQL:** Query, insert, update, delete records
- **CRM (SQLite):** Contact and lead management
- **User Management (SQLite):** User accounts and permissions

### File & Document Tools
- **PDF Reading:** Extract text from PDF files
- **OCR:** Extract text from images
- **Text Extraction:** Extract text from various document formats
- **File Operations:** Read, write, copy, move, delete files

### Media Tools
- **Audio Transcription:** Transcribe audio to text
- **Image Analysis:** Get image information

### System Tools
- **System Information:** Get system details
- **Process Information:** Get running process details
- **Network Information:** Get network interface details
- **System Logs:** Read log files
- **Command Execution:** Run system commands

### Utility Tools
- **Web Search:** Search the web using DuckDuckGo
- **HTTP Requests:** Make HTTP requests
- **Text Processing:** Format, extract, replace text
- **Encoding/Decoding:** Base64, hashing
- **Math & Time:** Calculations and time utilities

## Error Handling

All tools provide clear error messages when:
- Required dependencies are not installed
- Required environment variables are not set
- Services are not properly configured
- Files or resources are not found

## Customization

Users can:
1. **Extend existing tools:** Modify the implementation in `tools.py`
2**Add new tools:** Use the `@tool` decorator
3. **Replace implementations:** Swap out the function body
4. **Add new services:** Integrate with additional APIs

## Security Notes

- Store sensitive credentials in environment variables, not in code
- Use service accounts for Google APIs
- Use app passwords for email services
- Regularly rotate API keys and tokens
- Follow the principle of least privilege for API permissions

## Troubleshooting

### Common Issues

1**Import Errors:** Install the required optional dependencies
2. **Authentication Errors:** Check environment variables and API credentials
3. **Permission Errors:** Ensure proper file/directory permissions
4. **Network Errors:** Check internet connectivity and firewall settings

### Getting Help

- Check the error messages for specific guidance
- Verify all required environment variables are set
- Ensure optional dependencies are installed
- Test with simple examples first

## Next Steps

1. Install the optional dependencies you need
2. Configure the services you want to use
3. Test with simple examples4ntegrate into your applications
5. Customize as needed for your use case 

## ⚠️ Troubleshooting: textract
`textract` is currently broken on PyPI due to dependency metadata (see https://github.com/deanmalmgren/textract/issues/360). It is not included in requirements.txt. If you need it, install manually:

```bash
pip install --no-deps textract==1.6.4
pip install extract-msg==0.28.7
``` 