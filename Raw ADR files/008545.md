# ADR-005: FastAPI Backend Architecture

**Date**: 2025-12-31  
**Status**: Accepted  
**Decision Makers**: Architecture Team  
**Technical Story**: RESTful API Design for CV Checker

## Context

CV Checker requires a web API to:
- Accept CV and job description inputs from AG-UI frontend
- Orchestrate AI agent workflow for analysis
- Return structured analysis results
- Support future features (history, user management, batch processing)

Framework considerations evaluated:
1. **FastAPI**: Modern, async-first, automatic OpenAPI docs, type hints
2. **Flask**: Mature, simple, but synchronous by default
3. **Django REST Framework**: Full-featured but heavyweight for our needs

Key requirements:
- Async support for AI agent workflows
- Type safety and validation
- CORS support for AG-UI frontend
- Clean error handling
- API versioning for future compatibility
- Development speed and simplicity

## Decision

We will use **FastAPI** as the backend framework with a **RESTful API design** focused on a single primary endpoint for v1.

### API Structure

```
POST /api/v1/analyze
  - Input: CV markdown + job description
  - Output: Analysis result with score, recommendations, gaps, strengths

GET /api/v1/health
  - Health check endpoint

GET /api/v1/openapi.json
  - Auto-generated OpenAPI specification
```

### Key Design Principles

1. **Async-First**: All endpoints use async handlers for agent workflow
2. **Type Safety**: Pydantic models for request/response validation
3. **Versioning**: `/api/v1/` prefix allows future breaking changes
4. **Stateless**: No session management in v1 (aligned with ADR-004)
5. **CORS Enabled**: Allow AG-UI frontend to call API
6. **Structured Errors**: Consistent error response format

## Implementation

### FastAPI Application Setup

```python
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("CV Checker API starting up...")
    # Future: Initialize Cosmos DB connection, load models, etc.
    yield
    logger.info("CV Checker API shutting down...")
    # Future: Cleanup resources

app = FastAPI(
    title="CV Checker API",
    description="AI-powered CV analysis and job matching",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# CORS configuration for AG-UI frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local AG-UI development
        "http://localhost:5000",  # Alternative port
        "https://*.azurewebsites.net",  # Azure deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Request/Response Models

```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any

class AnalyzeRequest(BaseModel):
    """Request model for CV analysis."""
    cv_markdown: str = Field(
        ..., 
        min_length=100,
        max_length=50000,
        description="CV content in Markdown format"
    )
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Job description text"
    )
    
    @validator('cv_markdown', 'job_description')
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "cv_markdown": "# John Doe\n\n## Experience\n\n**Senior Python Developer**...",
                "job_description": "We are seeking a Senior Python Developer with 5+ years..."
            }
        }

class SkillMatchResponse(BaseModel):
    """Individual skill match in response."""
    skill_name: str
    required: bool
    candidate_has: bool
    proficiency_level: str | None = None
    years_experience: float | None = None
    match_score: float = Field(ge=0.0, le=1.0)

class AnalyzeResponse(BaseModel):
    """Response model for CV analysis."""
    analysis_id: str = Field(description="Unique analysis identifier")
    overall_score: float = Field(
        ge=0.0, 
        le=100.0,
        description="Overall match score (0-100)"
    )
    skill_matches: List[SkillMatchResponse] = Field(
        description="Detailed skill matching results"
    )
    experience_match: Dict[str, Any] = Field(
        description="Experience level analysis"
    )
    education_match: Dict[str, Any] = Field(
        description="Education requirements analysis"
    )
    strengths: List[str] = Field(
        description="Candidate strengths for this role"
    )
    gaps: List[str] = Field(
        description="Identified skill/experience gaps"
    )
    recommendations: List[str] = Field(
        description="Actionable recommendations"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
                "overall_score": 85.5,
                "skill_matches": [
                    {
                        "skill_name": "Python",
                        "required": True,
                        "candidate_has": True,
                        "proficiency_level": "advanced",
                        "years_experience": 5.0,
                        "match_score": 1.0
                    }
                ],
                "experience_match": {
                    "required_years": 5,
                    "candidate_years": 6,
                    "match": True
                },
                "education_match": {
                    "required": "Bachelor's in Computer Science",
                    "candidate": "Master's in Computer Science",
                    "match": True
                },
                "strengths": [
                    "Strong Python expertise with 6 years experience",
                    "Advanced cloud architecture skills",
                    "Excellent leadership experience"
                ],
                "gaps": [
                    "Limited Kubernetes experience",
                    "No mention of GraphQL"
                ],
                "recommendations": [
                    "Consider Kubernetes certification to strengthen DevOps profile",
                    "Add GraphQL projects to portfolio",
                    "Highlight any microservices experience more prominently"
                ]
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Dict[str, Any] | None = Field(
        default=None,
        description="Additional error context"
    )
```

### Main API Endpoint

```python
from fastapi import Depends, Request
from time import time

@app.post(
    "/api/v1/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze CV against job description",
    description="Submit a CV and job description to receive detailed matching analysis",
    responses={
        200: {
            "description": "Successful analysis",
            "model": AnalyzeResponse
        },
        400: {
            "description": "Invalid request (e.g., empty CV or job description)",
            "model": ErrorResponse
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error (e.g., AI service failure)",
            "model": ErrorResponse
        }
    }
)
async def analyze_cv(
    request: AnalyzeRequest,
    service: CVCheckerService = Depends(get_service)
) -> AnalyzeResponse:
    """
    Analyze CV against job description using AI agents.
    
    This endpoint orchestrates a multi-agent workflow to:
    1. Parse job requirements
    2. Parse CV content
    3. Perform comparative analysis
    4. Generate recommendations
    
    Returns comprehensive matching results with scores and recommendations.
    """
    start_time = time()
    
    try:
        logger.info(f"Starting CV analysis - CV length: {len(request.cv_markdown)}, "
                   f"JD length: {len(request.job_description)}")
        
        # Execute agent workflow (from ADR-001)
        analysis_result = await service.analyze_cv(
            cv_markdown=request.cv_markdown,
            job_description=request.job_description
        )
        
        # Convert internal model to API response
        response = AnalyzeResponse(
            analysis_id=analysis_result.id,
            overall_score=analysis_result.overall_score,
            skill_matches=[
                SkillMatchResponse(**match.model_dump()) 
                for match in analysis_result.skill_matches
            ],
            experience_match=analysis_result.experience_match,
            education_match=analysis_result.education_match,
            strengths=analysis_result.strengths,
            gaps=analysis_result.gaps,
            recommendations=analysis_result.recommendations
        )
        
        elapsed = time() - start_time
        logger.info(f"Analysis completed successfully in {elapsed:.2f}s - "
                   f"Score: {response.overall_score}")
        
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e),
                "details": {"field": "unknown"}
            }
        )
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "AnalysisError",
                "message": "Failed to complete CV analysis",
                "details": {"error_type": type(e).__name__}
            }
        )
```

### Health Check Endpoint

```python
from fastapi import status as http_status

@app.get(
    "/api/v1/health",
    status_code=http_status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Basic health status and version information
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "cv-checker-api"
    }
```

### Error Handling Middleware

```python
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic validation errors."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": {
                "errors": exc.errors(),
                "body": exc.body
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception on {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {
                "error_type": type(exc).__name__
            }
        }
    )
```

### Running the Application

```python
# main.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development only
        log_level="info"
    )
```

### Example Usage

```bash
# Start the server
python main.py

# Test with curl
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_markdown": "# John Doe\n\n## Skills\n- Python (5 years)\n- FastAPI\n- Azure",
    "job_description": "Senior Python Developer needed with 3+ years experience in FastAPI and cloud platforms."
  }'

# Response
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "overall_score": 87.5,
  "skill_matches": [
    {
      "skill_name": "Python",
      "required": true,
      "candidate_has": true,
      "proficiency_level": "advanced",
      "years_experience": 5.0,
      "match_score": 1.0
    }
  ],
  "strengths": ["Strong Python experience exceeds requirements"],
  "gaps": ["No specific mention of cloud deployment experience"],
  "recommendations": ["Highlight Azure deployment projects"]
}
```

## Consequences

### Positive

- **Auto-Generated Docs**: OpenAPI/Swagger UI at `/api/v1/docs` for free
- **Type Safety**: Pydantic catches errors before processing
- **Async Performance**: Native async support for AI agent workflows
- **Developer Experience**: Fast reload, excellent IDE support, clear error messages
- **API Versioning**: `/api/v1/` allows future non-breaking evolution
- **CORS Ready**: AG-UI frontend can call API directly
- **Testability**: Easy to write unit and integration tests with FastAPI TestClient
- **Production Ready**: Uvicorn/Gunicorn support for deployment

### Negative

- **Learning Curve**: Team must learn FastAPI patterns (minor - well documented)
- **Async Complexity**: Requires understanding of async/await patterns
- **Version Management**: Must maintain `/api/v1/` compatibility when adding `/api/v2/`

### Testing Strategy

```python
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

def test_analyze_success():
    """Test successful CV analysis."""
    response = client.post("/api/v1/analyze", json={
        "cv_markdown": "# Test CV\n\n## Skills\n- Python",
        "job_description": "Python developer needed"
    })
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert 0 <= data["overall_score"] <= 100

def test_analyze_empty_cv():
    """Test validation for empty CV."""
    response = client.post("/api/v1/analyze", json={
        "cv_markdown": "",
        "job_description": "Python developer needed"
    })
    assert response.status_code == 422

def test_health_check():
    """Test health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Deployment Configuration

```yaml
# Azure App Service example
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
azure-identity==1.15.0
# ... other dependencies

# Note: This project uses uv as the standard package manager
# Install: curl -LsSf https://astral.sh/uv/install.sh | sh
# Usage: uv pip install -r requirements.txt

# startup.sh
#!/bin/bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# App Service Configuration
PORT=8000
WEBSITES_PORT=8000
```

### Development Tooling

**Package Manager**: This project uses [**uv**](https://github.com/astral-sh/uv) as the standard Python package manager for significantly faster installations compared to pip.

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Add new package
uv pip install package-name

# Update requirements
uv pip freeze > requirements.txt
```

**Benefits of uv**:
- 10-100x faster than pip
- Compatible with existing pip workflows
- Works with requirements.txt and pyproject.toml
- Better dependency resolution

## Related Decisions

- ADR-001: Sequential agent workflow integrates as async service calls
- ADR-002: Azure OpenAI client initialized in service layer
- ADR-004: Stateless design aligns with in-memory v1 approach

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Azure App Service FastAPI Deployment](https://learn.microsoft.com/azure/app-service/quickstart-python)
