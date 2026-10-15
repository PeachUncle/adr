# ADR-0007: Backend Technology for API Demos

- **Status:** Proposed
- **Date:** 2025-12-08
- **Feature:** 1-robotics-book-spec
- **Context:** To effectively demonstrate advanced concepts like Vision-Language-Action (VLA) pipelines, a lightweight backend service is required to simulate handling API requests and integrating with models like LLMs.

## Decision

**FastAPI** (Python) will be the chosen framework for building any backend API demos required for the book.

## Consequences

### Positive

- **Technology Consistency:** Aligns with the project's primary language for robotics scripting (Python), reducing the number of languages readers need to be familiar with.
- **High Performance:** FastAPI is known for its high performance, which is beneficial even for small-scale demos.
- **Modern Features:** Offers modern Python features like type hints and asynchronous programming out of the box.
- **Automatic Documentation:** The automatic generation of interactive API documentation (via Swagger UI and ReDoc) is a significant advantage for an educational project, allowing readers to easily explore and test the demo APIs.

### Negative

- **Added Dependency:** Introduces another library to the project's Python dependencies.
- **Environment Setup:** Readers will need a properly configured Python environment with FastAPI and its dependencies installed to run the demos locally.

## Alternatives Considered

### Flask (Python)

- **Description:** A popular, minimalist Python web framework.
- **Reason for Rejection:** While Flask is a solid choice, FastAPI's built-in support for data validation (via Pydantic), asynchronous requests, and automatic API documentation provides a superior developer and learner experience for this project's needs.

### Node.js (Express)

- **Description:** Use a JavaScript-based backend to align with the Docusaurus frontend stack.
- **Reason for Rejection:** Rejected to maintain a clear separation between the frontend (JavaScript/Node.js for Docusaurus) and the robotics/AI backend (Python). Keeping the robotics-related code entirely in Python provides a more consistent learning path for the target audience.

## References

- **Implementation Plan:** D:\Quarter 4\ai-book\humanoid-robotic-book\specs\1-robotics-book-spec\plan.md
- **Related ADRs:** None
