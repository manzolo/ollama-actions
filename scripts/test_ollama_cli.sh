#!/bin/bash
#
# Integration tests for the ./ollama CLI wrapper
# Tests natural language commands for both bash and API actions
#

# Load environment variables
source "$(dirname "$0")/load_env.sh"

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Unicode symbols
CHECK="✓"
CROSS="✗"
ARROW="→"
BULLET="•"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=6

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OLLAMA_CLI="$PROJECT_ROOT/ollama"

# Function to print header
print_header() {
    echo ""
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to print test name
print_test() {
    local test_num=$1
    local test_name="$2"
    echo ""
    echo -e "${BOLD}${BLUE}Test $test_num/$TOTAL_TESTS:${NC} $test_name"
    echo -e "${DIM}${BULLET}${BULLET}${BULLET}${NC}"
}

# Function to print result
print_result() {
    local status=$1
    local message="$2"
    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}${BOLD}  ${CHECK} PASSED${NC} ${DIM}${message}${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}${BOLD}  ${CROSS} FAILED${NC} ${DIM}${message}${NC}"
        ((TESTS_FAILED++))
    fi
}

# Function to print data
print_data() {
    local label="$1"
    local value="$2"
    echo -e "${DIM}  ${ARROW} ${label}:${NC} ${CYAN}${value}${NC}"
}

# Function to cleanup test directories
cleanup_test_dirs() {
    cd "$PROJECT_ROOT"
    rm -rf test_folder_cli_* 2>/dev/null || true
}

# Check if ollama CLI exists
if [ ! -f "$OLLAMA_CLI" ]; then
    echo -e "${RED}${BOLD}${CROSS} ERROR:${NC} ./ollama CLI not found at $OLLAMA_CLI"
    exit 1
fi

if [ ! -x "$OLLAMA_CLI" ]; then
    echo -e "${RED}${BOLD}${CROSS} ERROR:${NC} ./ollama CLI is not executable"
    exit 1
fi

# Cleanup before tests
cleanup_test_dirs

print_header "Ollama CLI Integration Tests"
echo ""
echo -e "${DIM}Testing natural language commands with the ./ollama CLI wrapper${NC}"

# ============================================================================
# BASH COMMAND TESTS
# ============================================================================

print_header "Bash Commands"

# Test 1: List files
print_test 1 "List files in directory"
cd "$PROJECT_ROOT"
OUTPUT=$("$OLLAMA_CLI" -y "list files in current directory" 2>&1)
if echo "$OUTPUT" | grep -q "ollama"; then
    print_result "pass" "Found 'ollama' in output"
else
    print_result "fail" "Expected file not found"
fi

# Test 2: Create directory
print_test 2 "Create directory"
cd "$PROJECT_ROOT"
"$OLLAMA_CLI" -y "create a directory called test_folder_cli_001" > /dev/null 2>&1
if [ -d "test_folder_cli_001" ]; then
    print_result "pass" "Directory created successfully"
    print_data "Path" "test_folder_cli_001"
else
    print_result "fail" "Directory not created"
fi

# Test 3: Delete directory
print_test 3 "Delete directory"
cd "$PROJECT_ROOT"
"$OLLAMA_CLI" -y "delete the directory test_folder_cli_001" > /dev/null 2>&1
sleep 1
if [ ! -d "test_folder_cli_001" ]; then
    print_result "pass" "Directory deleted successfully"
else
    print_result "fail" "Directory still exists"
fi

# ============================================================================
# API ACTION TESTS
# ============================================================================

print_header "API Actions (User Management)"

# Test 4: Create user
print_test 4 "Create new user via API"
cd "$PROJECT_ROOT"
USER_OUTPUT=$("$OLLAMA_CLI" -y "Add a user named CLI Test User from TestCity, email clitest@example.com" 2>&1)
if echo "$USER_OUTPUT" | grep -q "CLI Test User"; then
    USER_ID=$(echo "$USER_OUTPUT" | grep -o '"id": "[^"]*"' | head -1 | cut -d'"' -f4)
    print_result "pass" "User created successfully"
    print_data "Name" "CLI Test User"
    print_data "City" "TestCity"
    print_data "User ID" "$USER_ID"
else
    print_result "fail" "User not created"
    USER_ID=""
fi

sleep 1

# Test 5: List users
print_test 5 "List all users"
cd "$PROJECT_ROOT"
if "$OLLAMA_CLI" -y "show me all users in the system" 2>&1 | grep -q "CLI Test User"; then
    print_result "pass" "User found in list"
else
    print_result "fail" "User not found in list"
fi

sleep 1

# Test 6: Delete user
if [ -n "$USER_ID" ]; then
    print_test 6 "Delete user by ID"
    cd "$PROJECT_ROOT"
    "$OLLAMA_CLI" -y "delete the user with ID $USER_ID" > /dev/null 2>&1
    print_result "pass" "User deletion executed"
    print_data "Deleted ID" "$USER_ID"
else
    print_test 6 "Delete user by ID"
    print_result "fail" "No user ID available"
fi

# ============================================================================
# FINAL SUMMARY
# ============================================================================

# Cleanup
cleanup_test_dirs

print_header "Test Summary"
echo ""

# Calculate percentage
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_PERCENT=$((TESTS_PASSED * 100 / TOTAL_TESTS))
else
    PASS_PERCENT=0
fi

# Print results with colors
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "  ${GREEN}${BOLD}${CHECK} All tests passed!${NC}"
else
    echo -e "  ${YELLOW}${BOLD}⚠ Some tests failed${NC}"
fi

echo ""
echo -e "  ${BOLD}Results:${NC}"
echo -e "    ${GREEN}${CHECK} Passed:${NC}  ${BOLD}${TESTS_PASSED}${NC}/${TOTAL_TESTS} ${DIM}(${PASS_PERCENT}%)${NC}"
echo -e "    ${RED}${CROSS} Failed:${NC}  ${BOLD}${TESTS_FAILED}${NC}/${TOTAL_TESTS}"
echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
