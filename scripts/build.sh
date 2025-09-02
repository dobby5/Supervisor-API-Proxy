#!/bin/bash
# ==============================================================================
# Build script for Home Assistant Supervisor API Proxy Add-on
# ==============================================================================

set -e

# Configuration
ADDON_NAME="supervisor_api_proxy"
ORGANIZATION="${ORGANIZATION:-homeassistant}"
REGISTRY="${REGISTRY:-ghcr.io}"
BUILD_FROM="${BUILD_FROM:-}"
CACHE_TAG="${CACHE_TAG:-cache}"
PUSH="${PUSH:-false}"
NO_CACHE="${NO_CACHE:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
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
    echo "  Home Assistant Add-on Builder"
    echo "=============================================================================="
    echo "  Add-on: $ADDON_NAME"
    echo "  Registry: $REGISTRY"
    echo "  Organization: $ORGANIZATION"
    echo "  Push images: $PUSH"
    echo "  Use cache: $([ "$NO_CACHE" = "true" ] && echo "No" || echo "Yes")"
    echo "=============================================================================="
    echo
}

check_dependencies() {
    log "Checking build dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check Docker Buildx
    if ! docker buildx version &> /dev/null; then
        log_error "Docker Buildx is required but not available"
        log "Install with: docker buildx install"
        exit 1
    fi
    
    # Check jq for JSON processing
    if ! command -v jq &> /dev/null; then
        log_warning "jq not found, some features may be limited"
    fi
    
    log_success "All dependencies available"
}

setup_buildx() {
    log "Setting up Docker Buildx..."
    
    # Create or use existing buildx instance
    if ! docker buildx inspect addon-builder &> /dev/null; then
        log "Creating new buildx instance..."
        docker buildx create --name addon-builder --driver docker-container --use
    else
        log "Using existing buildx instance..."
        docker buildx use addon-builder
    fi
    
    # Bootstrap the builder
    docker buildx inspect --bootstrap
    
    log_success "Buildx setup complete"
}

get_version() {
    if [ -f "config.yaml" ]; then
        VERSION=$(grep "version:" config.yaml | awk '{print $2}' | tr -d '"')
        if [ -z "$VERSION" ]; then
            VERSION="dev"
        fi
    else
        VERSION="dev"
    fi
    
    echo "$VERSION"
}

get_architectures() {
    if [ -f "config.yaml" ]; then
        # Extract architectures from config.yaml
        ARCHS=$(grep -A 10 "arch:" config.yaml | grep "  -" | awk '{print $2}' | tr '\n' ' ')
        if [ -z "$ARCHS" ]; then
            ARCHS="amd64"
        fi
    else
        ARCHS="amd64 aarch64 armhf armv7 i386"
    fi
    
    echo "$ARCHS"
}

build_single_arch() {
    local arch="$1"
    local version="$2"
    local image_name="$3"
    
    log "Building for architecture: $arch"
    
    # Determine base image
    local base_image
    case "$arch" in
        aarch64)
            base_image="ghcr.io/home-assistant/aarch64-base-python:3.11-alpine3.18"
            ;;
        amd64)
            base_image="ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18"
            ;;
        armhf)
            base_image="ghcr.io/home-assistant/armhf-base-python:3.11-alpine3.18"
            ;;
        armv7)
            base_image="ghcr.io/home-assistant/armv7-base-python:3.11-alpine3.18"
            ;;
        i386)
            base_image="ghcr.io/home-assistant/i386-base-python:3.11-alpine3.18"
            ;;
        *)
            log_error "Unsupported architecture: $arch"
            return 1
            ;;
    esac
    
    # Build arguments
    local build_args=(
        "--platform" "linux/$arch"
        "--build-arg" "BUILD_FROM=$base_image"
        "--tag" "$image_name:$version"
        "--tag" "$image_name:latest"
    )
    
    # Add cache arguments
    if [ "$NO_CACHE" != "true" ]; then
        build_args+=(
            "--cache-from" "type=registry,ref=$image_name:$CACHE_TAG"
            "--cache-to" "type=registry,ref=$image_name:$CACHE_TAG,mode=max"
        )
    else
        build_args+=("--no-cache")
    fi
    
    # Add push argument if enabled
    if [ "$PUSH" = "true" ]; then
        build_args+=("--push")
    else
        build_args+=("--load")
    fi
    
    # Build the image
    if docker buildx build "${build_args[@]}" .; then
        log_success "Successfully built $arch image"
        return 0
    else
        log_error "Failed to build $arch image"
        return 1
    fi
}

build_multi_arch() {
    local version="$1"
    local architectures=($2)
    
    log "Building multi-architecture image..."
    
    # Create platform list
    local platforms=""
    for arch in "${architectures[@]}"; do
        if [ -n "$platforms" ]; then
            platforms="$platforms,"
        fi
        platforms="$platforms linux/$arch"
    done
    
    local image_name="$REGISTRY/$ORGANIZATION/$arch-addon-$ADDON_NAME"
    
    # Build arguments for multi-arch
    local build_args=(
        "--platform" "$platforms"
        "--tag" "$image_name:$version"
        "--tag" "$image_name:latest"
    )
    
    # Add cache arguments
    if [ "$NO_CACHE" != "true" ]; then
        build_args+=(
            "--cache-from" "type=registry,ref=$image_name:$CACHE_TAG"
            "--cache-to" "type=registry,ref=$image_name:$CACHE_TAG,mode=max"
        )
    else
        build_args+=("--no-cache")
    fi
    
    # Add push argument if enabled
    if [ "$PUSH" = "true" ]; then
        build_args+=("--push")
    fi
    
    # Build the image
    if docker buildx build "${build_args[@]}" .; then
        log_success "Successfully built multi-architecture image"
        return 0
    else
        log_error "Failed to build multi-architecture image"
        return 1
    fi
}

validate_addon() {
    log "Validating add-on configuration..."
    
    # Check required files
    local required_files=("config.yaml" "Dockerfile" "README.md")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            return 1
        fi
    done
    
    # Validate config.yaml
    if command -v yq &> /dev/null; then
        if ! yq eval . config.yaml > /dev/null 2>&1; then
            log_error "Invalid YAML syntax in config.yaml"
            return 1
        fi
    elif command -v python3 &> /dev/null; then
        if ! python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" 2>/dev/null; then
            log_error "Invalid YAML syntax in config.yaml"
            return 1
        fi
    fi
    
    # Check Dockerfile syntax
    if ! docker build --dry-run . > /dev/null 2>&1; then
        log_warning "Dockerfile may have syntax issues"
    fi
    
    log_success "Add-on validation completed"
}

run_tests() {
    log "Running build-time tests..."
    
    # Run linting if available
    if [ -f "scripts/run_tests.sh" ]; then
        log "Running test suite..."
        if bash scripts/run_tests.sh --unit --quality; then
            log_success "Tests passed"
        else
            log_warning "Some tests failed"
        fi
    fi
    
    # Test Docker build (quick validation)
    log "Testing Docker build..."
    if docker build --target test . > /dev/null 2>&1; then
        log_success "Docker build test passed"
    elif docker build . -t test-build > /dev/null 2>&1; then
        log_success "Basic Docker build successful"
        docker rmi test-build > /dev/null 2>&1 || true
    else
        log_error "Docker build test failed"
        return 1
    fi
}

cleanup() {
    log "Cleaning up build artifacts..."
    
    # Remove temporary files
    rm -f .buildx-cache 2>/dev/null || true
    
    # Clean up Docker system if requested
    if [ "$CLEANUP_DOCKER" = "true" ]; then
        docker system prune -f > /dev/null 2>&1 || true
    fi
    
    log_success "Cleanup completed"
}

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --arch ARCH        Build for specific architecture (amd64, aarch64, etc.)"
    echo "  --multi-arch       Build for all supported architectures"
    echo "  --push             Push images to registry after building"
    echo "  --no-cache         Disable build cache"
    echo "  --registry REG     Docker registry (default: ghcr.io)"
    echo "  --org ORG          Organization name (default: homeassistant)"
    echo "  --version VER      Override version tag"
    echo "  --test             Run tests before building"
    echo "  --validate         Only validate add-on configuration"
    echo "  --cleanup          Clean up Docker system after build"
    echo "  --help             Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  ORGANIZATION       Docker organization/username"
    echo "  REGISTRY          Docker registry URL"
    echo "  PUSH              Push images after building (true/false)"
    echo "  NO_CACHE          Disable build cache (true/false)"
    echo "  CLEANUP_DOCKER    Clean up Docker system (true/false)"
    echo ""
    echo "Examples:"
    echo "  $0 --arch amd64 --push"
    echo "  $0 --multi-arch --test --push"
    echo "  $0 --validate"
}

main() {
    local architectures=""
    local build_multi_arch_flag=false
    local run_validation_only=false
    local run_tests_flag=false
    local version_override=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --arch)
                architectures="$2"
                shift 2
                ;;
            --multi-arch)
                build_multi_arch_flag=true
                shift
                ;;
            --push)
                PUSH=true
                shift
                ;;
            --no-cache)
                NO_CACHE=true
                shift
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --org)
                ORGANIZATION="$2"
                shift 2
                ;;
            --version)
                version_override="$2"
                shift 2
                ;;
            --test)
                run_tests_flag=true
                shift
                ;;
            --validate)
                run_validation_only=true
                shift
                ;;
            --cleanup)
                CLEANUP_DOCKER=true
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
    
    # Validation
    check_dependencies
    validate_addon
    
    if [ "$run_validation_only" = true ]; then
        log_success "Validation completed successfully"
        exit 0
    fi
    
    # Testing
    if [ "$run_tests_flag" = true ]; then
        run_tests
    fi
    
    # Setup build environment
    setup_buildx
    
    # Get version
    local version
    if [ -n "$version_override" ]; then
        version="$version_override"
    else
        version=$(get_version)
    fi
    
    log "Building version: $version"
    
    # Build process
    local build_errors=0
    
    if [ "$build_multi_arch_flag" = true ]; then
        # Multi-architecture build
        local all_archs
        all_archs=$(get_architectures)
        
        log "Building for architectures: $all_archs"
        
        if build_multi_arch "$version" "$all_archs"; then
            log_success "Multi-architecture build completed"
        else
            log_error "Multi-architecture build failed"
            build_errors=$((build_errors + 1))
        fi
    
    elif [ -n "$architectures" ]; then
        # Single architecture build
        local image_name="$REGISTRY/$ORGANIZATION/$architectures-addon-$ADDON_NAME"
        
        if build_single_arch "$architectures" "$version" "$image_name"; then
            log_success "Single architecture build completed"
        else
            log_error "Single architecture build failed"
            build_errors=$((build_errors + 1))
        fi
    
    else
        # Build for all architectures individually
        local all_archs
        all_archs=$(get_architectures)
        
        log "Building individual images for architectures: $all_archs"
        
        for arch in $all_archs; do
            local image_name="$REGISTRY/$ORGANIZATION/$arch-addon-$ADDON_NAME"
            
            if build_single_arch "$arch" "$version" "$image_name"; then
                log_success "Build completed for $arch"
            else
                log_error "Build failed for $arch"
                build_errors=$((build_errors + 1))
            fi
        done
    fi
    
    # Cleanup
    cleanup
    
    # Summary
    echo
    echo "=============================================================================="
    echo "  Build Summary"
    echo "=============================================================================="
    echo "  Version: $version"
    echo "  Registry: $REGISTRY"
    echo "  Organization: $ORGANIZATION"
    echo "  Pushed to registry: $PUSH"
    echo "  Build errors: $build_errors"
    
    if [ $build_errors -eq 0 ]; then
        echo -e "  Result: ${GREEN}BUILD SUCCESSFUL${NC}"
    else
        echo -e "  Result: ${RED}BUILD FAILED${NC}"
    fi
    
    echo "=============================================================================="
    
    exit $build_errors
}

# Handle signals
trap 'echo "Build interrupted"; cleanup; exit 130' INT TERM

# Run main function
main "$@"