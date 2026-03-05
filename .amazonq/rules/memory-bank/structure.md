# Project Structure

## Directory Organization

```
AI_HealthCare_Final_Project_Template/
├── ai_worker/              # AI model inference and training worker service
│   ├── core/               # Worker configuration and logging
│   │   ├── config.py       # Environment-based settings (Pydantic Settings)
│   │   └── logger.py       # Structured logging configuration
│   ├── schemas/            # Data schemas for worker tasks
│   ├── tasks/              # Task definitions for model operations
│   ├── main.py             # Worker entry point and task orchestration
│   └── Dockerfile          # Container image for AI worker
│
├── app/                    # FastAPI application server
│   ├── apis/               # API route handlers
│   │   ├── v1/             # Version 1 API endpoints
│   │   │   ├── auth.py     # Authentication endpoints (login, register)
│   │   │   └── users.py    # User management endpoints
│   │   └── __init__.py     # Router aggregation
│   ├── core/               # Application configuration
│   │   ├── config.py       # Settings management (database, JWT, CORS)
│   │   └── logger.py       # Application logging setup
│   ├── db/                 # Database layer
│   │   ├── migrations/     # Aerich migration files
│   │   └── databases.py    # Tortoise ORM initialization and config
│   ├── dependencies/       # FastAPI dependency injection
│   │   └── security.py     # Authentication dependencies (JWT verification)
│   ├── dtos/               # Data Transfer Objects (Pydantic models)
│   │   ├── auth.py         # Login/register request/response schemas
│   │   ├── base.py         # Base response schemas
│   │   └── users.py        # User-related DTOs
│   ├── models/             # Database models (Tortoise ORM)
│   │   └── users.py        # User table definition
│   ├── repositories/       # Data access layer
│   │   └── user_repository.py  # User CRUD operations
│   ├── services/           # Business logic layer
│   │   ├── auth.py         # Authentication service
│   │   ├── jwt.py          # JWT token generation/validation
│   │   └── users.py        # User management service
│   ├── tests/              # Test suite
│   │   ├── auth_apis/      # Authentication endpoint tests
│   │   ├── user_apis/      # User endpoint tests
│   │   └── conftest.py     # Pytest fixtures and configuration
│   ├── utils/              # Utility functions
│   │   ├── jwt/            # JWT helper functions
│   │   ├── common.py       # Shared utilities
│   │   └── security.py     # Password hashing and verification
│   ├── validators/         # Input validation logic
│   │   ├── common.py       # Shared validators
│   │   └── user_validators.py  # User-specific validation rules
│   ├── main.py             # FastAPI application entry point
│   └── Dockerfile          # Container image for API server
│
├── envs/                   # Environment configuration files
│   ├── .local.env          # Local development environment variables
│   ├── .prod.env           # Production environment variables
│   ├── example.local.env   # Template for local configuration
│   └── example.prod.env    # Template for production configuration
│
├── nginx/                  # Nginx reverse proxy configuration
│   ├── default.conf        # Local development proxy rules
│   ├── prod_http.conf      # Production HTTP configuration
│   └── prod_https.conf     # Production HTTPS configuration (SSL)
│
├── scripts/                # Automation scripts
│   ├── ci/                 # Continuous integration scripts
│   │   ├── check_mypy.sh   # Static type checking
│   │   ├── code_fommatting.sh  # Code formatting with Ruff
│   │   └── run_test.sh     # Test execution with coverage
│   ├── certbot.sh          # SSL certificate automation (Let's Encrypt)
│   └── deployment.sh       # AWS EC2 deployment automation
│
├── .github/                # GitHub configuration
│   ├── workflows/          # GitHub Actions CI/CD
│   │   └── checks.yml      # Automated checks on PR/push
│   ├── commit_template.txt # Commit message template
│   └── PULL_REQUEST_TEMPLATE.md  # PR description template
│
├── docker-compose.yml      # Local development stack
├── docker-compose.prod.yml # Production deployment stack
├── pyproject.toml          # UV/Python project configuration
├── uv.lock                 # Locked dependency versions
└── README.md               # Project documentation
```

## Core Components

### 1. FastAPI Application (app/)
**Purpose**: HTTP API server handling client requests, authentication, and business logic

**Architecture Pattern**: Layered architecture with clear separation of concerns
- **APIs Layer**: Route handlers that receive HTTP requests and return responses
- **Services Layer**: Business logic implementation, orchestrates repositories and utilities
- **Repositories Layer**: Data access abstraction, encapsulates database operations
- **Models Layer**: Database schema definitions using Tortoise ORM
- **DTOs Layer**: Request/response validation and serialization using Pydantic

**Key Relationships**:
```
Client Request → API Router → Service → Repository → Database Model → MySQL
                      ↓
                Dependencies (JWT Auth, Validation)
```

### 2. AI Worker (ai_worker/)
**Purpose**: Isolated service for compute-intensive AI operations (training, inference)

**Architecture Pattern**: Task-based worker with message queue
- Receives tasks from Redis queue
- Processes model operations independently from API server
- Returns results via Redis or database updates

**Key Relationships**:
```
API Server → Redis Queue → AI Worker → Model Processing → Result Storage
```

### 3. Database Layer (app/db/)
**Purpose**: Database connection management and schema migrations

**Components**:
- **databases.py**: Tortoise ORM configuration, connection pooling, model registration
- **migrations/**: Version-controlled schema changes managed by Aerich

**Migration Workflow**:
```
Model Changes → aerich migrate → Migration File → aerich upgrade → Database Schema Update
```

### 4. Authentication System
**Purpose**: Secure user authentication and authorization

**Flow**:
```
1. Register: Client → /auth/register → Password Hash → User Creation → JWT Token
2. Login: Client → /auth/login → Password Verify → JWT Token Generation
3. Protected Route: Client + JWT → Dependency Injection → Token Validation → Route Handler
```

**Components**:
- **services/auth.py**: Registration and login logic
- **services/jwt.py**: Token generation and validation
- **dependencies/security.py**: FastAPI dependency for route protection
- **utils/security.py**: Password hashing (bcrypt)

### 5. Configuration Management
**Purpose**: Environment-specific settings using Pydantic Settings

**Pattern**:
```python
# app/core/config.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    # Settings loaded from environment variables or .env file
```

**Environment Files**:
- `.local.env`: Development (localhost, debug mode)
- `.prod.env`: Production (EC2, optimized settings)

## Architectural Patterns

### Repository Pattern
Abstracts database operations from business logic:
```
Service → Repository Interface → Concrete Repository → ORM → Database
```
Benefits: Testability, swappable data sources, clean separation

### Dependency Injection
FastAPI's DI system for cross-cutting concerns:
```python
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user automatically injected after JWT validation
```

### DTO Pattern
Separate internal models from API contracts:
- **DTOs (dtos/)**: API request/response schemas (Pydantic)
- **Models (models/)**: Database schemas (Tortoise ORM)
- Allows independent evolution of API and database schemas

### Microservices Architecture
Two independent services communicating via Redis:
- **API Server**: Stateless, horizontally scalable
- **AI Worker**: Stateful, resource-intensive, independently scalable

### Configuration as Code
All infrastructure defined in version-controlled files:
- `docker-compose.yml`: Service definitions
- `nginx/*.conf`: Reverse proxy rules
- `pyproject.toml`: Dependencies and tool configurations

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                         Client                               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Port 80/443)                       │
│                   Reverse Proxy + SSL                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server (Port 8000)                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐ │
│  │   APIs   │→ │ Services │→ │Repositories│→ │  Models  │ │
│  └──────────┘  └──────────┘  └────────────┘  └──────────┘ │
│       ↓              ↓                              ↓        │
│  Dependencies   Business Logic              Database ORM    │
└────────┬────────────┬────────────────────────────┬─────────┘
         │            │                             │
         │            ↓                             ↓
         │    ┌──────────────┐          ┌──────────────────┐
         │    │     Redis    │          │   MySQL (3306)   │
         │    │   (6379)     │          │   User Data      │
         │    └──────┬───────┘          └──────────────────┘
         │           │
         │           │ Task Queue
         │           ↓
         │    ┌──────────────────────────────────────────┐
         │    │         AI Worker Service                │
         │    │  ┌────────┐  ┌────────┐  ┌───────────┐  │
         │    │  │ Tasks  │→ │ Models │→ │ Inference │  │
         │    │  └────────┘  └────────┘  └───────────┘  │
         │    └──────────────────────────────────────────┘
         │
         └─→ JWT Validation, Password Hashing, Utilities
```

## Deployment Architecture

### Local Development
```
docker-compose up → Starts all services (MySQL, Redis, FastAPI, AI Worker, Nginx)
                  → Volume mounts for hot-reload
                  → Exposed ports for debugging
```

### Production (AWS EC2)
```
1. Build: docker build → Tagged images
2. Push: Docker Hub repository
3. Deploy: SSH to EC2 → docker pull → docker-compose up
4. SSL: Certbot → Let's Encrypt → Nginx HTTPS config
```

## Extension Points

### Adding New API Endpoints
1. Create router in `app/apis/v1/new_feature.py`
2. Define DTOs in `app/dtos/new_feature.py`
3. Implement service in `app/services/new_feature.py`
4. Add repository if needed in `app/repositories/`
5. Register router in `app/apis/v1/__init__.py`

### Adding Database Models
1. Define model in `app/models/new_model.py`
2. Add to `MODELS` list in `app/db/databases.py`
3. Run `aerich migrate` to generate migration
4. Run `aerich upgrade` to apply changes

### Adding AI Tasks
1. Define task in `ai_worker/tasks/new_task.py`
2. Add schema in `ai_worker/schemas/`
3. Register task in `ai_worker/main.py`
4. Trigger from API via Redis queue
