import pytest
from src.tools import validate_bash_command, execute_bash, validate_api_request, execute_api

def test_validate_bash_command_allowed():
    """Tests that allowed commands are validated correctly."""
    parts, msg = validate_bash_command("ls -la")
    assert parts == ["ls", "-la"]
    assert msg == "OK"

def test_validate_bash_command_not_allowed():
    """Tests that not allowed commands are rejected."""
    parts, msg = validate_bash_command("rm -rf /")
    assert parts is None
    assert msg == "Command 'rm' is not allowed."

def test_validate_bash_command_list():
    """Tests that list commands are validated correctly."""
    parts, msg = validate_bash_command(["ls", "-la"])
    assert parts == ["ls", "-la"]
    assert msg == "OK"

def test_execute_bash_allowed():
    """Tests that allowed commands are executed correctly."""
    result = execute_bash("ls -la")
    assert result["status"] == "success"
    assert result["return_code"] == 0

def test_execute_bash_not_allowed():
    """Tests that not allowed commands are not executed."""
    result = execute_bash("rm -rf /")
    assert result["status"] == "error"
    assert result["output"] == "Command 'rm' is not allowed."

def test_validate_api_request_allowed():
    """Tests that allowed domains are validated correctly."""
    is_valid, msg = validate_api_request("http://jsonplaceholder.typicode.com/todos/1")
    assert is_valid is True
    assert msg == "OK"

def test_validate_api_request_not_allowed():
    """Tests that not allowed domains are rejected."""
    is_valid, msg = validate_api_request("http://example.com")
    assert is_valid is False
    assert msg == "Domain 'example.com' is not in the allowlist."

def test_execute_api_allowed():
    """Tests that API requests to allowed domains are executed correctly."""
    result = execute_api({
        "method": "GET",
        "url": "http://jsonplaceholder.typicode.com/todos/1",
        "headers": {},
        "body": {}
    })
    assert result["status"] == "success"
    assert result["status_code"] == 200

def test_execute_api_not_allowed():
    """Tests that API requests to not allowed domains are not executed."""
    result = execute_api({
        "method": "GET",
        "url": "http://example.com",
        "headers": {},
        "body": {}
    })
    assert result["status"] == "error"
    assert result["output"] == "Domain 'example.com' is not in the allowlist."
