# 🤖 Ollama Actions - LLM Agent with Docker "Arms"

[![CI](https://github.com/manzolo/ollama-actions/workflows/CI/badge.svg)](https://github.com/manzolo/ollama-actions/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

> A production-ready LLM-powered agent that can reason via Ollama and execute actions (Bash commands, HTTP requests) in a controlled, safe environment.

## ✨ Features

- 🧠 **LLM-Powered Reasoning** - Uses Ollama (Llama 3.2) for intelligent task interpretation
- 🔒 **Safety First** - Allowlist-based command and domain filtering
- 🐳 **Fully Dockerized** - All services containerized for easy deployment
- 💻 **CLI Tool** - Execute local commands via natural language with confirmation prompts
- 🎯 **Natural Language Interface** - Control user management with plain English
- 📊 **User Management API** - Full CRUD operations via REST API
- ✅ **Comprehensive Testing** - Direct API tests + LLM-based integration tests
- 🛠️ **Developer Friendly** - Makefile commands for all operations

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [CLI Tool](#-cli-tool)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Development](#development)
- [Safety & Security](#safety--security)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

```
┌─────────────────┐
│   User Request  │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────┐
│         Agent Service               │
│  ┌──────────────────────────────┐  │
│  │  1. Parse Natural Language   │  │
│  │  2. Generate Action Plan     │  │
│  │  3. Validate Safety          │  │
│  │  4. Execute Action           │  │
│  └──────────────────────────────┘  │
└─────────┬───────────────────────────┘
          │
    ┌─────┴─────┐
    │           │
    v           v
┌─────────┐ ┌──────────────┐
│ Ollama  │ │ User Service │
│  (LLM)  │ │   (CRUD)     │
└─────────┘ └──────────────┘
```

### Services

**🤖 Agent Service** (Port 8000)
- Flask application that orchestrates LLM interactions
- Validates and executes bash commands and API calls
- Enforces security allowlists

**🧠 Ollama Service** (Port 11434)
- Hosts the LLM (Llama 3.2 by default)
- Handles reasoning and action plan generation
- Supports multiple model options

**👥 User Service** (Port 8001)
- In-memory user database
- RESTful CRUD API
- Controlled via natural language through the agent

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional but recommended)
- 4GB+ RAM for running Llama 3.2

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/manzolo/ollama-actions.git
   cd ollama-actions
   ```

2. **Start all services**
   ```bash
   make install
   ```

   This will:
   - Build Docker containers
   - Download Llama 3.2 model (~2GB, first run only)
   - Start all services
   - Run health checks

3. **Verify installation**
   ```bash
   make health
   ```

### Using Docker Compose Directly

```bash
# Build
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 💻 CLI Tool

The Ollama Actions CLI allows you to execute commands on your local machine using natural language, with built-in safety confirmations.

### Quick Usage

```bash
# Execute commands with confirmation (default)
./ollama "Create a backup folder"
./ollama "List all Python files"

# Auto-confirm with --yes flag
./ollama --yes "Show current directory"

# Preview without executing
./ollama --dry-run "Delete all .tmp files"
```

### Installation Options

**Option 1: Use directly from project**
```bash
./ollama "your command here"
```

**Option 2: Add to PATH**
```bash
mkdir -p ~/bin
ln -s $(pwd)/ollama ~/bin/ollama
export PATH="$HOME/bin:$PATH"
ollama "create a logs folder"
```

**Option 3: System-wide installation**
```bash
sudo cp ollama /usr/local/bin/
sudo cp ollama-cli.py /usr/local/bin/
ollama "list all files"
```

### CLI Options

```bash
ollama [OPTIONS] "natural language prompt"

Options:
  -y, --yes         Auto-confirm execution (no prompt)
  --dry-run         Show command without executing
  --verbose         Show full agent response
  --agent-url URL   Custom agent URL (default: http://localhost:8000)
  -h, --help        Show help message
```

### Safety Features

✅ **Confirmation by default** - Always asks before executing (unless `--yes`)
✅ **Command allowlist** - Only approved commands run
✅ **Dry-run mode** - Test safely without execution
✅ **Visible commands** - Shows exactly what will run

📖 **Full CLI documentation:** [CLI_USAGE.md](CLI_USAGE.md)

## 💡 Usage Examples

### Natural Language Commands

```bash
# Add a user
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add a user named Mario Rossi from Florence, email mario@example.com"}'

# List all users
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me all users in the system"}'

# Execute bash commands
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List all files in the current directory"}'

# Make API requests
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Get todo item #1 from jsonplaceholder"}'
```

### Direct API Access

```bash
# List users directly
curl http://localhost:8000/users

# User service health
curl http://localhost:8001/

# Agent health
curl http://localhost:8000/health
```

## ⚙️ Configuration

### Environment Variables

Create or edit `.env` file:

```env
APP_PORT=8000              # Agent service port
USER_SERVICE_PORT=8001     # User service port
MODEL_NAME=llama3.2        # LLM model to use
```

**Available Models:**
- `llama3.2` - ⭐ Recommended (3B params, best balance)
- `llama3.1` - Larger model (8B params, more capable)
- `llama3.2:1b` - Smaller model (1B params, faster)
- `tinyllama` - Minimal model (not recommended for this use case)

### Safety Configuration

Edit `agent/src/tools.py` to customize:

**Allowed Commands:**
```python
ALLOWED_COMMANDS = {
    "ls", "cat", "echo", "pwd", "mkdir", "touch",
    "cp", "mv", "date", "whoami", "uname",
    "curl", "ping"
}
```

**Allowed Domains:**
```python
ALLOWED_DOMAINS = {
    "localhost",
    "127.0.0.1",
    "user-service",
    "jsonplaceholder.typicode.com",
    "httpbin.org"
}
```

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Test Categories

```bash
# Fast API tests (no LLM dependency)
make test-direct

# LLM-based agent tests (bash, API, user management)
make test-agent

# Full CRUD workflow tests
make test-crud

# Interactive CRUD tests
make test-crud-simple
```

### Manual Testing

```bash
# Test scripts
bash scripts/test_agent.sh
bash scripts/test_user_crud.sh
bash scripts/list_users.sh
```

## 📚 API Reference

### Agent Service (`http://localhost:8000`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/chat` | POST | Natural language interface |
| `/users` | GET | Proxy to user service (list users) |

### User Service (`http://localhost:8001`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/users` | GET | List all users |
| `/users` | POST | Create new user |
| `/users/<id>` | GET | Get user by ID |
| `/users/<id>` | PUT/PATCH | Update user |
| `/users/<id>` | DELETE | Delete user |

## 🛠️ Development

### Available Make Commands

```bash
make help               # Show all commands
make build              # Build Docker containers
make up                 # Start services
make down               # Stop services
make restart            # Restart all services
make logs               # View all logs
make logs-agent         # View agent logs only
make logs-ollama        # View Ollama logs only
make logs-user-service  # View user service logs only
make shell-agent        # Open shell in agent container
make shell-user-service # Open shell in user-service container
make clean              # Stop and remove volumes
```

### Project Structure

```
ollama-actions/
├── agent/                  # Agent service
│   ├── src/
│   │   ├── main.py        # Flask app & LLM integration
│   │   └── tools.py       # Safety & execution logic
│   ├── tests/             # Unit tests
│   └── Dockerfile
├── user-service/          # User management service
│   ├── src/
│   │   └── app.py         # Flask REST API
│   └── Dockerfile
├── scripts/               # Test scripts
├── docker-compose.yml     # Service orchestration
├── Makefile              # Development commands
├── .env                  # Configuration
└── README.md
```

### Adding New Capabilities

1. **Add new bash command:**
   - Update `ALLOWED_COMMANDS` in `agent/src/tools.py`
   - Add test case in `agent/tests/test_tools.py`

2. **Add new API domain:**
   - Update `ALLOWED_DOMAINS` in `agent/src/tools.py`
   - Add test case in `agent/tests/test_tools.py`

3. **Change LLM model:**
   - Update `MODEL_NAME` in `.env`
   - Run `make restart`

## 🔒 Safety & Security

### Built-in Safety Measures

✅ **Command Allowlisting** - Only pre-approved bash commands can execute
✅ **Domain Allowlisting** - Only whitelisted domains can be contacted
✅ **Timeout Protection** - All operations have 10-second timeouts
✅ **Input Validation** - All commands parsed and validated before execution
✅ **Sandbox Environment** - Operations run in isolated Docker containers

### Security Considerations

⚠️ **This is a demonstration project** - Not production-ready without additional hardening
⚠️ **In-Memory Storage** - User data is lost on restart
⚠️ **Local Deployment** - Designed for localhost development
⚠️ **No Authentication** - Services have no auth layer

For production deployment, consider:
- Adding authentication and authorization
- Using persistent storage (PostgreSQL, Redis)
- Implementing rate limiting
- Adding comprehensive logging and monitoring
- Running behind a reverse proxy with HTTPS
- Implementing role-based access control

## 📖 Documentation

- [CLAUDE.md](CLAUDE.md) - Detailed development guide
- [MODEL_COMPARISON.md](MODEL_COMPARISON.md) - LLM model comparison

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Meta Llama](https://llama.meta.com/) - Open source LLM models
- Flask - Python web framework

## 📞 Support

- 🐛 [Report Bug](https://github.com/manzolo/ollama-actions/issues)
- 💡 [Request Feature](https://github.com/manzolo/ollama-actions/issues)
- 📧 [Contact](mailto:your.email@example.com)

---

Made with ❤️ by [Your Name](https://github.com/manzolo)
