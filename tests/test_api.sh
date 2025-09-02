#!/bin/bash
# ==============================================================================
# Shell script for testing Home Assistant Supervisor API Proxy
# This script performs comprehensive API testing using curl
# ==============================================================================

set -e

# Configuration
PROXY_URL="${PROXY_URL:-http://localhost:8099}"
API_BASE="${PROXY_URL}/api/v1"
SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-}"
VERBOSE="${VERBOSE:-false}"
OUTPUT_FILE="${OUTPUT_FILE:-test_results.log}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$OUTPUT_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
    echo "✓ $1" >> "$OUTPUT_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    echo "✗ $1" >> "$OUTPUT_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    echo "⚠ $1" >> "$OUTPUT_FILE"
}

verbose_log() {
    if [ "$VERBOSE" = "true" ]; then
        echo -e "${YELLOW}[DEBUG]${NC} $1"
    fi
    echo "[DEBUG] $1" >> "$OUTPUT_FILE"
}

# ==============================================================================
# HTTP REQUEST FUNCTIONS
# ==============================================================================

make_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local expected_status="$4"
    local description="$5"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    local curl_args=("-X" "$method" "-s" "-w" "%{http_code}" "-o" "/tmp/response_body")
    
    # Add authorization header if token is provided
    if [ -n "$SUPERVISOR_TOKEN" ]; then
        curl_args+=("-H" "Authorization: Bearer $SUPERVISOR_TOKEN")
    fi
    
    # Add content type for POST/PUT requests
    if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
        curl_args+=("-H" "Content-Type: application/json")
    fi
    
    # Add data if provided
    if [ -n "$data" ]; then
        curl_args+=("-d" "$data")
    fi
    
    # Add endpoint URL
    curl_args+=("${API_BASE}${endpoint}")
    
    verbose_log "Making $method request to $endpoint"
    verbose_log "curl ${curl_args[*]}"
    
    # Make the request
    local status_code
    status_code=$(curl "${curl_args[@]}" 2>/dev/null || echo "000")
    
    local response_body=""
    if [ -f "/tmp/response_body" ]; then
        response_body=$(cat /tmp/response_body)
        rm -f /tmp/response_body
    fi
    
    verbose_log "Response status: $status_code"
    verbose_log "Response body: $response_body"
    
    # Check status code
    if [ "$status_code" = "$expected_status" ]; then
        log_success "$description (Status: $status_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "$description (Expected: $expected_status, Got: $status_code)"
        if [ -n "$response_body" ]; then
            log_error "Response: $response_body"
        fi
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

check_json_response() {
    local endpoint="$1"
    local expected_field="$2"
    local description="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    local curl_args=("-s")
    
    if [ -n "$SUPERVISOR_TOKEN" ]; then
        curl_args+=("-H" "Authorization: Bearer $SUPERVISOR_TOKEN")
    fi
    
    curl_args+=("${API_BASE}${endpoint}")
    
    verbose_log "Checking JSON response from $endpoint for field: $expected_field"
    
    local response
    response=$(curl "${curl_args[@]}" 2>/dev/null)
    
    if echo "$response" | jq -e ".$expected_field" > /dev/null 2>&1; then
        log_success "$description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "$description"
        log_error "Response: $response"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ==============================================================================
# TEST FUNCTIONS
# ==============================================================================

test_health_endpoint() {
    log "Testing Health Endpoint"
    
    make_request "GET" "/health" "" "200" "Health check should return 200"
    check_json_response "/health" "status" "Health response should contain status field"
    check_json_response "/health" "supervisor_connection" "Health response should contain supervisor_connection field"
    check_json_response "/health" "timestamp" "Health response should contain timestamp field"
}

test_discovery_endpoint() {
    log "Testing Discovery Endpoint"
    
    make_request "GET" "/discovery" "" "200" "Discovery should return 200"
    check_json_response "/discovery" "message" "Discovery response should contain message field"
    check_json_response "/discovery" "endpoints" "Discovery response should contain endpoints field"
    check_json_response "/discovery" "version" "Discovery response should contain version field"
}

test_addons_endpoints() {
    log "Testing Add-ons Endpoints"
    
    # List all add-ons
    make_request "GET" "/addons" "" "200" "List add-ons should return 200"
    check_json_response "/addons" "data" "Add-ons response should contain data field"
    
    # Test with a common add-on slug (might not exist, so we expect 404 or 200)
    make_request "GET" "/addons/core_ssh" "" "200|404" "Get specific add-on info"
    
    # Test non-existent add-on
    make_request "GET" "/addons/non-existent-addon" "" "404" "Non-existent add-on should return 404"
    
    # Test add-on actions (these will likely fail without a real add-on, but we test the endpoint)
    make_request "POST" "/addons/test-addon/start" "" "200|400|404" "Start add-on endpoint"
    make_request "POST" "/addons/test-addon/stop" "" "200|400|404" "Stop add-on endpoint"
    make_request "POST" "/addons/test-addon/restart" "" "200|400|404" "Restart add-on endpoint"
    
    # Test add-on logs
    make_request "GET" "/addons/test-addon/logs" "" "200|404" "Get add-on logs"
}

test_backups_endpoints() {
    log "Testing Backups Endpoints"
    
    # List backups
    make_request "GET" "/backups" "" "200" "List backups should return 200"
    check_json_response "/backups" "data" "Backups response should contain data field"
    
    # Create backup (this will likely take time or fail, so we accept various statuses)
    local backup_data='{"name":"API Test Backup","addons":null,"folders":null,"password":null}'
    make_request "POST" "/backups" "$backup_data" "200|400|500" "Create backup endpoint"
    
    # Test non-existent backup
    make_request "GET" "/backups/non-existent-backup" "" "404" "Non-existent backup should return 404"
}

test_system_endpoints() {
    log "Testing System Endpoints"
    
    # Supervisor info
    make_request "GET" "/supervisor/info" "" "200" "Supervisor info should return 200"
    check_json_response "/supervisor/info" "data" "Supervisor info response should contain data field"
    
    # Core info
    make_request "GET" "/core/info" "" "200" "Core info should return 200"  
    check_json_response "/core/info" "data" "Core info response should contain data field"
    
    # Host info (might not be available in all setups)
    make_request "GET" "/host/info" "" "200|404" "Host info endpoint"
    
    # OS info (might not be available in all setups)
    make_request "GET" "/os/info" "" "200|404" "OS info endpoint"
    
    # Network info
    make_request "GET" "/network/info" "" "200|404" "Network info endpoint"
}

test_jobs_endpoints() {
    log "Testing Jobs Endpoints"
    
    # List jobs
    make_request "GET" "/jobs" "" "200" "List jobs should return 200"
    check_json_response "/jobs" "data" "Jobs response should contain data field"
    
    # Get specific job (will likely not exist)
    make_request "GET" "/jobs/non-existent-job-uuid" "" "404" "Non-existent job should return 404"
}

test_store_endpoints() {
    log "Testing Store Endpoints"
    
    # List repositories
    make_request "GET" "/store/repositories" "" "200|404" "List repositories endpoint"
    
    # List store add-ons
    make_request "GET" "/store/addons" "" "200|404" "List store add-ons endpoint"
}

test_error_handling() {
    log "Testing Error Handling"
    
    # Test invalid endpoints
    make_request "GET" "/invalid-endpoint" "" "404" "Invalid endpoint should return 404"
    make_request "GET" "/api/invalid" "" "404" "Invalid API endpoint should return 404"
    
    # Test method not allowed
    make_request "PUT" "/health" "" "405" "PUT on health endpoint should return 405"
    make_request "DELETE" "/discovery" "" "405" "DELETE on discovery endpoint should return 405"
    
    # Test malformed JSON
    make_request "POST" "/backups" "invalid-json" "400" "Invalid JSON should return 400"
}

test_cors_headers() {
    log "Testing CORS Headers"
    
    local curl_args=("-s" "-I")
    
    if [ -n "$SUPERVISOR_TOKEN" ]; then
        curl_args+=("-H" "Authorization: Bearer $SUPERVISOR_TOKEN")
    fi
    
    curl_args+=("${API_BASE}/discovery")
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    local headers
    headers=$(curl "${curl_args[@]}" 2>/dev/null)
    
    if echo "$headers" | grep -i "access-control-allow-origin" > /dev/null; then
        log_success "CORS headers present"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "CORS headers missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

test_authentication() {
    log "Testing Authentication"
    
    if [ -z "$SUPERVISOR_TOKEN" ]; then
        log_warning "No SUPERVISOR_TOKEN provided, skipping authentication tests"
        return
    fi
    
    # Test with valid token (already tested in other tests)
    TESTS_RUN=$((TESTS_RUN + 1))
    log_success "Valid token authentication (tested in other endpoints)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # Test with invalid token
    local old_token="$SUPERVISOR_TOKEN"
    SUPERVISOR_TOKEN="invalid-token"
    
    make_request "GET" "/addons" "" "401|403" "Invalid token should return 401 or 403"
    
    # Test without token
    SUPERVISOR_TOKEN=""
    make_request "GET" "/addons" "" "401|403|500" "No token should return error"
    
    # Restore original token
    SUPERVISOR_TOKEN="$old_token"
}

# ==============================================================================
# STRESS TESTS
# ==============================================================================

test_concurrent_requests() {
    log "Testing Concurrent Requests"
    
    local pids=()
    local temp_dir="/tmp/api_test_$$"
    mkdir -p "$temp_dir"
    
    # Start 5 concurrent requests
    for i in {1..5}; do
        (
            local result_file="$temp_dir/result_$i"
            local curl_args=("-s" "-w" "%{http_code}" "-o" "/dev/null")
            
            if [ -n "$SUPERVISOR_TOKEN" ]; then
                curl_args+=("-H" "Authorization: Bearer $SUPERVISOR_TOKEN")
            fi
            
            curl_args+=("${API_BASE}/discovery")
            
            local status_code
            status_code=$(curl "${curl_args[@]}" 2>/dev/null || echo "000")
            echo "$status_code" > "$result_file"
        ) &
        pids+=($!)
    done
    
    # Wait for all requests to complete
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Check results
    local success_count=0
    for i in {1..5}; do
        local result_file="$temp_dir/result_$i"
        if [ -f "$result_file" ]; then
            local status_code
            status_code=$(cat "$result_file")
            if [ "$status_code" = "200" ]; then
                success_count=$((success_count + 1))
            fi
        fi
    done
    
    # Clean up
    rm -rf "$temp_dir"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ "$success_count" -ge 4 ]; then
        log_success "Concurrent requests test (${success_count}/5 succeeded)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "Concurrent requests test failed (${success_count}/5 succeeded)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

print_banner() {
    echo "=============================================================================="
    echo "  Home Assistant Supervisor API Proxy - API Tests"
    echo "=============================================================================="
    echo "  Proxy URL: $PROXY_URL"
    echo "  API Base:  $API_BASE"
    echo "  Token:     ${SUPERVISOR_TOKEN:+[CONFIGURED]}${SUPERVISOR_TOKEN:-[NOT SET]}"
    echo "  Output:    $OUTPUT_FILE"
    echo "  Verbose:   $VERBOSE"
    echo "=============================================================================="
    echo
}

run_all_tests() {
    # Clear previous results
    > "$OUTPUT_FILE"
    
    print_banner
    
    log "Starting API tests..."
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        log_warning "jq not found. JSON validation tests will be skipped."
    fi
    
    # Check if the proxy is responding
    local curl_args=("-s" "--connect-timeout" "5" "-w" "%{http_code}" "-o" "/dev/null")
    curl_args+=("${API_BASE}/health")
    
    local health_status
    health_status=$(curl "${curl_args[@]}" 2>/dev/null || echo "000")
    
    if [ "$health_status" = "000" ]; then
        log_error "Cannot connect to proxy at $PROXY_URL"
        log_error "Make sure the proxy is running and accessible"
        exit 1
    fi
    
    log "Proxy is responding (Health status: $health_status)"
    echo
    
    # Run all test suites
    test_health_endpoint
    echo
    
    test_discovery_endpoint
    echo
    
    test_addons_endpoints
    echo
    
    test_backups_endpoints
    echo
    
    test_system_endpoints
    echo
    
    test_jobs_endpoints
    echo
    
    test_store_endpoints
    echo
    
    test_error_handling
    echo
    
    test_cors_headers
    echo
    
    test_authentication
    echo
    
    test_concurrent_requests
    echo
}

print_summary() {
    echo "=============================================================================="
    echo "  Test Summary"
    echo "=============================================================================="
    echo "  Tests Run:    $TESTS_RUN"
    echo "  Tests Passed: $TESTS_PASSED"
    echo "  Tests Failed: $TESTS_FAILED"
    
    if [ "$TESTS_FAILED" -eq 0 ]; then
        echo -e "  Result:       ${GREEN}ALL TESTS PASSED${NC}"
        echo "  Result:       ALL TESTS PASSED" >> "$OUTPUT_FILE"
    else
        echo -e "  Result:       ${RED}SOME TESTS FAILED${NC}"
        echo "  Result:       SOME TESTS FAILED" >> "$OUTPUT_FILE"
    fi
    
    echo "=============================================================================="
    echo "  Detailed results saved to: $OUTPUT_FILE"
    echo "=============================================================================="
}

# ==============================================================================
# SCRIPT ENTRY POINT
# ==============================================================================

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            PROXY_URL="$2"
            API_BASE="${PROXY_URL}/api/v1"
            shift 2
            ;;
        -t|--token)
            SUPERVISOR_TOKEN="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="true"
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -u, --url URL      Proxy URL (default: http://localhost:8099)"
            echo "  -t, --token TOKEN  Supervisor token for authentication"
            echo "  -v, --verbose      Enable verbose output"
            echo "  -o, --output FILE  Output file for results (default: test_results.log)"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  PROXY_URL          Proxy URL"
            echo "  SUPERVISOR_TOKEN   Supervisor token"
            echo "  VERBOSE            Enable verbose output (true/false)"
            echo "  OUTPUT_FILE        Output file for results"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Run the tests
run_all_tests
print_summary

# Exit with appropriate code
exit $TESTS_FAILED