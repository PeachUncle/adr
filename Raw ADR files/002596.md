# ADR-0001: CMS and API Separation

**Status**: Accepted
**Date**: 2025-10-31 (Retroactive documentation)
**Deciders**: Original Architecture Team
**Related ADRs**: None

## Context

The MPSM Dashboard needs to interact with HP's SDS API to retrieve device data. We need to decide how to structure the application layers and where to handle authentication, API calls, and data presentation.

### Driving Factors:
- HP SDS API requires OAuth token management
- Frontend needs to display device data dynamically
- Security concerns with exposing API credentials
- Need for session management and user authentication
- Desire to keep frontend code maintainable

## Decision

We will implement a **three-tier architecture** with clear separation of concerns:

1. **Frontend (Browser)**: HTML/CSS/JavaScript presentation layer
2. **CMS Layer (PHP)**: Presentation logic, session management, API proxy
3. **mps-api Backend**: Authentication proxy, token management

### Architecture:

```
Browser → CMS (PHP/JS) → mps-api → HP SDS API
```

### Responsibilities:

**CMS Layer** (`/cms`):
- Serves HTML/CSS/JavaScript to browser
- Handles user authentication (login/logout)
- Manages PHP sessions
- Proxies API requests to mps-api
- Contains presentation logic (dashboard cards, modals)

**mps-api Backend** (`/mps-api`):
- Handles OAuth token acquisition and refresh
- Proxies authenticated requests to HP SDS API
- Returns JSON responses to CMS
- No direct frontend access

**Frontend (JavaScript)**:
- Dynamic UI updates
- AJAX calls to CMS API endpoints (not direct to mps-api)
- State management
- User interactions

## Consequences

### Positive
- **Security**: API credentials never exposed to browser
- **Separation of Concerns**: Clear boundaries between layers
- **Maintainability**: Each layer can be modified independently
- **Token Management**: Centralized in mps-api
- **Caching**: Can implement caching at CMS layer
- **Testing**: Each layer can be tested separately

### Negative
- **Additional Latency**: Extra hop through CMS layer
- **Complexity**: More moving parts to deploy and maintain
- **Debugging**: Harder to trace requests through multiple layers
- **Deployment**: Requires deploying two separate codebases (CMS + mps-api)

### Neutral
- **API Versioning**: Changes to HP API only affect mps-api layer
- **Authentication**: OAuth complexity hidden from frontend developers

## Implementation

### Directory Structure:
```
MPSM-Dashboard/
├── cms/                 # Frontend + Presentation Layer
│   ├── api/            # API endpoints (proxy to mps-api)
│   │   ├── login.php
│   │   ├── get-devices.php
│   │   └── get-supply-alerts.php
│   ├── assets/
│   │   ├── app.js      # Frontend JavaScript
│   │   └── style.css
│   ├── config.php      # Configuration
│   ├── functions.php   # Shared utilities
│   └── index.php       # Entry point
└── mps-api/            # Separate deployment
    └── query           # Query endpoint
```

### API Call Flow:
1. Frontend calls `cms/api/get-devices.php`
2. CMS PHP script calls `mps-api/query` with action `Device/List`
3. mps-api acquires/refreshes OAuth token
4. mps-api calls HP SDS API
5. mps-api returns JSON to CMS
6. CMS returns JSON to frontend
7. Frontend updates UI

### Configuration:
- CMS config: `cms/config.php` (defines mps-api URL, defaults)
- mps-api config: Environment variables (OAuth credentials)

## Alternatives Considered

### Alternative 1: Direct Frontend to API
**Description**: Frontend JavaScript calls HP SDS API directly

**Rejected Because**:
- Exposes OAuth credentials to browser (security risk)
- No server-side session management
- CORS issues with HP API
- No caching layer possible

### Alternative 2: Monolithic PHP Application
**Description**: Single PHP application handles everything

**Rejected Because**:
- Tightly couples presentation and API logic
- Harder to scale independently
- OAuth token management mixed with UI code
- Difficult to test components in isolation

### Alternative 3: Serverless Functions
**Description**: Use AWS Lambda or similar for API proxy

**Rejected Because**:
- Adds cloud infrastructure dependency
- Increases cost
- More complex deployment
- Current PHP hosting already available

## References

- Engineering Standards (in codebase comments)
- HP SDS API Documentation (external)
- OAuth 2.0 Specification

## Notes

This architecture has been in place since project inception. This ADR is being written retroactively to document the existing decision for future reference and to guide new developers.
