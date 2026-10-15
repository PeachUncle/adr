# ADR 002: Using Supabase for Authentication

**Status:** Accepted  
**Date:** 2025-11-28  
**Decision Makers:** Hassan RJ, Development Team

---

## Context

The RAG chatbot requires user authentication to provide personalized learning experiences based on user profiles (programming knowledge, learning goals, robotics experience). The authentication system must:
- Support email/password signup and signin
- Handle email verification
- Provide JWT tokens for API authentication
- Store user profile data (programming knowledge, learning goals, learning style)
- Scale without significant infrastructure management
- Integrate easily with React frontend
- Support Row Level Security (RLS) for data privacy

**Alternatives Considered:**
1. **Supabase Auth** - Hosted auth with PostgreSQL database
2. **Auth0** - Enterprise-grade auth platform
3. **Firebase Authentication** - Google's hosted auth service
4. **Custom JWT Auth** - Roll our own with bcrypt + FastAPI
5. **Clerk** - Modern auth platform with UI components

---

## Decision

We will use **Supabase Authentic** with **Supabase Auth UI React** components.

---

## Consequences

### Positive

1. **Integrated Solution**: Auth + Database + Row Level Security in one platform
2. **Free Tier**: Generous free tier (50,000 MAUs) suitable for educational project
3. **Official React UI**: Pre-built, customizable React components for signin/signup
4. **Email Verification**: Built-in email verification with customizable templates
5. **JWT Tokens**: Standard JWT tokens work seamlessly with FastAPI backend
6. **PostgreSQL**: Full-featured PostgreSQL database for user profiles
7. **RLS**: Row Level Security ensures users only access their own data
8. **Developer Experience**: Excellent documentation and DX
9. **No Lock-in**: Can export data and migrate if needed (open-source Supabase)

### Negative

1. **Vendor Dependency**: Relies on Supabase cloud service availability
2. **Limited Customization**: Email templates have some customization constraints
3. **Learning Curve**: Team needs to learn Supabase-specific concepts (RLS policies)
4. **Migration Complexity**: Moving to another platform requires data migration
5. **Cold Starts**: Free tier may experience cold starts after inactivity

### Mitigation

- **Vendor Dependency**: Monitor Supabase status page and have backup plan
- **Customization**: Acceptable trade-off for time savings and built-in features
- **Learning**: Comprehensive Supabase documentation and community resources
- **Migration**: Design user_profiles table with standard schema for portability
- **Cold Starts**: Acceptable for educational/demo purposes, upgrade if becomes production

---

## Implementation Notes

### Frontend Integration
- Install `@supabase/supabase-js` and `@supabase/auth-ui-react`
- Create `AuthContext` provider for global auth state using `onAuthStateChange`
- Build dedicated `/signin` and `/signup` pages with Supabase Auth UI components
- Style Auth UI to match teal theme (#1e7a6f)
- Create `/profile-setup` page for collecting learning preferences

### Backend Integration
- Install `supabase-py` Python client
- Use Supabase client with service role key for admin operations
- Validate JWT tokens in FastAPI middleware for protected endpoints
- Query `user_profiles` table to personalize chatbot responses

### Database Schema
```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  programming_knowledge TEXT CHECK (programming_knowledge IN ('beginner', 'intermediate', 'advanced')),
  prior_robotics_experience BOOLEAN DEFAULT FALSE,
  learning_goals TEXT[] DEFAULT '{}',
  preferred_learning_style TEXT CHECK (preferred_learning_style IN ('hands-on', 'theory-first', 'mixed')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = id);
```

### Environment Variables
- `SUPABASE_URL` - Project URL
- `SUPABASE_ANON_KEY` - Public anon key (frontend)
- `SUPABASE_SERVICE_ROLE_KEY` - Service role key (backend only)

---

## References

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase Auth UI React](https://supabase.com/docs/guides/auth/auth-helpers/auth-ui)
- [Project Constitution](./constitution.md) - Principle 3: Security First
- [Implementation Plan](../../plans/003-auth-system.md)
