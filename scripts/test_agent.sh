#!/bin/bash

# Load environment variables
source "$(dirname "$0")/load_env.sh"

echo "========================================="
echo "Testing Agent with LLM"
echo "========================================="

echo -e "\nTest 1: Bash Command - List files"
echo "Prompt: 'List the files in the current directory'"
echo "---"
curl -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "List the files in the current directory"}' | python3 -m json.tool

echo -e "\n\nTest 2: External API Request"
echo "Prompt: 'Get data from http://jsonplaceholder.typicode.com/todos/1'"
echo "---"
curl -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Send a GET request to http://jsonplaceholder.typicode.com/todos/1"}' | python3 -m json.tool

echo -e "\n\nTest 3: User Management - Add User"
echo "Prompt: 'Add a user named Test Agent User from TestCity, email test@agent.com'"
echo "---"
ADD_RESPONSE=$(curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Add a user named Test Agent User from TestCity, email is test@agent.com"}')

echo "$ADD_RESPONSE" | python3 -m json.tool

# Extract user ID from response
USER_ID=$(echo "$ADD_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('execution_result', {}).get('data', {}).get('user', {}).get('id', ''))" 2>/dev/null)

echo -e "\n\nTest 4: User Management - List Users"
echo "Prompt: 'Show me all users'"
echo "---"
curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Show me all users in the system"}' | python3 -m json.tool

if [ -n "$USER_ID" ]; then
    echo -e "\n\nTest 5: User Management - Delete User"
    echo "Prompt: 'Delete the user with ID $USER_ID'"
    echo "---"
    curl -s -X POST http://localhost:${APP_PORT}/chat \
         -H "Content-Type: application/json" \
         -d "{\"prompt\": \"Delete the user with ID $USER_ID\"}" | python3 -m json.tool
else
    echo -e "\n\nTest 5: SKIPPED - Could not extract user ID from add response"
fi

echo -e "\n\n========================================="
echo "Agent tests completed!"
echo "========================================="
