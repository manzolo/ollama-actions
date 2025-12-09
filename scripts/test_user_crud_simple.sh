#!/bin/bash

# Load environment variables
source "$(dirname "$0")/load_env.sh"

echo "========================================="
echo "Testing User CRUD with Natural Language"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Step 1: Add Mario Rossi${NC}"
echo -e "${YELLOW}Note: The LLM should interpret this and call the user service API${NC}"
echo "---"
curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Create a new user: name is Mario Rossi, city is Florence, email is mario.rossi@example.com"}' | python3 -m json.tool

echo -e "\n${GREEN}Waiting 3 seconds...${NC}"
sleep 3

echo -e "\n${BLUE}Step 2: List all users${NC}"
echo "---"
curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Show me all users in the system"}' | python3 -m json.tool

echo -e "\n${GREEN}Waiting 3 seconds...${NC}"
sleep 3

echo -e "\n${BLUE}Step 3: Add another user - Giulia Bianchi${NC}"
echo "---"
curl -s -X POST http://localhost:${APP_PORT}/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Add a new user named Giulia Bianchi from Milan, email giulia.bianchi@example.com"}' | python3 -m json.tool

echo -e "\n${GREEN}Waiting 3 seconds...${NC}"
sleep 3

echo -e "\n${BLUE}Step 4: List users again to see both users${NC}"
echo "---"
curl -s http://localhost:${USER_SERVICE_PORT}/users | python3 -m json.tool

echo -e "\n${YELLOW}Copy a user ID from above to test update and delete${NC}"
read -p "Enter User ID to update and delete: " USER_ID

if [ -n "$USER_ID" ]; then
    echo -e "\n${BLUE}Step 5: Update user $USER_ID${NC}"
    echo "---"
    curl -s -X POST http://localhost:${APP_PORT}/chat \
         -H "Content-Type: application/json" \
         -d "{\"prompt\": \"Update user $USER_ID: change city to Rome and set phone to +39 06 7654321\"}" | python3 -m json.tool

    echo -e "\n${GREEN}Waiting 3 seconds...${NC}"
    sleep 3

    echo -e "\n${BLUE}Step 6: Delete user $USER_ID${NC}"
    echo "---"
    curl -s -X POST http://localhost:${APP_PORT}/chat \
         -H "Content-Type: application/json" \
         -d "{\"prompt\": \"Delete user with ID $USER_ID from the system\"}" | python3 -m json.tool

    echo -e "\n${GREEN}Waiting 3 seconds...${NC}"
    sleep 3

    echo -e "\n${BLUE}Step 7: Verify deletion${NC}"
    echo "---"
    curl -s http://localhost:${USER_SERVICE_PORT}/users | python3 -m json.tool
else
    echo -e "${YELLOW}No user ID provided, skipping update and delete${NC}"
fi

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}Test Completed!${NC}"
echo -e "${GREEN}=========================================${NC}"
