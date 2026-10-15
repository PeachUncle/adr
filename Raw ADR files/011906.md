# Grafana Embedded in SPA for Visualizing Metrics Data

## Status
ACCEPTED

## Context
The Hospital Software System requires an effective visualization solution for displaying patient vital metrics. Choosing the right tool for visualizing metrics is crucial for a clear and insightful representation of healthcare data.

## Decision
After considering various options for visualizing patient vital metrics, including standalone Grafana, custom-built solutions, and external visualization tools, we decide to embed Grafana within the Single Page Application (SPA) for the following reasons:

### Choices Considered:

1. **Standalone Grafana:**
   - *Explanation:* Standalone Grafana instances would require separate navigation and authentication, leading to a fragmented user experience. Integration with the SPA provides a seamless interface for medical staff without the need to switch between applications.
   - *Configurability:* Limited configurability as standalone instances might not align seamlessly with the overall SPA design.

2. **Custom-Built Visualization:**
   - *Explanation:* Building a custom visualization solution demands significant development effort and ongoing maintenance. Embedding Grafana allows us to leverage a feature-rich, well-maintained tool, reducing the development overhead and providing a proven solution for visualizations.
   - *Configurability:* Custom-built solutions might offer high configurability but at the cost of increased development and maintenance complexity.

3. **External Visualization Tools:**
   - *Explanation:* While external tools may offer visualization capabilities, integrating them with the SPA can introduce complexities in data synchronization, user authentication, and maintaining a cohesive user interface. Embedding Grafana ensures a more straightforward integration and consistent user experience.
   - *Configurability:* External tools may have varying levels of configurability, but integrating them seamlessly with the SPA could be challenging.

## Configurability and Easiness to Add New Metrics:

- **Grafana Embedded in SPA:**
  - *Configurability:* Grafana provides a highly configurable environment, allowing medical staff to customize dashboards according to their needs. The SPA integration ensures a unified and familiar interface for configuration.
  - *Easiness to Add New Metrics:* Grafana's intuitive user interface simplifies the process of adding new metrics. With its support for various data sources and plugins, incorporating new metrics into existing dashboards is efficient and straightforward.

## Consequences
By embedding Grafana in the SPA, we leverage its extensive visualization features, empowering medical staff to interpret vital metrics effectively. This decision enhances the user experience, provides a versatile platform for creating insightful dashboards, and offers high configurability with ease of adding new metrics.

The chosen option of embedding Grafana in the SPA is preferred due to its seamless integration, reduced development effort compared to custom solutions, consistent user experience, high configurability, and ease of incorporating new metrics.
