# ADR 003: Database Technology Choice

**Status:** Accepted  
**Date:** January 2025  
**Deciders:** Development Team

## Context

The application requires a database solution for storing various types of content:

- Blog posts with metadata, tags, and reactions
- Book collection with reading status and notes
- CV/resume data with structured sections
- Signals/newsletter data with categorization
- User feedback and analytics data
- Admin configurations and settings

Key requirements:

- Real-time updates for admin interface
- Flexible schema for different content types
- Good performance for read-heavy workloads
- Scalability for growing content
- Integration with authentication system
- Minimal operational overhead

Options considered:

1. **PostgreSQL** - Relational database with JSON support
2. **MongoDB** - Document database with flexible schema
3. **Firebase Firestore** - Managed NoSQL with real-time features
4. **Supabase** - PostgreSQL with Firebase-like features

## Decision

We chose **Firebase Firestore** as our primary database solution.

### Database Architecture

#### Collections Structure

```
/blog-posts/{postId}
  - title, content, slug, published, tags
  - reactions: { likes, dislikes }
  - metadata: { createdAt, updatedAt, author }

/books/{bookId}
  - title, author, isbn, status, rating
  - notes, dateAdded, dateRead
  - categories, coverImage

/cv-data/current
  - personal: { name, title, email }
  - experience: [{ company, position, dates }]
  - education, skills, training

/signals/{signalId}
  - title, type, url, description
  - author, publishedDate, tags
  - createdAt, updatedAt

/feedback/{feedbackId}
  - category, message, page, timestamp
  - sessionId, userAgent, status

/analytics/{date}
  - pageViews, uniqueVisitors, metrics
  - aggregated daily statistics
```

#### Security Rules

```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Public read access for published content
    match /blog-posts/{postId} {
      allow read: if resource.data.published == true;
      allow write: if request.auth != null &&
                      request.auth.token.admin == true;
    }

    // User-specific book collections
    match /books/{bookId} {
      allow read, write: if request.auth != null &&
                            request.auth.uid == resource.data.userId;
    }
  }
}
```

## Implementation Details

### Firebase Admin SDK (Server-side)

```typescript
// Server-side database operations
import { getAdminFirestore } from "@/lib/firebase-admin";

const db = getAdminFirestore();
const blogPosts = await db
  .collection("blog-posts")
  .where("published", "==", true)
  .orderBy("publishedAt", "desc")
  .limit(10)
  .get();
```

### Firebase Client SDK (Client-side)

```typescript
// Real-time data updates
import { onSnapshot, collection } from "firebase/firestore";

const unsubscribe = onSnapshot(collection(db, "blog-posts"), (snapshot) => {
  const posts = snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
  }));
  setPosts(posts);
});
```

### Data Modeling Patterns

- **Denormalization:** Store frequently accessed data together
- **Subcollections:** Use for related data that grows over time
- **Composite Indexes:** Optimize for common query patterns
- **Atomic Updates:** Use transactions for data consistency

## Consequences

### Positive

- **Real-time Updates:** Automatic UI updates when data changes
- **Scalability:** Google's infrastructure handles scaling automatically
- **Security:** Built-in security rules with authentication integration
- **Offline Support:** Client SDK provides offline capabilities
- **No Server Management:** Fully managed service reduces operational overhead
- **Integration:** Seamless integration with Firebase Auth
- **Performance:** Global CDN and optimized for mobile/web

### Negative

- **Vendor Lock-in:** Dependent on Google Cloud Platform
- **Query Limitations:** No complex JOINs or advanced SQL features
- **Cost Predictability:** Pricing based on reads/writes can be unpredictable
- **Learning Curve:** NoSQL thinking required for data modeling
- **Limited Analytics:** No built-in advanced analytics like SQL databases

### Neutral

- **Schema Flexibility:** Can be an advantage or disadvantage depending on needs
- **Consistency Model:** Eventually consistent, acceptable for our use case

## Performance Optimizations

### Indexing Strategy

```javascript
// Composite indexes for common queries
db.collection("blog-posts")
  .where("published", "==", true)
  .where("tags", "array-contains", "tech")
  .orderBy("publishedAt", "desc");

// Single field indexes
-publishedAt(descending) - tags(array) - status(ascending);
```

### Caching Strategy

- **Client-side:** Firebase SDK automatic caching
- **Server-side:** Redis cache for frequently accessed data
- **CDN:** Static content served from edge locations

### Query Optimization

- Limit query results with pagination
- Use composite indexes for complex queries
- Denormalize data to reduce read operations
- Batch operations for multiple document updates

## Data Migration Strategy

### Current Data Structure

All data is already in Firestore with the established schema. Migration considerations for future:

### Schema Evolution

- Add new fields with default values
- Use versioning for breaking changes
- Implement gradual migration scripts
- Maintain backward compatibility

### Backup and Recovery

- Daily automated backups to Cloud Storage
- Point-in-time recovery capabilities
- Export/import tools for data portability
- Regular backup testing procedures

## Security Considerations

### Data Protection

- **Encryption:** Data encrypted at rest and in transit
- **Access Control:** Firestore security rules enforce permissions
- **Audit Logging:** All database operations logged
- **Personal Data:** Compliance with data protection regulations

### Security Rules Validation

```javascript
// Test security rules
await firebase.assertFails(db.collection("admin-only").add({ data: "test" }));

await firebase.assertSucceeds(
  adminDb.collection("admin-only").add({ data: "test" }),
);
```

## Monitoring and Observability

### Key Metrics

- Read/write operations per second
- Query performance and latency
- Error rates and failed operations
- Storage usage and growth trends

### Alerting

- High error rates on database operations
- Unusual query patterns or performance degradation
- Approaching quota limits
- Security rule violations

## Alternative Considerations

### When to Reconsider

- **Complex Analytics Needs:** If advanced SQL analytics become critical
- **Cost Optimization:** If predictable pricing becomes essential
- **Advanced Transactions:** If complex multi-document transactions are needed
- **Data Sovereignty:** If specific geographic data requirements emerge

### Migration Path

If migration becomes necessary:

1. **Supabase:** PostgreSQL with Firebase-like features
2. **PlanetScale:** Serverless MySQL with good scaling
3. **MongoDB Atlas:** If document model is preferred
4. **Traditional PostgreSQL:** For complex relational needs

---

**Related ADRs:** [002 Authentication Strategy](./002-authentication-strategy.md), [005 Security Implementation](./005-security-implementation.md)
