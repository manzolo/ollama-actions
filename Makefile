.PHONY: help build up down restart logs logs-agent logs-ollama logs-user-service clean test test-agent test-users test-crud test-crud-simple list-users health status ps exec-agent exec-user-service shell-agent shell-user-service

# Load environment variables
include .env
export

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "  Development:"
	@echo "    make build              - Build all Docker containers"
	@echo "    make up                 - Start all services"
	@echo "    make down               - Stop all services"
	@echo "    make restart            - Restart all services"
	@echo "    make clean              - Stop services and remove volumes"
	@echo ""
	@echo "  Logs:"
	@echo "    make logs               - View all service logs (follow mode)"
	@echo "    make logs-agent         - View agent service logs"
	@echo "    make logs-ollama        - View Ollama service logs"
	@echo "    make logs-user-service  - View user-service logs"
	@echo ""
	@echo "  Testing:"
	@echo "    make test               - Run all tests"
	@echo "    make test-direct        - Test direct API endpoints (fast, no LLM)"
	@echo "    make test-agent         - Test agent with LLM (bash, API, user management)"
	@echo "    make test-users         - Test user service integration"
	@echo "    make test-crud          - Test full CRUD operations"
	@echo "    make test-crud-simple   - Test CRUD with natural language (interactive)"
	@echo "    make list-users         - List all users"
	@echo ""
	@echo "  Status:"
	@echo "    make health             - Check health of all services"
	@echo "    make status             - Show service status"
	@echo "    make ps                 - List running containers"
	@echo ""
	@echo "  Shell Access:"
	@echo "    make shell-agent        - Open shell in agent container"
	@echo "    make shell-user-service - Open shell in user-service container"
	@echo "    make exec-agent CMD=... - Execute command in agent container"
	@echo "    make exec-user-service CMD=... - Execute command in user-service container"

# Development commands
build:
	@echo "Building Docker containers..."
	docker-compose build

up:
	@echo "Starting services..."
	docker-compose up -d
	@echo ""
	@echo "Services started! Use 'make logs' to view logs or 'make status' to check status."
	@echo "Agent available at: http://localhost:${APP_PORT}"
	@echo "User Service available at: http://localhost:${USER_SERVICE_PORT}"

down:
	@echo "Stopping services..."
	docker-compose down

restart: down up

clean:
	@echo "Stopping services and removing volumes..."
	docker-compose down -v
	@echo "Cleanup complete!"

# Logs
logs:
	docker-compose logs -f

logs-agent:
	docker-compose logs -f agent

logs-ollama:
	docker-compose logs -f ollama

logs-user-service:
	docker-compose logs -f user-service

# Testing
test:
	@echo "Waiting for services to be ready..."
	@sleep 5
	@make test-direct test-agent
	@echo ""
	@echo "All tests completed!"

test-direct:
	@echo "Testing direct API endpoints..."
	@bash scripts/test_direct_api.sh

test-agent:
	@echo "Testing agent basic functionality..."
	@bash scripts/test_agent.sh

test-users:
	@echo "Testing user service integration..."
	@bash scripts/test_user_service.sh

test-crud:
	@echo "Testing CRUD operations..."
	@bash scripts/test_user_crud.sh

test-crud-simple:
	@echo "Testing CRUD with natural language..."
	@bash scripts/test_user_crud_simple.sh

list-users:
	@bash scripts/list_users.sh

# Status commands
health:
	@echo "Checking service health..."
	@echo ""
	@echo "Agent Health:"
	@curl -s http://localhost:${APP_PORT}/health | python3 -m json.tool || echo "Agent not responding"
	@echo ""
	@echo "User Service Health:"
	@curl -s http://localhost:${USER_SERVICE_PORT}/ | python3 -m json.tool || echo "User Service not responding"

status:
	@docker-compose ps

ps:
	@docker-compose ps

# Shell access
shell-agent:
	@echo "Opening shell in agent container..."
	docker-compose exec agent /bin/bash

shell-user-service:
	@echo "Opening shell in user-service container..."
	docker-compose exec user-service /bin/bash

exec-agent:
	@docker-compose exec agent $(CMD)

exec-user-service:
	@docker-compose exec user-service $(CMD)

# Quick start
install: build up
	@echo ""
	@echo "Installation complete!"
	@echo "Waiting for services to be ready..."
	@sleep 5
	@make health
