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
            return None  # API calls are handled separately
        else:
            return None
    except Exception as e:
        print(f"{Colors.FAIL}Error parsing response: {e}{Colors.ENDC}")
        return None


def execute_api_action(api_plan: dict, dry_run: bool = False) -> int:
    """Execute API action from agent response"""
    try:
        method = api_plan.get('method', 'GET').upper()
        url = api_plan.get('url', '')
        headers = api_plan.get('headers', {})
        body = api_plan.get('body')

        if not url:
            print(f"{Colors.FAIL}Error: No URL provided in API action{Colors.ENDC}")
            return 1

        if dry_run:
            print(f"{Colors.OKCYAN}[DRY RUN] Would execute API request:{Colors.ENDC}")
            print(f"  Method: {method}")
            print(f"  URL: {url}")
            if headers:
                print(f"  Headers: {json.dumps(headers, indent=2)}")
            if body:
                print(f"  Body: {json.dumps(body, indent=2)}")
            return 0

        print(f"{Colors.OKGREEN}Executing API request: {method} {url}{Colors.ENDC}")
        if body:
            print(f"{Colors.OKCYAN}Request body: {json.dumps(body, indent=2)}{Colors.ENDC}")
        print()

        # Execute API request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body if body else None,
            timeout=30
        )

        # Display response
        print(f"{Colors.OKGREEN}Response Status: {response.status_code}{Colors.ENDC}")

        try:
            response_json = response.json()
            print(f"{Colors.OKCYAN}Response Body:{Colors.ENDC}")
            print(json.dumps(response_json, indent=2))
        except:
            print(f"{Colors.OKCYAN}Response Body:{Colors.ENDC}")
            print(response.text)

        print()
        if response.status_code < 400:
            print(f"{Colors.OKGREEN}✓ API request completed successfully{Colors.ENDC}")
            return 0
        else:
            print(f"{Colors.WARNING}⚠ API request returned error status {response.status_code}{Colors.ENDC}")
            return 1

    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}Error executing API request: {e}{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
        return 1


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

    parser.add_argument(
        '--get-command',
        action='store_true',
        help='Only print the generated command to stdout and exit'
    )

    args = parser.parse_args()

    # Load configuration
    agent_url, port = load_config()
    if args.agent_url:
        agent_url = args.agent_url

    # If just getting the command, skip all printing
    if not args.get_command:
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

    # Check action type
    llm_plan = response.get('llm_plan', {})
    action = llm_plan.get('action')

    # Check if agent already executed an API action
    # Note: We only display agent execution results for API actions
    # Bash actions should always be extracted and run locally on the host
    execution_result = response.get('execution_result', {})
    if execution_result and action == 'api':
        # Agent executed an API action, just display the result

        # For --get-command mode, we still want to show the result
        # (to avoid calling the agent twice and re-executing the action)
        # So we display the full result here and exit

        # Check agent execution status
        agent_status = execution_result.get('status')
        data = execution_result.get('data', {})

        # Check API response status (nested in data)
        api_status = data.get('status') if isinstance(data, dict) else None

        if not args.get_command:
            print(f"{Colors.OKGREEN}✓ Agent executed the API action{Colors.ENDC}")
            print()

        # Determine overall success
        if agent_status == 'success' and api_status != 'error':
            if not args.get_command:
                print(f"{Colors.OKGREEN}Result: Success{Colors.ENDC}")
            print(json.dumps(data, indent=2))
            sys.exit(0)
        elif api_status == 'error':
            # Agent executed successfully but API returned error
            if not args.get_command:
                print(f"{Colors.FAIL}Result: API Error{Colors.ENDC}")
            print(json.dumps(data, indent=2))
            sys.exit(1)
        else:
            # Agent execution failed
            if not args.get_command:
                print(f"{Colors.FAIL}Result: Execution Failed{Colors.ENDC}")
            print(json.dumps(execution_result, indent=2))
            sys.exit(1)

    # Handle API actions (when agent didn't execute them)
    if action == 'api':
        # Get API details from nested 'api' object
        api_details = llm_plan.get('api', {})

        if args.get_command:
            # For --get-command, show API details as a curl command
            method = api_details.get('method', 'GET')
            url = api_details.get('url', '')
            body = api_details.get('body')
            headers = api_details.get('headers', {})

            curl_cmd = f"curl -X {method}"
            for key, value in headers.items():
                curl_cmd += f" -H '{key}: {value}'"
            if body:
                curl_cmd += f" -d '{json.dumps(body)}'"
            curl_cmd += f" {url}"
            print(curl_cmd)
            sys.exit(0)

        # Show API action details
        print(f"{Colors.OKGREEN}📋 Generated API action:{Colors.ENDC}")
        print(f"{Colors.BOLD}   Method: {api_details.get('method', 'GET')}{Colors.ENDC}")
        print(f"{Colors.BOLD}   URL: {api_details.get('url', '')}{Colors.ENDC}")
        if api_details.get('body'):
            print(f"{Colors.BOLD}   Body: {json.dumps(api_details.get('body'), indent=2)}{Colors.ENDC}")
        print()

        # Ask for confirmation (unless --yes flag)
        if not args.yes:
            prompt_msg = f"{Colors.OKBLUE}Execute this API request? [Y/n]: {Colors.ENDC}"
            try:
                response_input = input(prompt_msg).strip().lower()
                if response_input in ['n', 'no']:
                    print(f"{Colors.WARNING}Cancelled.{Colors.ENDC}")
                    sys.exit(0)
            except (KeyboardInterrupt, EOFError):
                print()
                print(f"{Colors.WARNING}Cancelled.{Colors.ENDC}")
                sys.exit(0)

        # Execute API action
        exit_code = execute_api_action(api_details, dry_run=args.dry_run)
        sys.exit(exit_code)

    # Handle bash actions
    command = extract_command(response)

    if not command:
        if not args.get_command:
            print(f"{Colors.FAIL}✗ Could not extract a valid command from agent response.{Colors.ENDC}")
            if args.verbose is False:
                print(f"{Colors.OKCYAN}Tip: Use --verbose to see full response{Colors.ENDC}")
        sys.exit(1)

    # If --get-command is used, just print the command and exit
    if args.get_command:
        print(command)
        sys.exit(0)

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
