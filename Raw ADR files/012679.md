# ADR 001: Technology Stack Selection

## Status
Accepted

## Context
The Nx System Calculator requires a modern, maintainable web application stack that can:
- Perform complex calculations efficiently
- Provide a responsive, accessible UI
- Generate PDF reports
- Support API integrations
- Run optimally on Apple Silicon
- Be easily deployable and maintainable

Using the Recursive Iterative Self-Consistency (RISC) protocol, we evaluated three distinct approaches.

## Decision Approaches Evaluated

### Approach 1: React + Vite + FastAPI + Python
**Architecture:**
- Frontend: React 18 with Vite for fast builds
- Backend: FastAPI (Python 3.11+) for API
- Calculation Engine: Pure Python modules
- PDF Generation: ReportLab
- State Management: Zustand
- Database: SQLite for development, PostgreSQL for production

**Pros:**
- Python excellent for mathematical calculations
- FastAPI provides automatic OpenAPI documentation
- ReportLab mature for PDF generation
- Python ecosystem rich for data processing
- Type hints with Pydantic for validation
- Excellent Apple Silicon support (native Python 3.11+)
- Separation of concerns (frontend/backend)

**Cons:**
- Two separate codebases to maintain
- Requires CORS configuration
- More complex deployment (two services)
- Python slower than compiled languages for some operations

**Complexity Score:** 7/10
**Maintainability Score:** 8/10
**Performance Score:** 7/10
**Apple Silicon Optimization:** 9/10

### Approach 2: Next.js + Node.js + TypeScript
**Architecture:**
- Full-stack: Next.js 14 with App Router
- Language: TypeScript throughout
- Calculation Engine: TypeScript modules
- PDF Generation: Puppeteer or PDFKit
- State Management: React Context + Server Components
- Database: PostgreSQL with Prisma ORM

**Pros:**
- Single codebase for frontend and backend
- TypeScript provides excellent type safety
- Server components reduce client bundle size
- Built-in API routes
- Excellent developer experience
- Strong ecosystem for modern web apps
- Good Apple Silicon support

**Cons:**
- JavaScript/TypeScript less ideal for complex math
- Puppeteer heavy for PDF generation
- Server components learning curve
- More opinionated framework

**Complexity Score:** 6/10
**Maintainability Score:** 9/10
**Performance Score:** 8/10
**Apple Silicon Optimization:** 8/10

### Approach 3: Vue 3 + Django + Python
**Architecture:**
- Frontend: Vue 3 with Composition API
- Backend: Django 4.x with Django REST Framework
- Calculation Engine: Python modules
- PDF Generation: WeasyPrint or ReportLab
- State Management: Pinia
- Database: PostgreSQL

**Pros:**
- Django batteries-included approach
- Python for calculations
- Vue 3 lightweight and performant
- Django admin for configuration management
- Mature ecosystem

**Cons:**
- Django heavier than FastAPI
- More boilerplate than FastAPI
- Vue smaller ecosystem than React
- Django ORM overhead for simple operations

**Complexity Score:** 7/10
**Maintainability Score:** 7/10
**Performance Score:** 6/10
**Apple Silicon Optimization:** 8/10

## RISC Synthesis

After evaluating all three approaches, we synthesize the optimal solution:

**Selected: Hybrid of Approach 1 with enhancements**
- **Frontend:** React 18 + Vite + TypeScript
- **Backend:** FastAPI + Python 3.11+
- **Calculation Engine:** Pure Python with NumPy for performance
- **PDF Generation:** ReportLab with Pillow for images
- **State Management:** Zustand (lightweight, simple)
- **Database:** SQLite (development), PostgreSQL (production)
- **API Documentation:** Auto-generated via FastAPI
- **Testing:** Pytest (backend), Vitest + Testing Library (frontend)

### Rationale for Synthesis

1. **Python for Calculations:** Python's mathematical libraries and readability make it ideal for the calculation engine. NumPy provides Apple Silicon optimization via Accelerate framework.

2. **FastAPI for API:** Automatic OpenAPI docs, excellent performance, modern async support, and Pydantic validation align perfectly with our needs.

3. **React + Vite for Frontend:** React's ecosystem, component reusability, and Vite's speed provide the best developer experience. TypeScript adds type safety.

4. **Separation of Concerns:** Clear boundary between calculation logic and presentation allows independent scaling and testing.

5. **Apple Silicon Optimization:** Python 3.11+ and NumPy leverage Apple's Accelerate framework. Vite uses esbuild (Go-based) which is fast on ARM64.

## Risk Mitigation

### Risk 1: CORS Complexity
**Mitigation:** Use FastAPI CORS middleware with proper configuration. Document setup clearly.

### Risk 2: Deployment Complexity (Two Services)
**Mitigation:** Provide Docker Compose configuration for single-command deployment. Create unified deployment scripts.

### Risk 3: Type Safety Across Boundary
**Mitigation:** Generate TypeScript types from Pydantic models using tools like `pydantic-to-typescript`. Maintain OpenAPI spec as contract.

### Risk 4: PDF Generation Performance
**Mitigation:** Implement async PDF generation with background tasks. Cache common elements. Optimize ReportLab usage.

## Implementation Guidelines

### Project Structure
```
nx_system_calc/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── calculations/
│   │   │   ├── pdf/
│   │   │   └── email/
│   │   └── schemas/
│   ├── tests/
│   ├── config/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── tests/
│   └── package.json
├── docs/
├── config/
└── docker-compose.yml
```

### Technology Versions
- Python: 3.11+
- FastAPI: 0.104+
- React: 18.2+
- Vite: 5.0+
- TypeScript: 5.3+
- Node.js: 20 LTS

## Consequences

### Positive
- Clear separation enables independent development and testing
- Python calculation engine can be reused in other contexts
- FastAPI provides excellent API documentation automatically
- React ecosystem provides rich component libraries
- Type safety across the stack (Python type hints + TypeScript)
- Excellent performance on Apple Silicon

### Negative
- Need to maintain two separate dependency sets
- CORS configuration required
- Slightly more complex deployment than monolith
- Need to keep API contract in sync

### Neutral
- Team needs familiarity with both Python and TypeScript
- Two sets of testing frameworks to maintain

## References
- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Documentation: https://react.dev/
- Vite Documentation: https://vitejs.dev/
- ReportLab Documentation: https://www.reportlab.com/docs/
- Apple Silicon Python Optimization: https://developer.apple.com/metal/tensorflow-plugin/

## Date
2025-10-03

## Authors
AI Coding Assistant (RISC Protocol v6.0)

