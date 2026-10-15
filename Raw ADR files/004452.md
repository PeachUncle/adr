# ADR 0002 — Technology Stack and Languages

**Date:** 2024-12-04  
**Status:** accepted

## Context

Ursine Arcana requires a technology stack that supports:

- Cross-platform mobile development (iOS and Android)
- Real-time features (chat, presence, notifications)
- Secure handling of user data and media
- Scalability from MVP to production
- Type safety and maintainability

The project owner has specified **TypeScript** as the required language for all application code, with strict mode enabled.

## Decision

### Language & Type Safety

- **Language**: TypeScript for all frontend and backend code
- **Strict Mode**: `tsconfig.json` with `"strict": true`
- **Linting**: ESLint with `@typescript-eslint` plugin
- **Formatting**: Prettier

### Frontend

- **Framework**: React Native (Expo managed workflow)
- **Language**: TypeScript (strict)
- **Styling**: Tailwind CSS v4.0 via NativeWind
- **State Management**: React Context + hooks (Zustand if complexity warrants)
- **Navigation**: React Navigation v6

### Backend

- **Runtime**: Node.js (v20 LTS) on Firebase Functions
- **Language**: TypeScript (strict)
- **API Style**: RESTful HTTP functions + Firestore triggers
- **Authentication**: Firebase Authentication

### Database & Storage

- **Primary Database**: Cloud Firestore
- **File Storage**: Firebase Storage
- **Caching**: Firestore offline persistence (client-side)

### Infrastructure

- **Hosting**: Firebase (Functions, Hosting for admin dashboard)
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **Analytics**: Firebase Analytics (with opt-out)

### Admin Dashboard

- **Framework**: React (web)
- **Language**: TypeScript (strict)
- **Styling**: Tailwind CSS v4.0
- **Hosting**: Firebase Hosting

### TypeScript Configuration (shared base)

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### External Services (ADRs Required)

- **NSFW Moderation**: TBD (Google Cloud Vision or AWS Rekognition)
- **Ads Provider**: TBD (likely Google AdMob)
- **SMS Verification**: Firebase Auth Phone

## Consequences

**Positive:**

- Type safety catches errors at compile time
- Better IDE support (autocomplete, refactoring)
- Self-documenting code via type definitions
- Shared types between frontend and backend
- Strict mode prevents common JavaScript pitfalls

**Negative:**

- Slightly longer initial development time
- Build step required (compilation)
- Learning curve for developers unfamiliar with TypeScript

**Mitigations:**

- Shared types package for frontend/backend consistency
- Comprehensive type definitions for all data models
- ESLint rules to enforce type safety patterns
