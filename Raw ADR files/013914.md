# ADR 003: FastAPI for RAG Chatbot Backend

**Status:** Accepted  
**Date:** 2025-11-26  
**Decision Makers:** Hassan RJ, Development Team

---

## Context

The RAG chatbot requires a backend API to handle:
- Chat requests from the frontend
- RAG retrieval from Qdrant vector database
- Integration with Gemini API for LLM inference
- Authentication token validation
- Conversation history management
- Streaming responses to frontend

The backend framework must:
- Support async/await for concurrent request handling
- Provide automatic API documentation
- Enable easy integration with Python AI libraries
- Support CORS for cross-origin requests from Docusaurus frontend
- Have good performance characteristics
- Include built-in validation and type checking

**Alternatives Considered:**
1. **FastAPI** - Modern Python async web framework
2. **Django + DRF** - Full-featured web framework with Django REST Framework
3. **Flask** - Lightweight Python web framework
4. **Express.js** - Node.js web framework
5. **Axum** - Rust async web framework

---

## Decision

We will use **FastAPI** as the backend framework for the RAG chatbot API.

---

## Consequences

### Positive

1. **Async/Await Support**: Native async support for handling multiple concurrent requests efficiently
2. **Automatic Docs**: OpenAPI (Swagger) documentation generated automatically at `/docs`
3. **Type Hints**: Pydantic models for request/response validation with Python type hints
4. **Performance**: One of the fastest Python frameworks (comparable to Node.js/Go)
5. **Python Ecosystem**: Easy integration with OpenAI Agents SDK, Qdrant, sentence-transformers
6. **Developer Experience**: Excellent error messages, auto-completion, IDE support
7. **CORS Middleware**: Built-in CORS support for cross-origin requests
8. **Modern Stack**: WebSocket support for streaming responses
9. **Community**: Active community and frequent updates

### Negative

1. **Async Learning Curve**: Team needs to understand async/await patterns
2. **Deployment Complexity**: Requires ASGI server (Uvicorn, Hypercorn) instead of WSGI
3. **ORMS**: Less mature async ORM ecosystem compared to Django (not applicable - using Supabase)
4. **Production Deployment**: Need to configure workers and process management
5. **File Upload**: More manual configuration compared to Django

### Mitigation

- **Async Learning**: Python async is straightforward, team will learn quickly
- **Deployment**: Use Uvicorn with proper configuration, documentation provided
- **ORMs**: Using Supabase client which has async support built-in
- **Production**: Deploy with Gunicorn + Uvicorn workers or cloud platform
- **File Upload**: Not needed for chatbot API (text-only)

---

## Implementation Notes

### API Structure
```
backend/
├── main.py                 # FastAPI app initialization
├── chatbot.py              # RAG chatbot implementation
├── models/
│   └── schemas.py          # Pydantic models
├── auth/
│   ├── routes.py           # Auth endpoints
│   └── middleware.py       # JWT validation
└── config/
    └── supabase_client.py  # Supabase client setup
```

### Key Endpoints
- `POST /api/chat` - Send message to chatbot, receive streaming response
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Authenticate user
- `GET /api/auth/user` - Get current user from token
- `GET /healthz` - Health check endpoint

### Dependencies
```python
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
supabase==2.0.3
qdrant-client==1.7.0
openai==1.3.0  # For Agents SDK
```

### Deployment Configuration
```python
# main.py
app = FastAPI(
    title="Physical AI RAG Chatbot API",
    description="Backend API for RAG-powered chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://username.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Running Locally
```bash
# Development
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uv run gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## References

- [FastAPI Official Documentation](https://fastapi.tiangolo.com)
- [OpenAI Agents SDK](https://github.com/openai/swarm)
- [Project Constitution](./constitution.md) - Principle 5: Performance Requirements
- [Implementation Plan](../../plans/002-rag-chatbot-backend.md)
