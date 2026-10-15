
# Architecture Decision Record 002: Use Gradio for UI and MCP Server

- **Version:** 1.0
- **Status:** Accepted
- **Last Updated:** 2025-07-05 by Maksim Ilin
- **Summary:** This ADR documents the decision to use the Gradio library to build both the interactive web UI and the backend Model Context Protocol (MCP) server.

---

## Context

Our project requires two key interfaces:
1.  An interactive web application for users to visualize the forecast and interact with the model.
2.  An MCP-compliant API endpoint to allow an LLM agent to call our forecasting function as a tool.

We considered several options, including building a separate frontend (e.g., with React or Streamlit) and a separate backend API server (e.g., with Flask or FastAPI). However, this would increase complexity and require managing two distinct codebases.

## Decision

We have decided to use the **Gradio library** as the unified framework for both the user interface and the MCP server.

We will use `gradio.Interface` to build the web demo and will enable the MCP server by passing the `mcp_server=True` argument to the `launch()` method. This provides both required interfaces from a single codebase.

## Consequences

### Positive Consequences
*   **Simplicity and Speed:** Gradio allows us to create a functional UI with just a few lines of Python, dramatically accelerating development time.
*   **Unified Solution:** Both the UI and the MCP server are generated from the same function definition (`gr.Interface`). This reduces code duplication and ensures consistency between the demo and the tool.
*   **Low Learning Curve:** Gradio's API is simple and intuitive, allowing us to focus on our core logic rather than on web development complexities.
*   **Seamless Hugging Face Integration:** Gradio is the native framework for Hugging Face Spaces, making deployment trivial.

### Negative Consequences
*   **Less UI Customization:** Gradio is less flexible for detailed UI customization compared to a full frontend framework like React. For our research prototype, this is an acceptable trade-off.
*   **Dependency on Gradio's MCP Implementation:** We are reliant on Gradio's specific implementation of the MCP server. This is a reasonable dependency, as Gradio is a well-supported open-source project.
