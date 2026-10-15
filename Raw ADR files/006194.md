# ADR-010: Forecasting Model Selection

## Status
- Accepted

## Context
MobilityCorp requires accurate, scalable, and interpretable forecasting to anticipate demand for different vehicle types across city zones.  
The forecasting system must:
- Handle both **short-term (hourly)** and **medium-term (daily)** predictions.
- Scale across **hundreds of service zones** and different **vehicle categories** (scooters, bikes, cars, vans).
- Support **real-time data ingestion** (telemetry, weather, events, and historical bookings).
- Enable **retraining and evaluation** for continuous improvement.

Additionally, forecasts feed into:
- **Generative AI systems** (for proactive customer interactions).
- **Operational dashboards** for planning and reporting.

## Decision
Adopt a **hybrid forecasting architecture** combining:
1. **Prophet (Meta)** for interpretable, low-latency baseline forecasts per zone and vehicle type.  
2. **LSTM / Graph Neural Network (GNN)** models for spatiotemporal, citywide forecasts that capture relationships between zones and nonlinear dependencies.  
3. **Ensemble layer** that blends both predictions using weighted averaging or meta-regression for optimal accuracy.

### Key Decisions
- **Prophet** will run hourly to produce short-horizon forecasts (next 6–24 hours) per zone.  
- **LSTM/GNN** models will run less frequently (every 4–6 hours) to update multi-zone forecasts.  
- The **ensemble forecaster** will integrate outputs and push to the operations API for redistribution and GenAI insights.  
- Forecasts are stored in the **feature store** for reuse by RL and GenAI components.

## Rationale
- **Prophet Advantages:**  
  - Highly interpretable (decomposes trend, seasonality, and events).  
  - Excellent for smaller data sets and sparse zones.  
  - Fast retraining — suitable for continuous delivery.  

- **LSTM/GNN Advantages:**  
  - Captures **nonlinear, spatial, and temporal dependencies** (e.g., demand shifts between zones).  
  - Learns from large-scale historical data, improving medium-term accuracy.  

- **Ensemble Benefits:**  
  - Combines interpretability (Prophet) with accuracy (LSTM/GNN).  
  - Supports graceful degradation — if deep models fail, Prophet baseline remains reliable.

## Alternatives Considered
1. **Single Prophet-only solution**  
   - Simple, interpretable, fast  
   - Misses inter-zone effects and nonlinear patterns  
2. **LSTM-only solution**  
   - Accurate and dynamic  
   - Requires heavy compute and is less transparent for business reporting  
3. **Classical ARIMA/SARIMA**  
   - Lightweight, easy to explain  
   - Poor scalability across hundreds of zones; weak with external regressors  
4. **Pure ML Regression (XGBoost)**  
   - Handles external features well  
   - Limited temporal awareness without manual lag engineering  

## Consequences

**Positive**
- Robust forecasting pipeline balancing accuracy and explainability.  
- Flexibility to handle different time scales and zones.  
- Foundation for future reinforcement learning optimization and GenAI integrations.  
- Forecast data can be stored, versioned, and reused for model retraining or RAG context.

**Negative / Risks**
- Higher infrastructure complexity — dual model families with ensemble orchestration.  
- Increased compute cost for LSTM/GNN training.  
- Need for continuous validation to detect model drift and recalibrate ensemble weights.  

## Implementation Details
- **Training cadence:** Prophet hourly; LSTM/GNN every 4–6 hours.  
- **Features:** Historical rentals, time-of-day, weather, events, holidays, zone metadata.  
- **Evaluation:** MAPE / RMSE per zone; ensemble validation on rolling windows.  
- **Serving:** Deploy and serve via AI Gateway (ADR-05).  
- **Retraining trigger:** Data drift or >10% forecast error deviation.  

## Success Metrics
- <10% mean absolute percentage error (MAPE) for next-hour demand per zone.  
- ≥95% uptime for forecast API.  
- Consistent ensemble improvement ≥5% over Prophet-only baseline.  
