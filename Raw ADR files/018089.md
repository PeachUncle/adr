# ADR-001: Firebase as Primary Backend Platform

## Status
Accepted

## Context
Summer to Remember requires a backend platform that can handle:
- User authentication with Google accounts
- Real-time data synchronization across family members
- Integration with Google services (Tasks, Calendar, Photos)
- Minimal maintenance overhead for a family-focused project
- Strong security for private family data

We need to choose between several backend approaches:
1. **Firebase** - Google's comprehensive BaaS platform
2. **Supabase** - Open-source Firebase alternative
3. **Custom backend** - Node.js/Express with separate database
4. **Serverless functions** - Netlify/Vercel with external database

## Decision
We will use **Firebase** for authentication and minimal glue data, including:
- **Firebase Authentication** for Google OAuth
- **Firestore** for linking relationships between Google services (tasks ↔ events ↔ photos)

The primary data will live in Google services (Tasks, Calendar, Photos) with Firebase only storing the connections between them.

## Rationale

### Advantages of Firebase:
1. **Google Ecosystem Integration**: Seamless authentication with Google accounts
2. **Minimal Setup**: Simple authentication and basic data storage
3. **Security**: Built-in security rules and Google's infrastructure
4. **Cost Efficiency**: Minimal usage keeps costs very low
5. **Development Speed**: Quick setup for auth + simple data relationships
6. **Familiar APIs**: Well-documented SDKs for web development
7. **Google API Synergy**: Natural fit for connecting Google services

### Firebase vs Alternatives:

**vs Supabase:**
- Firebase has better Google services integration
- More mature real-time subscriptions
- Better offline support
- We're already in Google ecosystem

**vs Custom Backend:**
- Firebase eliminates server maintenance
- Built-in security and authentication
- Real-time features would require complex WebSocket implementation
- Google API integration more complex with custom auth

**vs Serverless + External DB:**
- Firebase provides cohesive ecosystem
- Real-time sync more complex with serverless
- Cold start issues with infrequent family usage

## Implementation Approach

Firebase will provide:
- **Authentication**: Google OAuth integration  
- **Minimal Data Storage**: Connection records between Google services only

Primary data sources remain:
- **Google Tasks**: Activity management and status tracking
- **Google Calendar**: Event scheduling and timing
- **Google Photos**: Memory storage and photo management

Firebase stores only the minimal linking data needed to connect these services together for each family.

## Consequences

### Positive:
- Minimal Firebase usage keeps costs very low
- Simple authentication with Google accounts
- Lightweight data model focuses on connections only
- Google services remain the source of truth
- Easy to understand and maintain architecture

### Negative:
- Still some vendor lock-in to Firebase for auth
- Need to manage relationships between Google services
- Limited real-time collaboration features in minimal setup
- Requires Google API integration complexity

### Mitigation Strategies:
- Keep Firestore data minimal and exportable
- Use standard authentication patterns for easier migration
- Focus on Google APIs as primary functionality
- Implement simple relationship management patterns

## Related Decisions
- [ADR-002: Google APIs Integration Strategy](002_google_apis_integration.md)
- [ADR-004: Firestore Data Model Design](004_firestore_data_model.md)

---
*Date: June 7, 2025*
*Participants: Josh Sloan*
*Status: Implemented in development plan*