# ✅ TodoApp — Full-Stack Task Management API

A production-grade task management application built with **FastAPI**, **SQLAlchemy**, and **Jinja2 Templates**. Features JWT authentication, role-based access control, full CRUD operations, database migrations with Alembic, and a responsive Bootstrap UI.

Built as part of a backend engineering portfolio to demonstrate RESTful API design, relational database modelling, authentication patterns, and testing best practices.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.13, FastAPI, Uvicorn |
| **Database** | SQLite (dev), PostgreSQL / MySQL (production-ready) |
| **ORM** | SQLAlchemy 2.x |
| **Migrations** | Alembic |
| **Auth** | JWT (python-jose), bcrypt (passlib), OAuth2 Password Flow |
| **Validation** | Pydantic v2 |
| **Frontend** | Jinja2 Templates, Bootstrap 4, Vanilla JavaScript |
| **Testing** | Pytest, FastAPI TestClient |

---

## Features

**Authentication & Authorisation**
- User registration with password hashing (bcrypt)
- JWT token-based authentication with configurable expiry
- Role-based access control (admin vs regular user)
- Protected routes with dependency injection
- Cookie-based session management for the web UI

**Todo Management**
- Create, read, update, and delete todos
- Owner-scoped queries — users can only access their own todos
- Priority levels (1–5) with validation
- Mark todos as complete/incomplete
- Admin endpoint to view all users' todos

**User Management**
- View profile information
- Change password with current password verification
- Update phone number

**Database**
- SQLAlchemy ORM with relationship mappings
- Foreign key constraints (todos → users)
- Alembic migrations for schema evolution
- Multi-database support (SQLite, PostgreSQL, MySQL)

**Web Interface**
- Server-side rendered pages with Jinja2
- Responsive Bootstrap UI
- Login, registration, todo list, add/edit todo pages
- Real-time form validation

---

## Project Structure

```
TodoApp/
├── routers/
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   └── bootstrap.css
│   │   ├── js/
│   │   │   └── auth.js
│   │   └── templates/
│   │       ├── layout.html
│   │       ├── navbar.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── todo.html
│   │       ├── add-todo.html
│   │       └── edit-todo.html
│   ├── auth.py            # Authentication routes (register, login, JWT)
│   ├── todos.py           # Todo CRUD routes
│   ├── admin.py           # Admin-only routes
│   └── users.py           # User profile routes
├── test/
│   ├── utils.py           # Shared test fixtures and overrides
│   ├── test_example.py    # Basic pytest examples
│   ├── test_main.py       # Health check tests
│   ├── test_todos.py      # Todo endpoint tests
│   ├── test_admin.py      # Admin endpoint tests
│   └── test_users.py      # User endpoint tests
├── alembic/
│   ├── versions/          # Migration scripts
│   └── env.py
├── main.py                # Application entry point
├── database.py            # Database engine and session config
├── models.py              # SQLAlchemy ORM models
├── alembic.ini            # Alembic configuration
└── requirements.txt       # Python dependencies
```

---

## Database Schema

```
┌──────────────┐       ┌──────────────────┐
│    users     │       │      todos       │
├──────────────┤       ├──────────────────┤
│ id (PK)      │──┐    │ id (PK)          │
│ email (UQ)   │  │    │ title            │
│ username (UQ)│  │    │ description      │
│ first_name   │  │    │ priority         │
│ last_name    │  │    │ complete         │
│ hashed_pass  │  └───▶│ owner_id (FK)    │
│ is_active    │       └──────────────────┘
│ role         │
│ phone_number │
└──────────────┘
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/TodoApp.git
cd TodoApp

# Create virtual environment
python -m venv fastapienv
source fastapienv/bin/activate   # macOS/Linux
fastapienv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
cd TodoApp
uvicorn main:app --reload
```

The app will be available at:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | Home page |
| http://127.0.0.1:8000/auth/login-page | Login |
| http://127.0.0.1:8000/auth/register-page | Registration |
| http://127.0.0.1:8000/docs | Swagger API docs |
| http://127.0.0.1:8000/redoc | ReDoc API docs |

### Run Tests

```bash
pytest -v
```

---

## API Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/` | Register a new user |
| POST | `/auth/token` | Login and receive JWT |

### Todos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Get all todos (owner-scoped) |
| GET | `/todo/{todo_id}` | Get a specific todo |
| POST | `/todo/` | Create a new todo |
| PUT | `/todo/{todo_id}` | Update a todo |
| DELETE | `/todo/{todo_id}` | Delete a todo |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/todo` | Get all todos (all users) |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/` | Get current user profile |
| PUT | `/user/password` | Change password |
| PUT | `/user/phonenumber/{phone_number}` | Update phone number |

---

## Database Configuration

The app supports multiple databases. Update `database.py` to switch:

```python
# SQLite (default — development)
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

# PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/TodoApplicationDatabase"

# MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@127.0.0.1:3306/TodoApplicationDatabase"
```

### Alembic Migrations

```bash
# Create a new migration
alembic revision -m "description of change"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

---

## Testing

Tests use a separate SQLite database (`testdb.db`) with dependency overrides to isolate test data from production:

```python
# Test database — completely separate from production
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

# Auth is bypassed in tests with a mock user
def override_get_current_user():
    return {'username': 'TestUser', 'id': 1, 'user_role': 'admin'}
```

Run the full suite:

```bash
pytest -v                    # All tests with verbose output
pytest test/test_todos.py    # Todo tests only
pytest test/test_auth.py     # Auth tests only
pytest --tb=short            # Shorter traceback on failures
```

---

## Environment Variables

For production, move sensitive values to environment variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key |
| `DATABASE_URL` | Database connection string |
| `ALGORITHM` | JWT algorithm (default: HS256) |

---

## Roadmap

- [ ] Add Redis caching for frequently accessed todos
- [ ] Celery integration for email reminders on due dates
- [ ] Docker and docker-compose for containerised deployment
- [ ] CI/CD pipeline with GitHub Actions
- [ ] React frontend (replacing Jinja2 templates)
- [ ] Prometheus metrics and structured logging

---

## Author

**Biswajit Biswas**

Backend Developer — Python, FastAPI, PostgreSQL, Redis, Docker

- Based in Oxford, UK
- Targeting mid-level backend engineering roles

---

## License

This project is built for educational and portfolio purposes.