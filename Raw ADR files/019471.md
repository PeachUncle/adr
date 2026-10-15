# ADR-002: Firebase as Primary Backend

**Status**: Accepted  
**Date**: 2024-10-01  
**Author**: Backend Lead  

## Context

TypeB needs a scalable backend solution that can handle real-time updates, user authentication, file storage, and push notifications. The team is small with limited backend expertise and needs to launch quickly.

## Decision

We will use Firebase (Firestore, Auth, Storage, Functions, FCM) as our primary backend infrastructure.

## Consequences

### Positive
- **Rapid development**: Pre-built auth, database, storage solutions
- **Real-time updates**: Built-in real-time synchronization
- **Managed infrastructure**: No servers to maintain
- **Automatic scaling**: Handles growth automatically
- **Cost-effective at start**: Generous free tier, pay-as-you-grow
- **Security**: Google-managed infrastructure with compliance certifications
- **Client SDKs**: Excellent React Native and web support

### Negative
- **Vendor lock-in**: Difficult to migrate away from Firebase
- **Limited query capabilities**: NoSQL limitations, no JOINs
- **Cost at scale**: Can become expensive with high usage
- **Cold starts**: Cloud Functions have latency on first invocation
- **Limited customization**: Must work within Firebase constraints

### Neutral
- NoSQL database requires different thinking than SQL
- Security rules have learning curve
- Requires careful data structure planning

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Custom Node.js + PostgreSQL | Full control, SQL queries, predictable costs | Requires DevOps, slower development, more complexity | Too much overhead for MVP |
| AWS Amplify | Similar to Firebase, AWS ecosystem | Steeper learning curve, less mature | Team unfamiliar with AWS |
| Supabase | Open source, PostgreSQL, similar features | Less mature, smaller community | Higher risk for production |
| Parse Platform | Open source, self-hosted option | Requires hosting, less features | More operational overhead |

## Implementation

### Architecture
```
Client Apps (Web/Mobile)
    ↓
Firebase SDK
    ↓
├── Firebase Auth (Authentication)
├── Firestore (Database)
├── Cloud Storage (Photos)
├── Cloud Functions (Business Logic)
└── FCM (Push Notifications)
```

### Data Structure
```javascript
// Collections
users/{userId}
families/{familyId}
tasks/{taskId}
photos/{photoId}
analytics/{eventId}
```

### Security Strategy
- Row-level security via Firestore rules
- Custom claims for role-based access
- Server-side validation in Cloud Functions

### Cost Management
- Monitor usage via Firebase Console
- Set budget alerts
- Implement caching strategies
- Archive old data

## Migration Path (Future)

If we need to migrate away from Firebase:
1. Abstract Firebase calls behind service interfaces
2. Implement data export functions
3. Gradually move to hybrid architecture
4. Use Firebase as cache/real-time layer only

## References

- [Firebase Pricing](https://firebase.google.com/pricing)
- [Firestore Best Practices](https://firebase.google.com/docs/firestore/best-practices)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)
- ADR-003: Data Model Design (future)
