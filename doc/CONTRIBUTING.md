# Contributing to Ollama Actions

First off, thank you for considering contributing to Ollama Actions! It's people like you that make this project better.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Be patient and welcoming
- Be collaborative
- Be thoughtful in the words you choose

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, curl commands, etc.)
- **Describe the behavior you observed and what you expected**
- **Include logs** from `docker compose logs`
- **Specify your environment** (OS, Docker version, model being used)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List some examples of how it would be used**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you're adding functionality
4. **Ensure tests pass** by running `make test`
5. **Update documentation** (README, CLAUDE.md, etc.) if needed
6. **Write a good commit message** following conventional commits format

#### Development Workflow

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/ollama-actions.git
cd ollama-actions

# Create a branch
git checkout -b feature/my-new-feature

# Make your changes
# ...

# Test your changes
make test

# Commit your changes
git commit -m "feat: add amazing new feature"

# Push to your fork
git push origin feature/my-new-feature

# Open a Pull Request on GitHub
```

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Maximum line length: 127 characters

```python
def example_function(param1, param2):
    """
    Brief description of what this function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    # Implementation here
    pass
```

### Testing

- Write tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Use descriptive test names

```python
def test_validate_bash_command_allowed():
    """Tests that allowed commands are validated correctly."""
    parts, msg = validate_bash_command("ls -la")
    assert parts == ["ls", "-la"]
    assert msg == "OK"
```

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(agent): add support for new LLM model

fix(user-service): resolve memory leak in user deletion

docs(readme): update installation instructions

test(tools): add tests for API validation
```

## Project Structure

```
ollama-actions/
├── agent/              # Agent service
│   ├── src/           # Source code
│   ├── tests/         # Unit tests
│   └── Dockerfile
├── user-service/      # User management service
│   ├── src/
│   └── Dockerfile
├── scripts/           # Test and utility scripts
└── .github/
    └── workflows/     # CI/CD workflows
```

## Adding New Features

### Adding a New Allowed Command

1. Update `ALLOWED_COMMANDS` in `agent/src/tools.py`
2. Add test in `agent/tests/test_tools.py`
3. Update documentation
4. Run tests: `make test`

### Adding a New Service

1. Create service directory with Dockerfile
2. Add service to `docker-compose.yml`
3. Update Makefile if needed
4. Add tests
5. Update documentation

### Changing the LLM Model

1. Update `.env` with new model name
2. Test with `make test`
3. Update `MODEL_COMPARISON.md` if significantly different
4. Update documentation

## Testing

### Running Tests

```bash
# All tests
make test

# Specific test categories
make test-direct      # Fast API tests
make test-agent       # LLM-based tests
make test-crud        # CRUD workflow tests

# Python unit tests
make exec-agent CMD="pytest tests/ -v"
```

### Writing Tests

- Place unit tests in `agent/tests/` or `user-service/tests/`
- Place integration tests in `scripts/`
- Ensure tests are deterministic
- Mock external dependencies when appropriate

## Documentation

- Update README.md for user-facing changes
- Update CLAUDE.md for development changes
- Add inline comments for complex logic
- Update API documentation if endpoints change

## Getting Help

- Check existing [issues](https://github.com/manzolo/ollama-actions/issues)
- Review [documentation](CLAUDE.md)
- Ask questions in issues or discussions

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- README acknowledgments section (for major contributions)

Thank you for contributing! 🙏
