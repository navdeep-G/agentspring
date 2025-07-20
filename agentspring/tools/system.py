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

@tool("calculate", "Perform mathematical calculations", permissions=[])
def calculate(expression: str):
    """Evaluate mathematical expressions safely"""
    import re
    
    # Handle sum operations specifically
    if expression.startswith('[') and expression.endswith(']'):
        # Convert list format to sum operation
        try:
            numbers = eval(expression)
            if isinstance(numbers, list):
                result = sum(numbers)
                return {"result": result, "expression": f"sum({expression})"}
        except:
            pass
    
    # Handle range expressions like "1-10" or "1 to 10"
    range_pattern = r'(\d+)\s*[-to]\s*(\d+)'
    range_match = re.match(range_pattern, expression)
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        result = sum(range(start, end + 1))
        return {"result": result, "expression": f"sum({start} to {end})"}
    
    # Handle simple arithmetic expressions
    # Only allow safe mathematical operations
    safe_chars = re.compile(r'^[0-9+\-*/().\s]+$')
    if not safe_chars.match(expression):
        # Try to clean the expression
        cleaned = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        if cleaned and safe_chars.match(cleaned):
            expression = cleaned
        else:
            raise ValueError(f"Expression '{expression}' contains unsafe characters. Use only numbers, +, -, *, /, (, ), and spaces.")
    
    try:
        result = eval(expression)
        return {"result": result, "expression": expression}
    except ZeroDivisionError:
        raise ValueError("Division by zero is not allowed")
    except Exception as e:
        raise ValueError(f"Invalid mathematical expression '{expression}': {str(e)}")

@tool("generate_random", "Generate a random number within a range", permissions=[])
def generate_random(min_value: int = 1, max_value: int = 100):
    """Generate a random integer between min_value and max_value"""
    import random
    # Convert to int if string is passed
    min_val = int(min_value) if isinstance(min_value, str) else min_value
    max_val = int(max_value) if isinstance(max_value, str) else max_value
    result = random.randint(min_val, max_val)
    return {"random_number": result, "range": f"{min_val}-{max_val}"}

@tool("is_prime", "Check if a number is prime", permissions=[])
def is_prime(number: int):
    """Check if a number is prime"""
    # Convert to int if string is passed
    num = int(number) if isinstance(number, str) else number
    if num < 2:
        return {"is_prime": False, "number": num}
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return {"is_prime": False, "number": num}
    return {"is_prime": True, "number": num}

@tool("text_to_uppercase", "Convert text to uppercase", permissions=[])
def text_to_uppercase(text: str):
    """Convert text to uppercase"""
    return {"uppercase_text": text.upper(), "original_text": text}

@tool("text_to_lowercase", "Convert text to lowercase", permissions=[])
def text_to_lowercase(text: str):
    """Convert text to lowercase"""
    return {"lowercase_text": text.lower(), "original_text": text}

@tool("count_characters", "Count characters in text", permissions=[])
def count_characters(text: str):
    """Count characters in text"""
    return {"character_count": len(text), "text": text}

@tool("reverse_text", "Reverse text", permissions=[])
def reverse_text(text: str):
    """Reverse text"""
    return {"reversed_text": text[::-1], "original_text": text}

@tool("extract_numbers", "Extract numbers from text", permissions=[])
def extract_numbers(text: str):
    """Extract all numbers from text"""
    import re
    numbers = re.findall(r'\d+', text)
    return {"numbers": [int(n) for n in numbers], "text": text}

@tool("sum_numbers", "Sum a list of numbers", permissions=[])
def sum_numbers(numbers: str):
    """Sum numbers from a comma-separated string"""
    try:
        num_list = [int(x.strip()) for x in numbers.split(',')]
        total = sum(num_list)
        return {"sum": total, "numbers": num_list}
    except ValueError:
        raise ValueError("Invalid number format")

@tool("multiply_numbers", "Multiply a list of numbers", permissions=[])
def multiply_numbers(numbers: str):
    """Multiply numbers from a comma-separated string"""
    try:
        num_list = [int(x.strip()) for x in numbers.split(',')]
        product = 1
        for num in num_list:
            product *= num
        return {"product": product, "numbers": num_list}
    except ValueError:
        raise ValueError("Invalid number format")

@tool("get_current_time", "Get current system time", permissions=[])
def get_current_time():
    """Get current system time"""
    from datetime import datetime
    now = datetime.now()
    return {
        "timestamp": now.isoformat(),
        "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second
    }

@tool("get_system_info", "Get basic system information", permissions=[])
def get_system_info():
    """Get basic system information"""
    import platform
    import os
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "current_directory": os.getcwd()
    }

@tool("format_text", "Format text with various options", permissions=[])
def format_text(text: str, operation: str = "uppercase"):
    """Format text with various operations"""
    operations = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "title": text.title(),
        "capitalize": text.capitalize(),
        "strip": text.strip(),
        "reverse": text[::-1]
    }
    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}")
    return {"formatted_text": operations[operation], "original_text": text, "operation": operation}

@tool("extract_regex", "Extract text using regex pattern", permissions=[])
def extract_regex(text: str, pattern: str):
    """Extract text using regex pattern"""
    import re
    try:
        matches = re.findall(pattern, text)
        return {"matches": matches, "pattern": pattern, "text": text}
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

@tool("replace_text", "Replace text using regex pattern", permissions=[])
def replace_text(text: str, pattern: str, replacement: str):
    """Replace text using regex pattern"""
    import re
    try:
        result = re.sub(pattern, replacement, text)
        return {"replaced_text": result, "original_text": text, "pattern": pattern, "replacement": replacement}
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

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

@tool("count_words", "Count the number of words in a string", permissions=[])
def count_words(text: str):
    word_count = len(text.split())
    return {"word_count": word_count, "text": text}

@tool("summarize_text", "Summarize text by returning the first sentence or a short summary", permissions=[])
def summarize_text(text: str):
    # Simple summary: first sentence or first 20 words
    import re
    sentences = re.split(r'(?<=[.!?]) +', text)
    if sentences and len(sentences[0].split()) <= 20:
        summary = sentences[0]
    else:
        summary = ' '.join(text.split()[:20]) + ("..." if len(text.split()) > 20 else "")
    return {"summary": summary, "text": text} 