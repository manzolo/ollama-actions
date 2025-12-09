#!/bin/bash

# Load environment variables
source "$(dirname "$0")/load_env.sh"

echo "========================================="
echo "Testing User Service Integration"
echo "========================================="

echo -e "\n1. Testing User Service Health..."
curl -s http://localhost:${USER_SERVICE_PORT}/ | python3 -m json.tool

echo -e "\n\n2. Testing Agent: Add user Mario Rossi from Florence..."
curl -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Add a new user named Mario Rossi who lives in Florence, Italy. His email is mario.rossi@example.com"}' | python3 -m json.tool

echo -e "\n\n3. Testing Agent: List all users..."
curl -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Get the list of all users from the user service"}' | python3 -m json.tool

echo -e "\n\n4. Direct test: Get all users from user-service..."
curl -s http://localhost:${USER_SERVICE_PORT}/users | python3 -m json.tool

echo -e "\n\nTests completed!"
