"""
Communication Tools for AgentSpring
Includes email, SMS, Slack, and Discord messaging capabilities
"""
import os
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from . import tool

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

@tool("send_email", "Send an email using SMTP", permissions=[])
def send_email(to: str, subject: str, body: str, html_body: str = "", from_email: str = ""):
    """Send an email using configured SMTP settings"""
    try:
        # Get SMTP configuration from environment
        smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        username = os.getenv("EMAIL_USERNAME", from_email)
        password = os.getenv("EMAIL_PASSWORD")
        
        if not username or not password:
            raise Exception("Email configuration not found. Set EMAIL_USERNAME and EMAIL_PASSWORD environment variables.")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = username
        msg['To'] = to
        msg['Subject'] = subject
        
        # Add text and HTML parts
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        
        return {
            "success": True,
            "message": f"Email sent successfully to {to}",
            "subject": subject
        }
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise Exception(f"Failed to send email: {e}")

@tool("send_sms", "Send an SMS message via Twilio", permissions=[])
def send_sms(to: str, message: str, from_number: str = ""):
    """Send an SMS message using Twilio"""
    if not TWILIO_AVAILABLE:
        raise Exception("Twilio not available. Install with: pip install twilio")
    
    try:
        # Get Twilio configuration
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        default_from = os.getenv("TWILIO_FROM_NUMBER", from_number)
        
        if not account_sid or not auth_token:
            raise Exception("Twilio configuration not found. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")
        
        if not default_from:
            raise Exception("Twilio from number not configured. Set TWILIO_FROM_NUMBER environment variable.")
        
        # Send SMS
        client = Client(account_sid, auth_token)
        message_obj = client.messages.create(
            body=message,
            from_=default_from,
            to=to
        )
        
        return {
            "success": True,
            "message": f"SMS sent successfully to {to}",
            "message_sid": message_obj.sid,
            "status": message_obj.status
        }
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        raise Exception(f"Failed to send SMS: {e}")

@tool("send_slack_message", "Send a Slack message via webhook", permissions=[])
def send_slack_message(channel: str, message: str, username: str = "AgentSpring Bot"):
    """Send a message to Slack using webhook"""
    try:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            raise Exception("Slack webhook URL not configured. Set SLACK_WEBHOOK_URL environment variable.")
        
        payload = {
            "channel": channel,
            "text": message,
            "username": username
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Slack message sent to #{channel}",
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        raise Exception(f"Failed to send Slack message: {e}")

@tool("send_discord_message", "Send a Discord message via webhook", permissions=[])
def send_discord_message(channel: str, message: str, username: str = "AgentSpring Bot"):
    """Send a message to Discord using webhook"""
    try:
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            raise Exception("Discord webhook URL not configured. Set DISCORD_WEBHOOK_URL environment variable.")
        
        payload = {
            "content": message,
            "username": username
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Discord message sent to #{channel}",
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Failed to send Discord message: {e}")
        raise Exception(f"Failed to send Discord message: {e}")

@tool("send_notification", "Send a notification to multiple channels", permissions=[])
def send_notification(message: str, channels: List[str] = [], subject: str = "Notification"):
    """Send a notification to multiple channels (email, SMS, Slack, Discord)"""
    results = {}
    
    for channel in channels:
        try:
            if channel.startswith("email:"):
                email = channel.split(":", 1)[1]
                results[channel] = send_email(email, subject or "Notification", message)
            elif channel.startswith("sms:"):
                phone = channel.split(":", 1)[1]
                results[channel] = send_sms(phone, message)
            elif channel.startswith("slack:"):
                slack_channel = channel.split(":", 1)[1]
                results[channel] = send_slack_message(slack_channel, message)
            elif channel.startswith("discord:"):
                discord_channel = channel.split(":", 1)[1]
                results[channel] = send_discord_message(discord_channel, message)
            else:
                results[channel] = {"success": False, "error": f"Unknown channel type: {channel}"}
        except Exception as e:
            results[channel] = {"success": False, "error": str(e)}
    
    return {
        "success": any(r.get("success", False) for r in results.values()),
        "results": results,
        "message": f"Notification sent to {len(channels)} channels"
    } 