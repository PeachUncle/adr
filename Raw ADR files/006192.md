# Architecture Decision Record (ADR)

## ADR-04: Machine Learning Traffic Prediction for Micromobility Demand

## Status
- ACCEPTED

## Context
Operations teams need reliable forecasts of electric bike and scooter usage at specific hubs to guide fleet rebalancing, charging logistics, and staffing. Historic ridership data is available at 15-minute granularity for each micromobility station along with weather feeds, event calendars, and station metadata. Demand patterns vary widely by time of day, season, and local context, making heuristic approaches brittle. We require a model that can generalize across locations, adapt to new signals, and expose predictions through our backend services with latency under 500 ms.

## Decision
Adopt a supervised regression model (gradient boosted trees via XGBoost) trained on aggregated historical data to predict the expected number of departures and arrivals per location for configurable time horizons (15 minutes to 24 hours).

- **Training features**  
  - `timestamp_features`: hour of day, day of week, week of year, month, holiday indicator, school term indicator.  
  - `weather_snapshot`: temperature, feels-like temperature, precipitation probability, wind speed, humidity, snow depth.  
  - `recent_ridership`: departures and arrivals in the past 1h, 3h, 24h windows; rolling averages and trend slopes.  
  - `seasonal_history`: same-slot ridership aggregations for prior 7 days and prior 4 weeks.  
  - `location_profile`: station capacity, dock availability, land-use category (residential, commercial, mixed), proximity to transit, population density.  
  - `event_signals`: binary indicators for nearby scheduled events (sports, concerts, festivals) and estimated attendance.  
  - `mobility_context`: active service alerts (road closures, bike lane maintenance) and competitor scooter deployments.

- **Model training pipeline**  
  - Daily ETL job builds feature tables in the analytics warehouse (BigQuery).  
  - Training runs nightly via Apache Spark batch jobs on the analytics cluster, producing a model artifact with metadata (feature schema, evaluation metrics).  
  - Model version is registered in MLflow; promotion to production requires MAPE < 12% on latest validation set and drift checks on key features.

- **Inference usage**  
  - Real-time inference exposed through a REST endpoint (`/traffic-forecast`) deployed as a stateless microservice (FastAPI) with autoscaling.  
  - Service retrieves the latest model from MLflow, uses Redis feature store for low-latency feature lookup, and returns predictions plus confidence intervals.  
  - Batch forecasts generated hourly and published to Kafka topic `demand.forecast` for downstream scheduling systems (charging, rebalancing dashboards).

- **Observability**  
  - Prometheus metrics for latency, error rate, and prediction distribution.  
  - Shadow deployments for new model versions and automatic rollback on SLA breach.

## Alternatives Considered
- Rule-based heuristics driven by historical averages (rejected: poor adaptability to weather/events).
- Classical time-series per station (ARIMA/Prophet) (rejected: high operational overhead and difficulty leveraging shared signals across locations).
- Deep learning sequence models (LSTM/Temporal Fusion Transformer) (deferred: higher complexity and infrastructure cost for marginal accuracy gains at current scale).

## Consequences
- Need to maintain data quality checks for feature pipelines and monitor feature drift.  
- Requires ML platform investment (MLflow, feature store, automated training jobs).  
- Enables improved operational planning and customer availability by providing consistent forecasts.  
- Introduces dependency on weather and event data providers; contracts must ensure uptime and data freshness.
