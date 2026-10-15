# Use Backend-Based Alerting for Sensor Threshold Notifications

**Date:** 2025-08-28

## Status

Accepted

## Context

Timely notification when sensor values exceed defined thresholds is critical for air quality monitoring and operational safety. While Grafana offers powerful alerting capabilities (see [ADR-14](0014-use-grafana-alerting-for-sensor-availability-notifications.md)), its configuration for value-based threshold alerting—especially with dynamic, per-device rules—proved to be overly complex and difficult to maintain.

Several alternatives were considered:

### Alternatives Considered

**1. Grafana Unified Alerting:**  
Grafana’s alerting system is well-suited for metric-based and availability notifications. However, implementing fine-grained, per-device threshold alerts for air quality metrics (e.g., temperature, humidity, pollen, particulate matter) would require extensive dashboard and rule configuration. Managing dynamic thresholds and custom notification logic for each sensor in Grafana was found to be impractical and error-prone.

**2. Backend-Based Alerting:**  
Integrating alerting logic directly into the backend API allows for flexible, programmatic threshold checks and notification workflows. The backend can evaluate incoming sensor data against configured thresholds, manage alert cooldowns, and send context-rich email notifications to operators. This approach centralizes alerting logic, simplifies threshold management, and enables stateful alerting (e.g., cooldown resets when values return to normal).

## Decision

We will implement **backend-based alerting** for sensor threshold notifications.

- The backend API receives all sensor values and evaluates them against configured thresholds.
- When a threshold is exceeded, the backend sends an alert email to the responsible operator.
- A state-based cooldown prevents repeated notifications while the value remains outside the threshold.
- The cooldown is reset only when the value returns to the normal range, allowing new alerts for subsequent threshold violations.
- Alerting configuration (thresholds, email addresses) is managed via API endpoints.

This approach avoids the complexity of managing dynamic alerting rules in Grafana and ensures maintainable, scalable, and context-aware notifications.

## Consequences

* **Simplified Alerting Logic:** Threshold checks and notifications are handled programmatically in the backend, reducing operational overhead.
* **Maintainable and Scalable:** Alerting rules and thresholds can be updated via API, supporting future expansion and customization.
* **Context-Rich Notifications:** Emails include device, metric, value, threshold details, and actionable recommendations.
* **Unified Data Flow:** All sensor data and alerting logic are managed in one place, improving reliability and traceability.
* **Reduced Grafana Complexity:** Grafana remains focused on visualization and availability monitoring, while the backend handles value-based alerts.