# ADR-001: Technology Stack Selection

**Author: JP + 2025-06-15**
**Status**: Accepted
**Date**: 2025-06-15

## Context

The AI Marketing Campaign Post Generator platform requires a modern, scalable technology stack that can support AI-powered marketing content generation. The solution needs to:

1. Handle real-time AI content generation with Gemini and Veo APIs
2. Provide a responsive, modern user interface
3. Scale to support thousands of concurrent users
4. Deploy efficiently on Google Cloud Platform
5. Support rapid development and iteration

## Decision

We have selected the following technology stack:

### Frontend
- **React 18** with TypeScript for the user interface
- **Vite** for fast development and building
- **Tailwind CSS** + **shadcn/ui** for styling and components
- **React Router** for client-side routing
- **React Context** for state management (POC phase)

### Backend
- **Python 3.9+** as the primary backend language
- **Google ADK (Agent Development Kit)** for AI agent orchestration
- **FastAPI** for REST API services (planned)
- **Pydantic** for data validation and serialization

### AI Services
- **Google Gemini** for text generation and summarization
- **Google Veo** for video content generation (planned)
- **Google ADK Sequential Agents** for workflow orchestration

### Database & Storage
- **Firestore** for document storage (campaigns, ideas)
- **Google Cloud Storage** for media assets
- **Browser localStorage** for temporary POC storage

### Infrastructure & Deployment
- **Google Cloud Platform** as the primary cloud provider
- **Cloud Run** for containerized backend services
- **Firebase Hosting** for frontend deployment
- **Docker** for containerization
- **GitHub Actions** for CI/CD

## Alternatives Considered

### Frontend Alternatives
- **Next.js**: Rejected due to complexity for this use case
- **Vue.js**: Rejected due to team familiarity with React
- **Angular**: Rejected due to overhead for this project size

### Backend Alternatives
- **Node.js**: Rejected due to Python ADK requirement
- **Django**: Rejected due to FastAPI's better async support
- **Flask**: Considered but FastAPI chosen for better OpenAPI support

### Database Alternatives
- **PostgreSQL**: Rejected due to Google Cloud native preference
- **MongoDB**: Rejected due to Firestore's better GCP integration
- **Redis**: Will be used for caching, not primary storage

## Consequences

### Positive
- **Rapid Development**: React + TypeScript enables fast UI development
- **AI Integration**: Python ADK provides direct access to Google AI services
- **Scalability**: Google Cloud services can scale automatically
- **Type Safety**: TypeScript and Pydantic provide end-to-end type safety
- **Modern DX**: Vite and modern tooling provide excellent developer experience

### Negative
- **Learning Curve**: Team needs to learn Google ADK and Firestore
- **Vendor Lock-in**: Heavy dependency on Google Cloud services
- **Complexity**: Multiple technologies require coordination
- **Cost**: Google Cloud services may be expensive at scale

### Risks
- **API Limits**: Gemini/Veo APIs may have rate limits or availability issues
- **Technology Changes**: Google ADK is relatively new and may evolve rapidly
- **Integration Complexity**: Frontend-backend integration requires careful design

## Implementation Notes

1. Start with POC using mocked AI functions
2. Gradually replace mocks with real ADK integration
3. Use 2 Musketeers pattern with Makefile for consistent development
4. Implement proper error handling and fallback strategies
5. Monitor performance and costs closely during development

## Review Date

This ADR should be reviewed after MVP completion (estimated 6 weeks) to assess if the technology choices are meeting project needs. 