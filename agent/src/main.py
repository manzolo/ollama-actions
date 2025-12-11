import os
import json
import time
import requests
from flask import Flask, request, jsonify
from tools import execute_bash, execute_api

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# --- CONVERSATION MEMORY ---
# Store conversation history per session
# Key: session_id, Value: list of message dicts with role/content
conversation_history = {}

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3.2")
APP_PORT = int(os.environ.get("APP_PORT", 5000))
USER_SERVICE_PORT = int(os.environ.get("USER_SERVICE_PORT", 5001))
USER_SERVICE_HOST = f"http://user-service:{USER_SERVICE_PORT}"
DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

# --- OLLAMA HELPERS ---

def wait_for_ollama():
    """Loops until Ollama is ready."""
    print(f"Waiting for Ollama at {OLLAMA_HOST}...")
    while True:
        try:
            resp = requests.get(f"{OLLAMA_HOST}/api/tags")
            if resp.status_code == 200:
                print("Ollama is ready!")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)

def check_and_pull_model():
    """Checks if the model exists, otherwise pulls it."""
    print(f"Checking for model '{MODEL_NAME}'...")
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags")
        models = [m['name'] for m in resp.json().get('models', [])]
        
        # Check against full name or 'latest'
        if MODEL_NAME in models or f"{MODEL_NAME}:latest" in models:
            print(f"Model '{MODEL_NAME}' is already present.")
            return

        print(f"Model '{MODEL_NAME}' not found. Pulling... (This might take a while)")
        pull_resp = requests.post(f"{OLLAMA_HOST}/api/pull", json={"name": MODEL_NAME}, stream=True)
        # Consume stream to ensure it finishes
        for line in pull_resp.iter_lines():
            if line:
                print(f"Pulling: {line.decode('utf-8')}")
        print("Model pulled successfully.")

    except Exception as e:
        print(f"Error checking/pulling model: {e}")

def chat_with_ollama(user_instruction):
    """
    Sends the user prompt to Ollama with the specialized system prompt.
    Returns the raw response text.
    """
    system_prompt = f"""
You are a helpful Agent that can ONLY perform two types of actions: bash commands or API requests.
You must reply with ONLY valid JSON. No markdown, no explanations, ONLY JSON.

AVAILABLE ACTIONS:

1. "bash" - Execute a shell command
   Example: {{"action": "bash", "command": "ls -la"}}

2. "api" - Make an HTTP API request
   Example: {{"action": "api", "api": {{"method": "GET", "url": "https://jsonplaceholder.typicode.com/todos/1", "headers": {{}}, "body": {{}}}}}}

IMPORTANT RULES:
- ONLY use "action": "bash" or "action": "api"
- DO NOT use any other action types (no "email", no "search", etc)
- For user management, use API calls to http://user-service:{USER_SERVICE_PORT}/users
- To add a user, use: {{"action": "api", "api": {{"method": "POST", "url": "http://user-service:{USER_SERVICE_PORT}/users", "headers": {{}}, "body": {{"name": "Name", "city": "City", "email": "email@example.com"}}}}}}
- To list users, use: {{"action": "api", "api": {{"method": "GET", "url": "http://user-service:{USER_SERVICE_PORT}/users", "headers": {{}}, "body": {{}}}}}}
- To delete a user, use: {{"action": "api", "api": {{"method": "DELETE", "url": "http://user-service:{USER_SERVICE_PORT}/users/USER_ID", "headers": {{}}, "body": {{}}}}}}

Return ONLY JSON matching one of the two action formats above.
"""
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_instruction}
        ],
        "stream": False,
         "format": "json" # Ollama supports forcing JSON mode with newer models
    }

    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload)
        resp_data = resp.json()
        return resp_data.get("message", {}).get("content", "{}")
    except Exception as e:
        return json.dumps({"error": str(e)})

def chat_with_ollama_with_history(user_instruction, message_history):
    """
    Sends the user prompt to Ollama WITH full conversation history.
    This allows the LLM to maintain context across multiple exchanges.

    Args:
        user_instruction: Current user prompt
        message_history: List of previous message dicts (role/content)

    Returns:
        Raw response text from Ollama
    """
    system_prompt = f"""
You are a helpful Agent that can ONLY perform two types of actions: bash commands or API requests.
You must reply with ONLY valid JSON. No markdown, no explanations, ONLY JSON.

AVAILABLE ACTIONS:

1. "bash" - Execute a shell command
   Example: {{"action": "bash", "command": "ls -la"}}

2. "api" - Make an HTTP API request
   Example: {{"action": "api", "api": {{"method": "GET", "url": "https://jsonplaceholder.typicode.com/todos/1", "headers": {{}}, "body": {{}}}}}}

IMPORTANT RULES:
- ONLY use "action": "bash" or "action": "api"
- DO NOT use any other action types (no "email", no "search", etc)
- For user management, use API calls to http://user-service:{USER_SERVICE_PORT}/users
- To add a user, use: {{"action": "api", "api": {{"method": "POST", "url": "http://user-service:{USER_SERVICE_PORT}/users", "headers": {{}}, "body": {{"name": "Name", "city": "City", "email": "email@example.com"}}}}}}
- To list users, use: {{"action": "api", "api": {{"method": "GET", "url": "http://user-service:{USER_SERVICE_PORT}/users", "headers": {{}}, "body": {{}}}}}}
- To delete a user, use: {{"action": "api", "api": {{"method": "DELETE", "url": "http://user-service:{USER_SERVICE_PORT}/users/USER_ID", "headers": {{}}, "body": {{}}}}}}

CONTEXT AWARENESS:
- You can now remember previous commands and their results from this conversation
- Use pronouns like "it", "that folder", "the file" when referring to previous context
- When the user says "create X in it" or "add Y there", refer to the conversation history to understand the context

Return ONLY JSON matching one of the two action formats above.
"""

    # Build full message array: system + all history
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(message_history)

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "format": "json"
    }

    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload)
        resp_data = resp.json()
        return resp_data.get("message", {}).get("content", "{}")
    except Exception as e:
        return json.dumps({"error": str(e)})

# --- FLASK ROUTES ---

@app.route("/", methods=["GET"])
def handle_index():
    return jsonify({
        "status": "ok",
        "message": "LLM Agent is running.",
        "endpoints": {
            "POST /chat": "Interact with the LLM agent",
            "GET /health": "Check agent and Ollama health",
            "GET /users": "List all users from user service"
        }
        }), 200

@app.route("/health", methods=["GET"])
def handle_health():
    """Checks connection to Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags")
        if resp.status_code == 200:
            return jsonify({"status": "ok", "ollama_status": "connected"}), 200
        else:
            return jsonify({"status": "error", "ollama_status": "disconnected"}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "ollama_status": "disconnected"}), 500

@app.route("/users", methods=["GET"])
def handle_users():
    """Proxy endpoint to list all users from user-service."""
    try:
        resp = requests.get(f"{USER_SERVICE_HOST}/users", timeout=10)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to connect to user service: {str(e)}"
        }), 500

@app.route("/debug/session/<session_id>", methods=["GET"])
def debug_session(session_id):
    """Debug endpoint to view conversation history for a session"""
    if session_id in conversation_history:
        return jsonify({
            "session_id": session_id,
            "message_count": len(conversation_history[session_id]),
            "messages": conversation_history[session_id]
        })
    else:
        return jsonify({"error": "Session not found"}), 404

@app.route("/debug/sessions", methods=["GET"])
def debug_sessions():
    """Debug endpoint to list all active sessions"""
    sessions = {}
    for sid, history in conversation_history.items():
        sessions[sid] = {
            "message_count": len(history),
            "last_message": history[-1] if history else None
        }
    return jsonify({"sessions": sessions})

@app.route("/debug/session/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    """Clear conversation history for a specific session"""
    if session_id in conversation_history:
        del conversation_history[session_id]
        return jsonify({"status": "success", "message": f"Cleared session {session_id}"})
    else:
        return jsonify({"error": "Session not found"}), 404

@app.route("/debug/sessions", methods=["DELETE"])
def clear_all_sessions():
    """Clear all conversation history"""
    conversation_history.clear()
    return jsonify({"status": "success", "message": "Cleared all sessions"})

@app.route("/chat", methods=["POST"])
def handle_chat():
    data = request.json
    user_prompt = data.get("prompt")
    session_id = data.get("session_id", "default")  # Get session ID or use "default"

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    print(f"[Session: {session_id}] Received prompt: {user_prompt}")

    # Initialize conversation history for this session if it doesn't exist
    if session_id not in conversation_history:
        conversation_history[session_id] = []
        print(f"[Session: {session_id}] Started new conversation")

    # Add user message to history
    conversation_history[session_id].append({
        "role": "user",
        "content": user_prompt
    })

    # Debug: Print conversation history if DEBUG is enabled
    if DEBUG:
        print(f"[Session: {session_id}] Conversation history has {len(conversation_history[session_id])} messages")
        for i, msg in enumerate(conversation_history[session_id]):
            content_preview = msg['content'][:100] if len(msg['content']) > 100 else msg['content']
            print(f"  [{i}] {msg['role']}: {content_preview}...")

    # 1. Ask LLM with full conversation history
    llm_response_text = chat_with_ollama_with_history(
        user_prompt,
        conversation_history[session_id]
    )
    print(f"[Session: {session_id}] LLM Response: {llm_response_text}")

    # 2. Parse JSON (handle markdown-wrapped JSON)
    try:
        # Try to extract JSON from markdown code blocks if present
        import re
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', llm_response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1).strip()
        else:
            json_text = llm_response_text.strip()

        action_plan = json.loads(json_text)
    except json.JSONDecodeError:
        return jsonify({
            "error": "Failed to parse LLM response as JSON",
            "raw_response": llm_response_text
        }), 500

    # 3. Execute Action
    action_type = action_plan.get("action")
    execution_result = {}

    if action_type == "bash":
        cmd = action_plan.get("command")
        execution_result = execute_bash(cmd)

    elif action_type == "api":
        api_details = action_plan.get("api", {})
        execution_result = execute_api(api_details)

    else:
        execution_result = {"error": f"Unknown action: {action_type}"}

    # Add assistant response to history
    # Format it clearly so the LLM understands what command it generated
    if action_type == "bash":
        assistant_content = f"I suggested the bash command: {action_plan.get('command', 'N/A')}"
    elif action_type == "api":
        api_details = action_plan.get("api", {})
        assistant_content = f"I suggested an API call: {api_details.get('method', 'GET')} {api_details.get('url', 'N/A')}"
    else:
        assistant_content = llm_response_text  # Fallback to raw response

    conversation_history[session_id].append({
        "role": "assistant",
        "content": assistant_content
    })

    print(f"[Session: {session_id}] Conversation length: {len(conversation_history[session_id])} messages")

    # 4. Return result with session_id
    return jsonify({
        "llm_plan": action_plan,
        "execution_result": execution_result,
        "session_id": session_id  # Return session ID so client can reuse it
    })

if __name__ == "__main__":
    wait_for_ollama()
    check_and_pull_model()
    app.run(host="0.0.0.0", port=APP_PORT)
