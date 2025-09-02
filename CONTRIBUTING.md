# Contributing to Home Assistant Supervisor API Proxy

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10+ installed
- Docker and Docker Compose
- Git for version control
- A GitHub account
- Basic knowledge of Flask, REST APIs, and Home Assistant

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Bug fixes, new features, improvements
- **Documentation**: API docs, guides, examples
- **Testing**: Add or improve test coverage
- **Security**: Report security vulnerabilities responsibly

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/ha-supervisor-proxy.git
cd ha-supervisor-proxy

# Add upstream remote
git remote add upstream https://github.com/original/ha-supervisor-proxy.git
```

### 2. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt

# Install development dependencies
pip install black isort flake8 bandit pytest coverage
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
export SUPERVISOR_TOKEN="your_test_token"
export SUPERVISOR_URL="http://localhost:8080"  # For testing
export LOG_LEVEL="debug"
```

### 4. Verify Setup

```bash
# Run tests to verify setup
./scripts/run_tests.sh --all

# Start the application
python app.py
```

## Making Changes

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Development Workflow

1. **Write Tests First** (TDD approach recommended)
2. **Implement Changes**
3. **Update Documentation**
4. **Test Thoroughly**
5. **Commit Changes**

### 3. Commit Guidelines

We use [Conventional Commits](https://conventionalcommits.org/):

```bash
# Format
type(scope): description

# Examples
feat(api): add backup restore endpoint
fix(auth): handle invalid token gracefully
docs(android): update integration guide
test(api): add unit tests for health endpoint
refactor(proxy): improve error handling
```

**Types:**
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation updates
- `test` - Adding or updating tests
- `refactor` - Code refactoring
- `perf` - Performance improvements
- `ci` - CI/CD changes
- `build` - Build system changes

## Testing

### Running Tests

```bash
# Run all tests
./scripts/run_tests.sh

# Run specific test types
./scripts/run_tests.sh --unit          # Unit tests only
./scripts/run_tests.sh --integration   # Integration tests
./scripts/run_tests.sh --api          # API tests
./scripts/run_tests.sh --coverage     # With coverage

# Run single test file
python -m pytest tests/test_app.py -v
```

### Writing Tests

#### Unit Tests

```python
# tests/test_feature.py
import pytest
from app import app

class TestNewFeature:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_new_feature(self, client):
        response = client.get('/api/v1/new-feature')
        assert response.status_code == 200
        data = response.get_json()
        assert 'expected_field' in data
```

#### Integration Tests

```python
# tests/test_integration_feature.py
import pytest
import requests

class TestFeatureIntegration:
    def test_feature_with_mock_supervisor(self, mock_supervisor, proxy_server):
        response = requests.get('http://localhost:8099/api/v1/new-feature')
        assert response.status_code == 200
```

### Test Requirements

- **Coverage**: Maintain >85% code coverage
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test full request/response cycles  
- **API Tests**: Test actual HTTP endpoints
- **Error Cases**: Test error handling and edge cases

## Code Style

### Python Code Style

We use automated formatting and linting:

```bash
# Format code
black app.py tests/

# Sort imports
isort app.py tests/

# Check linting
flake8 app.py --max-line-length=100 --ignore=E203,W503

# Security check
bandit -r app.py
```

### Code Style Guidelines

- **Line Length**: Maximum 100 characters
- **Imports**: Organized with isort
- **Formatting**: Consistent with Black
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use where beneficial
- **Comments**: Clear and concise

### Example Code Style

```python
def process_addon_request(slug: str, action: str) -> Dict[str, Any]:
    """Process add-on management requests.
    
    Args:
        slug: The add-on slug identifier
        action: The action to perform (start, stop, etc.)
        
    Returns:
        Dict containing the operation result
        
    Raises:
        ProxyError: If the operation fails
    """
    if not slug or not action:
        raise ProxyError("Invalid parameters", 400)
    
    try:
        response, status = make_supervisor_request(
            "POST", f"/addons/{slug}/{action}"
        )
        return response.json(), status
    except Exception as e:
        logger.error(f"Add-on {action} failed for {slug}: {str(e)}")
        raise ProxyError(f"Operation failed: {str(e)}", 500)
```

## Submitting Changes

### 1. Pre-submission Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for significant changes)
- [ ] Commit messages follow conventional format
- [ ] No sensitive information in commits

### 2. Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### 3. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)

## Related Issues
Fixes #123
```

### 4. Code Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Peer Review**: At least one maintainer reviews changes
3. **Feedback**: Address review comments promptly
4. **Approval**: Changes approved by maintainer
5. **Merge**: Maintainer merges the pull request

## Architecture Guidelines

### Project Structure

```
ha-supervisor-proxy/
├── app.py                 # Main Flask application
├── config.yaml           # Add-on configuration
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── run.sh                # Startup script
├── tests/                # Test suite
├── scripts/              # Build and deployment scripts
├── docs/                 # Documentation
├── android-client/       # Android integration code
└── .github/              # GitHub workflows
```

### Adding New Endpoints

1. **Define Route**: Add Flask route decorator
2. **Implement Function**: Create endpoint function
3. **Add Proxy Decorator**: Use `@proxy_request` decorator
4. **Error Handling**: Implement proper error handling
5. **Add Tests**: Unit and integration tests
6. **Update Documentation**: API reference and examples

Example:

```python
@app.route('/api/v1/new-feature/<param>', methods=['GET', 'POST'])
@proxy_request('/supervisor/new-feature/{param}')
def new_feature(param):
    """New feature endpoint."""
    pass
```

### Security Considerations

- **Input Validation**: Validate all inputs
- **Authentication**: Verify Supervisor token
- **Authorization**: Check permissions
- **Error Handling**: Don't leak sensitive information
- **Logging**: Log security-relevant events

## Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. **Prepare Release**: Update version, changelog
2. **Create Tag**: `git tag v1.2.3`
3. **Push Tag**: Triggers automated release
4. **GitHub Release**: Automatically created
5. **Docker Images**: Multi-architecture builds
6. **Announcement**: Community notification

### Pre-release Testing

Before major releases:

- [ ] Full test suite passes
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Migration guide updated

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code review and collaboration
- **Security**: Private reporting for security issues

### Getting Help

- **Documentation**: Check existing documentation first
- **Search Issues**: Look for similar problems
- **Ask Questions**: Use GitHub Discussions
- **Join Community**: Home Assistant Discord/Forum

### Recognition

Contributors are recognized through:

- **Git History**: All contributions are tracked
- **Release Notes**: Contributors mentioned in releases  
- **Documentation**: Contributors page (if requested)
- **GitHub**: Profile contributions visible

## Development Tips

### Local Testing

```bash
# Start mock supervisor for testing
python tests/mock_supervisor.py &

# Start proxy in development mode
export SUPERVISOR_URL=http://localhost:8080
export SUPERVISOR_TOKEN=test-token
python app.py

# Test with curl
curl -H "Authorization: Bearer test-token" \
     http://localhost:8099/api/v1/health
```

### Debugging

```bash
# Enable debug logging
export LOG_LEVEL=debug

# Use Python debugger
import pdb; pdb.set_trace()

# Check proxy logs
tail -f /path/to/logs
```

### Performance Testing

```bash
# Simple load test
ab -n 100 -c 10 http://localhost:8099/api/v1/health

# Monitor resource usage
docker stats ha-supervisor-proxy
```

## FAQ

**Q: How do I test Android integration locally?**
A: Use the Android emulator with network bridge to connect to your development proxy.

**Q: Can I add support for new Supervisor API endpoints?**
A: Yes! Add the endpoint following the proxy pattern and include tests.

**Q: How do I handle breaking changes in the Supervisor API?**
A: Version the proxy API and maintain backward compatibility when possible.

**Q: What's the review process timeline?**
A: Most reviews are completed within 48-72 hours. Complex changes may take longer.

---

Thank you for contributing to the Home Assistant Supervisor API Proxy! Your contributions help make Home Assistant more accessible and powerful for everyone.