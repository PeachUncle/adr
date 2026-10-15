# ADR-003: Use Firebase for Authentication and Database

## Status

**Accepted** - December 2024

## Context

The receiptscan-backend requires:
- User authentication and authorization
- Scalable NoSQL database for receipts and user data
- File storage for receipt images
- Real-time updates (potential future feature)
- Minimal operational overhead

We needed a backend-as-a-service (BaaS) solution that integrates well with our tech stack and provides enterprise-grade security without requiring extensive infrastructure management.

## Decision

We will use **Firebase** (Google's mobile and web application development platform) for:

1. **Firebase Authentication**: User authentication with JWT tokens
2. **Cloud Firestore**: NoSQL document database for structured data
3. **Cloud Storage**: File storage for receipt images
4. **Firebase Admin SDK**: Server-side integration

### Key Components

- **Authentication**: Firebase Auth with JWT token verification
- **Database**: Firestore for receipts, users, audit logs
- **Storage**: Cloud Storage for receipt images with signed URLs
- **Security**: Firestore Security Rules for data access control

## Consequences

### Positive

- **Managed Infrastructure**: No need to manage servers or databases
- **Scalability**: Automatically scales with usage
- **Security**: Enterprise-grade security built-in
- **Authentication**: Robust auth system with multiple providers
- **Real-time Capabilities**: Firestore supports real-time updates
- **Integration**: Official SDKs for Node.js with TypeScript support
- **Cost-Effective**: Pay-as-you-go pricing
- **Developer Experience**: Excellent documentation and tooling
- **Backup & Recovery**: Automated backups included

### Negative

- **Vendor Lock-in**: Tightly coupled to Firebase/Google Cloud ecosystem
- **Cost at Scale**: Can become expensive with high usage
- **Query Limitations**: Firestore has some query constraints compared to SQL
- **Learning Curve**: Team needs to learn Firebase concepts
- **Offline Support**: Limited control over offline behavior in server environments

### Neutral

- **NoSQL Database**: Different paradigm from traditional SQL databases
- **Managed Service**: Less control over infrastructure configuration

## Implementation

### Authentication
```typescript
import admin from 'firebase-admin';

// Verify Firebase ID tokens
const decodedToken = await admin.auth().verifyIdToken(idToken);
const userId = decodedToken.uid;
```

### Database Operations
```typescript
// Firestore queries
const receipts = await db.collection('receipts')
  .where('userId', '==', userId)
  .where('date', '>=', startDate)
  .orderBy('date', 'desc')
  .limit(20)
  .get();
```

### File Storage
```typescript
// Upload with signed URL
const file = bucket.file(filePath);
await file.save(buffer);
const [url] = await file.getSignedUrl({
  action: 'read',
  expires: Date.now() + 3600 * 1000, // 1 hour
});
```

## Alternatives Considered

1. **AWS (Cognito + DynamoDB + S3)**
   - Pros: More flexible, enterprise features
   - Cons: More complex setup, steeper learning curve
   - Reason rejected: Higher operational complexity

2. **MongoDB Atlas + Auth0**
   - Pros: Familiar SQL-like queries, flexible auth
   - Cons: Requires managing multiple services
   - Reason rejected: Additional integration complexity

3. **PostgreSQL + Passport.js**
   - Pros: Full SQL capabilities, complete control
   - Cons: Requires server management, more code for auth
   - Reason rejected: Higher operational overhead

4. **Supabase**
   - Pros: Open-source Firebase alternative
   - Cons: Smaller ecosystem, less mature
   - Reason rejected: Less enterprise-proven

## Mitigation Strategies

### Vendor Lock-in
- Abstract Firebase operations behind repository layer
- Use standard interfaces (e.g., `UserRepository`) to enable future migration
- Keep business logic independent of Firebase-specific features

### Cost Management
- Implement caching to reduce database reads
- Use Firestore indexes efficiently
- Monitor usage with Firebase Console
- Set up budget alerts

### Query Limitations
- Design data models to work with Firestore's query capabilities
- Use composite indexes for complex queries
- Denormalize data where appropriate

## Migration Path

If we need to migrate away from Firebase:

1. Implement new repository layer with different database
2. Run dual-write temporarily (both Firebase and new DB)
3. Migrate data incrementally
4. Switch read operations to new DB
5. Remove Firebase dependencies

## References

- [Firebase Documentation](https://firebase.google.com/docs)
- [Cloud Firestore](https://firebase.google.com/docs/firestore)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
