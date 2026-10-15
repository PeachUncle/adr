
# Architecture Decision Record 003: Select FMCG Kaggle Dataset

- **Version:** 1.0
- **Status:** Accepted
- **Last Updated:** 2025-07-05 by Maksim Ilin
- **Summary:** This ADR documents the decision to use a specific public dataset from Kaggle for model training and demonstration.

---

## Context

To develop and validate our forecasting prototype, we required a dataset with specific characteristics:
1.  **Publicly Accessible:** Must have a permissive license for use in research and publication.
2.  **Time-Series Format:** Must contain timestamped observations (ideally daily).
3.  **Relevant Domain:** Should be from the Supply Chain Management or logistics domain.
4.  **Multiple Series:** Must contain data for multiple distinct items (e.g., SKUs, products) to demonstrate the model's utility in a realistic multi-product scenario.
5.  **Sufficient Data:** Must have enough historical data to observe patterns like trend and seasonality.

## Decision

We have decided to use the **"FMCG Sales Demand Forecasting and Optimization" dataset** available on Kaggle.

The data will be included in the repository as `FMCG_Sales.csv` and will be processed according to the steps outlined in `docs/DATA_PREPROCESSING.md`.

## Consequences

### Positive Consequences
*   **Meets All Criteria:** The dataset perfectly matches our requirements, containing daily order quantities for nearly 2,000 product SKUs across multiple warehouses.
*   **Reproducibility:** Using a public, static dataset ensures that our research is fully reproducible by others.
*   **Ideal for Exponential Smoothing:** The nature of the data (daily demand with potential trend and seasonality) is well-suited for the Holt-Winters Exponential Smoothing model we chose.
*   **No Data Privacy Concerns:** As a public dataset, it eliminates any issues related to handling sensitive or proprietary corporate data.

### Negative Consequences
*   **Static Data:** The dataset is a fixed snapshot in time and does not represent a live, evolving data stream. This is an acceptable limitation for a research prototype.
*   **Synthetic Elements Possible:** As with many public datasets, some data points may be synthetic or anonymized, but the overall patterns are sufficient for our demonstration purposes.
