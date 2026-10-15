# 0003: Adopt a Modular Project Structure

* **Status:** Accepted
* **Date:** 2025-07-03

## Context

As the project grew from a single agent to a multi-agent team, keeping all the code in a single `main.py` file became unsustainable. This approach leads to poor readability, makes code reuse difficult, and mixes different concerns (e.g., agent definitions, tool functions, application logic) in one place. To ensure the project is maintainable and scalable, a more organized file structure is necessary.

## Decision

Iwill adopt a **modular project structure** by organizing the code into logical directories, with each directory representing a distinct concern. Iwill use `__init__.py` files to define these directories as Python packages, allowing for clean, relative imports between them.

The chosen structure is:

* **`agents/`**: Contains all `agno` Agent and Team definitions.
* **`config/`**: Contains static configuration, like database connection details.
* **`tools/`**: Contains all functions decorated with `@tool` that agents can use.
* **`main.py`**: A clean, top-level entry point for running the primary application logic.

## Consequences

### Positive

* **Improved Maintainability:** Code is easier to find, read, and modify. Onboarding new developers is simpler as the project layout is logical and self-documenting.
* **Scalability:** The structure makes it easy to add new agents, tools, or configurations without cluttering existing files.
* **Clear Separation of Concerns:** The file system itself enforces a separation between agent logic, business tools, and application configuration.
* **Reusability:** Tools and configurations can be more easily imported and reused across different parts of the application (e.g., in both `main.py` and a future `playground.py`).

### Negative

* **Increased Boilerplate:** The modular structure introduces a higher number of files and requires an understanding of Python's import system.
* **Slightly More Complex Setup:** For a very small project, this might seem like over-engineering, but the benefits quickly outweigh this as the project grows.
