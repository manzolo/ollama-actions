# Ollama Actions CLI Usage Guide

The Ollama Actions CLI allows you to execute commands on your local machine using natural language.

## Quick Start

```bash
# Make sure services are running
make up

# Use the CLI
./ollama "Create a asktemp folder"
```

## Installation

### Option 1: Use Directly from Project

```bash
# From project directory
./ollama "your command here"
```

### Option 2: Add to PATH (Optional)

```bash
# Create symlink in local bin
mkdir -p ~/bin
ln -s $(pwd)/ollama ~/bin/ollama

# Add to PATH if not already (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/bin:$PATH"

# Now use from anywhere
ollama "create a backup folder"
```

### Option 3: System-wide Installation

```bash
sudo cp ollama /usr/local/bin/
sudo cp ollama-cli.py /usr/local/bin/

# Now available system-wide
ollama "list all files"
```

## Usage

### Basic Syntax

```bash
./ollama "natural language command"
```

### Command Options

```bash
ollama [OPTIONS] "prompt"

Options:
  -y, --yes         Automatically confirm execution (no prompt)
  --dry-run         Show what would be executed without running it
  --verbose         Show full agent response
  --agent-url URL   Specify custom agent URL
  -h, --help        Show help message
```

## Examples

### Basic Commands

```bash
# Create folders
./ollama "Create a asktemp folder"
./ollama "Make a directory called backup"

# List files
./ollama "List all files in the current directory"
./ollama "Show me all Python files"

# File operations
./ollama "Copy file.txt to backup.txt"
./ollama "Move all .log files to logs folder"

# System information
./ollama "Show current directory"
./ollama "Display disk usage"
./ollama "Check current date and time"
```

### With Confirmation (Default)

```bash
$ ./ollama "Create a test folder"
Ollama Actions CLI
Prompt: Create a test folder

🤖 Asking agent...
📋 Generated command:
   mkdir -p test

Execute this command? [Y/n]: y
Executing: mkdir -p test

✓ Command completed successfully
```

### Auto-Confirm with --yes

```bash
# Skip confirmation prompt
./ollama --yes "Create logs folder"
./ollama -y "List all files"
```

### Dry Run Mode

```bash
# See what would be executed without running it
$ ./ollama --dry-run "Delete all .tmp files"
Ollama Actions CLI
Prompt: Delete all .tmp files

🤖 Asking agent...
📋 Generated command:
   rm -f *.tmp

[DRY RUN] Would execute: rm -f *.tmp
```

### Verbose Mode

```bash
# See full agent response
./ollama --verbose "Show current directory"
```

## Safety Features

### Built-in Protections

✅ **Confirmation by Default** - Always asks before executing (unless `--yes`)
✅ **Command Allowlist** - Only approved commands can run (configured in agent)
✅ **Local Execution** - Runs in current directory with your permissions
✅ **Dry Run Option** - Test without executing
✅ **Visible Commands** - Always shows what will be executed

### Command Allowlist

The agent only generates commands from this allowlist (configured in `agent/src/tools.py`):

- `ls`, `cat`, `echo`, `pwd`
- `mkdir`, `touch`, `cp`, `mv`
- `date`, `whoami`, `uname`
- `curl`, `ping`

⚠️ **Dangerous commands like `rm -rf /` are NOT allowed**

### What the CLI Does NOT Do

❌ Does not execute API calls (only local bash commands)
❌ Does not have access to your passwords or secrets
❌ Does not run with elevated privileges (unless you use sudo)
❌ Does not persist command history (each call is independent)

## Advanced Usage

### Custom Agent URL

```bash
# Connect to agent on different port
./ollama --agent-url http://localhost:9000 "list files"

# Connect to remote agent
./ollama --agent-url http://agent.example.com:8000 "show date"
```

### Scripting with CLI

```bash
# Use in scripts with --yes flag
#!/bin/bash

./ollama --yes "Create backup folder"
./ollama --yes "Copy important.txt to backup/"
./ollama --yes "List files in backup"
```

### Error Handling

```bash
# CLI returns exit codes
./ollama --yes "list files"
if [ $? -eq 0 ]; then
    echo "Success!"
else
    echo "Failed!"
fi
```

## Troubleshooting

### Agent Not Running

```
Error: Cannot connect to agent at http://localhost:8000
Make sure the agent is running: make up
```

**Solution:**
```bash
# Start services
make up

# Verify agent is running
make health
```

### Command Not Allowed

If the agent refuses to generate a command, it might not be in the allowlist.

**Solution:**
1. Check `agent/src/tools.py` for allowed commands
2. Add your command to `ALLOWED_COMMANDS`
3. Restart agent: `make restart`

### Wrong Command Generated

If the agent generates an incorrect command, try:

1. **Be more specific:**
   ```bash
   # Instead of: "create folder"
   ./ollama "create a folder named test123"
   ```

2. **Use dry-run first:**
   ```bash
   ./ollama --dry-run "your command"
   ```

3. **Check with verbose:**
   ```bash
   ./ollama --verbose "your command"
   ```

## Tips & Best Practices

### Writing Good Prompts

✅ **Good:**
```bash
./ollama "Create a folder named backup"
./ollama "List all Python files in current directory"
./ollama "Copy config.json to config.backup.json"
```

❌ **Too Vague:**
```bash
./ollama "do something"
./ollama "files"
```

### When to Use --yes

Use `--yes` for:
- Scripting
- Commands you run frequently
- Safe operations (creating folders, listing files)

DON'T use `--yes` for:
- Destructive operations (deleting files)
- Commands you're unsure about
- First time trying a prompt

### Safety Checklist

Before using `--yes`:
1. ✅ Test with default confirmation first
2. ✅ Use `--dry-run` to preview
3. ✅ Understand what the command does
4. ✅ Make sure you're in the correct directory

## Examples by Category

### File & Directory Operations

```bash
./ollama "Create a new folder called projects"
./ollama "Make directories src, tests, and docs"
./ollama "Copy all .txt files to backup folder"
./ollama "List all files sorted by size"
```

### System Information

```bash
./ollama "Show current working directory"
./ollama "Display current user"
./ollama "Show system information"
./ollama "Display current date and time"
```

### File Searching

```bash
./ollama "List all Python files"
./ollama "Find all markdown files"
./ollama "Show all .log files"
```

### Network Commands

```bash
./ollama "Ping google.com"
./ollama "Check connectivity to localhost"
```

## Integration with Other Tools

### Use with Make

```bash
# Start services, then use CLI
make up && ./ollama "create logs folder"
```

### Use with Git

```bash
./ollama "Show current git branch" # Not allowed (git not in allowlist)
# Add git to allowlist first
```

### Pipe Output

```bash
# Show command without executing
./ollama --dry-run "list files" | grep "Would execute"
```

## FAQ

**Q: Is this safe to use?**
A: Yes, with proper precautions. Always review commands before confirming, use `--dry-run` for testing, and the agent has built-in allowlists.

**Q: Can I use this for complex multi-command operations?**
A: The CLI executes one command at a time. For complex workflows, call it multiple times or use the agent API directly.

**Q: Does this work without an internet connection?**
A: Yes! Once the model is downloaded, everything runs locally. The agent, CLI, and model all work offline.

**Q: Can I customize which commands are allowed?**
A: Yes, edit `agent/src/tools.py` and update `ALLOWED_COMMANDS`, then restart the agent.

**Q: What if the agent generates the wrong command?**
A: That's why confirmation is the default! Review the command before pressing Y. Use `--dry-run` to test safely.

## See Also

- [README.md](README.md) - Project overview
- [CLAUDE.md](CLAUDE.md) - Development guide
- [MODEL_COMPARISON.md](MODEL_COMPARISON.md) - LLM model details
