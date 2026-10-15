# 007: Swiping Screen Architecture

## Status
Accepted

## Context

The swiping screen is a core feature of MoviePicker that allows users to browse and interact with movie recommendations in an engaging way. The architecture includes :

1. Efficiently load and manage movie data
2. Handle real-time matching through WebSocket connections
3. Provide smooth transitions and animations
4. Support infinite scrolling/pagination
5. Maintain state for user interactions
6. Handle various loading and error states

## Decision

We implemented the SwipingScreen component with the following architectural decisions:

### State Management
- Used React's useState for managing local component state
- Key states include:
  - movies[] - Array of loaded movies
  - currentMovie - Currently displayed movie
  - currentIndex - Index tracking position in movie list
  - loading/loadingMore - Loading state indicators
  - showMatch/showPostMatchOptions - UI state for matches

### Data Loading
- Implemented pagination with infinite scroll
- Fetch movies in batches based on session preferences
- Maintain a buffer of pre-loaded movies
- Show loading states while fetching more content

### Real-time Matching
- WebSocket integration for immediate match notifications
- Match overlay system for displaying successful matches
- Post-match flow with options to continue or view matches

### User Interaction
- Swipe animations for like/skip actions
- Vertical button layout for primary actions
- Info popup for additional movie details
- Trailer link integration
- Progress indicator showing position in movie list

### Error Handling
- Graceful fallbacks for missing images
- Loading states for various scenarios
- Empty state handling when no more movies are available

## Consequences

### Pros
1. Smooth user experience with minimal loading interruptions
2. Efficient memory usage through pagination
3. Immediate feedback for user actions
4. Scalable architecture for handling large sets of movies
5. Consistent experience across different states (loading, error, empty)
6. Real-time match notifications enhance engagement

### Cons
1. Complex state management with multiple useState hooks
2. Need to carefully manage memory for preloaded movies
3. Multiple API calls required for detailed movie information
4. WebSocket connection needs careful handling for reconnection scenarios

### Mitigations
1. Consider using a state management library for complex state
2. Implement cleanup of unused movie data
3. Batch API calls where possible
4. Add WebSocket reconnection logic
5. Implement proper error boundaries

## References
- SwipingScreen.js implementation
- WebSocket integration documentation
- TMDB API documentation for movie data
