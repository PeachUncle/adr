# 0007: Adopt a Single, Autonomous Database Analyst Agent

* **Status:** Accepted
* **Date:** 2025-07-05

## Context

The previous architecture, based on a team of specialized agents (inspector, SQL generator, coordinator), was robust for simple, well-defined tasks. However, it proved to be limited and prone to failure when trying to answer more complex questions that required reasoning across multiple tables (e.g., `JOINs`) or autonomous exploration of the database. The team's rigid workflow prevented the system from formulating dynamic plans, and the conditional logic in the coordinator's prompt to handle different types of questions (discovery vs. query) was causing reasoning failures in the LLM.

## Decision

I have decided to abandon the multi-agent architecture and consolidate all functionality into a single, more intelligent **`Autonomous_DB_Analyst_Agent`**. This decision implies:

1. **Single, Centralized Agent:** A single agent will be responsible for the entire query lifecycle: understanding the user's request, exploring the database (if necessary), fetching the schemas of multiple tables, formulating a complex query (with `JOINs`, `CTEs`, etc.), and executing it.

2. **Complete Toolset:** This agent will have access to the full suite of database tools (`list_schemas`, `list_tables`, `fetch_schema`, `execute_query`), giving it complete autonomy to interact with the database.

3. **Reasoning-Oriented Prompt:** The agent's instructions will be rewritten not as a rigid algorithm, but as a "reasoning workflow" that guides it on *how to think* to solve a problem. This includes the sequential calling of tools to avoid API overload and the integration of explicit security rules.

## Consequences

### Positive

* **Greater Capability and Flexibility:** The agent can now answer a much broader range of complex questions that require combining data from multiple sources, becoming a true "database analyst" and fulfilling the requirement of being "unlimited read-only."

* **True Autonomy:** The agent can formulate and execute its own multi-step plans, rather than following a predefined flow, which is a more powerful and scalable approach to problem-solving.

* **Simplified Logic:** It removes the complexity of managing communication and state-passing between multiple agents, consolidating the logic into a single point.

### Negative

* **Greater Dependence on a Single Prompt:** The system's success now depends entirely on the quality and robustness of a single, longer, and more complex prompt. An error in this prompt has a greater impact on the system as a whole.

* **Requirement for a More Powerful Model:** To manage the complex reasoning cycle, this agent requires a high-end model (like `llama3-70b-8192`), which can increase cost and latency compared to using smaller models for simpler tasks in the previous architecture.

* **New Types of Errors:** The autonomy to call multiple tools introduced a new type of error (parallel tool calling) that had to be mitigated with explicit instructions for sequential execution.
