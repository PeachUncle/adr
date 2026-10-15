# ADR 0003 — Discovery Model and User Interactions

**Date:** 2024-12-04  
**Status:** accepted

## Context

The app requires a discovery mechanism for users to find and connect with others. Two primary models exist in the market:

1. **Matching Model** (Tinder-style): Users swipe/like, mutual likes create matches, only matches can chat.
2. **Grid Model** (Grindr/Barq!-style): Users see a grid of nearby profiles sorted by distance, anyone can message anyone.

The product owner has specified the Grid Model for Ursine Arcana.

## Decision

1. **Discovery Model**: Grid feed displaying profiles sorted by proximity (closest first).

2. **Feed Behavior**:
   - Default sort: Distance (ascending)
   - Secondary sort: Last active time (recent first, for same distance)
   - Pagination: Load 20 profiles at a time, infinite scroll
   - Refresh: Pull-to-refresh updates feed

3. **User Interactions**:
   - **Message**: Initiate chat with any visible user
   - **Hide**: Remove user from your feed; they can still see you; reversible
   - **Block**: Mutual invisibility; prevents messaging; logged for safety
   - **Report**: Flag user for moderation review

4. **Visibility Controls**:
   - Users can hide themselves from the feed entirely (go invisible)
   - Users can control who sees their distance (everyone, no one)
   - Blocked users are mutually invisible

5. **No Matching System**: There is no like/pass mechanism, no mutual match requirement, no match notifications.

## Consequences

**Positive:**

- Familiar UX for target audience (Grindr/Barq! users)
- Lower friction to start conversations
- Simpler data model (no matches collection)

**Negative:**

- Higher potential for unwanted messages (mitigated by block/report)
- No "mutual interest" signal before messaging
- May require rate limiting on message initiation

**Mitigations:**

- Robust blocking with immediate effect
- Report system with quick moderator response
- Optional "message requests" feature in future (ADR if needed)
