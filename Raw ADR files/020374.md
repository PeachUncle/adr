# ADR-0001: Flask Backend Architecture

**Status:** Accepted  
**Date:** 2025-11-26 (Updated 2025-12-01)  
**Supersedes:** None  
**Superseded By:** N/A

---

## Context

We needed to select a backend framework and establish architectural patterns for the work productivity tracking application. The system requirements include:

- Local-first architecture (single-user, privacy-focused)
- RESTful API for React frontend
- SQLite database integration
- Support for 7 core features (daily focus, learning, skills, meetings, goals, feedback, energy)
- Rapid MVP development with January deadline
- Scalability from MVP to full feature set

Key considerations:

- Python familiarity and ecosystem
- Simple deployment (local desktop application)
- Clear separation of concerns
- Maintainability and testability
- Support for database migrations

## Decision

We will use **Flask with the Application Factory pattern**, organized with **Blueprints by feature** and a **Service Layer** for business logic.

### Core Architecture Components:

1. **Application Factory Pattern**

   - Function-based app creation: `create_app(config_name)`
   - Supports multiple configurations (dev, test, production)
   - Enables testing with different configurations
   - Prevents circular imports

2. **Blueprint Organization by Feature**

   - `/api/projects` - Project organization and management (Priority #1)
   - `/api/tasks` - Daily focus system
   - `/api/learnings` - Learning journal
   - `/api/skills` - Skills matrix
   - `/api/meetings` - Meeting tracking
   - `/api/goals` - Goals and hiring readiness
   - `/api/feedback` - Feedback capture
   - `/api/energy` - Energy and engagement monitoring

3. **Service Layer Pattern**

   - Business logic in dedicated service classes
   - Route handlers remain thin (request/response only)
   - Services are reusable and testable
   - Clear separation from data access

4. **Required Flask Extensions (MVP)**
   - `Flask-SQLAlchemy` - ORM for database operations
   - `Flask-Migrate` - Database migration management
   - `Flask-CORS` - Cross-origin resource sharing for React integration
   - `python-dotenv` - Environment variable management

### Project Structure:

```
backend/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration classes
│   ├── models/               # Database models (by feature)
│   ├── api/                  # API blueprints (by feature)
│   ├── services/             # Business logic
│   ├── utils/                # Utility functions
│   └── extensions.py         # Flask extensions initialization
├── instance/                 # Instance-specific files (gitignored)
├── migrations/               # Database migrations
├── tests/                    # Test suite
├── .env                      # Environment variables (gitignored)
├── .env.example              # Environment template
├── requirements.txt          # Dependencies
├── run.py                    # Application entry point
└── README.md                 # Setup instructions
```

## Consequences

### Positive

- **Scalability**: Blueprint structure allows adding features incrementally without touching existing code
- **Maintainability**: Clear separation of concerns (routes, services, models)
- **Testability**: Application factory enables testing with different configurations; service layer is easily unit-tested
- **Developer Experience**: Flask's simplicity combined with clear structure reduces cognitive load
- **Flexibility**: Configuration management supports dev/test/prod environments seamlessly
- **Industry Standard**: Follows Flask best practices (2024)
- **Feature Alignment**: Blueprint organization maps directly to our 7 core features

### Negative

- **Initial Complexity**: Application factory and blueprints add upfront setup overhead compared to simple Flask app
- **Learning Curve**: Developers unfamiliar with application factory pattern need to learn it
- **Boilerplate**: More files and structure than a minimal Flask app
- **Abstraction**: Service layer adds an additional layer between routes and data

**Mitigation:**

- Complexity is one-time cost with long-term maintainability benefits
- Clear documentation and templates provided
- Structure pays off as soon as second feature is added
- Boilerplate is manageable and promotes consistency

## Alternatives Considered

### Alternative 1: Django

**Description:** Full-featured Python web framework with batteries included

**Pros:**

- Built-in admin interface
- More features out of the box
- Strong ORM
- Large ecosystem

**Cons:**

- Heavyweight for our simple use case
- Steeper learning curve
- Opinionated structure may be too rigid
- Overkill for REST API + React frontend
- Slower development for simple APIs

**Why Not Chosen:** Too heavy for local-first, single-user application. We don't need admin interface, built-in templating, or many Django features. Flask's simplicity better matches our needs.

### Alternative 2: FastAPI

**Description:** Modern, fast Python API framework with automatic OpenAPI docs

**Pros:**

- Excellent performance (async)
- Automatic API documentation
- Type hints and validation
- Modern Python features

**Cons:**

- Less mature ecosystem than Flask
- Async complexity unnecessary for local app
- Smaller community and fewer resources
- Overkill for single-user local application

**Why Not Chosen:** Performance benefits irrelevant for local single-user app. Async adds unnecessary complexity. Flask's maturity and simplicity preferred for MVP timeline.

### Alternative 3: Simple Flask App (No Structure)

**Description:** Minimal Flask application without application factory or blueprints

**Pros:**

- Quickest to start
- Minimal boilerplate
- Easy to understand initially
- Fewer files

**Cons:**

- Difficult to test
- Hard to add features as app grows
- No clear organization
- Circular import issues
- Doesn't scale beyond toy apps

**Why Not Chosen:** Would need refactoring as soon as we add multiple features. MVP needs to scale to 7 features; simple app would become unmaintainable quickly.

## Implementation Notes

1. **Setup Priority:**

   - Create application factory first
   - Add configuration classes (dev, test, prod)
   - Initialize Flask-SQLAlchemy and Flask-Migrate
   - Create first blueprint (tasks) as template for others

2. **Configuration Management:**

   - Use environment variables via `python-dotenv`
   - Separate configs for dev/test/prod
   - Keep secrets in `.env` (gitignored)
   - Provide `.env.example` template

3. **Service Layer Guidelines:**

   - One service per major entity (TaskService, LearningService, etc.)
   - Services handle business logic only
   - Keep services stateless
   - Services can call other services if needed

4. **Blueprint Conventions:**
   - URL prefix matches feature (`/api/tasks`, `/api/learnings`)
   - Consistent HTTP methods (GET, POST, PUT, DELETE)
   - Standard response format (JSON)
   - Proper HTTP status codes

## References

- [Flask Backend Architecture Research](../research/tech-stack/flask-backend-architecture.md) - Comprehensive analysis (632 lines)
- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [Flask Application Factory Pattern](https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/)
- [Flask Blueprints](https://flask.palletsprojects.com/en/3.0.x/blueprints/)

## Related ADRs

- **ADR-0002:** React Frontend Architecture - Frontend counterpart to this backend architecture
- **ADR-0003:** SQLite Database Design - Database layer supporting these API blueprints
- **ADR-0004:** Flask-React Integration Strategy - Integration approach for this backend with React
- **ADR-0005:** Projects as Foundation Architecture - Feature priority decision that added `/api/projects` blueprint

---

**Last Updated:** 2025-11-26  
**Status:** ✅ Accepted and Active
