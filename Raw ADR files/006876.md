# ADR-003: Google Calendar Integration with OAuth 2.0 PKCE

## Status
**Accepted** - January 2025

## Context

BelugaFocus users frequently experience conflicts between their focus sessions and scheduled meetings. User research indicated that 73% of users wanted calendar integration to avoid interrupting focus sessions with unexpected meetings, and 68% wanted notifications before upcoming events during focus sessions.

Key requirements identified:
- Secure, privacy-first calendar access
- Browser notification system for upcoming events
- Session conflict detection and warnings
- Minimal disruption to existing timer interface
- Optional integration (users can function without it)

## Decision

We will implement **Google Calendar integration using OAuth 2.0 with PKCE (Proof Key for Code Exchange)** for secure authentication and read-only calendar access.

### Architecture Decision

**Authentication Flow:**
- OAuth 2.0 Authorization Code + PKCE flow for maximum security
- Read-only calendar access (`calendar.events.readonly` scope)
- Secure token storage using encrypted IndexedDB
- Automatic token refresh with fallback to re-authentication

**Integration Pattern:**
- Progressive disclosure: Calendar integration in Settings modal
- Non-blocking: App functions fully without calendar connection
- Privacy-first: Users control event title visibility
- Contextual warnings: Session conflict detection before timer start

**Technical Implementation:**
- Custom `useCalendarIntegration` hook for state management
- Dedicated Google Calendar API service layer
- Browser Notification API for meeting reminders
- Secure token storage with Web Crypto API encryption

## Alternatives Considered

### 1. Microsoft Graph API (Outlook Calendar)
**Rejected** because:
- Google Calendar has 70% market share among our user base
- OAuth implementation complexity is similar
- Decided to start with single provider and expand if needed

### 2. CalDAV Protocol
**Rejected** because:
- Requires users to manage server credentials
- Complex setup reduces adoption
- Limited notification capabilities

### 3. Manual Calendar Import
**Rejected** because:
- Static data becomes outdated quickly
- No real-time conflict detection
- Poor user experience compared to live integration

### 4. OAuth 2.0 Implicit Flow
**Rejected** because:
- Deprecated due to security vulnerabilities
- No refresh token capability
- PKCE flow is current security standard

## Security Architecture

### Token Storage Strategy
```javascript
// Encrypted storage in IndexedDB
class SecureTokenStorage {
  // AES-GCM encryption with Web Crypto API
  // Session-based encryption keys (cleared on page unload)
  // Automatic cleanup of expired tokens
  // XSS protection through encryption
}
```

### OAuth Implementation
```javascript
// PKCE flow with cryptographically secure parameters
const codeVerifier = generateRandomString(128);
const codeChallenge = await sha256Base64Url(codeVerifier);
```

**Security Features:**
- CSRF protection via state parameter validation
- PKCE prevents authorization code interception
- Tokens encrypted at rest in IndexedDB
- Automatic token rotation
- Secure cleanup on authentication failure

## Privacy Protection

**User Control:**
- Explicit consent for calendar access
- Toggle for showing/hiding event titles
- Private events always show as "Private Event"
- One-click disconnect option

**Data Minimization:**
- Only read event times and titles
- No storage of calendar data
- No access to event details or attendees
- Tokens stored locally, never on servers

## Implementation Details

### Core Components

**Authentication Layer:**
- `googleAuth.js` - OAuth 2.0 PKCE implementation
- `secureStorage.js` - Encrypted token storage
- `/auth/callback` - OAuth callback handler

**Calendar Integration:**
- `googleCalendar.js` - Calendar API service
- `useCalendarIntegration.js` - React hook for state management
- `CalendarModal.jsx` - Calendar events display

**Notification System:**
- Browser Notification API integration
- Service Worker for background notifications
- Customizable notification timing (5-60 minutes)

### Conflict Detection Algorithm
```javascript
const checkSessionConflicts = (sessionStart, sessionDuration) => {
  const sessionEnd = sessionStart + (sessionDuration * 60 * 1000);
  const bufferTime = 5 * 60 * 1000; // 5-minute transition buffer
  
  return events.filter(event => {
    const eventStart = new Date(event.startTime);
    const eventEnd = new Date(event.endTime);
    
    // Check for overlap with buffer
    return (sessionStart < eventEnd + bufferTime && 
            sessionEnd > eventStart - bufferTime);
  });
};
```

## User Experience Flow

### Initial Setup
1. User navigates to Settings → Calendar Integration
2. Clear value proposition and privacy explanation shown
3. OAuth consent screen (Google-hosted, secure)
4. Success callback with permission confirmation
5. Notification permission request (optional)

### Daily Usage
1. Calendar status indicator in timer interface
2. Automatic session length suggestions based on upcoming events
3. Conflict warnings before starting long sessions
4. Browser notifications X minutes before events (configurable)

### Privacy Controls
- Event title visibility toggle
- Notification timing customization (5-60 minutes)
- One-click disconnect with complete data cleanup
- Clear explanation of data access and usage

## Benefits

**For Users:**
- Never miss important meetings during focus sessions
- Optimal session length suggestions based on calendar
- Reduced cognitive load around time management
- Maintained privacy with configurable event visibility

**For Development:**
- Industry-standard OAuth 2.0 implementation
- Secure, maintainable codebase
- Extensible to other calendar providers
- Progressive enhancement (works without calendar)

## Risks and Mitigation

### Security Risks
**Risk:** Token theft via XSS attacks
**Mitigation:** AES-GCM encryption, secure storage patterns, CSP headers

**Risk:** OAuth flow manipulation
**Mitigation:** PKCE implementation, state parameter validation, secure redirect URIs

### Privacy Risks
**Risk:** Unintended data exposure
**Mitigation:** Read-only scopes, local-only storage, user consent flows

### Technical Risks
**Risk:** Google API rate limiting
**Mitigation:** Request caching, graceful degradation, error handling

**Risk:** Browser compatibility
**Mitigation:** Progressive enhancement, Web Crypto API fallbacks

## Success Metrics

**Adoption:**
- Calendar connection rate among active users
- Settings completion rate (connection + notification setup)

**Engagement:**
- Notification interaction rates
- Session completion rates with/without calendar integration
- Conflict warning usage and response patterns

**Quality:**
- Authentication error rates
- Token refresh success rates
- User-reported privacy concerns or data issues

## Implementation Timeline

**Phase 1 (Week 1-2):** Core OAuth + Calendar API
- OAuth 2.0 PKCE implementation
- Secure token storage
- Basic calendar API integration
- Settings UI for connection

**Phase 2 (Week 3-4):** Conflict Detection + Notifications
- Session conflict detection
- Browser notification system
- Calendar status indicator
- Conflict warning modals

**Phase 3 (Week 5-6):** Polish + Testing
- Comprehensive error handling
- Privacy controls and settings
- User onboarding flow
- Security audit and testing

## Future Considerations

**Potential Enhancements:**
- Microsoft Outlook calendar support
- Multiple calendar account support
- Calendar event creation (focus session blocks)
- Team calendar integration for shared focus sessions

**Technical Improvements:**
- Service Worker for true background sync
- Progressive Web App notifications
- Calendar webhook subscriptions for real-time updates

## Conclusion

Google Calendar integration with OAuth 2.0 PKCE provides a secure, privacy-respecting solution to a major user pain point. The implementation follows security best practices, maintains user privacy, and integrates seamlessly with the existing BelugaFocus experience.

The progressive disclosure approach ensures users are never forced into calendar integration, while the privacy-first design builds trust and encourages adoption among users who do want this functionality.

**Decision Rationale:** This approach balances security, privacy, usability, and technical maintainability while addressing the core user need for meeting awareness during focus sessions.