# Backend Architecture Decisions

## Status

Accepted

## Context

We need to build a backend system for the FODMAP Helper application that will:
- Store and manage food items and their FODMAP classifications
- Provide RESTful APIs for the React frontend
- Be easily maintainable and scalable
- Have good performance characteristics
- Be easy to develop and test

Key considerations:
- The system needs to handle food items and their FODMAP properties
- Data validation is crucial for maintaining data integrity
- The system should be easily deployable
- Future migration to a different database system should be possible
- Development speed and ease of maintenance are priorities

## Decision

We will implement the backend with the following technology choices:

1. **Web Framework**: FastAPI
   - Modern, fast Python framework
   - Built-in OpenAPI documentation
   - Native async support
   - Type hints and automatic validation

2. **Database**: SQLite (initially)
   - Simple to set up and maintain
   - No separate server required
   - Easy to migrate to PostgreSQL later
   - Suitable for development and small deployments

3. **ORM**: SQLAlchemy
   - Industry standard Python ORM
   - Database agnostic
   - Robust query building
   - Good migration support via Alembic

4. **Project Structure**:
   ```
   app/
   ├── main.py         # FastAPI entrypoint
   ├── routes/         # API route definitions
   ├── models/         # SQLAlchemy models
   ├── schemas/        # Pydantic schemas
   ├── db/            # DB init and session config
   └── config.py      # Settings and environment config
   ```

5. **Development Tools**:
   - python-dotenv for environment management
   - pytest for testing
   - Docker for containerization
   - Black for code formatting
   - Flake8 for linting

## Consequences

### Positive

- FastAPI provides excellent developer experience and performance
- SQLite simplifies initial development and deployment
- SQLAlchemy allows easy database migration path
- Clear project structure promotes maintainability
- Built-in API documentation with OpenAPI
- Strong type checking and validation with Pydantic

### Negative

- SQLite may need migration to PostgreSQL for production scale
- Some additional setup required for async operations
- Learning curve for team members new to FastAPI
- Need to manage SQLite file backups

### Neutral

- Need to maintain clear separation between models and schemas
- Regular dependency updates required
- Documentation needs to be maintained

## References

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
* [12-Factor App Methodology](https://12factor.net/) 