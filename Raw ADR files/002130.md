## ADR 001: Backend Framework — FastAPI

### Context
 We need a backend framework that can rapidly expose APIs for our EdTech platform, including endpoints for user management, course content, assessments, and AI-powered features. The framework should support asynchronous operations, integration with our LLM/embedding pipelines, and provide high performance and scalability. Additionally, we want strong developer experience and clear documentation to facilitate rapid iteration during MVP development.

### Options
**FastAPI**: Modern Python framework, supports async operations, automatic OpenAPI documentation, high performance, and easy integration with AI and database services. Excellent DX and widely adopted in AI/ML ecosystems.

**Django (REST Framework)**: Mature Python framework with built-in ORM, authentication, and admin interface. Slightly heavier and more opinionated, but robust for full-featured apps.

**Flask**: Lightweight Python microframework, simple and flexible, but requires more boilerplate for async support, validation, and documentation.

**Node.js/Express**: JavaScript/TypeScript option, widely used, async by default, but adds a different tech stack compared to Python-based AI pipelines.

### Decision
 We chose FastAPI for its combination of high performance, async support, seamless API documentation, and strong integration with Python-based AI/ML tools. It enables rapid development of REST endpoints and will streamline the connection between our frontend and AI services.

### Status
 Accepted — stands for MVP and initial production deployment.

### Consequences
**Positive:**
1. High-performance async framework suitable for AI-heavy workloads.
2. Automatic OpenAPI and Swagger documentation for APIs.
3. Strong Python ecosystem compatibility (AI/ML libraries).
4. Minimal boilerplate and excellent developer experience.

**Negative / Risks:**
1. Less built-in “batteries included” features compared to Django (e.g., admin interface, authentication scaffolding).
2. Requires careful structuring for larger applications to maintain modularity.