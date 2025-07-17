"""
System & Admin Tools for AgentSpring
Includes system info, logs, math, environment, and command tools
"""
import os
import platform
import subprocess
import math
import statistics
from typing import List, Optional
from . import tool

@tool("get_system_info", "Get comprehensive system information", permissions=[])
def get_system_info():
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "cwd": os.getcwd()
    }

@tool("get_current_time", "Get current date and time with timezone", permissions=[])
def get_current_time():
    from datetime import datetime
    import time
    return {
        "datetime": datetime.now().isoformat(),
        "timestamp": time.time()
    }

@tool("calculate", "Perform mathematical calculations with enhanced functions", permissions=[])
def calculate(expression: str):
    try:
        result = eval(expression, {"__builtins__": None}, {"math": math, "statistics": statistics})
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e), "expression": expression}

@tool("generate_hash", "Generate various types of hashes", permissions=[])
def generate_hash(data: str, algorithm: str = "md5"):
    import hashlib
    h = getattr(hashlib, algorithm, None)
    if not h:
        raise Exception(f"Unsupported hash algorithm: {algorithm}")
    return {"hash": h(data.encode()).hexdigest(), "algorithm": algorithm}

@tool("encode_base64", "Encode string to base64", permissions=[])
def encode_base64(data: str):
    import base64
    return {"encoded": base64.b64encode(data.encode()).decode()}

@tool("decode_base64", "Decode base64 string", permissions=[])
def decode_base64(encoded_data: str):
    import base64
    return {"decoded": base64.b64decode(encoded_data.encode()).decode()}

@tool("format_text", "Format text with various transformations", permissions=[])
def format_text(text: str, operation: str = "lower"):
    if operation == "lower":
        return {"result": text.lower()}
    elif operation == "upper":
        return {"result": text.upper()}
    elif operation == "title":
        return {"result": text.title()}
    elif operation == "capitalize":
        return {"result": text.capitalize()}
    else:
        return {"result": text}

@tool("extract_regex", "Extract text using regular expressions", permissions=[])
def extract_regex(text: str, pattern: str):
    import re
    matches = re.findall(pattern, text)
    return {"matches": matches}

@tool("replace_text", "Replace text using regular expressions", permissions=[])
def replace_text(text: str, pattern: str, replacement: str):
    import re
    result = re.sub(pattern, replacement, text)
    return {"result": result}

@tool("get_environment_variable", "Get environment variable", permissions=[])
def get_environment_variable(name: str, default: str = ""):
    return {"value": os.getenv(name, default)}

@tool("set_environment_variable", "Set environment variable", permissions=[])
def set_environment_variable(name: str, value: str):
    os.environ[name] = value
    return {"success": True, "name": name, "value": value}

@tool("list_environment_variables", "List all environment variables", permissions=[])
def list_environment_variables():
    return {"env": dict(os.environ)}

@tool("create_temp_file", "Create a temporary file", permissions=[])
def create_temp_file(content: str = "", suffix: str = ".tmp"):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return {"temp_file": path}

@tool("create_temp_directory", "Create a temporary directory", permissions=[])
def create_temp_directory():
    import tempfile
    path = tempfile.mkdtemp()
    return {"temp_dir": path}

@tool("run_command", "Run a system command", permissions=[])
def run_command(command: str, timeout: int = 30):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, timeout=timeout, text=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e), "command": command}

@tool("get_logs", "Get system logs from a file", permissions=[])
def get_logs(service: str = "api"):
    log_file = f"{service}.log"
    if not os.path.exists(log_file):
        return {"error": f"Log file {log_file} not found"}
    with open(log_file, 'r') as f:
        return {"log_file": log_file, "content": f.read()} 