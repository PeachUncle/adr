# 5. Database Stack

Date: 2025-06-17

## Status

Accepted

## Context

The application requires a database solution that is affordable for a hobby project (e.g. scaling to zero) with minimal operational overhead. We need both a database engine and an ORM that provide type safety and integrate well with our TypeScript stack. As mentioned in ADR-0004, I prefer the infrastructure to be managed by companies headquartered in Europe wherever possible.

## Decision

We will use:
- **Prisma** as our ORM
- **Aiven** as our PostgreSQL hosting provider
- **UpCloud** as the bare metal provider (backing Aiven)

Aiven and UpCloud are both headquartered in Helsinki (Finland) but we will use UpCloud's Frankfurt data centre to be close to Koyeb.

### Alternatives Considered

**ORM:**
- **Drizzle** - Rejected in favour of Prisma's better schema readability
- **Sequelize** - Rejected due to reduced learning opportunity since I am already familiar with raw SQL

**Database Hosting:**
- **Neon** - Rejected due to US ownership
- **Supabase** - Rejected due to US ownership
- **Xata Lite** - British company but hardware is AWS (Amazon Web Services)
- **Scaleway** - French company with own hardware but rejected due to lack of free tier

### Key Factors

- **Developer experience**: E.g. type safety, schema management and automatic migrations
- **Geographic preference**: European ownership preferred
- **Cost-effectiveness**: Hosting provider must have a free tier or at least scale to zero
- **Compatibility with app host**: Koyeb recommends Aiven at
  https://www.koyeb.com/blog/which-cloud-database-platform-to-choose-for-your-applications

## Consequences

**What becomes easier:**
- Transferable skills due to wide adoption of Prisma ORM
- Entire database stack owned by European companies
- Aiven's DB offering is more mature than Koyeb's

**What becomes more difficult:**
- Prisma's code generation approach adds a build step
- Less flexibility compared to raw SQL for complex queries
- One more account to manage, compared to hosting database with Koyeb

**Risks:**
- Dependency on both Aiven and UpCloud platform stability
  - Minimal risk since both are well established
