## ADR 001: Backend Framework — FastAPI

### Context

We need a backend web framework that allows us to rapidly build and expose APIs to support our frontend and external integrations (e.g., OpenAI API). The framework should support asynchronous requests, type safety, and auto-generated documentation for easier collaboration and testing. Since our team is relatively small, developer productivity and learning curve are critical factors.

### Options

**FastAPI**: Modern, async-first Python framework, built-in OpenAPI schema generation, excellent type hint support, strong ecosystem.

**Flask**: Lightweight and flexible, mature ecosystem, but synchronous by default and lacks built-in type safety and async support.

**Django**: Full-featured web framework with ORM, authentication, and admin UI; powerful but heavier than needed for a lightweight API service.

**Express.js (Node.js)**: Mature and flexible, with wide community support, but would require the team to shift from Python to JavaScript/TypeScript for backend.

### Decision

We decided to adopt FastAPI as our backend framework. It provides high performance with async support, clear typing, and automatic OpenAPI documentation, which helps us deliver endpoints quickly and maintain reliability. The Python ecosystem also aligns with our team’s skills and makes integrating with AI/ML libraries easier.

### Status

Accepted — this decision stands for the MVP and initial production deployment.

### Consequences

**Positive:**

1. Faster development and fewer bugs due to type hints and schema generation.
2. Easy integration with async libraries and APIs.
3. Strong alignment with Python ecosystem for potential ML expansion.

**Negative / Risks:**

1. Smaller ecosystem compared to Flask/Django.
2. Some team members may need to learn async programming patterns.

**Future pivots:**

1. If our requirements shift toward greater scalability or advanced enterprise features, we may consider transitioning some components to a different framework better suited for those needs.
