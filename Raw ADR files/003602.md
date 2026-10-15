# ADR-005: Use FastAPI for AI/ML Service

## Status
Accepted

## Date
2025-12-19

## Context

We need to build an AI/ML service for Smart Health Synchronizer that can:
- Analyze patient symptoms using NLP
- Recommend appropriate doctors based on symptoms
- Provide health risk predictions
- Serve machine learning models efficiently
- Communicate with Django backend via REST API
- Handle concurrent requests efficiently

### Requirements
- Python-based (ML libraries compatibility)
- Fast performance for ML inference
- Async support for concurrent requests
- Easy API documentation
- Type validation
- Quick development

### Options Considered

**Option 1: FastAPI**
- Modern, fast framework
- Built-in async support
- Automatic OpenAPI docs
- Type hints with Pydantic
- Perfect for ML model serving

**Option 2: Flask**
- Lightweight and simple
- Synchronous by default
- Manual documentation
- Requires extensions for async

**Option 3: Django REST Framework**
- Already using for main backend
- Heavier than needed for ML service
- Limited async support
- Overkill for ML serving

## Decision

We will use **FastAPI** for the AI/ML service.

## Rationale

### Why FastAPI?

1. **Performance**
   - One of the fastest Python frameworks
   - Built on Starlette (async) and Pydantic (validation)
   - Comparable to NodeJS and Go performance
   - Perfect for ML model inference

2. **Async Support**
   - Native async/await support
   - Handle multiple concurrent requests
   - Non-blocking I/O operations
   - Important for ML inference workloads

3. **Automatic Documentation**
   - OpenAPI (Swagger) documentation auto-generated
   - Interactive API docs at `/docs`
   - ReDoc at `/redoc`
   - No manual documentation needed

4. **Type Safety**
   - Pydantic for data validation
   - Type hints throughout
   - Catch errors before runtime
   - Better IDE support

5. **ML/AI Ecosystem**
   - Works perfectly with:
     - scikit-learn
     - TensorFlow
     - PyTorch
     - spaCy
     - transformers
   - Easy to load and serve models

6. **Developer Experience**
   - Simple and intuitive API
   - Fast development
   - Excellent error messages
   - Modern Python features

7. **Production Ready**
   - Used by Microsoft, Uber, Netflix
   - Battle-tested in production
   - Good for microservices
   - Easy to deploy

## Consequences

### Positive

✅ **Performance**
- High throughput for ML predictions
- Async operations don't block
- Efficient resource usage
- Fast response times

✅ **Developer Productivity**
- Quick to write API endpoints
- Auto-generated documentation
- Type hints catch errors early
- Less boilerplate code

✅ **API Documentation**
- OpenAPI schema generated automatically
- Interactive docs for testing
- Easy for backend team to integrate
- Self-documenting code

✅ **Type Safety**
- Pydantic models validate input
- Type hints prevent bugs
- Better IDE autocomplete
- Clear API contracts

✅ **ML Model Serving**
- Easy to load models at startup
- Efficient inference
- Batch prediction support
- Model versioning possible

✅ **Microservice Architecture**
- Independent deployment
- Scales separately from backend
- Can be updated independently
- Clear separation of concerns

### Negative

❌ **Newer Framework**
- Less mature than Flask/Django
- Smaller ecosystem
- Mitigation: Growing rapidly, good documentation

❌ **Learning Curve**
- Async concepts to learn
- Pydantic models
- Mitigation: Excellent documentation, simple API

❌ **ORM Support**
- No built-in ORM like Django
- Mitigation: Don't need database in AI service

## Implementation Details

### Project Structure
```
ai-service/
├── app/
│   ├── main.py           # FastAPI application
│   ├── api/              # API endpoints
│   │   ├── routes.py     # Route definitions
│   │   └── schemas.py    # Pydantic models
│   ├── models/           # ML models
│   │   ├── symptom_analyzer.py
│   │   ├── doctor_recommender.py
│   │   └── trained_models/  # Saved models
│   ├── services/         # Business logic
│   │   ├── prediction.py
│   │   └── preprocessing.py
│   └── utils/            # Utilities
│       ├── validators.py
│       └── helpers.py
├── tests/                # Tests
├── requirements.txt      # Dependencies
└── README.md
```

### Key Dependencies
```
fastapi==0.104.0+
uvicorn[standard]==0.24.0+
pydantic==2.5.0+
scikit-learn==1.3.0+
pandas==2.1.0+
numpy==1.24.0+
spacy==3.7.0+
python-multipart==0.0.6
```

### Example Endpoint
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Smart Health AI Service",
    description="AI-powered symptom analysis and doctor recommendation",
    version="1.0.0"
)

class SymptomRequest(BaseModel):
    symptoms: List[str]
    severity: str
    duration: str

class DoctorRecommendation(BaseModel):
    specialty: str
    confidence: float
    reasoning: str

@app.post("/api/analyze-symptoms", response_model=DoctorRecommendation)
async def analyze_symptoms(request: SymptomRequest):
    """
    Analyze patient symptoms and recommend appropriate doctor specialty.
    """
    # ML model inference here
    return {
        "specialty": "General Physician",
        "confidence": 0.85,
        "reasoning": "Based on common cold symptoms"
    }
```

### API Design

**Base URL:** `http://localhost:8001`

**Endpoints:**
```
POST /api/analyze-symptoms
POST /api/recommend-doctors
POST /api/predict-risk
GET  /health (health check)
GET  /docs (Swagger UI)
GET  /redoc (ReDoc)
```

### Communication with Backend

**Pattern:** REST API calls from Django backend

```python
# Django backend calls AI service
import requests

ai_service_url = "http://localhost:8001"

response = requests.post(
    f"{ai_service_url}/api/analyze-symptoms",
    json={
        "symptoms": ["fever", "cough"],
        "severity": "moderate",
        "duration": "3 days"
    }
)

recommendation = response.json()
```

### Model Loading
```python
# Load models at startup (once)
from fastapi import FastAPI
import joblib

app = FastAPI()

@app.on_event("startup")
async def load_models():
    app.state.symptom_model = joblib.load("models/symptom_analyzer.pkl")
    app.state.recommender_model = joblib.load("models/recommender.pkl")
```

### Deployment
- Run with Uvicorn ASGI server
- Can use Docker for containerization
- Easy to scale horizontally
- Can use load balancer

## Why Not Django for AI Service?

**Reasons to use FastAPI instead:**
1. **Performance**: 3x faster than Django for API responses
2. **Async**: Native async for ML inference
3. **Simplicity**: Lighter weight, perfect for ML serving
4. **Microservice**: Better suited for separate service
5. **Documentation**: Auto-generated OpenAPI docs

**When to use Django:**
- Need ORM and database operations
- Need admin panel
- Building monolithic application
- Need Django's security features

## Alternatives for Specific Features

- **Web Server**: Uvicorn (ASGI)
- **Validation**: Pydantic (built-in)
- **Documentation**: OpenAPI/Swagger (auto-generated)
- **ML Libraries**: scikit-learn, spaCy, transformers
- **Async**: Native async/await

## Review Date

This decision will be reviewed at the end of Sprint 6 when AI service is implemented.

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [FastAPI for Machine Learning](https://fastapi.tiangolo.com/deployment/)

## Notes

- FastAPI is perfect for ML model serving
- Async support crucial for handling concurrent predictions
- Auto-generated documentation simplifies integration
- Clear separation between main backend and AI service
- Can be deployed independently and scaled separately
- Modern, fast, and developer-friendly
- Industry standard for ML API serving
