# AgentSpring Tool Configuration Guide

This guide explains how to configure and use all the real implementations in AgentSpring's tool registry.

## Overview

AgentSpring now includes real, working implementations for all tools. Users can:
- Install optional dependencies as needed
- Configure services via environment variables
- Use tools immediately without writing integration code
- **Orchestrate tools in multi-step workflows using natural language prompts**

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
export SMTP_PORT=587
export SMTP_USERNAME=your-email@gmail.com
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

### Slack Integration
Configure Slack webhook for sending messages:
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Tool Usage

### Use a Tool Directly
```python
from agentspring.tools import tool_registry
result = tool_registry.execute_tool("read_file", file_path="README.md")
print(result.result["content"])
```

### Register a Custom Tool
```python
from agentspring.tools import tool_registry
@tool_registry.register
def greet(name: str) -> dict:
    return {"greeting": f"Hello, {name}!"}
```

### Orchestrate Tools with Natural Language
You can use AgentSpring's orchestration system to chain tools dynamically:
```python
from agentspring.orchestration import create_orchestrator
orchestrator = create_orchestrator()
result = orchestrator.execute_prompt("Read the README file, summarize it, and send the summary to Slack.")
print(result)
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
1. **Extend existing tools:** Modify the implementation in `tools/`
2. **Add new tools:** Use the `@tool_registry.register` decorator
3. **Replace implementations:** Swap out the function body

See the main [README](README.md) for more details and orchestration examples. 