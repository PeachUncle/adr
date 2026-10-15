# 0008: Adopt Streamlit for the Graphical User Interface

* **Status:** Accepted
* **Date:** 2025-07-09

## Context

The project evolved from a command-line tool to a system requiring richer, more user-friendly interaction. The need to support features like file uploads (for PDFs) and a continuous chat interface made the basic `Agno Playground` insufficient. A framework was needed to build a custom web application that could orchestrate interactions with the different agents (database analysis and document analysis) in a single place.

## Decision

I decided to adopt **Streamlit** as the framework for building the application's graphical user interface. The main application will be served via an `app.py` script.

This choice was based on the following points:

1. **Rapid Development:** Streamlit allows for the creation of rich, interactive web applications by writing only Python code, which drastically accelerates development.
2. **Python-Native Ecosystem:** It integrates seamlessly with the rest of our codebase, including the data science and AI libraries I'm already using.
3. **Simplicity (KISS):** It avoids the complexity of a full-stack architecture (e.g., Flask/React), which would be overkill for the project's current needs.

## Consequences

### Positive

* **Speed of Implementation:** The ability to build a functional chat interface with file uploads in a matter of hours is a significant advantage.
* **Simplified Maintenance:** Maintaining the application is easier as it does not require knowledge of JavaScript, HTML, or CSS.
* **Focus on Data and AI:** The framework is optimized for data and AI use cases, offering components like spinners and state management that are ideal for LLM interactions.

### Negative

* **Less Control Over Design:** Streamlit offers less flexibility for customizing the application's appearance (styling) compared to traditional frontend frameworks.
* **Execution Model:** Streamlit's execution model, which re-runs the script on every interaction, requires careful state management (`st.session_state`) and caching (`st.cache_resource`) to prevent the unnecessary re-initialization of heavy services, such as the AI models.
