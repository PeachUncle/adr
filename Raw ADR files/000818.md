# ADR-0001: Multi-User Authentication and Persistence Architecture

## Status

Proposed

## Context

The BFR Trainer is currently a client-side static web application that uses browser `localStorage` for progress tracking. This architecture serves single-user scenarios effectively but has significant limitations for multi-user environments:

### Current Architecture Limitations
- **No user identification**: All progress is anonymous and device-bound
- **No data portability**: Progress cannot be shared across devices or browsers
- **No collaborative features**: Instructors cannot track student progress
- **No administrative oversight**: No ability to manage users or aggregate analytics
- **Data loss risk**: Browser storage can be cleared, losing all progress
- **Limited scalability**: Cannot support organizational deployments

### Business Requirements for Multi-User Support
- **Student-Instructor workflows**: CFIs need to track student BFR progress
- **Cross-device synchronization**: Users want access from multiple devices
- **Organizational deployment**: Flight schools need centralized user management
- **Progress analytics**: Aggregate reporting on learning effectiveness
- **Data persistence**: Reliable long-term storage of user progress
- **Security compliance**: Proper authentication and data protection

### Technical Context
The current application architecture consists of:
- Vanilla JavaScript ES6 modules (no framework dependencies)
- Static HTML/CSS with inline SVG assets
- Client-side routing and state management
- localStorage persistence with JSON serialization
- ~200 FAR Part 91 sections with progress tracking
- Flashcard system with spaced repetition scheduling
- Quiz system with multiple choice questions
- Visual identification practice (sectional charts, runway markings)

## Decision

We will implement a **Node.js backend with Fastify framework** and **PostgreSQL database** to support multi-user authentication and persistence, while maintaining the existing client-side application structure.

### Core Technology Stack
- **API Server**: Node.js with Fastify framework
- **Database**: PostgreSQL with JSONB columns for progress documents
- **Authentication**: JSON Web Tokens (JWT) with access + refresh token pattern
- **Password Security**: Argon2id hashing algorithm
- **Session Management**: HTTP-only cookies for token storage
- **Concurrency Control**: Optimistic concurrency with version fields
- **Authorization**: Role-based access control (user, instructor, admin)

### Architecture Overview
```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   Fastify API     │───▶│   PostgreSQL    │
│ (Static Assets) │    │  (Node.js)        │    │   Database      │
│                 │    │                   │    │                 │
│ - Study/Quiz UI │    │ - Authentication  │    │ - User accounts │
│ - Progress View │    │ - Progress API    │    │ - JSONB progress│
│ - localStorage  │    │ - User Management │    │ - Session data  │
│   (cache only)  │    │ - Role-based auth │    │ - Admin data    │
└─────────────────┘    └───────────────────┘    └─────────────────┘
```

### Database Schema Design
```sql
-- Users table with authentication data
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role VARCHAR(50) DEFAULT 'user', -- user, instructor, admin
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP,
  email_verified BOOLEAN DEFAULT FALSE,
  active BOOLEAN DEFAULT TRUE
);

-- Progress documents with JSONB for flexible schema
CREATE TABLE user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  progress_data JSONB NOT NULL, -- Full progress object
  version INTEGER DEFAULT 1, -- Optimistic concurrency
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id)
);

-- Session management for refresh tokens
CREATE TABLE user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  refresh_token_hash TEXT NOT NULL,
  device_info TEXT,
  ip_address INET,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Authentication Flow
1. **Registration/Login**: User provides credentials
2. **Password Verification**: Argon2id hash verification
3. **Token Generation**: 
   - Short-lived access token (15 minutes) - in memory
   - Long-lived refresh token (7 days) - HTTP-only cookie
4. **API Authorization**: Bearer token in Authorization header
5. **Token Refresh**: Automatic refresh using HTTP-only cookie
6. **Logout**: Token invalidation and session cleanup

### Progress Synchronization Strategy
- **Optimistic Concurrency**: Version-based conflict detection
- **Client-First Updates**: Immediate UI updates with server sync
- **Conflict Resolution**: Last-write-wins with user notification
- **Offline Support**: localStorage cache with sync on reconnection
- **Delta Synchronization**: Only sync changed progress sections

## Consequences

### Positive Consequences
- **Multi-device access**: Users can access progress from any device
- **Instructor capabilities**: CFIs can track and review student progress
- **Data reliability**: Professional-grade persistence with backups
- **Scalability**: Can support thousands of concurrent users
- **Security**: Industry-standard authentication and authorization
- **Analytics**: Aggregate progress data for learning insights
- **Compliance**: Proper data handling for educational institutions

### Negative Consequences
- **Increased complexity**: Backend infrastructure and deployment requirements
- **Operating costs**: Database hosting, server resources, monitoring
- **Development overhead**: Authentication, user management, API development
- **Deployment complexity**: Multi-tier architecture vs static site
- **New failure modes**: Network connectivity, server downtime, database issues

### Risk Mitigation
- **Graceful degradation**: localStorage cache allows offline operation
- **Progressive enhancement**: Core features work without authentication
- **Migration strategy**: Seamless upgrade path from current localStorage
- **Backup strategy**: Regular database backups and disaster recovery
- **Monitoring**: Application performance and error tracking

## Alternatives Considered

### 1. Azure Active Directory B2C + Cosmos DB
**Pros:**
- Managed identity service with enterprise features
- Global distribution with Cosmos DB
- Built-in compliance (SOC, HIPAA, etc.)
- Social login integration
- Serverless compute options

**Cons:**
- Vendor lock-in to Microsoft ecosystem
- Higher complexity for small-scale deployments  
- Cost can escalate with usage
- Learning curve for Azure-specific services
- Less control over authentication flows

**Decision**: Rejected due to vendor lock-in and complexity for initial implementation

### 2. Firebase Authentication + Firestore
**Pros:**
- Rapid development with managed services
- Real-time synchronization capabilities
- Built-in offline support
- Mobile SDK integration
- Generous free tier

**Cons:**
- Vendor lock-in to Google ecosystem
- Limited complex query capabilities
- Pricing unpredictability at scale
- Less flexibility for custom authentication logic

**Decision**: Rejected due to vendor lock-in and query limitations

### 3. Supabase (PostgreSQL + Auth)
**Pros:**
- Open-source Postgres backend
- Built-in authentication and real-time features
- Self-hosting option available
- Familiar SQL interface
- Growing ecosystem

**Cons:**
- Smaller ecosystem compared to established solutions
- Less mature tooling and documentation
- Potential migration challenges if service changes
- Custom business logic limitations

**Decision**: Considered but chose self-managed for maximum control

### 4. Serverless Functions + DynamoDB
**Pros:**
- Highly scalable and cost-effective for variable workloads
- No server management required
- Built-in high availability
- Pay-per-use pricing model

**Cons:**
- Cold start latency for infrequent use
- Vendor lock-in (AWS)
- Complex local development setup
- DynamoDB learning curve and query limitations

**Decision**: Rejected due to complexity and vendor lock-in

## Migration Strategy

### Phase 1: Backend Infrastructure (Weeks 1-2)
- Set up Node.js/Fastify API server
- Implement PostgreSQL database schema
- Create user registration and authentication endpoints
- Implement JWT token management
- Set up development and testing environments

### Phase 2: Progress API (Weeks 3-4)
- Design progress data API endpoints
- Implement JSONB progress storage and retrieval
- Add optimistic concurrency control
- Create progress synchronization logic
- Test with existing progress data formats

### Phase 3: Client Integration (Weeks 5-6)
- Add authentication UI to existing client application
- Implement API client with token management
- Add progress synchronization to existing state management
- Maintain localStorage as fallback/cache
- Test migration of existing user data

### Phase 4: Advanced Features (Weeks 7-8)
- Implement instructor role and student management
- Add admin dashboard and user management
- Implement cross-device progress synchronization
- Add progress analytics and reporting
- Performance optimization and monitoring

### Phase 5: Production Deployment (Weeks 9-10)
- Production environment setup
- Database migration and backup procedures
- Load testing and performance validation
- Security audit and penetration testing
- Documentation and user migration guides

### Data Migration Process
1. **Import Tool**: Create utility to import localStorage JSON to database
2. **Migration UI**: Allow users to upload existing progress data
3. **Account Linking**: Connect existing progress to new user accounts
4. **Validation**: Verify data integrity after migration
5. **Rollback Plan**: Maintain ability to export data back to localStorage

## Implementation Details

### Security Considerations
- **Password Requirements**: Minimum 8 characters, complexity validation
- **Rate Limiting**: Login attempts, API requests per user/IP
- **Input Validation**: Comprehensive sanitization of all inputs
- **SQL Injection Prevention**: Parameterized queries only
- **XSS Protection**: Content Security Policy headers
- **CSRF Protection**: Double-submit cookie pattern
- **HTTPS Only**: Enforce secure connections in production
- **Token Security**: Short-lived access tokens, secure refresh storage

### Performance Considerations  
- **Database Indexing**: Optimized indexes for user lookups and progress queries
- **Connection Pooling**: Efficient database connection management
- **Caching Strategy**: Redis for session data and frequently accessed content
- **API Response Times**: Target <200ms for progress operations
- **Concurrent Users**: Design for 1000+ simultaneous active users
- **Progress Data Size**: Optimize JSONB storage for large progress documents

### Monitoring and Observability
- **Application Metrics**: Response times, error rates, user activity
- **Database Monitoring**: Query performance, connection counts, storage usage
- **User Analytics**: Progress completion rates, feature usage patterns
- **Error Tracking**: Comprehensive logging and alerting
- **Security Monitoring**: Failed authentication attempts, suspicious activity

## References

- [Fastify Framework Documentation](https://www.fastify.io/)
- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [Argon2 Password Hashing](https://github.com/P-H-C/phc-winner-argon2)
- [OWASP Authentication Guidelines](https://owasp.org/www-project-authentication-cheat-sheet/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)