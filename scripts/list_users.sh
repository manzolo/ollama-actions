#!/bin/bash

# Load environment variables
source "$(dirname "$0")/load_env.sh"

echo "Fetching all users..."
echo ""

# Use the agent's proxy endpoint to list users
curl -s http://localhost:${APP_PORT}/users | python3 -m json.tool
