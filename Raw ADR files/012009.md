# ADR 003 - Matching UI Components Architecture

Date: 2025-03-03

## Status
Accepted

## Summary
In the context of displaying real-time movie matches in a multi-user movie selection application, facing the need for consistent and engaging user experience across match events, we decided to implement a two-component modal system (MatchOverlay and PostMatchOptions) to achieve an intuitive  match notification flow, accepting the added complexity of managing multiple modal states.

## Context
The key requirements for displaying movie matches are:
- Immediate action when a movie match occurs
- Clear UI for matched movie details
- User options for continuing their session
- Consistent experience across all users in a session
- Smooth transition between match notification and subsequent actions

Technical considerations:
- Match events can occur at any time during the swiping experience
- Multiple users need to see the same match information simultaneously
- The UI must handle both the initial match notification and post-match user decisions
- The system needs to maintain state for matches across components
- The interface should be reusable across different parts of the application

## Decision
We have decided to split the matching UI into two distinct but complementary components:

1. MatchOverlay Component:
   - Handles the immediate match notification
   - Displays movie details (image, title, genres, description)
   - Shows match percentage
   - Provides primary action to add movie to matches
   - Uses a modal overlay design for focus and visibility
   - Connected to the SwipingScreen. 

2. PostMatchOptions Component:
   - Manages post-match user flow
   - Provides clear options: "Keep Swiping" or "View Matches"
   - Uses consistent modal styling for continuity (Styling in Login.js)
   - Handles state transitions between matching and subsequent user actions

Both components use a modal pattern to ensure:
- Focus on the match event
- Consistent visual hierarchy
- Clear user action paths
- Reusable modal interaction patterns

## Consequences

Pros:
- Clear separation of concerns between match notification and post-match actions
- Reusable modal pattern for future similar interactions
- Consistent user experience across the application
- Flexible component structure allowing for future enhancements
- Improved state management through component separation

Cons:
- Additional complexity in managing multiple modal states
- Need to coordinate state between two separate components
- Additional testing required for various state combinations

Neutral:
- Modal-based approach requires careful handling of web responsiveness
- State management needs to be handled at a higher level
- Components need to be synchronised with backend match events

