# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an LLM-powered agent built with Docker and Ollama. The agent can reason through user prompts and execute controlled actions (Bash commands or HTTP API requests) on a Linux system.

## Architecture

The project consists of three main services:

**Ollama Service**: Hosts a local LLM (e.g., Llama 3.1, TinyLlama)

**Agent Service** (Flask app in `agent/src/`):
- `main.py`: Flask application that handles HTTP requests, communicates with Ollama, and parses/executes action plans
- `tools.py`: Safety mechanisms and execution logic for bash commands and API requests
  - Maintains allowlists for safe commands and domains
  - Validates and executes actions with timeouts and error handling

**User Service** (Flask app in `user-service/src/`):
- `app.py`: REST API for managing users in an in-memory database
- Provides CRUD endpoints: POST /users (create), GET /users (list), GET /users/<id> (get), PUT/PATCH /users/<id> (update), DELETE /users/<id> (delete)
- Uses simple Python dict as in-memory database with UUID-based user IDs

The flow is: User Prompt → Ollama LLM (generates JSON action plan) → Safety Validation → Execution → Result

## Development Commands

The project includes a Makefile for easy management. Run `make help` to see all available commands.

### Build and Run
```bash
# Quick start (build + start services)
make install

# Build containers
make build

# Start services
make up

# Stop services
make down

# Restart services
make restart

# View logs
make logs

# Stop and remove volumes
make clean

# Alternative: using docker compose directly
docker compose build
docker compose up -d
docker compose down
```

### Testing
```bash
# Run all integration tests
make test

# Test agent functionality (includes bash, API, and user management tests)
make test-agent

# Test user service integration
make test-users

# Test CRUD operations
make test-crud

# Test CRUD with natural language (interactive)
make test-crud-simple

# List all users
make list-users

# Run Python unit tests
docker compose exec agent pytest tests/
make exec-agent CMD="pytest tests/"

# Run specific test file
docker compose exec agent pytest tests/test_tools.py

# Run single test
docker compose exec agent pytest tests/test_tools.py::test_validate_bash_command_allowed

# Manual API test - Agent
curl -X POST http://localhost:${APP_PORT}/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List the files in the current directory"}'

# Manual API test - User Service
curl -X POST http://localhost:${APP_PORT}/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add a new user named Mario Rossi who lives in Florence"}'

# Direct user service test
curl http://localhost:${USER_SERVICE_PORT}/users

# List users via agent proxy endpoint
curl http://localhost:${APP_PORT}/users
```

### Development
```bash
# Check service health
make health

# View service status
make status

# View logs
make logs               # All services
make logs-agent         # Agent only
make logs-ollama        # Ollama only
make logs-user-service  # User service only

# Shell access
make shell-agent
make shell-user-service

# Execute command in container
make exec-agent CMD="pytest tests/"
make exec-user-service CMD="ls -la"
```

## Configuration

**Environment Variables** (configured in `.env` file):
- `MODEL_NAME`: LLM model to use (default: `llama3.2`; alternatives: `llama3.1`, `llama3.2:1b`, `tinyllama`)
- `APP_PORT`: Agent service port (default: `8000`)
- `USER_SERVICE_PORT`: User service port (default: `8001`)
- `OLLAMA_HOST`: Ollama endpoint (default: `http://ollama:11434`; for external Ollama: `http://host.docker.internal:11434`)
- `COMPOSE_PROFILES`: Set to `local-ollama` to start local Ollama container, leave empty for external Ollama

**Important**: Ports are configured via `.env` file and read at runtime. Never hardcode ports in source files.

**Switching Between Local and External Ollama:**
```bash
# Use local Ollama container
make use-local-ollama
make restart

# Use external Ollama instance
make use-external-ollama
# Edit .env to configure your external URL
make restart

# Check current configuration
make show-ollama-config
```

The system uses Docker Compose profiles to conditionally start the Ollama container only when needed.

**Safety Allowlists** (in `agent/src/tools.py`):
- `ALLOWED_COMMANDS`: Bash executables the agent can run (e.g., `ls`, `cat`, `mkdir`)
- `ALLOWED_DOMAINS`: HTTP domains the agent can contact (e.g., `jsonplaceholder.typicode.com`, `localhost`, `user-service`)

Modify these allowlists to expand or restrict agent capabilities.

## Key Implementation Details

**System Prompt** (in `main.py`): Instructs Ollama to respond with JSON-formatted action plans with either `"action": "bash"` or `"action": "api"` and their respective parameters.

**Safety Enforcement**:
- Bash: Uses `shlex.split()` to parse commands, validates the executable against `ALLOWED_COMMANDS` allowlist
- API: Validates hostname against `ALLOWED_DOMAINS` allowlist via `urlparse()`
- Both: Enforce 10-second execution timeout via `subprocess.timeout` and `requests.timeout`

**Action Execution**:
- Bash actions use `subprocess.run()` with captured output and return code
- API actions use `requests.request()` with support for custom headers/body
- Responses unified as structured dicts with status, output, and metadata

**Agent Endpoints**:
- `POST /chat`: Main LLM interaction endpoint
- `GET /health`: Health check for agent and Ollama connectivity
- `GET /users`: Proxy endpoint that lists all users from the user-service (convenient alternative to going through /chat)

## Testing Strategy

Tests focus on safety validation and execution boundaries:
- `test_tools.py` validates command/domain allowlists work correctly
- Tests verify both allowed and disallowed operations are handled properly
- Mock external API calls (jsonplaceholder.typicode.com) for test reliability

When adding new allowed commands or domains, add corresponding test cases to `test_tools.py`.

## Common Development Tasks

**Using the Makefile**:
The project includes a comprehensive Makefile. Run `make help` to see all available commands.

**Add a new allowed bash command**:
1. Add command name to `ALLOWED_COMMANDS` in `agent/src/tools.py`
2. Add test case to `agent/tests/test_tools.py` for the new command
3. Run `make exec-agent CMD="pytest tests/"` to verify

**Add a new allowed domain**:
1. Add domain to `ALLOWED_DOMAINS` in `agent/src/tools.py`
2. Add test case to `agent/tests/test_tools.py` validating the domain
3. Run `make exec-agent CMD="pytest tests/"` to verify

**Change the LLM model**:
- Update `MODEL_NAME` in `.env` file
- Run `make restart` to apply changes
- First run will pull the model (may take several minutes)

**Change service ports**:
- Update `APP_PORT` or `USER_SERVICE_PORT` in `.env` file
- Run `make restart` to apply changes

**Debug Ollama connectivity**:
- Check logs: `make logs-ollama`
- Verify health: `make health`
- Ensure all services are on the same Docker network: `llm_net`

**View service logs**:
- All services: `make logs`
- Specific service: `make logs-agent`, `make logs-ollama`, or `make logs-user-service`

**Access container shell**:
- Agent: `make shell-agent`
- User service: `make shell-user-service`
