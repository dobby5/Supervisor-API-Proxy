#!/bin/bash
# ==============================================================================
# Test runner script for Home Assistant Supervisor API Proxy
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$PROJECT_DIR/tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_banner() {
    echo "=============================================================================="
    echo "  Home Assistant Supervisor API Proxy - Test Suite"
    echo "=============================================================================="
    echo "  Project Dir: $PROJECT_DIR"
    echo "  Tests Dir:   $TESTS_DIR"
    echo "=============================================================================="
    echo
}

check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv "$PROJECT_DIR/venv"
    fi
    
    # Activate virtual environment
    source "$PROJECT_DIR/venv/bin/activate"
    
    # Install test dependencies
    log "Installing test dependencies..."
    pip3 install -r "$TESTS_DIR/requirements.txt" > /dev/null 2>&1
    
    # Install project dependencies
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip3 install -r "$PROJECT_DIR/requirements.txt" > /dev/null 2>&1
    fi
    
    log_success "Dependencies installed"
}

run_unit_tests() {
    log "Running unit tests..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    if python3 -m pytest "$TESTS_DIR/test_app.py" -v --tb=short; then
        log_success "Unit tests passed"
        return 0
    else
        log_error "Unit tests failed"
        return 1
    fi
}

run_integration_tests() {
    log "Running integration tests..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    if python3 -m pytest "$TESTS_DIR/test_integration.py" -v --tb=short; then
        log_success "Integration tests passed"
        return 0
    else
        log_error "Integration tests failed"
        return 1
    fi
}

run_api_tests() {
    log "Running API tests..."
    
    # Check if API test script is executable
    if [ ! -x "$TESTS_DIR/test_api.sh" ]; then
        chmod +x "$TESTS_DIR/test_api.sh"
    fi
    
    # Set default values for API tests
    export PROXY_URL="${PROXY_URL:-http://localhost:8099}"
    export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-test-token}"
    export VERBOSE="${VERBOSE:-false}"
    
    if "$TESTS_DIR/test_api.sh" --url "$PROXY_URL" --token "$SUPERVISOR_TOKEN"; then
        log_success "API tests passed"
        return 0
    else
        log_error "API tests failed"
        return 1
    fi
}

run_code_quality_checks() {
    log "Running code quality checks..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Install quality tools
    pip3 install flake8 black isort > /dev/null 2>&1
    
    local errors=0
    
    # Check Python code formatting with black
    if ! python3 -m black --check app.py 2>/dev/null; then
        log_warning "Code formatting issues found (run: black app.py)"
        errors=$((errors + 1))
    else
        log_success "Code formatting is good"
    fi
    
    # Check import sorting
    if ! python3 -m isort --check-only app.py 2>/dev/null; then
        log_warning "Import sorting issues found (run: isort app.py)"
        errors=$((errors + 1))
    else
        log_success "Import sorting is good"
    fi
    
    # Check code style with flake8
    if ! python3 -m flake8 app.py --max-line-length=100 --ignore=E203,W503 2>/dev/null; then
        log_warning "Code style issues found"
        errors=$((errors + 1))
    else
        log_success "Code style is good"
    fi
    
    return $errors
}

run_coverage_tests() {
    log "Running coverage analysis..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Install coverage
    pip3 install coverage > /dev/null 2>&1
    
    # Run tests with coverage
    if python3 -m coverage run -m pytest "$TESTS_DIR/test_app.py" -v > /dev/null 2>&1; then
        # Generate coverage report
        local coverage_percent
        coverage_percent=$(python3 -m coverage report | tail -1 | awk '{print $4}')
        
        log_success "Coverage analysis completed: $coverage_percent"
        
        # Generate HTML coverage report
        python3 -m coverage html -d "$PROJECT_DIR/htmlcov" > /dev/null 2>&1
        log "HTML coverage report generated in htmlcov/"
        
        return 0
    else
        log_error "Coverage analysis failed"
        return 1
    fi
}

run_docker_tests() {
    log "Running Docker build test..."
    
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not available, skipping Docker tests"
        return 0
    fi
    
    cd "$PROJECT_DIR"
    
    # Build Docker image
    if docker build -t ha-supervisor-proxy-test . > /dev/null 2>&1; then
        log_success "Docker build successful"
        
        # Clean up test image
        docker rmi ha-supervisor-proxy-test > /dev/null 2>&1 || true
        
        return 0
    else
        log_error "Docker build failed"
        return 1
    fi
}

cleanup() {
    log "Cleaning up test artifacts..."
    
    # Remove test output files
    rm -f "$PROJECT_DIR/test_results.log"
    rm -f "$PROJECT_DIR/.coverage"
    rm -rf "$PROJECT_DIR/htmlcov"
    rm -rf "$PROJECT_DIR/__pycache__"
    rm -rf "$PROJECT_DIR/tests/__pycache__"
    
    # Deactivate virtual environment if active
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        deactivate
    fi
    
    log_success "Cleanup completed"
}

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --unit         Run unit tests only"
    echo "  --integration  Run integration tests only"  
    echo "  --api          Run API tests only"
    echo "  --quality      Run code quality checks only"
    echo "  --coverage     Run coverage analysis only"
    echo "  --docker       Run Docker tests only"
    echo "  --all          Run all tests (default)"
    echo "  --clean        Clean up test artifacts"
    echo "  --help         Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  PROXY_URL      Proxy URL for API tests (default: http://localhost:8099)"
    echo "  SUPERVISOR_TOKEN  Supervisor token for API tests"
    echo "  VERBOSE        Enable verbose output (true/false)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests"
    echo "  $0 --unit --quality                  # Run unit tests and quality checks"
    echo "  PROXY_URL=http://192.168.1.100:8099 $0 --api  # Run API tests with custom URL"
}

main() {
    local run_unit=false
    local run_integration=false
    local run_api=false
    local run_quality=false
    local run_coverage=false
    local run_docker=false
    local run_all=true
    local clean_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --unit)
                run_unit=true
                run_all=false
                shift
                ;;
            --integration)
                run_integration=true
                run_all=false
                shift
                ;;
            --api)
                run_api=true
                run_all=false
                shift
                ;;
            --quality)
                run_quality=true
                run_all=false
                shift
                ;;
            --coverage)
                run_coverage=true
                run_all=false
                shift
                ;;
            --docker)
                run_docker=true
                run_all=false
                shift
                ;;
            --all)
                run_all=true
                shift
                ;;
            --clean)
                clean_only=true
                shift
                ;;
            --help)
                print_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    print_banner
    
    # Clean up if requested
    if [ "$clean_only" = true ]; then
        cleanup
        exit 0
    fi
    
    local total_errors=0
    local tests_run=0
    
    # Set up dependencies
    check_dependencies
    
    # Run selected tests
    if [ "$run_all" = true ]; then
        run_unit=true
        run_integration=true
        run_api=true
        run_quality=true
        run_coverage=true
        run_docker=true
    fi
    
    if [ "$run_unit" = true ]; then
        tests_run=$((tests_run + 1))
        if ! run_unit_tests; then
            total_errors=$((total_errors + 1))
        fi
        echo
    fi
    
    if [ "$run_integration" = true ]; then
        tests_run=$((tests_run + 1))
        if ! run_integration_tests; then
            total_errors=$((total_errors + 1))
        fi
        echo
    fi
    
    if [ "$run_api" = true ]; then
        tests_run=$((tests_run + 1))
        if ! run_api_tests; then
            total_errors=$((total_errors + 1))
        fi
        echo
    fi
    
    if [ "$run_quality" = true ]; then
        tests_run=$((tests_run + 1))
        if ! run_code_quality_checks; then
            total_errors=$((total_errors + 1))
        fi
        echo
    fi
    
    if [ "$run_coverage" = true ]; then
        tests_run=$((tests_run + 1))
        if ! run_coverage_tests; then
            total_errors=$((total_errors + 1))
        fi
        echo
    fi
    
    if [ "$run_docker" = true ]; then
        tests_run=$((tests_run + 1))
        if ! run_docker_tests; then
            total_errors=$((total_errors + 1))
        fi
        echo
    fi
    
    # Print final summary
    echo "=============================================================================="
    echo "  Final Test Summary"
    echo "=============================================================================="
    echo "  Test Suites Run:   $tests_run"
    echo "  Test Suites Failed: $total_errors"
    
    if [ "$total_errors" -eq 0 ]; then
        echo -e "  Overall Result:    ${GREEN}ALL TESTS PASSED${NC}"
    else
        echo -e "  Overall Result:    ${RED}SOME TESTS FAILED${NC}"
    fi
    
    echo "=============================================================================="
    
    # Clean up
    cleanup
    
    # Exit with appropriate code
    exit $total_errors
}

# Run the main function with all arguments
main "$@"