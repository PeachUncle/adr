# ADR-003: Use Django REST Framework for Backend API

## Status
Accepted

## Date
2025-12-19

## Context

We need to build a robust, scalable backend API for Smart Health Synchronizer that can:
- Handle user authentication (doctors and patients)
- Manage health records and prescriptions
- Serve blog content
- Integrate with AI service for recommendations
- Provide secure, RESTful API endpoints

### Requirements
- Python-based (team familiarity)
- RESTful API support
- Built-in authentication
- ORM for database operations
- Good documentation tools
- Active community support

### Options Considered

**Option 1: Django REST Framework (DRF)**
- Built on Django (mature, battle-tested)
- Powerful serializers and validators
- Built-in authentication support
- Excellent ORM (Django ORM)
- drf-spectacular for API documentation
- Large ecosystem and community

**Option 2: FastAPI**
- Modern, fast performance
- Built-in async support
- Automatic OpenAPI docs
- Type hints with Pydantic
- Smaller ecosystem

**Option 3: Flask + Flask-RESTful**
- Lightweight and flexible
- Simple to learn
- Requires more manual setup
- Smaller ecosystem than Django

## Decision

We will use **Django REST Framework (DRF)** for the backend API.

## Rationale

### Why Django REST Framework?

1. **Mature and Battle-Tested**
   - Used by Instagram, Mozilla, Pinterest, NASA
   - 10+ years of production use
   - Proven at scale

2. **Comprehensive Feature Set**
   - Built-in ORM (no need for SQLAlchemy)
   - Admin interface for data management
   - Migrations system
   - Authentication and permissions
   - Serializers for data validation

3. **Security**
   - Built-in protection against common vulnerabilities
   - CSRF protection
   - SQL injection prevention
   - XSS protection
   - Secure password hashing

4. **Developer Productivity**
   - Less boilerplate code
   - Convention over configuration
   - Excellent documentation
   - Large ecosystem of packages

5. **Healthcare Industry Use**
   - HIPAA-compliant applications built with Django
   - Strong data validation
   - Audit trail capabilities
   - Secure by default

6. **Learning and Career**
   - Industry-standard framework
   - Large job market demand
   - Excellent learning resources
   - Strong community support

## Consequences

### Positive

✅ **Rapid Development**
- Built-in admin panel for data management
- ORM handles database operations
- Authentication system ready to use
- Less code to write and maintain

✅ **Security**
- Security best practices built-in
- Regular security updates
- Well-documented security features

✅ **Scalability**
- Proven to scale (Instagram, etc.)
- Good caching support
- Database query optimization tools

✅ **API Documentation**
- drf-spectacular for OpenAPI/Swagger
- Auto-generated, interactive docs
- Easy to maintain

✅ **Testing**
- Built-in test framework
- pytest-django for advanced testing
- Easy to mock and test APIs

✅ **Integration**
- Easy to integrate with PostgreSQL
- Good support for JWT authentication
- Can communicate with FastAPI service

### Negative

❌ **Learning Curve**
- Django has many concepts to learn
- ORM can be complex for beginners
- Mitigation: We have learning roadmap

❌ **Monolithic by Default**
- Django encourages monolithic architecture
- Mitigation: We use DRF for API-only, separate frontend

❌ **Performance**
- Slower than FastAPI for high-concurrency
- Mitigation: Sufficient for our use case, can optimize later

❌ **Async Support**
- Limited async support compared to FastAPI
- Mitigation: Not critical for our current requirements

## Implementation Details

### Project Structure
```
backend/
├── src/
│   ├── config/           # Django settings
│   └── apps/             # Django applications
│       ├── users/        # User management
│       ├── doctors/      # Doctor profiles
│       ├── patients/     # Patient profiles
│       ├── appointments/ # Appointment system
│       ├── prescriptions/# Digital prescriptions
│       ├── blogs/        # Blog system
│       └── health_records/ # Health data
```

### Key Packages
```
Django==4.2+
djangorestframework==3.14+
djangorestframework-simplejwt==5.3+
drf-spectacular==0.26+
psycopg2-binary==2.9+
django-cors-headers==4.3+
django-filter==23.5+
```

### Authentication
- JWT (JSON Web Tokens) using djangorestframework-simplejwt
- Separate tokens for doctors and patients
- Token refresh mechanism

### API Documentation
- drf-spectacular for OpenAPI 3.0 schema
- Swagger UI at `/api/docs/`
- ReDoc at `/api/redoc/`

## Alternatives for Specific Features

- **Admin Panel**: Django Admin (included)
- **API Docs**: drf-spectacular (OpenAPI/Swagger)
- **Authentication**: djangorestframework-simplejwt (JWT)
- **CORS**: django-cors-headers
- **Filtering**: django-filter

## Review Date

This decision will be reviewed at the end of Sprint 3 (6 weeks) to ensure it meets our needs.

## References

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Spectacular](https://drf-spectacular.readthedocs.io/)
- [REST API Best Practices](https://restfulapi.net/)

## Notes

- DRF is the industry standard for Python-based REST APIs
- Perfect for healthcare applications requiring security and data integrity
- Excellent for learning and career development
- Well-suited for our Smart Health Synchronizer requirements
