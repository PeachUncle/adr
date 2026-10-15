# ADR 001: Choice of Technology Stack

## Status

Accepted

## Context

The Personalized News Aggregator project requires a full-stack solution encompassing a backend API, a frontend user interface, a database, web scraping capabilities, and LLM integration. The technology choices need to support rapid development, good performance, maintainability, and a positive developer experience. The project is intended to be run in a devcontainer environment.

## Decision

The following technology stack was chosen:

| Component         | Technology                               |
| :---------------- | :--------------------------------------- |
| **Backend**       | Python with FastAPI                      |
| **Frontend**      | TypeScript with Next.js (React)          |
| **Database**      | SQLite (for development), PostgreSQL (for production) |
| **Web Scraping**  | `requests` & `BeautifulSoup` (initially), `trafilatura` (for content extraction) |
| **LLM Interface** | Google Gemini API (via `google-generativeai` Python library) |

## Justification

*   **Backend (Python with FastAPI):**
    *   Python offers a mature ecosystem for web scraping (`requests`, `BeautifulSoup`) and data handling.
    *   FastAPI is a modern, high-performance web framework that is easy to learn and supports asynchronous operations, ideal for I/O-bound tasks like web requests and LLM API calls. Its use of Python type hints aligns well with modern Python development.

*   **Frontend (TypeScript with Next.js):**
    *   Next.js (built on React) provides an excellent developer experience with features like file-based routing, server-side rendering (SSR), static site generation (SSG), and optimized image handling.
    *   TypeScript adds static typing, which helps catch errors early, improves code quality, and enhances maintainability, especially for larger projects.

*   **Database (SQLite/PostgreSQL):**
    *   SQLite is serverless, self-contained, and file-based, making it extremely simple for local development setup within a devcontainer.
    *   PostgreSQL is a powerful, open-source object-relational database system with a strong reputation for reliability, feature robustness, and performance, making it an ideal choice for production environments. This dual-database strategy provides ease of development and production-grade stability.

*   **Web Scraping (`requests`, `BeautifulSoup`, `trafilatura`):**
    *   `requests` and `BeautifulSoup` provide a simple and effective combination for fetching and parsing static HTML content from websites, suitable for initial development and many common use cases.
    *   `trafilatura` is specifically chosen for extracting the core article text from HTML, removing boilerplate (ads, navigation, comments), which is crucial for feeding clean data to the LLM.

*   **LLM Interface (Google Gemini API):**
    *   The Google Gemini API offers free access (within limits), a significantly larger context window (128K tokens) compared to self-hosted models like Gemma (8K tokens), and simplifies the project setup by removing the need for local GPU resources. This allows for broader accessibility and easier development on standard hardware. The `google-generativeai` Python library provides a convenient way to interact with the API.

## Consequences

*   **Learning Curve:** Developers unfamiliar with FastAPI, Next.js, or TypeScript might have a slight learning curve. However, these are popular and well-documented technologies.
*   **Devcontainer Complexity:** While the devcontainer simplifies individual developer setup, maintaining the Docker and devcontainer configurations adds a layer of complexity to the project infrastructure.
*   **External API Dependency:** Relying on the Google Gemini API introduces an external dependency. API changes, rate limits, or cost implications (if usage exceeds free tiers) need to be monitored.
*   **Build Steps:** The frontend (Next.js/TypeScript) requires a build step.
*   **Python and Node.js Ecosystems:** The project will need to manage dependencies and tooling from both Python and Node.js ecosystems.

This stack provides a balanced approach, leveraging modern, efficient technologies suitable for the project's goals. The use of a devcontainer mitigates many setup and consistency issues.
