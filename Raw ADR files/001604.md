# ADR-003: Use PostgreSQL + MongoDB Hybrid Database

**Status**: Accepted  
**Date**: 2025-10-18  
**Deciders**: Software Architect, Technical Lead, Database Administrator

## Context

The Eucharist Understanding Platform has diverse data storage requirements that fall into two distinct categories:

### Structured Data Needs

- User accounts and authentication
- User profiles and preferences
- Prayer intentions with relationships
- Bookmarks and progress tracking
- User activity and engagement metrics
- Relational data requiring strong consistency
- Data requiring ACID compliance
- Complex queries with joins

### Flexible Content Needs

- Educational articles with varying structures
- Gospel readings and reflections
- Eucharistic miracle stories with rich metadata
- Historical timeline events
- Theological content with versioning
- Multilingual content
- Content that evolves in structure over time
- Document-oriented data

We need a database solution that:

- Provides ACID guarantees for critical user data
- Offers flexibility for content management
- Scales efficiently for both read and write operations
- Supports complex queries where needed
- Enables rapid content iteration
- Maintains data integrity
- Performs well under load
- Fits within operational budget

### Key Requirements

- Strong consistency for user data
- Flexible schema for content
- Good query performance
- Horizontal scalability
- Reliable backup and recovery
- Multi-region capability (future)
- Cost-effective for open-source project

## Decision

We will use a **hybrid database approach**:

- **PostgreSQL** for structured, relational data
- **MongoDB** for flexible, document-oriented content
- **Redis** for caching and session management

This polyglot persistence approach uses the right tool for each type of data.

### Database Allocation

#### PostgreSQL - Structured Data

```sql
Primary Use Cases:
- users, user_profiles
- authentication, sessions
- prayer_intentions
- bookmarks, favorites
- user_progress, streaks
- community_posts, comments
- relationships (followers, etc.)
- analytics, audit_logs

Why PostgreSQL:
- ACID compliance critical for user data
- Complex queries with joins needed
- Strong data integrity constraints
- Excellent JSON support for flexibility
- Mature, battle-tested reliability
- Great tooling and ecosystem
```

#### MongoDB - Content & Documents

```javascript
Primary Use Cases:
- educational_articles
- gospel_readings
- eucharistic_miracles
- reflections
- timeline_events
- multimedia_metadata
- content_versions
- localized_content

Why MongoDB:
- Flexible document schema for content
- Natural fit for CMS needs
- Easy versioning and evolution
- Fast read performance
- Horizontal scaling capability
- JSON-native storage
```

#### Redis - Caching & Sessions

```javascript
Primary Use Cases:
- Session storage
- API response caching
- Daily Gospel caching
- Rate limiting counters
- Real-time features (future)
- Temporary data

Why Redis:
- In-memory speed
- Built-in data structures
- TTL support
- Pub/sub capabilities
- Simple integration
```

### Architecture Pattern

```
┌─────────────────────────────────────────────┐
│           Application Layer                 │
└───────────┬─────────────┬───────────────────┘
            │             │
     ┌──────▼──────┐  ┌──▼──────────┐
     │ Sequelize   │  │  Mongoose   │
     │    ORM      │  │    ODM      │
     └──────┬──────┘  └──┬──────────┘
            │             │
     ┌──────▼──────┐  ┌──▼──────────┐
     │ PostgreSQL  │  │  MongoDB    │
     │             │  │             │
     │ Structured  │  │  Content    │
     │    Data     │  │  Documents  │
     └─────────────┘  └─────────────┘
            │             │
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │    Redis    │
            │   Cache     │
            └─────────────┘
```

### Data Consistency Strategy

**Strong Consistency**: PostgreSQL for critical user data
**Eventual Consistency**: MongoDB for content (acceptable delay)
**Cache Invalidation**: Redis with TTL and manual invalidation

### Separation Principle

⚠️ **Critical Rule**: Never mix data concerns

- User data → PostgreSQL only
- Content data → MongoDB only
- No cross-database joins at database level
- Application layer handles cross-database queries if needed

## Consequences

### Positive

✅ **Right Tool for Each Job**: Each database optimized for its specific use case

✅ **PostgreSQL Benefits**:

- ACID compliance for user data
- Strong referential integrity
- Complex query support
- Proven reliability
- Excellent backup tools
- Strong community support

✅ **MongoDB Benefits**:

- Schema flexibility for evolving content
- Fast reads for content delivery
- Natural JSON/document storage
- Easy horizontal scaling
- Simple content versioning
- Great for CMS use cases

✅ **Performance**: Each database type optimized for its data access patterns

✅ **Scalability**: Can scale each database independently based on needs

✅ **Developer Experience**:

- Sequelize ORM for PostgreSQL
- Mongoose ODM for MongoDB
- Familiar tools and patterns

✅ **Future-Proof**: Easy to add more specialized databases if needed

✅ **Cost Optimization**: Can size each database appropriately

### Negative

⚠️ **Operational Complexity**: Two databases to manage, monitor, and backup

⚠️ **Learning Curve**: Team needs to understand both SQL and NoSQL paradigms

⚠️ **No Cross-Database Joins**: Application must handle relationships across databases

⚠️ **Transaction Complexity**: Can't use database transactions across PostgreSQL and MongoDB

⚠️ **Deployment Complexity**: More infrastructure to deploy and maintain

⚠️ **Backup Strategy**: Need separate backup procedures for each database

⚠️ **Monitoring**: Need to monitor multiple database systems

⚠️ **Cost**: Two database services instead of one (though managed services mitigate this)

### Neutral

➖ **Data Synchronization**: Rare cross-database updates need careful handling

➖ **Migration Effort**: More complex data migrations than single database

➖ **Testing**: Need to test with both databases in integration tests

## Alternatives Considered

### 1. PostgreSQL Only

**Pros**:

- Single database to manage
- Can use JSONB for flexible content
- Strong ACID compliance everywhere
- Simpler operations
- Familiar to most developers

**Cons**:

- JSONB queries less efficient than MongoDB
- Not optimal for CMS use case
- Less natural for document storage
- Harder to evolve content schemas
- Slower for document-heavy queries

**Why Not**: While PostgreSQL's JSONB is powerful, it's not as natural or performant as MongoDB for content management. The CMS features would be more complex to implement and maintain.

### 2. MongoDB Only

**Pros**:

- Single database to manage
- Flexible schema everywhere
- Fast document queries
- Good for content-heavy apps
- Horizontal scaling

**Cons**:

- Weaker relational capabilities
- No strong ACID guarantees (prior to 4.0)
- Not ideal for complex joins
- Less mature for transactional data
- Referential integrity not enforced

**Why Not**: User authentication, relationships, and transactional data benefit significantly from PostgreSQL's ACID guarantees and referential integrity. MongoDB's transaction support is newer and less mature.

### 3. MySQL + MongoDB

**Pros**:

- Similar to our approach
- MySQL widely known
- Good performance

**Cons**:

- PostgreSQL has better JSON support
- PostgreSQL more feature-rich
- MySQL licensing considerations
- Less advanced features than PostgreSQL

**Why Not**: PostgreSQL offers better JSON capabilities, more advanced features (like full-text search), and a more permissive license for open-source projects.

### 4. Cloud-Native Solutions (DynamoDB, Cosmos DB)

**Pros**:

- Fully managed
- Auto-scaling
- High availability
- Great performance

**Cons**:

- Vendor lock-in
- Higher costs at scale
- Limited portability
- Learning curve for specific APIs
- Less flexibility in hosting

**Why Not**: We want database portability for an open-source project. Contributors should be able to run the platform on various clouds or on-premises. Vendor lock-in limits this flexibility.

### 5. NewSQL (CockroachDB, YugabyteDB)

**Pros**:

- SQL interface
- Horizontal scaling
- ACID compliance
- Modern architecture

**Cons**:

- Less mature ecosystems
- Smaller communities
- Fewer tools and resources
- Higher learning curve
- Less proven at scale
- Still need separate document store

**Why Not**: While promising, NewSQL databases are less mature than PostgreSQL/MongoDB. For an open-source project, we prioritize mature, well-documented technologies with large communities.

## Implementation Plan

### Phase 1: PostgreSQL Setup (Week 1)

- [x] Set up PostgreSQL instance
- [ ] Create database schemas
- [ ] Configure Sequelize ORM
- [ ] Implement migration system
- [ ] Set up connection pooling
- [ ] Configure backup strategy

### Phase 2: MongoDB Setup (Week 2)

- [x] Set up MongoDB instance
- [ ] Design document schemas
- [ ] Configure Mongoose ODM
- [ ] Implement validation schemas
- [ ] Set up indexing strategy
- [ ] Configure backup strategy

### Phase 3: Redis Setup (Week 3)

- [ ] Set up Redis instance
- [ ] Configure cache client
- [ ] Implement cache strategies
- [ ] Set up session storage
- [ ] Configure TTL policies

### Phase 4: Integration (Week 4)

- [ ] Implement repository pattern
- [ ] Create data access layer
- [ ] Handle cross-database queries
- [ ] Implement data consistency checks
- [ ] Create seeding scripts
- [ ] Write integration tests

### Phase 5: Optimization (Ongoing)

- [ ] Add database indexes
- [ ] Optimize query patterns
- [ ] Implement read replicas
- [ ] Set up monitoring
- [ ] Configure alerts
- [ ] Performance testing

## Technical Specifications

### PostgreSQL Schema Example

```sql
-- Core user table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    display_name VARCHAR(100),
    avatar_url TEXT,
    role VARCHAR(20) DEFAULT 'user',
    email_verified BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);

-- User profiles
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    location VARCHAR(100),
    interests TEXT[],
    prayer_streak INTEGER DEFAULT 0,
    last_active_date DATE,
    preferences JSONB DEFAULT '{}',
    notification_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prayer intentions
CREATE TABLE prayer_intentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_private BOOLEAN DEFAULT false,
    is_answered BOOLEAN DEFAULT false,
    category VARCHAR(50),
    prayer_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_intentions_user ON prayer_intentions(user_id);
CREATE INDEX idx_intentions_category ON prayer_intentions(category);
CREATE INDEX idx_intentions_created ON prayer_intentions(created_at);
```

### MongoDB Schema Example

```javascript
// Educational article schema
const articleSchema = new Schema(
  {
    title: {
      type: String,
      required: true,
      index: true,
    },
    slug: {
      type: String,
      required: true,
      unique: true,
      index: true,
    },
    content: {
      type: String,
      required: true,
    },
    summary: String,
    category: {
      type: String,
      enum: ['eucharist-basics', 'history', 'saints', 'miracles', 'theology'],
      index: true,
    },
    tags: [String],

    // Theological review
    theologicalReview: {
      reviewed: { type: Boolean, default: false },
      reviewedBy: String,
      reviewDate: Date,
      magisteriumRefs: [String],
      imprimatur: String,
    },

    // Localization
    language: {
      type: String,
      default: 'en',
      index: true,
    },
    translations: [
      {
        language: String,
        title: String,
        content: String,
        summary: String,
      },
    ],

    // Metadata
    author: {
      id: String, // Reference to PostgreSQL user
      name: String,
    },
    publishedAt: Date,
    updatedAt: Date,
    viewCount: { type: Number, default: 0 },
    readingTime: Number,

    // Media
    featuredImage: {
      url: String,
      alt: String,
      credits: String,
    },

    // SEO
    seo: {
      metaTitle: String,
      metaDescription: String,
      keywords: [String],
    },
  },
  {
    timestamps: true,
  }
);

// Indexes
articleSchema.index({ title: 'text', content: 'text' });
articleSchema.index({ publishedAt: -1 });
articleSchema.index({ 'author.id': 1 });
```

### Data Access Layer Pattern

```typescript
// Repository interface
interface IUserRepository {
  findById(id: string): Promise<User>;
  findByEmail(email: string): Promise<User>;
  create(user: CreateUserDto): Promise<User>;
  update(id: string, data: UpdateUserDto): Promise<User>;
  delete(id: string): Promise<void>;
}

// PostgreSQL implementation
class UserRepository implements IUserRepository {
  // Uses Sequelize
}

interface IArticleRepository {
  findBySlug(slug: string): Promise<Article>;
  search(query: string): Promise<Article[]>;
  create(article: CreateArticleDto): Promise<Article>;
  update(id: string, data: UpdateArticleDto): Promise<Article>;
}

// MongoDB implementation
class ArticleRepository implements IArticleRepository {
  // Uses Mongoose
}
```

## Database Configuration

### Connection Pooling

```javascript
// PostgreSQL
const sequelize = new Sequelize(process.env.DATABASE_URL, {
  pool: {
    max: 20,
    min: 5,
    acquire: 30000,
    idle: 10000,
  },
});

// MongoDB
mongoose.connect(process.env.MONGODB_URI, {
  maxPoolSize: 20,
  minPoolSize: 5,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
});
```

### Backup Strategy

- **PostgreSQL**: Daily full backups, continuous WAL archiving
- **MongoDB**: Daily snapshots, oplog for point-in-time recovery
- **Retention**: 30 days for daily, 12 months for monthly
- **Testing**: Monthly backup restoration tests

## Security Considerations

### Access Control

- Separate database users for application and admin
- Principle of least privilege
- No root/admin access from application
- Connection string encryption
- VPC/private network isolation

### Data Encryption

- Encryption at rest enabled
- TLS for data in transit
- Sensitive fields encrypted in application
- Key rotation policy

### Audit Logging

- Track schema changes
- Log administrative actions
- Monitor suspicious queries
- Regular security reviews

## Performance Considerations

### PostgreSQL Optimization

- Appropriate indexes for common queries
- Query plan analysis
- Connection pooling
- Read replicas for scaling reads
- Partitioning for large tables

### MongoDB Optimization

- Index strategy for queries
- Compound indexes where beneficial
- Covered queries when possible
- Sharding strategy (future)
- Aggregation pipeline optimization

### Redis Configuration

- Appropriate eviction policies
- Memory limits set
- Persistence configured
- Master-replica for HA

## Monitoring & Metrics

### Key Metrics to Track

**PostgreSQL**:

- Query performance
- Connection pool utilization
- Cache hit ratio
- Slow query log
- Table bloat
- Replication lag

**MongoDB**:

- Query execution time
- Collection scan ratio
- Index usage
- Document size growth
- Replication lag
- Connection count

**Redis**:

- Hit/miss ratio
- Memory usage
- Eviction rate
- Key expiration
- Connection count

### Tools

- PostgreSQL: pg_stat_statements, pgAdmin
- MongoDB: MongoDB Atlas monitoring, mongostat
- Redis: Redis CLI, RedisInsight
- General: Prometheus + Grafana

## Success Criteria

- [x] Both databases set up and running
- [ ] All schemas implemented
- [ ] ORMs/ODMs configured and tested
- [ ] Migration scripts working
- [ ] Backup/restore tested
- [ ] Performance targets met
- [ ] Security measures implemented
- [ ] Monitoring in place
- [ ] Documentation complete
- [ ] Team trained on both databases

## Cost Estimation

### Development Environment

- PostgreSQL: Free (local)
- MongoDB: Free (local or Atlas free tier)
- Redis: Free (local)

### Production (Managed Services)

- PostgreSQL (RDS/Cloud SQL): ~$50-100/month (small instance)
- MongoDB (Atlas): ~$60-150/month (small cluster)
- Redis (ElastiCache/Cloud): ~$25-50/month (small instance)
- **Total**: ~$135-300/month

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Sequelize ORM](https://sequelize.org/)
- [Mongoose ODM](https://mongoosejs.com/)
- [Database Design Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)
- [Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html)

## Revision History

- **2025-10-18**: Initial version - Accepted
- **Status**: Active

---

**Next Review**: 2026-04-18 (6 months)  
**Owner**: Software Architect  
**Stakeholders**: Backend Team, Database Administrator, Technical Lead
