import os
import json
import time
import requests
from flask import Flask, request, jsonify
from tools import execute_bash, execute_api

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3.1")
APP_PORT = int(os.environ.get("APP_PORT", 5000))
USER_SERVICE_PORT = int(os.environ.get("USER_SERVICE_PORT", 5001))
USER_SERVICE_HOST = f"http://user-service:{USER_SERVICE_PORT}"

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

@app.route("/chat", methods=["POST"])
def handle_chat():
    data = request.json
    user_prompt = data.get("prompt")
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    print(f"Received prompt: {user_prompt}")
    
    # 1. Ask LLM
    llm_response_text = chat_with_ollama(user_prompt)
    print(f"LLM Response: {llm_response_text}")

    # 2. Parse JSON
    try:
        action_plan = json.loads(llm_response_text)
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

    # 4. Return result
    return jsonify({
        "llm_plan": action_plan,
        "execution_result": execution_result
    })

if __name__ == "__main__":
    wait_for_ollama()
    check_and_pull_model()
    app.run(host="0.0.0.0", port=APP_PORT)
