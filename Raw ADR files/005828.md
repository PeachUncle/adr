# Use Grafana Dashboards for Sensor Data Availability Monitoring

**Date:** 2025-08-20

## Status

Accepted

## Context

Our IoT monitoring stack collects sensor data via MQTT and stores it in TimescaleDB.  
To ensure system reliability, we must verify that expected sensor readings are consistently ingested into the database and detect outages or communication gaps early.

The goal is to provide a **clear visibility layer** for sensor availability using Grafana dashboards. This should highlight:

- How many data points were **expected** vs. how many were **actually ingested**
- The **availability percentage** per device
- Any **gaps in data transmission**

Grafana is already part of our stack, which makes it a natural choice for visualization.

### Alternatives Considered

**1. Raw SQL Queries via pgAdmin:**  
Direct SQL queries in pgAdmin can reveal missing or delayed sensor data. However, this approach is manual, requires database expertise, and lacks visual clarity for stakeholders.

**2. Custom React Dashboard:**  
Building a custom frontend to visualize expected vs. actual values offers full flexibility but duplicates Grafana functionality. It requires significant development effort and ongoing maintenance.


## Decision

We will implement availability monitoring in **Grafana dashboards**, based on TimescaleDB views.

- Use PostgreSQL datasource (`timescaledb`) pre-provisioned in Grafana.
- Build panels to display:
  - **Expected vs. Actual Totals** (Stat panels per device)
  - **Availability Percentage** (Gauge visualization with thresholds)
  - **Data Gaps** (Table listing gaps longer than 10 minutes)
- Leverage TimescaleDB views (`v_totals_since_start_by_device`, `v_sensor_gaps`) for efficient queries.
- Refresh dashboards every 30s for near real-time visibility.

## Consequences

* **Low Effort, High Value:** Reuses Grafana, which is already deployed in the stack.
* **Immediate Visibility:** Operators can quickly see if sensors are dropping data.
* **Alerting Ready:** Grafana Alerting can be added later to notify when availability falls below thresholds.