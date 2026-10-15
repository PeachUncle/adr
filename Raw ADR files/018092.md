# ADR-008: Google Services as Data Architecture Backbone

## Status
Accepted

## Context
The family summer tracker needs a data architecture that minimizes complexity while maximizing integration with tools the family already uses. We need to decide how to structure the relationship between idea generation, activity planning, scheduling, and memory capture.

## Decision
Use **Google services as the primary data backbone** with the web app serving as an intelligent interface layer:

- **Google Tasks**: Activity idea pool and brainstorming repository
- **Google Calendar**: Scheduled activities and actual event management  
- **Google Photos**: Memory storage and photo organization
- **Local app state**: Priority rankings, notes, and UI enhancements only

## Rationale

### Google Tasks as Idea Pool
- Families already brainstorm in various ways (Notes, Tasks, conversations)
- Google Tasks provides familiar mobile/desktop experience for adding ideas
- No need to rebuild task creation UI - leverage Google's polished interface
- Natural separation between "ideas" and "committed activities"

### Google Calendar as Activity System
- Calendar is the natural home for scheduled family activities
- Family members already check calendar for planning
- Automatic notification and reminder system
- Integration with other calendar events (work, school, etc.)

### Google Photos as Memory System
- Families already store photos in Google Photos
- Automatic backup and organization features
- Sharing capabilities with extended family
- No need to build photo storage infrastructure

### App as Intelligence Layer
- Provides prioritization and decision-making tools
- Bridges the gap between "ideas" (Tasks) and "commitments" (Calendar)
- Adds family-specific context and notes
- Creates seamless promotion flow: Task → Planning → Calendar Event

## Implementation Architecture

```
Google Tasks (Ideas) → Web App (Planning) → Google Calendar (Events)
                           ↓
                    Firebase/Local Storage (App State)
                           ↓  
                    Google Photos (Memories)
```

**Data Storage Strategy:**

**Google Services (Source of Truth):**
- Google Tasks: Task content, completion status, due dates
- Google Calendar: Event details, timing, attendees
- Google Photos: Images, albums, metadata

**Firebase Firestore (App-Specific State):**
- Task list ID for "Summer 2024 Activities" (per user)
- Task priorities and family notes (keyed by Google task ID)
- Promotion tracking (which tasks became calendar events)
- Calendar event IDs linked to original task IDs
- User preferences and app configuration

**Local Storage (Temporary/Cache):**
- Recently viewed tasks for offline display
- Draft notes before Firebase sync
- UI state (expanded/collapsed sections)

**Data Flow:**
1. Family adds activity ideas to Google Tasks naturally
2. App fetches tasks and overlays Firebase-stored priorities/notes
3. Selected tasks get promoted to calendar events via app
4. Firebase stores task→event mapping for tracking
5. Completed activities link to Google Photos albums
6. App provides unified family dashboard view with all data sources

## Consequences

**Positive:**
- Leverages existing family workflows and Google account integration
- Minimal data storage requirements (only UI state and notes)
- Natural separation of concerns (ideas vs commitments vs memories)
- Family can use familiar Google apps alongside custom interface
- Reduces app complexity - no need to rebuild Google's functionality

**Negative:**
- Dependency on Google service availability and APIs
- Limited customization of core data models
- Requires multiple API integrations and proper scope management
- Potential for data scattered across services (though this mirrors real usage)

**Mitigation:**
- Implement proper error handling and offline indicators
- Clear user communication about which service owns what data
- Graceful degradation when APIs are unavailable

## Implementation Notes

**Firebase Firestore Schema:**
```javascript
// Per-user document
users/{userId}: {
  taskListId: "GTgxODA4...", // Google Tasks list ID
  preferences: { ... }
}

// Task enhancements (keyed by Google task ID)  
taskEnhancements/{googleTaskId}: {
  userId: "user123",
  priority: "high|medium|low",
  familyNotes: "Kids really want this one",
  promotedToEventId: "cal_event_123", // null if not promoted
  createdAt: timestamp
}
```

**Google APIs Integration:**
- Google Tasks: Create/connect to "Summer 2024 Activities" list on first auth
- Store the task list ID in Firebase for future API calls
- Google Calendar: Create events with consistent naming/tagging for filtering
- Google Photos: Link albums by activity name or date correlation

**Data Synchronization:**
- Firebase stores app-specific enhancements, not duplicate Google data
- Always fetch fresh task content from Google Tasks API
- Use Google task IDs as foreign keys in Firebase documents

## References
- ADR-002: Google APIs Integration Strategy (technical implementation)
- Stories 004-007: Task viewing, prioritization, and promotion workflow
- Vision: Leveraging family's existing Google ecosystem