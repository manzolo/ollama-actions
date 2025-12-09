import subprocess
import requests
import json
import shlex
from urllib.parse import urlparse

# --- SAFETY CONFIGURATION ---

# Allowed Bash commands (block risky ones like rm -rf /)
ALLOWED_COMMANDS = {
    # File operations
    "ls", "cat", "echo", "pwd", "mkdir", "touch", "cp", "mv", 
    # System info
    "date", "whoami", "uname",
    # Network
    "curl", "ping" 
}

# Allowed API Domains (Allow localhost for training purposes and some safe external ones if needed)
ALLOWED_DOMAINS = {
    "localhost",
    "127.0.0.1",
    "user-service",  # Internal user management service
    "jsonplaceholder.typicode.com", # Good for testing
    "httpbin.org" # Good for testing
}

# --- IMPLEMENTATION ---

def validate_bash_command(command):
    """
    Parses a bash command and checks if the executable is in the allowlist.
    Returns (list, message).
    """
    if isinstance(command, list):
        parts = command
    elif isinstance(command, str):
        parts = shlex.split(command)
    else:
        return None, "Command must be a string or a list"

    if not parts:
        return None, "Empty command"
    
    program = parts[0]
    
    if program not in ALLOWED_COMMANDS:
        return None, f"Command '{program}' is not allowed."
        
    return parts, "OK"

def execute_bash(command):
    """
    Executes a bash command if allowed.
    Returns a unified result dict.
    """
    parts, msg = validate_bash_command(command)
    if not parts:
        return {"status": "error", "output": msg}

    try:
        result = subprocess.run(
            parts, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        return {
            "status": "success" if result.returncode == 0 else "failure",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Command timed out"}
    except Exception as e:
        return {"status": "error", "output": str(e)}

def validate_api_request(url):
    """
    Checks if the URL hostname is in the allowlist.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL"
            
        # Check against allowed domains
        # This is a strict string match for simplicity. 
        # In prod you might handle subdomains etc.
        if hostname in ALLOWED_DOMAINS:
            return True, "OK"
            
        return False, f"Domain '{hostname}' is not in the allowlist."
    except Exception as e:
        return False, f"Error validating URL: {str(e)}"

def execute_api(api_details):
    """
    Executes an HTTP API request.
    Expected dict structure:
    {
        "method": "GET" | "POST" | ...,
        "url": "http://...",
        "headers": {},
        "body": {}
    }
    """
    method = api_details.get("method", "GET").upper()
    url = api_details.get("url")
    headers = api_details.get("headers", {})
    body = api_details.get("body", {})

    is_valid, msg = validate_api_request(url)
    if not is_valid:
        return {"status": "error", "output": msg}

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body,
            timeout=10
        )
        
        # Try to parse JSON response, fallback to text
        try:
            resp_data = response.json()
        except:
            resp_data = response.text

        return {
            "status": "success",
            "status_code": response.status_code,
            "data": resp_data
        }

    except Exception as e:
        return {"status": "error", "output": str(e)}
