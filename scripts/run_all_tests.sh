#!/bin/bash
#
# Master test runner with beautiful output
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
ROCKET="🚀"
GEAR="⚙️"
PACKAGE="📦"

# Test suite tracking
TOTAL_SUITES=3
SUITES_PASSED=0
SUITES_FAILED=0

START_TIME=$(date +%s)

# Function to print main header
print_main_header() {
    clear
    echo ""
    echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║                                                ║${NC}"
    echo -e "${BOLD}${CYAN}║        ${PACKAGE}  Test Suite Runner  ${PACKAGE}               ║${NC}"
    echo -e "${BOLD}${CYAN}║                                                ║${NC}"
    echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to print suite header
print_suite() {
    local suite_num=$1
    local suite_name="$2"
    echo ""
    echo -e "${BOLD}${MAGENTA}┌─────────────────────────────────────────────────┐${NC}"
    echo -e "${BOLD}${MAGENTA}│ ${NC}${BOLD}Suite $suite_num/$TOTAL_SUITES: $suite_name${NC}"
    echo -e "${BOLD}${MAGENTA}└─────────────────────────────────────────────────┘${NC}"
    echo ""
}

# Function to run test suite
run_suite() {
    local suite_name="$1"
    local script_path="$2"
    local suite_num=$3

    print_suite "$suite_num" "$suite_name"

    echo -e "${DIM}  ${ARROW} Running: ${script_path}${NC}"
    echo ""

    # Run the test and capture output
    if bash "$script_path" 2>&1; then
        echo ""
        echo -e "${GREEN}${BOLD}  ${CHECK} Suite passed${NC}"
        ((SUITES_PASSED++))
        return 0
    else
        echo ""
        echo -e "${RED}${BOLD}  ${CROSS} Suite failed${NC}"
        ((SUITES_FAILED++))
        return 1
    fi
}

# Function to print final summary
print_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))

    echo ""
    echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║              Final Test Summary                ║${NC}"
    echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ $SUITES_FAILED -eq 0 ]; then
        echo -e "  ${GREEN}${BOLD}${CHECK} All test suites passed!${NC}"
    else
        echo -e "  ${YELLOW}${BOLD}⚠  Some test suites failed${NC}"
    fi

    echo ""
    echo -e "  ${BOLD}Test Suites:${NC}"
    echo -e "    ${GREEN}${CHECK} Passed:${NC}  ${BOLD}${SUITES_PASSED}${NC}/${TOTAL_SUITES}"
    echo -e "    ${RED}${CROSS} Failed:${NC}  ${BOLD}${SUITES_FAILED}${NC}/${TOTAL_SUITES}"
    echo ""
    echo -e "  ${BOLD}Duration:${NC} ${duration}s"
    echo ""
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Main execution
print_main_header

echo -e "${DIM}Waiting for services to be ready...${NC}"
sleep 5
echo ""

# Run test suites
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_suite "Direct API Tests" "$SCRIPT_DIR/test_direct_api.sh" 1 || true
run_suite "Agent Integration Tests" "$SCRIPT_DIR/test_agent.sh" 2 || true
run_suite "Ollama CLI Tests" "$SCRIPT_DIR/test_ollama_cli.sh" 3 || true

# Print summary
print_summary

# Exit with appropriate code
if [ $SUITES_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
