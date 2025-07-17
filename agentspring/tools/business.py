"""
Business Tools for AgentSpring
Includes calendar, CRM, user management, and report tools
"""
from typing import List, Optional
from . import tool
import sqlite3

@tool("create_event", "Create a Google Calendar event", permissions=[])
def create_event(title: str, start_time: str, end_time: str, attendees: list = []):
    # Placeholder: Implement Google Calendar API integration
    return {
        "success": True,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "attendees": attendees,
        "message": "Event created (demo)"
    }

@tool("list_events", "List Google Calendar events", permissions=[])
def list_events(calendar_id: str = "primary"):
    # Placeholder: Implement Google Calendar API integration
    return {
        "success": True,
        "calendar_id": calendar_id,
        "events": [],
        "message": "Events listed (demo)"
    }

@tool("create_user", "Create a user account (SQLite)", permissions=[])
def create_user(username: str, email: str, password: str):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')
    c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return {"success": True, "user_id": user_id}

@tool("update_permissions", "Update user permissions (SQLite)", permissions=[])
def update_permissions(username: str, permissions: list):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS permissions (username TEXT, permission TEXT)''')
    c.execute('DELETE FROM permissions WHERE username = ?', (username,))
    for perm in permissions:
        c.execute('INSERT INTO permissions (username, permission) VALUES (?, ?)', (username, perm))
    conn.commit()
    conn.close()
    return {"success": True, "username": username, "permissions": permissions}

@tool("generate_report", "Generate a business report (demo)", permissions=[])
def generate_report(report_type: str, parameters: dict = {}):
    # Demo: just return a summary
    return {
        "success": True,
        "report_type": report_type,
        "parameters": parameters,
        "summary": f"Report '{report_type}' generated (demo)"
    } 