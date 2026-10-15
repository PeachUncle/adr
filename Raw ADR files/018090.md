# ADR-004: Minimal Firestore Data Model for Google Services Integration

## Status
Accepted

## Context
Summer to Remember needs a lightweight data model that:
- **Links Google services** - Connect Tasks, Calendar events, and Photos
- **Family-based isolation** - Each family's connections are separate
- **Simple relationships** - Minimal glue data between Google APIs
- **No data duplication** - Google services remain the source of truth
- **Basic activity tracking** - Status and relationships only

We need to design a minimal Firestore schema that:
1. Connects Google service IDs together
2. Provides family-based access control
3. Stores only essential relationship data
4. Avoids duplicating Google API data

## Decision
We will use a **minimal linking collection structure** with Google service IDs as references and basic status tracking only.

## Data Model Approach

The minimal data model focuses on connection records rather than data duplication:

### Primary Collections:
- **Families**: Basic family information and Google service configuration
- **Users**: User profiles and family memberships
- **Activity Links**: Connection records linking Google Tasks, Calendar events, and Photos

### Core Principles:
- **Reference-Only Storage**: Store only Google service IDs, not duplicate data
- **Family Isolation**: Each family's links are completely separate
- **Minimal Schema**: Simple structure focusing on relationships between services
- **Google APIs as Source**: All detailed data fetched fresh from Google services

This approach minimizes Firebase storage costs while maintaining clear relationships between Google services.

## Security Approach

The security model implements simple family-based access control:

- **Family Isolation**: Each family's data is completely separate from other families
- **Member Authentication**: Only authenticated family members can access family data
- **User Ownership**: Users can only access their own profile and family memberships
- **Simple Rules**: Straightforward security rules without complex permission logic

This approach provides robust data protection while maintaining simple, understandable access patterns.

## Data Access Pattern

The query approach prioritizes simplicity and efficiency:

- **Link-First Queries**: Fetch connection records from Firestore first
- **API Enrichment**: Use Google service IDs to fetch detailed data from APIs
- **Real-time Links**: Subscribe to Firestore changes for live collaboration
- **On-Demand Data**: Fetch Google API data only when needed by the UI

This pattern minimizes Firebase costs while providing fresh data from Google services.

## Data Operations

The operational approach emphasizes simplicity and cost efficiency:

- **Minimal Firestore Operations**: Only essential link records stored and updated
- **Google API Priority**: Primary data operations happen via Google services
- **UI-Level Caching**: Temporary caching in application memory rather than persistent storage
- **Simple Indexing**: Basic queries by family and update time only

This keeps Firebase usage minimal while providing responsive user experience.

## Evolution Strategy

The minimal schema design supports future changes:

- **Simple Migration**: Connection records easy to modify as needs change
- **Stable Foundation**: Google APIs remain unchanged regardless of schema evolution
- **Export Capability**: Basic family data can be easily exported for portability
- **Extension Ready**: Additional Google services can be integrated with minimal schema changes

This approach provides flexibility for future enhancements while maintaining current simplicity.

## Consequences

### Positive:
- **Minimal Firebase usage**: Very low costs and simple data model
- **Google APIs as source**: Always fresh data, no sync issues
- **Simple relationships**: Easy to understand and maintain
- **Family isolation**: Clear data separation between families
- **Flexible**: Easy to add new Google service connections

### Negative:
- **API dependency**: Requires internet for most functionality
- **Multiple API calls**: Need to fetch from different Google services
- **No rich queries**: Limited to simple ID-based lookups
- **Google API limits**: Subject to Google's rate limiting

### Mitigation:
- Cache Google API responses in UI for performance
- Batch API calls where possible
- Implement retry logic for rate limits
- Keep Firestore data minimal and focused

## Related Decisions
- [ADR-001: Firebase as Primary Backend Platform](001_firebase_backend_platform.md)
- [ADR-002: Google APIs Integration Strategy](002_google_apis_integration.md)

---
*Date: June 7, 2025*
*Participants: Josh Sloan*
*Status: Schema defined, security rules pending implementation*