#!/bin/bash

# Load environment variables
source "$(dirname "$0")/load_env.sh"

echo "========================================="
echo "Testing Direct API Endpoints"
echo "========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Helper function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="${4:-}"

    echo -e "\n${BLUE}Testing: $name${NC}"

    if [ -n "$data" ]; then
        response=$(curl -s -X $method "$url" -H "Content-Type: application/json" -d "$data")
    else
        response=$(curl -s -X $method "$url")
    fi

    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $response"
        ((FAILED++))
    fi
}

# Test Agent Health
test_endpoint "Agent Health" "http://localhost:${APP_PORT}/health"

# Test User Service Health
test_endpoint "User Service Health" "http://localhost:${USER_SERVICE_PORT}/"

# Test List Users (empty)
test_endpoint "List Users (should be empty)" "http://localhost:${USER_SERVICE_PORT}/users"

# Test Agent Proxy - List Users
test_endpoint "Agent Proxy - List Users" "http://localhost:${APP_PORT}/users"

# Test Create User
echo -e "\n${BLUE}Testing: Create User${NC}"
CREATE_RESPONSE=$(curl -s -X POST "http://localhost:${USER_SERVICE_PORT}/users" \
    -H "Content-Type: application/json" \
    -d '{"name": "Test User", "city": "Test City", "email": "test@example.com"}')

if [ $? -eq 0 ] && echo "$CREATE_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    echo "$CREATE_RESPONSE" | python3 -m json.tool
    ((PASSED++))

    # Extract user ID
    USER_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])" 2>/dev/null)
    echo -e "\nCreated user ID: $USER_ID"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "$CREATE_RESPONSE"
    ((FAILED++))
fi

# Test List Users (should have 1 user)
test_endpoint "List Users (should have 1 user)" "http://localhost:${USER_SERVICE_PORT}/users"

# Test Get Specific User
if [ -n "$USER_ID" ]; then
    test_endpoint "Get User by ID" "http://localhost:${USER_SERVICE_PORT}/users/$USER_ID"

    # Test Update User
    test_endpoint "Update User" "http://localhost:${USER_SERVICE_PORT}/users/$USER_ID" "PUT" \
        '{"name": "Updated User", "city": "Updated City"}'

    # Test Delete User
    test_endpoint "Delete User" "http://localhost:${USER_SERVICE_PORT}/users/$USER_ID" "DELETE"
fi

# Test List Users (should be empty again)
test_endpoint "List Users (should be empty again)" "http://localhost:${USER_SERVICE_PORT}/users"

# Summary
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Tests Passed: $PASSED${NC}"
echo -e "${RED}Tests Failed: $FAILED${NC}"
echo -e "${BLUE}=========================================${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All direct API tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
