## Context
Converting the API Management page to a unified Settings page requires coordinating changes across multiple pages (Settings, Translation, main app) and ensuring consistent model selection UI. The change introduces default model preferences stored in session state, which need to be accessible across pages while maintaining backward compatibility.

## Goals / Non-Goals

### Goals
- Provide centralized configuration for API keys and default models
- Reduce friction by allowing users to set defaults once instead of selecting models on each page
- Maintain existing API key management functionality unchanged
- Ensure model selection UI consistency across Settings and Translation pages
- Set sensible defaults ("minimax/minimax-m2:free") for new users

### Non-Goals
- Changing API key storage mechanism (still session-based)
- Modifying OpenRouter API integration patterns
- Adding database persistence for settings (session state only)
- Changing existing model selection behavior on Translation page (page-specific selection still works)

## Decisions

### Decision: Reuse Model Selection UI Component
- **What**: Create a reusable function/component for model selection that matches Translation page UI exactly
- **Why**: Ensures consistency and reduces code duplication
- **Alternatives considered**: 
  - Separate implementation in Settings (rejected - would create inconsistency)
  - Inline model selection code (rejected - violates DRY principle)

### Decision: Session State Storage for Defaults
- **What**: Store default models in `st.session_state.default_translation_model` and `st.session_state.default_enhancement_model`
- **Why**: Consistent with existing session-based storage pattern, simple implementation, no database needed
- **Alternatives considered**:
  - File-based storage (rejected - not suitable for multi-user cloud deployment)
  - Database storage (rejected - overkill for this use case, adds complexity)

### Decision: Default Model Fallback Chain
- **What**: Page-specific selection > Settings default > "minimax/minimax-m2:free" hardcoded fallback
- **Why**: Provides maximum flexibility while ensuring system always has a model to use
- **Alternatives considered**:
  - Require explicit selection (rejected - poor UX, would block users)
  - Different fallback for each feature (rejected - inconsistent behavior)

### Decision: Warning Before Operations
- **What**: Display warnings when attempting translation/enhancement without configured model, but allow operation with fallback
- **Why**: Guides users to configure settings while not blocking functionality
- **Alternatives considered**:
  - Block operations completely (rejected - too restrictive)
  - Silent fallback (rejected - users won't know why a specific model is used)

### Decision: Gear Icon Navigation
- **What**: Use gear icon (⚙️) with navigation to Settings page
- **Why**: Standard UI pattern, clear visual indicator for settings access
- **Alternatives considered**:
  - Text link (rejected - less visually distinct)
  - Button (rejected - gear icon is more compact and standard)

## Risks / Trade-offs

### Risk: Session State Persistence
- **Mitigation**: Document that defaults reset on session end, consider adding info message

### Risk: Model Selection UI Inconsistency
- **Mitigation**: Extract model selection into reusable function, test UI matches exactly

### Risk: Default Model Availability
- **Mitigation**: Hardcode fallback to "minimax/minimax-m2:free" which is a free, widely available model

### Trade-off: Page-Specific vs Default Model Priority
- **Decision**: Page-specific selection overrides default (more flexible)
- **Impact**: Users can still customize per-page while benefiting from defaults

## Migration Plan

### Phase 1: Settings Page Creation
1. Rename API_Management.py to Settings.py
2. Add model selection sections
3. Initialize defaults in session state

### Phase 2: Integration
1. Add gear icons to Translation and main app pages
2. Update functions to use defaults
3. Add warning messages

### Phase 3: Testing
1. Update existing tests
2. Add new Playwright tests
3. Verify UI consistency

### Rollback Plan
- Revert Settings.py rename if needed
- Default fallback ensures system continues working even if Settings page has issues

## Open Questions
- Should we show a visual indicator when using default vs page-specific model? (Implementation decision: Yes, via info message)
- Should default models persist across browser sessions? (Decision: No, session-based only for now)

