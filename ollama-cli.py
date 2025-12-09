#!/usr/bin/env python3
"""
Ollama Actions CLI - Natural language command executor
"""

import sys
import os
import subprocess
import requests
import json
import argparse
from typing import Optional, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_config() -> Tuple[str, int]:
    """Load configuration from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    app_port = 8000  # default

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('APP_PORT='):
                    try:
                        app_port = int(line.split('=')[1])
                    except:
                        pass

    agent_url = f"http://localhost:{app_port}"
    return agent_url, app_port


def call_agent(prompt: str, agent_url: str) -> Optional[dict]:
    """Call the agent API with a natural language prompt"""
    try:
        response = requests.post(
            f"{agent_url}/chat",
            json={"prompt": prompt},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}Error: Cannot connect to agent at {agent_url}{Colors.ENDC}")
        print(f"{Colors.WARNING}Make sure the agent is running: make up{Colors.ENDC}")
        return None
    except requests.exceptions.Timeout:
        print(f"{Colors.FAIL}Error: Request timed out{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}Error: {str(e)}{Colors.ENDC}")
        return None


def extract_command(agent_response: dict) -> Optional[str]:
    """Extract the bash command from agent response"""
    try:
        llm_plan = agent_response.get('llm_plan', {})
        action = llm_plan.get('action')

        if action == 'bash':
            return llm_plan.get('command')
        elif action == 'api':
            return None  # API calls are not executed locally
        else:
            return None
    except Exception as e:
        print(f"{Colors.FAIL}Error parsing response: {e}{Colors.ENDC}")
        return None


def ask_confirmation(command: str, default: bool = True) -> bool:
    """Ask user for confirmation to execute command"""
    default_str = "Y/n" if default else "y/N"
    prompt_msg = f"{Colors.OKBLUE}Execute this command? [{default_str}]: {Colors.ENDC}"

    try:
        response = input(prompt_msg).strip().lower()

        if response == '':
            return default

        return response in ['y', 'yes']
    except (KeyboardInterrupt, EOFError):
        print()
        return False


def execute_command(command: str, dry_run: bool = False) -> int:
    """Execute bash command in current directory"""
    if dry_run:
        print(f"{Colors.OKCYAN}[DRY RUN] Would execute: {command}{Colors.ENDC}")
        return 0

    try:
        print(f"{Colors.OKGREEN}Executing: {command}{Colors.ENDC}")
        print()

        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            check=False
        )

        print()
        if result.returncode == 0:
            print(f"{Colors.OKGREEN}✓ Command completed successfully{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Command exited with code {result.returncode}{Colors.ENDC}")

        return result.returncode
    except Exception as e:
        print(f"{Colors.FAIL}Error executing command: {e}{Colors.ENDC}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Ollama Actions CLI - Execute commands with natural language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ollama-cli "Create a asktemp folder"
  ollama-cli "List all Python files"
  ollama-cli "Show current directory"
  ollama-cli --dry-run "Delete all .log files"
  ollama-cli --yes "Create backup folder"
        """
    )

    parser.add_argument(
        'prompt',
        type=str,
        help='Natural language command to execute'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running it'
    )

    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Automatically confirm execution (skip confirmation prompt)'
    )

    parser.add_argument(
        '--agent-url',
        type=str,
        help='Agent URL (default: read from .env or http://localhost:8000)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show full agent response'
    )

    args = parser.parse_args()

    # Load configuration
    agent_url, port = load_config()
    if args.agent_url:
        agent_url = args.agent_url

    # Print header
    print(f"{Colors.HEADER}{Colors.BOLD}Ollama Actions CLI{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Prompt: {args.prompt}{Colors.ENDC}")
    print()

    # Call agent
    print(f"{Colors.OKBLUE}🤖 Asking agent...{Colors.ENDC}")
    response = call_agent(args.prompt, agent_url)

    if not response:
        sys.exit(1)

    # Show full response if verbose
    if args.verbose:
        print(f"\n{Colors.OKCYAN}Full Agent Response:{Colors.ENDC}")
        print(json.dumps(response, indent=2))
        print()

    # Extract command
    command = extract_command(response)

    if not command:
        action = response.get('llm_plan', {}).get('action')
        if action == 'api':
            print(f"{Colors.WARNING}⚠ Agent suggested an API call, not a bash command.{Colors.ENDC}")
            print(f"{Colors.OKCYAN}This CLI only executes local bash commands.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ Could not extract a valid command from agent response.{Colors.ENDC}")
            if args.verbose is False:
                print(f"{Colors.OKCYAN}Tip: Use --verbose to see full response{Colors.ENDC}")
        sys.exit(1)

    # Show command
    print(f"{Colors.OKGREEN}📋 Generated command:{Colors.ENDC}")
    print(f"{Colors.BOLD}   {command}{Colors.ENDC}")
    print()

    # Ask for confirmation (unless --yes flag)
    if not args.yes:
        if not ask_confirmation(command):
            print(f"{Colors.WARNING}Cancelled.{Colors.ENDC}")
            sys.exit(0)

    # Execute command
    exit_code = execute_command(command, dry_run=args.dry_run)
    sys.exit(exit_code)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(130)
