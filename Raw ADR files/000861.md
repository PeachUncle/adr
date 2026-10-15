# ADR-000: Context Sync and Project Foundation

**Date:** 2025-10-17  
**Status:** Accepted  
**Deciders:** Development Team  

## Context

Starting development of Basketball AI Ecosystem MVP with the following components:
- AI jump-shot critique using MediaPipe Pose → TensorFlow Lite
- Training blueprints & EvalRank system
- Community feed
- Auth, storage, payments-ready infrastructure

## Context Files Analysis

The mentioned context files (VIDEO_UPLOAD_FIX.md, VIDEO_RENDERING_FIX.md, API_FIXES_COMPLETE.md, ACCURACY_IMPROVEMENTS.md) were not found in the current repository state. The repository appears to be in an initial state with only basic configuration files.

## Technology Stack Decisions

### Frontend
- React Native with Expo for cross-platform mobile development
- TypeScript for type safety
- Expo Camera for video recording

### Backend
- Node.js with Express/Fastify (to be determined based on performance needs)
- PostgreSQL for primary database
- Redis for caching and sessions

### AI/ML
- MediaPipe Pose for keypoint extraction
- TensorFlow Lite for on-device inference
- FastAPI microservice for AI processing (optional for low-end devices)

### Infrastructure
- Firebase Auth for authentication (JWT tokens)
- AWS S3 + CloudFront for video storage and CDN
- Stripe for payments (prepared, can be stubbed)
- Sentry for error tracking
- GA4/Amplitude for analytics

### Development
- pnpm for package management (workspace support)
- ESLint + Prettier for code formatting
- GitHub Actions for CI/CD
- Feature flags for risky changes

## Project Structure

```
/
├── src/                 # React Native/Expo app
├── backend/             # API service
├── packages/            # Shared packages
├── docs/                # Documentation and ADRs
├── .github/             # GitHub workflows and templates
└── tools/               # Development tools and scripts
```

## Next Steps

1. Implement T-001: Monorepo & Tooling setup
2. Set up backend health endpoints (T-002)
3. Configure Firebase Auth integration (T-003)
4. Design and implement Postgres schema (T-004)
5. Set up CI/CD pipeline (T-005)

## Consequences

- Establishes clear technology boundaries
- Enables rapid iteration with proper tooling
- Provides foundation for scalable architecture
- Sets up observability from day one
