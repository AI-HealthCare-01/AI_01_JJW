# Technology Stack

## Programming Languages

### Python 3.13+
- **Primary Language**: All application and worker code
- **Type Hints**: Full type annotation support for static analysis
- **Async/Await**: Native async support for FastAPI and Tortoise ORM

## Core Frameworks & Libraries

### Web Framework
- **FastAPI 0.128.0+**: Modern async web framework
  - Automatic OpenAPI/Swagger documentation
  - Pydantic integration for validation
  - Dependency injection system
  - High performance (Starlette + Uvicorn)

### ORM & Database
- **Tortoise ORM 0.25.3+**: Async ORM inspired by Django ORM
  - Async query execution
  - Model relationships (ForeignKey, ManyToMany)
  - Query builder with type safety
- **Aerich 0.9.2+**: Database migration tool for Tortoise ORM
- **asyncmy 0.2.11+**: Async MySQL driver

### AI/ML Libraries
- **PyTorch**: Deep learning framework (CPU-optimized via custom index)
  - torchvision: Computer vision models and transforms
  - torchaudio: Audio processing
- **scikit-learn 1.8.0+**: Traditional ML algorithms
- **sentence-transformers 5.2.0+**: Transformer-based embeddings

### Authentication & Security
- **PyJWT 2.10.1+**: JSON Web Token implementation
- **passlib[bcrypt] 1.7.4+**: Password hashing library
- **bcrypt <=4.0.1**: Bcrypt algorithm for password hashing
- **cryptography 46.0.3+**: Cryptographic primitives

### Data Validation & Serialization
- **Pydantic 2.12.5+**: Data validation using Python type hints
- **pydantic-settings 2.12.0+**: Settings management from environment
- **orjson 3.11.5+**: Fast JSON serialization (used as default response)

### Caching & Message Queue
- **Redis 7.1.0+**: In-memory data store
  - Caching layer
  - Task queue for AI worker
  - Session storage

### HTTP Client
- **httpx 0.28.1+**: Async HTTP client for external API calls

### Utilities
- **python-dateutil 2.9.0+**: Date/time parsing and manipulation
- **tomlkit 0.14.0+**: TOML file parsing

## Development Tools

### Package Management
- **UV**: Ultra-fast Python package installer and resolver
  - Replaces pip, pip-tools, virtualenv
  - Rust-based for performance
  - Lock file support (uv.lock)

### Code Quality
- **Ruff 0.14.14+**: Extremely fast Python linter and formatter
  - Replaces: Flake8, isort, Black, pyupgrade
  - Rules: pycodestyle (E/W), pyflakes (F), isort (I), mccabe (C90), flake8-bugbear (B), pyupgrade (UP), pep8-naming (N)
  - Line length: 120 characters
  - Auto-formatting with consistent style

### Type Checking
- **Mypy 1.19.1+**: Static type checker
  - Enforces type hints
  - Catches type errors before runtime
- **Type Stubs**:
  - types-passlib 1.7.7+
  - types-python-dateutil 2.9.0+

### Testing
- **Pytest**: Testing framework
- **pytest-asyncio 1.3.0+**: Async test support
  - asyncio_mode = "auto"
  - Session-scoped event loop
- **Coverage 7.13.2+**: Code coverage measurement

## Infrastructure & Deployment

### Containerization
- **Docker**: Container runtime
  - Multi-stage builds for optimization
  - Platform support: linux/amd64, linux/arm64
- **Docker Compose**: Multi-container orchestration
  - Local development stack
  - Production deployment configuration

### Web Server
- **Nginx**: Reverse proxy and web server
  - SSL/TLS termination
  - Static file serving
  - Load balancing ready
- **Uvicorn 0.40.0+**: ASGI server for FastAPI
  - Hot reload in development
  - Production-ready performance

### Database
- **MySQL 8.0**: Relational database
  - UTF-8 (utf8mb4) character set
  - Persistent volumes
  - Health checks

### SSL/TLS
- **Certbot**: Let's Encrypt certificate automation
  - Automatic renewal
  - Nginx integration

## Development Commands

### Environment Setup
```bash
# Install dependencies (creates virtual environment automatically)
uv sync

# Install only API server dependencies
uv sync --group app

# Install only AI worker dependencies
uv sync --group ai

# Install development tools
uv sync --group dev

# Install all dependency groups
uv sync --all-groups
```

### Running Services Locally

#### Using UV (Development)
```bash
# Run FastAPI server with hot reload
uv run uvicorn app.main:app --reload

# Run FastAPI on custom host/port
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run AI worker
uv run python -m ai_worker.main
```

#### Using Docker Compose
```bash
# Start all services (MySQL, Redis, FastAPI, AI Worker, Nginx)
docker-compose up -d --build

# Start specific service
docker compose up -d --build fastapi
docker compose up -d --build ai-worker

# View logs
docker-compose logs -f fastapi
docker-compose logs -f ai-worker

# Stop all services
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

### Database Management

#### Migrations with Aerich
```bash
# Initialize Aerich (first time only)
uv run aerich init -t app.db.databases.TORTOISE_ORM

# Initialize database
uv run aerich init-db

# Create migration after model changes
uv run aerich migrate --name "description_of_changes"

# Apply migrations
uv run aerich upgrade

# Rollback last migration
uv run aerich downgrade

# Show migration history
uv run aerich history
```

### Code Quality & Testing

#### Formatting
```bash
# Check code formatting
./scripts/ci/code_fommatting.sh

# Or manually with Ruff
uv run ruff check .
uv run ruff format .

# Auto-fix issues
uv run ruff check --fix .
```

#### Type Checking
```bash
# Run Mypy type checker
./scripts/ci/check_mypy.sh

# Or manually
uv run mypy app/ ai_worker/
```

#### Testing
```bash
# Run all tests with coverage
./scripts/ci/run_test.sh

# Or manually with pytest
uv run pytest

# Run specific test file
uv run pytest app/tests/auth_apis/test_login.py

# Run with coverage report
uv run pytest --cov=app --cov-report=html

# Run async tests
uv run pytest -v --asyncio-mode=auto
```

### Deployment

#### Build and Push Docker Images
```bash
# Build API server image
docker build -f app/Dockerfile -t username/repo:app-v1.0.0 .

# Build AI worker image
docker build -f ai_worker/Dockerfile -t username/repo:ai-v1.0.0 .

# Push to Docker Hub
docker push username/repo:app-v1.0.0
docker push username/repo:ai-v1.0.0
```

#### Automated Deployment to EC2
```bash
# Make script executable
chmod +x scripts/deployment.sh

# Run deployment script (interactive)
./scripts/deployment.sh
# Prompts for:
# - Docker Hub credentials
# - Repository name
# - Service selection (FastAPI/AI-Worker)
# - Version tag
# - SSH key filename
# - EC2 IP address
# - HTTPS configuration
```

#### SSL Certificate Setup
```bash
# Make script executable
chmod +x scripts/certbot.sh

# Run Certbot automation
./scripts/certbot.sh
# Prompts for:
# - Domain name
# - Email address
# - SSH key filename
# - EC2 IP address
```

### Environment Configuration

#### Local Development
```bash
# Copy example environment file
cp envs/example.local.env envs/.local.env

# Edit environment variables
# Set: DB_HOST=localhost, DEBUG=true, etc.

# Create symlink for Docker Compose
ln -s envs/.local.env .env
```

#### Production
```bash
# Copy example environment file
cp envs/example.prod.env envs/.prod.env

# Edit environment variables
# Set: DB_HOST=mysql, DEBUG=false, JWT secrets, etc.

# Create symlink for Docker Compose
ln -s envs/.prod.env .env
```

## Configuration Files

### pyproject.toml
- Project metadata and dependencies
- Dependency groups: app, ai, dev
- Tool configurations: Ruff, Pytest, Aerich, Mypy
- Custom PyTorch index for CPU-only builds

### docker-compose.yml
- Service definitions (MySQL, Redis, FastAPI, AI Worker, Nginx)
- Network configuration (bridge network: ws)
- Volume mounts for persistence
- Health checks for service dependencies
- Environment variable injection

### Ruff Configuration
```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "C90", "B", "UP", "N"]
ignore = ["UP046", "E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports
"db/migrations/*" = ["ALL"]  # Skip migration files
```

### Pytest Configuration
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
```

## API Documentation

### Swagger UI
- URL: `http://localhost/api/docs` (local) or `https://yourdomain.com/api/docs` (production)
- Interactive API testing
- Request/response schemas
- Authentication testing

### ReDoc
- URL: `http://localhost/api/redoc`
- Alternative documentation view
- Better for reading/printing

### OpenAPI JSON
- URL: `http://localhost/api/openapi.json`
- Machine-readable API specification
- For code generation tools

## Performance Optimization

### FastAPI
- ORJSON for faster JSON serialization
- Async endpoints for I/O-bound operations
- Connection pooling for database
- Redis caching for frequently accessed data

### Docker
- Multi-stage builds to reduce image size
- .dockerignore to exclude unnecessary files
- Health checks for graceful startup
- Resource limits (memory: 4GB for AI worker)

### Database
- Indexed columns for fast queries
- Connection pooling via Tortoise ORM
- Async queries to prevent blocking

## Monitoring & Logging

### Application Logging
- Structured logging via `app/core/logger.py` and `ai_worker/core/logger.py`
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- JSON-formatted logs for production parsing

### Container Logs
```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f fastapi
docker-compose logs -f ai-worker

# View last N lines
docker-compose logs --tail=100 fastapi
```

### Health Checks
- MySQL: `mysqladmin ping`
- Redis: `redis-cli ping`
- FastAPI: Depends on MySQL and Redis health
- Nginx: Depends on FastAPI availability
