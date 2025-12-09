#!/bin/bash

# Load environment variables
source "$(dirname "$0")/load_env.sh"

echo "========================================="
echo "Testing User CRUD via Chat Agent"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Step 1: Add a user via chat${NC}"
echo "Prompt: 'Add a new user named Mario Rossi who lives in Florence, Italy. Email: mario.rossi@example.com, phone: +39 055 1234567'"
echo "---"
ADD_RESPONSE=$(curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"Add a new user named Mario Rossi who lives in Florence, Italy. Email is mario.rossi@example.com and phone is +39 055 1234567. Send a POST request to http://user-service:${USER_SERVICE_PORT}/users with this data\"}")

echo "$ADD_RESPONSE" | python3 -m json.tool

# Extract user ID from response
USER_ID=$(echo "$ADD_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('execution_result', {}).get('data', {}).get('user', {}).get('id', ''))" 2>/dev/null)

if [ -z "$USER_ID" ]; then
    echo -e "\n${YELLOW}Warning: Could not extract user ID from response. Fetching from user list...${NC}"
    # Try to get user ID by listing all users
    LIST_RESPONSE=$(curl -s http://localhost:${USER_SERVICE_PORT}/users)
    USER_ID=$(echo "$LIST_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); users=data.get('users', []); print(users[0]['id'] if users else '')" 2>/dev/null)
fi

echo -e "\n${GREEN}User ID: $USER_ID${NC}"

sleep 2

echo -e "\n${BLUE}Step 2: List all users to verify creation${NC}"
echo "Prompt: 'Get all users from the user service'"
echo "---"
curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"Send a GET request to http://user-service:${USER_SERVICE_PORT}/users to get all users\"}" | python3 -m json.tool

sleep 2

echo -e "\n${BLUE}Step 3: Update the user via chat${NC}"
echo "Prompt: 'Update user to change city to Rome and add address'"
echo "---"
if [ -n "$USER_ID" ]; then
    curl -s -X POST http://localhost:${APP_PORT}/chat \
         -H "Content-Type: application/json" \
         -d "{\"prompt\": \"Update the user with ID $USER_ID. Change the city to Rome and set address to Via Roma 123. Send a PUT request to http://user-service:${USER_SERVICE_PORT}/users/$USER_ID with the updated data\"}" | python3 -m json.tool
else
    echo -e "${YELLOW}Skipping update - User ID not found${NC}"
fi

sleep 2

echo -e "\n${BLUE}Step 4: Get the updated user to verify changes${NC}"
echo "---"
if [ -n "$USER_ID" ]; then
    curl -s -X POST http://localhost:${APP_PORT}/chat \
         -H "Content-Type: application/json" \
         -d "{\"prompt\": \"Get the user details for user ID $USER_ID. Send a GET request to http://user-service:${USER_SERVICE_PORT}/users/$USER_ID\"}" | python3 -m json.tool
else
    echo -e "${YELLOW}Skipping - User ID not found${NC}"
fi

sleep 2

echo -e "\n${BLUE}Step 5: Delete the user via chat${NC}"
echo "Prompt: 'Delete the user'"
echo "---"
if [ -n "$USER_ID" ]; then
    curl -s -X POST http://localhost:${APP_PORT}/chat \
         -H "Content-Type: application/json" \
         -d "{\"prompt\": \"Delete the user with ID $USER_ID. Send a DELETE request to http://user-service:${USER_SERVICE_PORT}/users/$USER_ID\"}" | python3 -m json.tool
else
    echo -e "${YELLOW}Skipping delete - User ID not found${NC}"
fi

sleep 2

echo -e "\n${BLUE}Step 6: Verify user is deleted${NC}"
echo "---"
curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"Get all users from http://user-service:${USER_SERVICE_PORT}/users to verify the user was deleted\"}" | python3 -m json.tool

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}CRUD Test Completed!${NC}"
echo -e "${GREEN}=========================================${NC}"
