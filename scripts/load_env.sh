#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults if not set
export APP_PORT=${APP_PORT:-5000}
export USER_SERVICE_PORT=${USER_SERVICE_PORT:-5001}
