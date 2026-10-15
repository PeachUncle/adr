# ADR-001: Architecture Overview

**Status**: Accepted  
**Date**: 2025-12-02  
**Decision Makers**: Development Team  

---

## Context

The POC-MarketPredictor-ML project requires a scalable, maintainable architecture that supports:
- Real-time market data predictions
- Machine learning model training and serving
- WebSocket-based live updates
- Multi-source data integration (YFinance, CoinGecko, OpenAI)
- Production-ready monitoring and error tracking

---

## Decision

We adopt a **microservices-inspired architecture** with the following components:

### 1. **Backend: FastAPI + Python**
- **Framework**: FastAPI for async HTTP/WebSocket support
- **ML Stack**: scikit-learn, XGBoost for model training
- **Data Sources**: yfinance, CoinGecko API, OpenAI API
- **Caching**: In-memory TTL cache with rate limiting
- **Monitoring**: Prometheus metrics, Sentry error tracking

### 2. **Frontend: React + Vite**
- **Framework**: React 18 with hooks and functional components
- **Build Tool**: Vite for fast HMR and optimized builds
- **State Management**: Local component state (no Redux needed for POC)
- **Error Tracking**: Sentry with performance monitoring
- **UI**: Responsive design with CSS Grid/Flexbox

### 3. **Model Training Pipeline**
- **Offline Training**: Scheduled training jobs (trainer.py)
- **Online Learning**: Incremental updates (online_trainer.py)
- **Model Evaluation**: Automated promotion based on metrics
- **Drift Detection**: Statistical tests for model degradation

### 4. **Data Flow**

```
┌─────────────┐
│  YFinance   │───┐
└─────────────┘   │
                  ├──> [Cache Layer] ──> [Backend API] ──> [ML Model] ──> [WebSocket] ──> [Frontend]
┌─────────────┐   │
│  CoinGecko  │───┤
└─────────────┘   │
                  │
┌─────────────┐   │
│  OpenAI API │───┘
└─────────────┘
```

---

## Alternatives Considered

### 1. **Monolithic Flask Application**
- **Pros**: Simpler deployment, less overhead
- **Cons**: No async support, slower WebSocket performance, harder to scale

### 2. **Django + Django Channels**
- **Pros**: Batteries-included framework, mature ecosystem
- **Cons**: Heavier footprint, slower async performance than FastAPI, unnecessary ORM for our use case

### 3. **Microservices with Kubernetes**
- **Pros**: Maximum scalability, service isolation
- **Cons**: Overkill for POC, high operational complexity, longer development time

### 4. **Frontend: Next.js**
- **Pros**: SSR, better SEO, API routes
- **Cons**: Heavier than Vite, SSR not needed for dashboard, more complex setup

---

## Consequences

### Positive
- ✅ **Fast Development**: FastAPI + Vite enable rapid iteration
- ✅ **Real-time Updates**: Native WebSocket support in FastAPI
- ✅ **Type Safety**: Python type hints + PropTypes for JavaScript
- ✅ **Scalability**: Async backend can handle high concurrency
- ✅ **Observability**: Prometheus + Sentry provide production-grade monitoring
- ✅ **Cost-Effective**: No complex orchestration, runs on single server

### Negative
- ⚠️ **Single Point of Failure**: Monolithic backend (mitigated with Docker restart policies)
- ⚠️ **In-Memory Cache**: Lost on restart (acceptable for POC, can upgrade to Redis)
- ⚠️ **No Database**: All data fetched from APIs (by design, reduces complexity)

### Risks
- **Rate Limiting**: YFinance/CoinGecko have API limits → Mitigated with caching and rate limiter
- **Model Staleness**: Need periodic retraining → Automated with training pipeline
- **API Downtime**: Upstream API failures → Graceful error handling with fallbacks

---

## Implementation Notes

### Backend Structure
```
market_predictor/
├── server.py        # FastAPI app, routes, WebSocket
├── trading.py       # ML model, predictions, signals
├── cache.py         # TTL cache implementation
├── rate_limiter.py  # Rate limiting for external APIs
└── logging_config.py # Structured logging
```

### Frontend Structure
```
frontend/src/
├── App.jsx                  # Main orchestration
├── main.jsx                 # Entry point + Sentry
├── sentry.js                # Error tracking config
└── components/
    ├── StockRanking.jsx     # Stock predictions table
    ├── CryptoPortfolio.jsx  # Crypto rankings
    ├── AIAnalysisSection.jsx # OpenAI insights
    └── HelpModal.jsx        # User guidance
```

### Deployment
- **Docker**: Multi-stage builds for production
- **Docker Compose**: Local development with Prometheus/Grafana
- **Gunicorn**: Production WSGI server with 4 workers
- **Environment Variables**: 12-factor app configuration

---

## Related Decisions
- [ADR-002: Model Training Strategy](./ADR-002-model-training-strategy.md)
- [ADR-003: Caching Strategy](./ADR-003-caching-strategy.md)

---

## References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Twelve-Factor App Methodology](https://12factor.net/)
