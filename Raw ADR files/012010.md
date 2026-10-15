# ADR 004 - Session Creation Architecture

Date: 2025-03-03

## Status
Accepted

## Summary
In the context of initiating group movie-watching sessions, facing the need for flexible configuration and real-time group coordination, we decided to implement a comprehensive session creation interface with WebSocket integration to achieve seamless group formation and preference management, accepting the complexity of managing multiple user preferences and real-time connections.

## Context
The key requirements for creating movie sessions are:
- Allow users to configure multiple movie preferences (genres, platforms)
- Generate unique session identifiers for group joining
- Enable real-time connection establishment
- Support sharing session information
- Handle session state management

Technical considerations:
- Integration with TMDB API for movie data (present in routes.py)
- WebSocket connection management for real-time updates
- Environment-specific configuration (development vs production)
- Multiple streaming platform support
- Genre and provider ID mapping requirements
- Mobile-friendly interface requirements

## Decision
We have implemented the CreateSession component with the following architectural decisions:

1. State Management:
   - Use of React's useState for local state management
   - Separate state handling for UI elements and session data
   - Centralised mapping of genre and provider IDs

2. API Integration:
   - Environment-based API configuration
   - RESTful endpoint for session creation
   - WebSocket connection establishment for real-time updates

3. User Interface Architecture:
   - Split into logical sections (genres, platforms, preferences)
   - Modular component structure with PinGenerated as a child component
   - Progressive disclosure pattern for genre selection

4. Data Flow:
   - One-way data flow for preference selection
   - Event-driven architecture for session creation
   - Callback-based communication with parent components

## Consequences

Pros:
- Clear separation of concerns between UI, state management, and API integration
- Flexible configuration options for users
- Reusable mapping system for genres and platforms
- Scalable approach to adding new streaming platforms
- Built-in support for real-time session management

Cons:
- Complex state management across multiple preferences
- Need to maintain synchronization between frontend and backend IDs
- Additional complexity in handling environment-specific configurations
- Potential performance impact from large mapping objects

Neutral:
- WebSocket connection management requires careful error handling
- Environment variables need to be properly configured in deployment
- Session state needs to be managed at a higher application level
