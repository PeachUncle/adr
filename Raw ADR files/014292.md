# ADR-001: Technology Stack Selection

## Status
**ACCEPTED** - 2024-01-XX

## Context
We need to select a technology stack for the Pokedex learning project that will teach the complete development cycle from backend to frontend to CI/CD, with a focus on DevOps practices.

## Decision
We will use the following technology stack:

### Backend
- **Language**: Python 3.11+
- **Framework**: Flask with Flask-RESTful
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **API Documentation**: Flask-RESTX (Swagger)
- **Testing**: pytest + Flask-Testing
- **Security**: Flask-JWT-Extended + bcrypt
- **Caching**: Redis (planned)
- **Data Validation**: Marshmallow

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **UI Library**: Tailwind CSS + Headless UI
- **Testing**: Vitest + Testing Library

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Cloud**: AWS (ECS + RDS + CloudFront)
- **Monitoring**: CloudWatch + DataDog
- **Infrastructure**: Terraform

## Rationale

### Why Python/Flask?
1. **Learning Value**: Python is the user's most-used language, allowing focus on concepts rather than syntax
2. **DevOps Relevance**: Python is widely used in DevOps tooling and automation
3. **Flask Simplicity**: Lightweight framework that teaches web fundamentals without magic
4. **SQLAlchemy**: Industry-standard ORM that teaches database concepts
5. **Ecosystem**: Rich ecosystem for data processing and API development

### Why React/TypeScript?
1. **Industry Standard**: Most in-demand frontend technology
2. **TypeScript**: Provides type safety and better developer experience
3. **Vite**: Fast build tool with excellent developer experience
4. **Learning Value**: Teaches modern frontend development patterns

### Why PostgreSQL?
1. **ACID Compliance**: Reliable for production applications
2. **JSON Support**: Can store Pokemon data flexibly
3. **SQLAlchemy Integration**: Excellent Python integration
4. **Production Ready**: Industry standard for web applications

### Why JWT + bcrypt?
1. **Industry Standard**: JWT is the most common authentication method
2. **Stateless**: No server-side session storage needed
3. **Security**: bcrypt provides secure password hashing
4. **Scalability**: JWT works well with microservices and load balancing

### Why AWS?
1. **Industry Standard**: Most common cloud platform
2. **DevOps Learning**: Comprehensive DevOps tooling
3. **Free Tier**: Good for learning and development
4. **Career Relevance**: High demand for AWS skills

## Consequences

### Positive
- **Learning Focus**: User can focus on concepts rather than learning new syntax
- **Industry Relevance**: All technologies are widely used in production
- **DevOps Integration**: Good integration between all components
- **Documentation**: Excellent documentation and community support

### Negative
- **Python Performance**: Slower than Go/Rust for some operations
- **Flask Simplicity**: May need to add more structure as project grows
- **AWS Complexity**: Steep learning curve for cloud services

## Alternatives Considered

### Backend Alternatives
- **Node.js/Express**: Rejected - User wanted to use Python
- **Go/Gin**: Rejected - Steeper learning curve, different language from frontend
- **Django**: Rejected - Too much "magic" for learning purposes

### Frontend Alternatives
- **Vue.js**: Rejected - Smaller job market
- **Svelte**: Rejected - Smaller ecosystem
- **Angular**: Rejected - Too complex for learning project

### Database Alternatives
- **MongoDB**: Rejected - Less ACID compliance, different learning curve
- **SQLite**: Rejected - Not suitable for production deployment

### Security Alternatives
- **Session-based Auth**: Rejected - Less scalable, requires server-side storage
- **OAuth2**: Rejected - Too complex for MVP, can be added later
- **Basic Auth**: Rejected - Not secure enough for production

## Implementation Notes

### Current Implementation Status
- ✅ **Flask-RESTful Migration**: Complete with API versioning
- ✅ **JWT Authentication**: Complete with access/refresh tokens
- ✅ **Role-Based Access Control**: Admin vs regular user permissions
- ✅ **Password Security**: bcrypt hashing implemented
- ✅ **API Documentation**: Flask-RESTX with Swagger UI
- ✅ **Database Models**: User and Pokemon models with relationships
- ✅ **Protected Endpoints**: Authentication required for sensitive operations
- ✅ **Comprehensive Documentation**: Syntax guides and implementation docs
- ✅ **Requirements Management**: All dependencies documented

### Security Implementation
- **JWT Tokens**: Access (1 hour) and refresh (30 days) tokens
- **Password Hashing**: bcrypt with salt for secure storage
- **Role-Based Access**: Admin users have elevated permissions
- **Protected Routes**: Sensitive endpoints require authentication
- **Input Validation**: Request parsing and validation on all endpoints

### API Structure
- **Versioning**: All endpoints prefixed with `/api/v1/`
- **Public Endpoints**: Pokemon data, authentication
- **Protected Endpoints**: User management, favorites
- **Documentation**: Available at `/docs/` endpoint

### Next Steps
1. ✅ **Database Design ADR**: Document schema decisions and relationships
2. ✅ **Environment Setup**: Create development environment
3. ✅ **Database Migration**: Set up SQLite and run migrations
4. ✅ **Testing**: Implement comprehensive test suite
5. [ ] **API Design ADR**: Document API patterns and versioning strategy
6. [ ] **Security ADR**: Document authentication and authorization strategy
7. [ ] **PokeAPI Integration**: Implement external data source
8. [ ] **Frontend Development**: Begin React implementation

## Review
This ADR will be reviewed after Phase 1 completion to ensure the technology choices align with learning objectives and implementation requirements.

## Related ADRs
- **ADR-002**: Database Design and Schema Decisions (✅ ACCEPTED)
- **ADR-003**: API Design Patterns and Versioning Strategy (Pending)
- **ADR-004**: Security Implementation and Authentication Strategy (Pending)
