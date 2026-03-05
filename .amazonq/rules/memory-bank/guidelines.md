# Development Guidelines

## Code Quality Standards

### File Organization
- **Empty __init__.py files**: Package initialization files are kept empty to serve purely as package markers
- **Flat imports**: Import statements are organized at the top of files without nested grouping
- **Absolute imports**: Always use absolute imports from project root (e.g., `from app.services.auth import AuthService`)

### Code Formatting (Ruff)
- **Line length**: Maximum 120 characters
- **Quote style**: Double quotes for strings
- **Indentation**: 4 spaces (no tabs)
- **Import sorting**: Automatic with isort rules (stdlib → third-party → local)
- **Trailing commas**: Preserved for multi-line structures

### Naming Conventions
- **Files**: Snake_case with descriptive suffixes
  - Routers: `*_routers.py` (e.g., `auth_routers.py`, `user_routers.py`)
  - Services: `*.py` in services/ (e.g., `auth.py`, `users.py`)
  - Repositories: `*_repository.py` (e.g., `user_repository.py`)
  - Models: Plural nouns (e.g., `users.py`)
  - DTOs: Singular domain (e.g., `auth.py`, `users.py`)
  
- **Classes**: PascalCase with descriptive suffixes
  - Services: `*Service` (e.g., `AuthService`, `UserManageService`)
  - Repositories: `*Repository` (e.g., `UserRepository`)
  - DTOs: `*Request`, `*Response` (e.g., `SignUpRequest`, `LoginResponse`)
  - Models: Singular nouns (e.g., `User`)
  
- **Functions/Methods**: Snake_case, verb-first for actions
  - API handlers: Match HTTP method + resource (e.g., `signup`, `login`, `user_me_info`)
  - Service methods: Action verbs (e.g., `authenticate`, `check_email_exists`)
  - Repository methods: CRUD verbs (e.g., `get_user`, `create_user`, `exists_by_email`)
  
- **Variables**: Snake_case, descriptive names
  - Constants: UPPER_SNAKE_CASE (e.g., `ALLOWED_UPDATE_FIELDS`, `TORTOISE_APP_MODELS`)
  - Private attributes: Prefix with underscore (e.g., `self._model`)

### Type Annotations
- **Comprehensive typing**: All function parameters and return types must have type hints
- **Union types**: Use modern syntax `str | None` instead of `Optional[str]`
- **Annotated types**: Use `Annotated` for validation metadata
  ```python
  from typing import Annotated
  from pydantic import Field, AfterValidator
  
  password: Annotated[str, Field(min_length=8), AfterValidator(validate_password)]
  ```
- **Generic types**: Specify container types (e.g., `dict[str, Any]`, `list[User]`)

### Documentation
- **Minimal comments**: Code should be self-documenting through clear naming
- **Korean error messages**: User-facing messages in Korean for localization
  ```python
  raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일입니다.")
  ```
- **No docstrings**: Functions and classes do not use docstrings; rely on type hints and clear names

## Architectural Patterns

### Layered Architecture
Strict separation of concerns across layers:

```
API Layer (apis/) → Service Layer (services/) → Repository Layer (repositories/) → Model Layer (models/)
```

**Rules**:
- API handlers only call services, never repositories or models directly
- Services orchestrate business logic, call repositories for data access
- Repositories encapsulate all database operations
- Models define database schema only, no business logic

**Example**:
```python
# API Layer - auth_routers.py
@auth_router.post("/signup")
async def signup(
    request: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Response:
    await auth_service.signup(request)
    return Response(content={"detail": "회원가입이 성공적으로 완료되었습니다."})

# Service Layer - auth.py
class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
    
    async def signup(self, data: SignUpRequest) -> User:
        await self.check_email_exists(data.email)
        async with in_transaction():
            user = await self.user_repo.create_user(...)
        return user

# Repository Layer - user_repository.py
class UserRepository:
    def __init__(self):
        self._model = User
    
    async def create_user(self, email: str, ...) -> User:
        return await self._model.create(email=email, ...)
```

### Dependency Injection Pattern
FastAPI's DI system for all cross-cutting concerns:

**Service Injection**:
```python
from typing import Annotated
from fastapi import Depends

async def endpoint(
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    # Service automatically instantiated
```

**Authentication Dependency**:
```python
from app.dependencies.security import get_request_user

async def protected_endpoint(
    user: Annotated[User, Depends(get_request_user)],
):
    # User extracted from JWT token automatically
```

**Cookie Extraction**:
```python
from fastapi import Cookie

async def token_refresh(
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    # Cookie value automatically extracted
```

### Repository Pattern
All database access through repository classes:

**Structure**:
```python
class UserRepository:
    def __init__(self):
        self._model = User  # Private model reference
    
    # Query methods
    async def get_user(self, user_id: int) -> User | None:
        return await self._model.get_or_none(id=user_id)
    
    # Existence checks
    async def exists_by_email(self, email: str) -> bool:
        return await self._model.filter(email=email).exists()
    
    # Create operations
    async def create_user(self, ...) -> User:
        return await self._model.create(...)
    
    # Update operations
    async def update_instance(self, user: User, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if value is not None:
                setattr(user, key, value)
        await user.save(update_fields=update_fields)
```

**Naming conventions**:
- `get_*`: Retrieve single entity (returns `Model | None`)
- `get_all`: Retrieve all entities
- `exists_by_*`: Boolean existence checks
- `create_*`: Create new entity
- `update_*`: Modify existing entity

### DTO Pattern
Separate API contracts from database models:

**Request DTOs**:
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Annotated

class SignUpRequest(BaseModel):
    email: Annotated[EmailStr, Field(None, max_length=40)]
    password: Annotated[str, Field(min_length=8), AfterValidator(validate_password)]
    name: Annotated[str, Field(max_length=20)]
```

**Response DTOs**:
```python
class LoginResponse(BaseModel):
    access_token: str

class TokenRefreshResponse(LoginResponse): ...  # Inheritance for identical schemas
```

**Validation**:
- Use `Annotated` with `Field` for constraints
- Use `AfterValidator` for custom validation logic
- Validators defined in `app/validators/`

### Service Layer Patterns

**Service initialization**:
```python
class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.jwt_service = JwtService()
```

**Business logic methods**:
```python
async def signup(self, data: SignUpRequest) -> User:
    # 1. Validation
    await self.check_email_exists(data.email)
    
    # 2. Data transformation
    normalized_phone = normalize_phone_number(data.phone_number)
    
    # 3. Transaction management
    async with in_transaction():
        user = await self.user_repo.create_user(...)
    
    return user
```

**Validation methods**:
```python
async def check_email_exists(self, email: str | EmailStr) -> None:
    if await self.user_repo.exists_by_email(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일입니다.")
```

### Configuration Management

**Settings class**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
    
    ENV: Env = Env.LOCAL
    SECRET_KEY: str = f"default-secret-key{uuid.uuid4().hex}"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
```

**Usage**:
```python
from app.core import config

# Access settings
database_url = f"{config.DB_HOST}:{config.DB_PORT}"
```

**Environment-specific logic**:
```python
from app.core.config import Env

secure = True if config.ENV == Env.PROD else False
```

## API Development Patterns

### Router Definition
```python
from fastapi import APIRouter, status

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(...) -> Response:
    ...
```

**Conventions**:
- Router variable: `{domain}_router` (e.g., `auth_router`, `user_router`)
- Prefix: `/domain` (e.g., `/auth`, `/users`)
- Tags: Match domain for OpenAPI grouping
- Explicit status codes for non-200 responses

### Response Handling

**JSON responses**:
```python
from fastapi.responses import ORJSONResponse as Response

return Response(content={"detail": "메시지"}, status_code=status.HTTP_201_CREATED)
```

**Model validation responses**:
```python
@user_router.get("/me", response_model=UserInfoResponse)
async def user_me_info(user: User) -> Response:
    return Response(UserInfoResponse.model_validate(user).model_dump())
```

**Cookie setting**:
```python
resp = Response(content=LoginResponse(...).model_dump())
resp.set_cookie(
    key="refresh_token",
    value=str(token),
    httponly=True,
    secure=True if config.ENV == Env.PROD else False,
    domain=config.COOKIE_DOMAIN or None,
    expires=expiration_time,
)
return resp
```

### Error Handling

**HTTPException pattern**:
```python
from fastapi import HTTPException, status

# Not found
if not user:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="이메일 또는 비밀번호가 올바르지 않습니다."
    )

# Conflict
if await self.user_repo.exists_by_email(email):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="이미 사용중인 이메일입니다."
    )

# Unauthorized
if not refresh_token:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token is missing."
    )

# Locked
if not user.is_active:
    raise HTTPException(
        status_code=status.HTTP_423_LOCKED,
        detail="비활성화된 계정입니다."
    )
```

**Status code usage**:
- `200 OK`: Successful GET/PATCH
- `201 CREATED`: Successful POST (creation)
- `400 BAD_REQUEST`: Invalid credentials or input
- `401 UNAUTHORIZED`: Missing or invalid authentication
- `409 CONFLICT`: Resource already exists
- `423 LOCKED`: Account disabled

## Database Patterns

### Model Definition
```python
from tortoise import fields, models
from enum import StrEnum

class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class User(models.Model):
    id = fields.BigIntField(primary_key=True)
    email = fields.CharField(max_length=40)
    hashed_password = fields.CharField(max_length=128)
    gender = fields.CharEnumField(enum_type=Gender)
    birthday = fields.DateField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "users"
```

**Field conventions**:
- Primary key: `id = fields.BigIntField(primary_key=True)`
- Enums: Use `StrEnum` with `CharEnumField`
- Timestamps: `auto_now_add=True` for creation, `auto_now=True` for updates
- Booleans: Provide defaults (e.g., `default=True`)
- Nullable: Explicit `null=True` when needed

### Transaction Management
```python
from tortoise.transactions import in_transaction

async with in_transaction():
    user = await self.user_repo.create_user(...)
    # Multiple operations in same transaction
```

### Query Patterns
```python
# Get or None
user = await self._model.get_or_none(id=user_id)

# Existence check
exists = await self._model.filter(email=email).exists()

# Create
user = await self._model.create(email=email, ...)

# Update with specific fields
await self._model.filter(id=user_id).update(last_login=datetime.now())

# Update instance
setattr(user, key, value)
await user.save(update_fields=update_fields)
```

### Database Initialization
```python
from tortoise.contrib.fastapi import register_tortoise

TORTOISE_APP_MODELS = [
    "aerich.models",
    "app.models.users",
]

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "dialect": "asyncmy",
            "credentials": {...},
        },
    },
    "apps": {
        "models": {
            "models": TORTOISE_APP_MODELS,
        },
    },
}

def initialize_tortoise(app: FastAPI) -> None:
    Tortoise.init_models(TORTOISE_APP_MODELS, "models")
    register_tortoise(app, config=TORTOISE_ORM)
```

## Security Patterns

### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Usage**:
```python
# On signup
hashed_password = hash_password(data.password)
user = await self.user_repo.create_user(..., hashed_password=hashed_password)

# On login
if not verify_password(data.password, user.hashed_password):
    raise HTTPException(...)
```

### JWT Authentication
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_request_user(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    token = credential.credentials
    verified = JwtService().verify_jwt(token=token, token_type="access")
    user_id = verified.payload["user_id"]
    user = await UserRepository().get_user(user_id)
    if not user:
        raise HTTPException(detail="Authenticate Failed.", status_code=status.HTTP_401_UNAUTHORIZED)
    return user
```

**Protected routes**:
```python
@user_router.get("/me")
async def user_me_info(
    user: Annotated[User, Depends(get_request_user)],
):
    # user is automatically authenticated
```

## Validation Patterns

### Custom Validators
```python
import re
from datetime import date

def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("비밀번호는 8자 이상이어야 합니다.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("비밀번호에는 대문자, 소문자, 특수문자, 숫자가 각 하나씩 포함되어야 합니다.")
    # Additional checks...
    return password

def validate_phone_number(phone_number: str) -> str:
    patterns = [
        r"010-\d{4}-\d{4}",
        r"010\d{8}",
        r"\+8210\d{8}",
    ]
    if not any(re.fullmatch(p, phone_number) for p in patterns):
        raise ValueError("유효하지 않은 휴대폰 번호 형식입니다.")
    return phone_number

def validate_birthday(birthday: date | str) -> date:
    if isinstance(birthday, str):
        try:
            birthday = date.fromisoformat(birthday)
        except ValueError as e:
            raise ValueError("올바르지 않은 날짜 형식입니다. format: YYYY-MM-DD") from e
    
    is_over_14 = birthday < datetime.now(tz=config.TIMEZONE).date() - relativedelta(years=14)
    if not is_over_14:
        raise ValueError("서비스 약관에 따라 만14세 미만은 회원가입이 불가합니다.")
    return birthday
```

### DTO Validation Integration
```python
from pydantic import AfterValidator

class SignUpRequest(BaseModel):
    password: Annotated[str, Field(min_length=8), AfterValidator(validate_password)]
    phone_number: Annotated[str, AfterValidator(validate_phone_number)]
    birth_date: Annotated[date, AfterValidator(validate_birthday)]
```

## Utility Patterns

### Data Normalization
```python
def normalize_phone_number(phone_number: str) -> str:
    # Remove hyphens and country code
    normalized = phone_number.replace("-", "").replace("+82", "0")
    return normalized
```

**Usage in service**:
```python
normalized_phone_number = normalize_phone_number(data.phone_number)
await self.check_phone_number_exists(normalized_phone_number)
```

### Timezone Handling
```python
from datetime import datetime
from app.core import config

# Always use configured timezone
current_time = datetime.now(config.TIMEZONE)
user.updated_at = datetime.now(config.TIMEZONE)
```

## Testing Patterns

### Async Test Configuration
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
```

### Test Organization
```
app/tests/
├── auth_apis/          # Authentication endpoint tests
├── user_apis/          # User endpoint tests
└── conftest.py         # Shared fixtures
```

## Common Idioms

### Ellipsis for Empty Inheritance
```python
class TokenRefreshResponse(LoginResponse): ...
```
Use when child class has identical structure to parent.

### Conditional Defaults
```python
secure = True if config.ENV == Env.PROD else False
domain = config.COOKIE_DOMAIN or None
```

### Dictionary Unpacking for Updates
```python
for key, value in data.items():
    if value is not None:
        setattr(user, key, value)
        update_fields.append(key)
```

### Type Union for Flexibility
```python
async def create_user(
    self,
    email: str | EmailStr,  # Accept both types
    ...
) -> User:
```

### Constants for Magic Values
```python
ALLOWED_UPDATE_FIELDS = ["name", "phone_number", "gender", "birthday"]
UPDATED_AT_FIELD = "updated_at"
```

## File Structure Conventions

### Router Files
- One router per file
- Router variable exported at module level
- Endpoints grouped by resource

### Service Files
- One service class per file
- Service instantiates its own dependencies in `__init__`
- Public methods for business operations
- Private/protected methods for validation

### Repository Files
- One repository class per model
- `_model` attribute for model reference
- CRUD methods with consistent naming

### DTO Files
- Group related DTOs by domain
- Request/Response pairs in same file
- Inherit for schema reuse

### Model Files
- One model per file (or related models together)
- Enums defined in same file as model
- Meta class for table configuration
