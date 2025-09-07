# CI/CD Guide

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Food Receipt Analyzer project.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and includes:

- **Code Quality Checks**: Automated linting, formatting, and security scanning
- **Testing**: Unit tests, integration tests, and coverage reporting
- **Docker Build**: Multi-platform container image building and publishing
- **Security Scanning**: Vulnerability scanning for both code and container images
- **Deployment Verification**: Automated testing of deployed containers
- **Release Management**: Automated versioning and release creation

## Workflows

### 1. Code Quality (`code-quality.yml`)

**Triggers**: Pull requests and pushes to `main`/`develop` branches

**Checks**:
- Code formatting with Black
- Import sorting with isort
- Linting with flake8
- Security scanning with bandit
- Dependency vulnerability scanning with safety

### 2. Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers**: Pull requests and pushes to `main`/`develop` branches

**Stages**:
1. **Test Stage**: Runs all tests with coverage reporting
2. **Build and Push Stage**: Builds and publishes Docker images (main branch only)
3. **Deploy Verification Stage**: Tests the built container

### 3. Docker Build (`docker-build.yml`)

**Triggers**: Pushes to `main`/`develop`, tags, and pull requests

**Features**:
- Multi-platform builds (linux/amd64, linux/arm64)
- Automated tagging strategy
- Security scanning with Trivy and Grype
- SBOM (Software Bill of Materials) generation
- Container testing and verification

### 4. Release Management (`release.yml`)

**Triggers**: Manual workflow dispatch

**Features**:
- Automated version bumping (patch/minor/major)
- Changelog generation
- GitHub release creation
- Docker image tagging for releases

## Container Registry

Images are published to GitHub Container Registry (ghcr.io):

```bash
# Latest development image
docker pull ghcr.io/your-org/food-receipt-analyzer:latest

# Specific version
docker pull ghcr.io/your-org/food-receipt-analyzer:v1.0.0

# Branch-specific image
docker pull ghcr.io/your-org/food-receipt-analyzer:develop
```

## Tagging Strategy

### Automatic Tags

- `latest`: Latest build from main branch
- `develop`: Latest build from develop branch
- `main-<sha>-<timestamp>`: SHA-based tags for main branch
- `pr-<number>`: Pull request builds

### Release Tags

- `v1.2.3`: Exact version tag
- `1.2`: Minor version tag
- `1`: Major version tag
- `stable`: Latest stable release

## Local Development

### Pre-commit Testing

Run the local CI test script before pushing:

```bash
python scripts/local_ci_test.py
```

This script runs the same checks as the CI pipeline locally.

### Code Quality Setup

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run individual checks:

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code
flake8 .

# Security scan
bandit -r .
safety check

# Run tests
pytest --cov=.
```

### Docker Testing

Build and test locally:

```bash
# Build image
docker build -t food-receipt-analyzer:local .

# Run container
docker run -p 8501:8501 -e OPENROUTER_API_KEY=your_key food-receipt-analyzer:local

# Verify deployment
python scripts/verify_deployment.py --url http://localhost:8501
```

## Configuration Files

### Code Quality Configuration

- `.flake8`: Flake8 linting configuration
- `pyproject.toml`: Black, isort, pytest, and coverage configuration
- `.bandit`: Bandit security scanner configuration

### Version Management

- `VERSION`: Current version number
- `.bumpversion.cfg`: Version bumping configuration

### Docker Configuration

- `Dockerfile`: Multi-stage production build
- `.dockerignore`: Files excluded from Docker context

## Security Features

### Code Security

- **Bandit**: Scans for common security issues in Python code
- **Safety**: Checks for known vulnerabilities in dependencies
- **Dependency Pinning**: All dependencies are pinned to specific versions

### Container Security

- **Trivy**: Vulnerability scanner for container images
- **Grype**: Additional vulnerability scanning
- **SBOM Generation**: Software Bill of Materials for transparency
- **Non-root User**: Containers run as non-root user
- **Minimal Base Image**: Uses Python slim image to reduce attack surface

### Secrets Management

- API keys and secrets are managed through GitHub Secrets
- No secrets are hardcoded in the codebase
- Environment variables are used for configuration

## Monitoring and Alerts

### Build Status

- GitHub Actions provide build status badges
- Failed builds trigger notifications
- Pull request checks prevent merging broken code

### Security Alerts

- Dependabot monitors for dependency vulnerabilities
- Security scanning results are uploaded to GitHub Security tab
- SARIF reports provide detailed vulnerability information

## Deployment Verification

The pipeline includes automated deployment verification:

1. **Health Check**: Verifies Streamlit health endpoint
2. **Main Page Test**: Ensures the application loads correctly
3. **Static Resources**: Checks if CSS/JS resources are accessible
4. **Container Startup**: Validates proper container initialization

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check the GitHub Actions logs
   - Run `python scripts/local_ci_test.py` locally
   - Ensure all dependencies are properly specified

2. **Docker Build Issues**
   - Verify Dockerfile syntax
   - Check if all required files are included (not in .dockerignore)
   - Test build locally: `docker build -t test .`

3. **Test Failures**
   - Run tests locally: `pytest -v`
   - Check test coverage: `pytest --cov=.`
   - Ensure test data and fixtures are available

4. **Security Scan Failures**
   - Review security scan reports in GitHub Security tab
   - Update vulnerable dependencies
   - Fix code issues identified by bandit

### Getting Help

1. Check the GitHub Actions logs for detailed error messages
2. Review the configuration files for syntax errors
3. Test changes locally before pushing
4. Consult the project documentation and requirements

## Best Practices

### Development Workflow

1. Create feature branches from `develop`
2. Run local CI tests before pushing
3. Create pull requests to `develop` branch
4. Ensure all CI checks pass before merging
5. Use `main` branch for production releases

### Code Quality

1. Follow PEP 8 style guidelines
2. Write comprehensive tests for new features
3. Keep dependencies up to date
4. Document significant changes
5. Use meaningful commit messages

### Security

1. Never commit secrets or API keys
2. Regularly update dependencies
3. Review security scan results
4. Use environment variables for configuration
5. Follow principle of least privilege

## Release Process

### Creating a Release

1. Ensure all changes are merged to `main`
2. Go to GitHub Actions → Release Management
3. Click "Run workflow"
4. Select version bump type (patch/minor/major)
5. The workflow will:
   - Bump version numbers
   - Create git tag
   - Build and tag Docker images
   - Create GitHub release with changelog

### Hotfix Process

1. Create hotfix branch from `main`
2. Make necessary changes
3. Create pull request to `main`
4. After merge, create patch release
5. Cherry-pick changes to `develop` if needed