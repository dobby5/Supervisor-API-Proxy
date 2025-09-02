#!/bin/bash
# ==============================================================================
# Deployment script for Home Assistant Supervisor API Proxy Add-on
# ==============================================================================

set -e

# Configuration
ADDON_NAME="supervisor_api_proxy"
ORGANIZATION="${ORGANIZATION:-homeassistant}"
REGISTRY="${REGISTRY:-ghcr.io}"
BRANCH="${BRANCH:-main}"
TAG_PREFIX="${TAG_PREFIX:-v}"
DRY_RUN="${DRY_RUN:-false}"

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
    echo "  Home Assistant Add-on Deployment"
    echo "=============================================================================="
    echo "  Add-on: $ADDON_NAME"
    echo "  Organization: $ORGANIZATION"
    echo "  Registry: $REGISTRY"
    echo "  Branch: $BRANCH"
    echo "  Dry Run: $DRY_RUN"
    echo "=============================================================================="
    echo
}

check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "Git is required but not installed"
        exit 1
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Must be run from a git repository"
        exit 1
    fi
    
    # Check if working directory is clean
    if [ "$DRY_RUN" != "true" ] && ! git diff-index --quiet HEAD --; then
        log_error "Working directory is not clean. Commit or stash changes first."
        exit 1
    fi
    
    # Check Docker authentication
    if [ "$DRY_RUN" != "true" ]; then
        if ! docker pull hello-world > /dev/null 2>&1; then
            log_warning "Docker authentication may be required"
        fi
    fi
    
    # Check GitHub CLI (optional)
    if command -v gh &> /dev/null; then
        if gh auth status > /dev/null 2>&1; then
            log_success "GitHub CLI authenticated"
        else
            log_warning "GitHub CLI not authenticated (some features may be limited)"
        fi
    else
        log_warning "GitHub CLI not available (some features may be limited)"
    fi
    
    log_success "Prerequisites check completed"
}

get_current_version() {
    if [ -f "config.yaml" ]; then
        grep "version:" config.yaml | awk '{print $2}' | tr -d '"'
    else
        echo "unknown"
    fi
}

get_next_version() {
    local current_version="$1"
    local version_type="${2:-patch}"
    
    # Parse semantic version
    if [[ "$current_version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        local major="${BASH_REMATCH[1]}"
        local minor="${BASH_REMATCH[2]}"
        local patch="${BASH_REMATCH[3]}"
        
        case "$version_type" in
            major)
                echo "$((major + 1)).0.0"
                ;;
            minor)
                echo "$major.$((minor + 1)).0"
                ;;
            patch)
                echo "$major.$minor.$((patch + 1))"
                ;;
            *)
                echo "$current_version"
                ;;
        esac
    else
        echo "1.0.0"
    fi
}

update_version() {
    local new_version="$1"
    
    log "Updating version to $new_version..."
    
    # Update config.yaml
    if [ -f "config.yaml" ]; then
        if command -v sed &> /dev/null; then
            sed -i.bak "s/version: .*/version: \"$new_version\"/" config.yaml
            rm -f config.yaml.bak
        else
            log_error "sed command not available for version update"
            return 1
        fi
    fi
    
    # Update other version references if they exist
    if [ -f "build.yaml" ]; then
        sed -i.bak "s/version: .*/version: \"$new_version\"/" build.yaml 2>/dev/null || true
        rm -f build.yaml.bak 2>/dev/null || true
    fi
    
    log_success "Version updated to $new_version"
}

create_git_tag() {
    local version="$1"
    local tag_name="$TAG_PREFIX$version"
    
    log "Creating git tag: $tag_name"
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warning "DRY RUN: Would create tag $tag_name"
        return 0
    fi
    
    # Check if tag already exists
    if git rev-parse "$tag_name" > /dev/null 2>&1; then
        log_error "Tag $tag_name already exists"
        return 1
    fi
    
    # Create annotated tag
    git tag -a "$tag_name" -m "Release version $version
    
Home Assistant Supervisor API Proxy $version

Features:
- REST API proxy for Home Assistant Supervisor
- Android client support with Retrofit
- Multi-architecture Docker images
- Comprehensive test suite
- Security scanning and monitoring

Supported architectures: amd64, aarch64, armhf, armv7, i386"
    
    log_success "Git tag $tag_name created"
}

push_changes() {
    local version="$1"
    local tag_name="$TAG_PREFIX$version"
    
    log "Pushing changes and tags to remote..."
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warning "DRY RUN: Would push changes and tag $tag_name"
        return 0
    fi
    
    # Push commits
    git push origin "$BRANCH"
    
    # Push tags
    git push origin "$tag_name"
    
    log_success "Changes and tags pushed to remote"
}

build_and_push_images() {
    local version="$1"
    
    log "Building and pushing Docker images..."
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warning "DRY RUN: Would build and push images for version $version"
        return 0
    fi
    
    # Run build script
    if [ -f "scripts/build.sh" ]; then
        chmod +x scripts/build.sh
        if ./scripts/build.sh --multi-arch --push --version "$version"; then
            log_success "Docker images built and pushed"
        else
            log_error "Failed to build and push Docker images"
            return 1
        fi
    else
        log_error "Build script not found: scripts/build.sh"
        return 1
    fi
}

create_github_release() {
    local version="$1"
    local tag_name="$TAG_PREFIX$version"
    
    log "Creating GitHub release..."
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warning "DRY RUN: Would create GitHub release for $tag_name"
        return 0
    fi
    
    if ! command -v gh &> /dev/null; then
        log_warning "GitHub CLI not available, skipping release creation"
        return 0
    fi
    
    # Generate release notes
    local release_notes
    release_notes=$(cat << EOF
# 🚀 Home Assistant Supervisor API Proxy $version

A comprehensive REST API proxy for Home Assistant Supervisor, enabling external access from Android applications and other clients.

## ✨ Features

- **Complete Supervisor API Proxy** - Access all Supervisor endpoints through a clean REST interface
- **Android Integration** - Full Retrofit-based Kotlin client for Android development
- **Multi-Architecture Support** - Docker images for amd64, aarch64, armhf, armv7, and i386
- **Security First** - Token-based authentication with CORS support
- **Health Monitoring** - Built-in health checks and API discovery endpoints
- **Comprehensive Testing** - Full test suite with unit, integration, and security tests

## 📦 Installation

1. Add this repository to your Home Assistant Add-on store
2. Search for "Supervisor API Proxy" in the Add-on store  
3. Click Install and configure the add-on
4. Start the add-on

## 🔧 Configuration

\`\`\`yaml
log_level: info
cors_origins:
  - "*"  # Configure for production use
port: 8099
ssl: false
\`\`\`

## 📱 Android Development

The included Kotlin client provides easy integration for Android apps:

\`\`\`kotlin
val apiService = SupervisorApiClient.create(
    baseUrl = "http://your-ha-ip:8099",
    authToken = "your_supervisor_token"
)
\`\`\`

See the [Android Integration Guide](docs/android-integration.md) for complete documentation.

## 🏗️ Supported Architectures

- **amd64** - Intel/AMD 64-bit processors
- **aarch64** - ARM 64-bit processors (Raspberry Pi 4, etc.)  
- **armhf** - ARM 32-bit hard float
- **armv7** - ARM v7 32-bit processors
- **i386** - Intel 32-bit processors

## 🔗 Links

- [📚 Documentation](https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')#readme)
- [🐛 Report Issues](https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/issues)
- [💬 Discussions](https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/discussions)

---

**Full Changelog**: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/compare/$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "initial")...$tag_name
EOF
)
    
    # Create release
    if gh release create "$tag_name" \
        --title "Release $version" \
        --notes "$release_notes" \
        --latest; then
        log_success "GitHub release created: $tag_name"
    else
        log_error "Failed to create GitHub release"
        return 1
    fi
}

update_repository_json() {
    local version="$1"
    
    log "Updating repository.json..."
    
    # Create or update repository.json
    cat > repository.json << EOF
{
  "name": "Home Assistant Supervisor API Proxy Repository",
  "url": "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')",
  "maintainer": "Home Assistant Community",
  "description": "Repository for the Home Assistant Supervisor API Proxy Add-on"
}
EOF
    
    # Commit the update if not in dry run mode
    if [ "$DRY_RUN" != "true" ]; then
        git add repository.json
        git commit -m "Update repository.json for version $version" || true
    fi
    
    log_success "Repository metadata updated"
}

rollback_changes() {
    local version="$1"
    local tag_name="$TAG_PREFIX$version"
    
    log_warning "Rolling back changes due to deployment failure..."
    
    # Remove git tag if it was created
    if git rev-parse "$tag_name" > /dev/null 2>&1; then
        git tag -d "$tag_name" || true
        log_warning "Removed local tag $tag_name"
    fi
    
    # Reset version changes
    git checkout HEAD -- config.yaml build.yaml 2>/dev/null || true
    
    log_warning "Rollback completed - please review any remaining changes"
}

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --version VERSION  Deploy specific version (e.g., 1.2.3)"
    echo "  --bump TYPE        Bump version automatically (major|minor|patch)"
    echo "  --tag-prefix TAG   Git tag prefix (default: v)"
    echo "  --branch BRANCH    Git branch to deploy from (default: main)"
    echo "  --registry REG     Docker registry (default: ghcr.io)"
    echo "  --org ORG          Organization name (default: homeassistant)"
    echo "  --dry-run          Show what would be done without making changes"
    echo "  --skip-build       Skip Docker image building"
    echo "  --skip-release     Skip GitHub release creation"
    echo "  --help             Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  ORGANIZATION       Docker organization"
    echo "  REGISTRY          Docker registry URL"
    echo "  DRY_RUN           Enable dry run mode (true/false)"
    echo "  GITHUB_TOKEN      GitHub token for release creation"
    echo ""
    echo "Examples:"
    echo "  $0 --bump patch              # Bump patch version and deploy"
    echo "  $0 --version 1.2.0           # Deploy specific version"
    echo "  $0 --dry-run --bump minor    # Preview minor version bump"
}

main() {
    local version_arg=""
    local bump_type=""
    local skip_build=false
    local skip_release=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                version_arg="$2"
                shift 2
                ;;
            --bump)
                bump_type="$2"
                shift 2
                ;;
            --tag-prefix)
                TAG_PREFIX="$2"
                shift 2
                ;;
            --branch)
                BRANCH="$2"
                shift 2
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --org)
                ORGANIZATION="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-build)
                skip_build=true
                shift
                ;;
            --skip-release)
                skip_release=true
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
    
    # Prerequisites check
    check_prerequisites
    
    # Determine version to deploy
    local current_version
    current_version=$(get_current_version)
    
    local target_version
    if [ -n "$version_arg" ]; then
        target_version="$version_arg"
    elif [ -n "$bump_type" ]; then
        target_version=$(get_next_version "$current_version" "$bump_type")
    else
        target_version="$current_version"
    fi
    
    log "Current version: $current_version"
    log "Target version: $target_version"
    
    # Confirm deployment
    if [ "$DRY_RUN" != "true" ] && [ "$target_version" != "$current_version" ]; then
        echo
        read -p "Deploy version $target_version? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Start deployment process
    local deployment_error=false
    
    # Update version if needed
    if [ "$target_version" != "$current_version" ]; then
        if ! update_version "$target_version"; then
            deployment_error=true
        fi
    fi
    
    # Update repository metadata
    if [ "$deployment_error" = false ]; then
        if ! update_repository_json "$target_version"; then
            deployment_error=true
        fi
    fi
    
    # Commit changes
    if [ "$deployment_error" = false ] && [ "$DRY_RUN" != "true" ]; then
        if [ "$target_version" != "$current_version" ]; then
            git add config.yaml build.yaml repository.json 2>/dev/null || git add config.yaml repository.json
            git commit -m "Bump version to $target_version

- Update version in configuration files
- Update repository metadata
- Prepare for release $target_version"
        fi
    fi
    
    # Create git tag
    if [ "$deployment_error" = false ]; then
        if ! create_git_tag "$target_version"; then
            deployment_error=true
        fi
    fi
    
    # Build and push Docker images
    if [ "$deployment_error" = false ] && [ "$skip_build" = false ]; then
        if ! build_and_push_images "$target_version"; then
            deployment_error=true
        fi
    fi
    
    # Push changes to remote
    if [ "$deployment_error" = false ]; then
        if ! push_changes "$target_version"; then
            deployment_error=true
        fi
    fi
    
    # Create GitHub release
    if [ "$deployment_error" = false ] && [ "$skip_release" = false ]; then
        if ! create_github_release "$target_version"; then
            deployment_error=true
        fi
    fi
    
    # Handle deployment result
    if [ "$deployment_error" = true ]; then
        log_error "Deployment failed!"
        if [ "$DRY_RUN" != "true" ]; then
            rollback_changes "$target_version"
        fi
        exit 1
    else
        echo
        echo "=============================================================================="
        echo "  Deployment Summary"
        echo "=============================================================================="
        echo "  Version: $target_version"
        echo "  Registry: $REGISTRY"
        echo "  Organization: $ORGANIZATION"
        echo "  Dry Run: $DRY_RUN"
        echo "  Git Tag: $TAG_PREFIX$target_version"
        
        if [ "$DRY_RUN" = "true" ]; then
            echo -e "  Status: ${YELLOW}DRY RUN COMPLETED${NC}"
        else
            echo -e "  Status: ${GREEN}DEPLOYMENT SUCCESSFUL${NC}"
            echo ""
            echo "🎉 Home Assistant Supervisor API Proxy $target_version has been deployed!"
            echo ""
            echo "Next steps:"
            echo "- Monitor the release for any issues"
            echo "- Update documentation if needed"
            echo "- Announce the release to the community"
        fi
        
        echo "=============================================================================="
    fi
}

# Handle signals
trap 'echo "Deployment interrupted"; exit 130' INT TERM

# Run main function
main "$@"