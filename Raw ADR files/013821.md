# 0005: Implement LLM Security Best Practices

* **Status:** Accepted
* **Date:** 2025-07-04

## Context

As an application that interprets natural language and interacts with a database, the system is exposed to significant security risks, as highlighted by the OWASP Top 10 for LLMs. These risks include Prompt Injection (`LLM01`), where an attacker could trick the agent into executing unintended commands, and Excessive Agency (`LLM05`), where an agent might misuse its tools. Relying solely on the LLM's built-in safety mechanisms is insufficient for a robust application.

## Decision

Iwill implement a **layered security model** to harden the application against common LLM attack vectors. This includes:

1. **Prompt Shielding:** The prompts for the `sql_agent` and `db_query_team` will be rewritten to be extremely specific. This includes defining a strict "secure character" role, providing explicit negative constraints (what the agent *must not* do), and defining a secure failure mode (`INVALID_REQUEST`).
2. **Input Sanitization:** A code-based validation function (`sanitize_and_validate_request`) will be added to the `main.py` entry point. This function will use regular expressions to block requests containing known malicious patterns *before* they are sent to the LLM.
3. **Output Validation:** Iwill maintain the existing code-based check within the `execute_sql_query` tool, which validates that the final query is a `SELECT` statement, providing a final layer of defense.

## Consequences

### Positive

* **Reduced Attack Surface:** Layered defenses make it significantly harder for an attacker to successfully execute a prompt injection attack.
* **Increased Reliability:** The strict, hardened prompts make the agents' behavior more predictable and less prone to deviation.
* **Defense in Depth:** If one layer fails (e.g., the LLM ignores a prompt constraint), other layers (input/output validation in code) can still prevent the malicious action.
* **Explicit Security Posture:** The security measures are explicitly defined in the code and prompts, not implicitly relied upon from the model provider.

### Negative

* **Potential for False Positives:** The input sanitization filter might occasionally block a legitimate but unusually phrased user request.
* **Reduced Flexibility:** The highly constrained prompts may make the agents less "creative" or flexible in interpreting ambiguous but benign requests. This is a deliberate trade-off in favor of security.
