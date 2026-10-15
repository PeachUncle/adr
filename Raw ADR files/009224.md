# Architecture Decision Record 001: Use Exponential Smoothing as Initial Model

- **Version:** 1.0
- **Status:** Accepted
- **Last Updated:** 2025-07-05 by Maksim Ilin
- **Summary:** This ADR documents the decision to select Exponential Smoothing as the primary forecasting method for the initial prototype.

---

## Context

For the initial phase of our research project, we required a statistical forecasting method to serve as the core logic of our MCP-enabled tool. The selection criteria were that the model must be:

1.  **Well-Established:** Widely used and understood within the logistics and supply chain domain.
2.  **Computationally Efficient:** Capable of running quickly with low memory overhead to ensure low latency for an MCP API call.
3.  **Simple to Implement:** The implementation complexity should be low, allowing us to focus on the novel MCP architecture rather than on complex model tuning.
4.  **Sufficiently Powerful:** Able to capture common time-series patterns like trend and seasonality.
5.  **Not Obsolete:** Still considered a valid and effective technique for relevant tasks like demand forecasting.

We evaluated three primary candidates against these criteria: Exponential Smoothing (ES), ARIMA, and Causal Regression.

## Decision

We have decided to implement **Exponential Smoothing (specifically, the Holt-Winters method)** as the first and primary statistical model for our prototype.

The model will be implemented using the `statsmodels` Python library. It will be configured to handle both trend and seasonality, making it robust for the selected FMCG dataset.

## Consequences

This decision has the following positive and negative consequences:

### Positive Consequences
*   **Rapid Development:** The simplicity of ES allows for fast implementation, enabling us to quickly build a working end-to-end prototype.
*   **High Performance:** ES has very low computational and memory requirements, making it an ideal candidate for a lightweight, scalable MCP tool that can respond with minimal latency.
*   **Meets Project Scope:** This choice perfectly aligns with our `PROJECT_CHARTER`, which prioritizes demonstrating the MCP architecture over complex modeling.
*   **Strong Research Baseline:** Using a well-understood model like ES provides a solid, defensible baseline for our research paper. We can clearly articulate its strengths and limitations.
*   **Ease of Maintenance:** The model is easy to understand and debug for all team members, regardless of their statistical expertise.

### Negative Consequences
*   **Limited Explanatory Power:** Unlike Causal Regression, ES cannot incorporate external variables (e.g., promotions, holidays). It can only explain the future based on past patterns, not external drivers.
*   **Potentially Lower Accuracy on Complex Series:** For time series with highly complex, non-linear autocorrelation patterns, a finely-tuned ARIMA model might theoretically achieve higher accuracy, though at a significant cost in complexity and performance.
*   **Future Work Required:** This decision implies that demonstrating the integration of more complex models (like Regression) is deferred to future work. The current prototype will not be able to answer "what-if" questions related to external factors.