# ADR-008: Chatbot Navigation Enhancement Architecture

**Status**: Accepted  
**Date**: 2025-12-01  
**Deciders**: Development Team  
**Related**: specs/008-chatbot-navigation-enhancement

## Context

The Physical AI textbook chatbot needed enhanced navigation capabilities to help students quickly find specific content. The existing implementation only supported module-level navigation, lacking week-specific navigation, visual feedback, and efficient development workflow.

### Requirements
- Navigate to specific weeks (1-13) via chatbot
- Visual highlighting of target content after navigation
- Local backend support for faster development
- Fix broken navigation links throughout the site

### Constraints
- Must maintain backward compatibility with existing navigation
- Must work with Docusaurus routing system
- Must support both development and production environments
- Must be performant (no lag in navigation or highlighting)

## Decision

We will implement a comprehensive navigation enhancement with four key components:

1. **Week-Specific Navigation Map**: Add explicit entries for all 13 weeks in COURSE_NAVIGATION
2. **Animated Content Highlighting**: Create ContentHighlight component with CSS animations
3. **Local Backend with Fallback**: Implement automatic backend selection based on environment
4. **Anchor Fragment Support**: Enhance navigation tool to support section-level navigation

## Alternatives Considered

### Alternative 1: Dynamic Week Parsing

**Approach**: Parse week numbers from user input dynamically without explicit map entries.

**Pros**:
- Fewer entries in navigation map
- Automatically handles any week number
- Less maintenance when adding weeks

**Cons**:
- More complex parsing logic
- Harder to test edge cases
- No explicit documentation of available weeks
- Potential for parsing errors

**Why Rejected**: Explicit entries provide better reliability, testability, and documentation.

### Alternative 2: Third-Party Animation Library

**Approach**: Use libraries like Framer Motion or React Spring for highlighting.

**Pros**:
- Rich animation features
- Well-tested implementations
- Advanced animation controls

**Cons**:
- Additional dependency (~50KB)
- Learning curve for team
- Overkill for simple fade animation
- Bundle size increase

**Why Rejected**: CSS animations are sufficient, performant, and have no dependencies.

### Alternative 3: Environment Variable Backend Configuration

**Approach**: Use environment variables to configure backend URL.

**Pros**:
- Explicit configuration
- No automatic detection logic
- Clear separation of environments

**Cons**:
- Requires manual configuration
- Easy to forget to set variables
- No automatic fallback
- More setup for developers

**Why Rejected**: Automatic detection with fallback provides better developer experience.

### Alternative 4: Client-Side Only Anchor Handling

**Approach**: Handle all anchor navigation in frontend without backend support.

**Pros**:
- Simpler backend implementation
- No tool signature changes
- All logic in one place

**Cons**:
- Backend can't suggest specific sections
- No server-side anchor validation
- Misses opportunity for intelligent navigation
- Limited chatbot capabilities

**Why Rejected**: Backend anchor support enables more intelligent navigation suggestions.

## Rationale

### Week-Specific Navigation Map

Explicit entries provide:
- **Fast lookup**: O(1) dictionary access
- **Clear documentation**: All available weeks visible in code
- **Easy testing**: Property tests can validate all entries
- **Flexible matching**: Supports "week 9", "week9", "9th week"

### Animated Content Highlighting

CSS-based highlighting provides:
- **Performance**: GPU-accelerated animations
- **No dependencies**: Pure CSS solution
- **Smooth UX**: Professional fade-in/fade-out
- **Accessibility**: Can be disabled via prefers-reduced-motion

### Local Backend with Fallback

Automatic backend selection provides:
- **Fast iteration**: Test backend changes without deployment
- **Reliability**: Falls back if local backend unavailable
- **Zero configuration**: Works out of the box
- **Production safety**: Always uses production when deployed

### Anchor Fragment Support

Section-level navigation enables:
- **Precise targeting**: Navigate to exact content location
- **Better UX**: Highlight shows exactly where to look
- **Standard approach**: Uses URL fragments (path#anchor)
- **Backward compatible**: Works without anchors too

## Consequences

### Positive

- **Improved UX**: Students can navigate directly to any week
- **Visual feedback**: Clear indication of target content location
- **Faster development**: Local backend speeds up iteration
- **Better navigation**: Section-level precision
- **Maintainable**: Clear structure, well-tested
- **Scalable**: Easy to add more navigation entries

### Negative

- **More entries**: COURSE_NAVIGATION map is larger (100+ entries)
- **Manual updates**: Adding weeks requires updating navigation map
- **Local backend**: Developers must run backend locally
- **Animation complexity**: CSS animations require careful tuning
- **Anchor dependency**: Highlighting requires consistent anchor IDs

### Mitigation Strategies

**For navigation map size**:
- Group related entries with comments
- Use consistent naming patterns
- Property tests validate all entries

**For manual updates**:
- Document update process
- Property tests catch missing entries
- Consider code generation for future

**For local backend requirement**:
- Clear documentation in README
- Automatic fallback to production
- Error messages guide developers

**For animation complexity**:
- Well-documented CSS
- Tested across browsers
- Respects user motion preferences

**For anchor dependency**:
- Graceful fallback if anchor missing
- Validation in property tests
- Consistent anchor generation

## Implementation

### COURSE_NAVIGATION Structure

```python
COURSE_NAVIGATION = {
    # Week entries (26 total: 13 with space, 13 without)
    "week 1": {"path": "/docs/module1/week1-intro-physical-ai", "title": "Week 1: Introduction to Physical AI"},
    "week1": {"path": "/docs/module1/week1-intro-physical-ai", "title": "Week 1: Introduction to Physical AI"},
    
    # Topic entries with anchors (50+ entries)
    "vslam": {"path": "/docs/module3/week9-isaac-2#vslam", "title": "Visual SLAM"},
    
    # Anchor-only entries (4 entries)
    "learning outcomes": {"path": "#learning-outcomes", "title": "Learning Outcomes", "is_anchor_only": True},
}
```

### ContentHighlight Component

```typescript
export default function ContentHighlight(): React.JSX.Element {
  const location = useLocation();
  const [highlight, setHighlight] = useState<HighlightState>({
    isActive: false,
    targetElement: null,
    rect: null,
  });

  useEffect(() => {
    const hash = location.hash;
    if (!hash) return;
    
    const targetId = hash.slice(1);
    const element = document.getElementById(targetId);
    
    if (element) {
      // Scroll and highlight
      // Auto-clear after 3 seconds
    }
  }, [location.hash]);
  
  // Render animated overlay
}
```

### Fallback Mechanism

```typescript
const isDevelopment = typeof window !== 'undefined' && 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const PRIMARY_API_URL = isDevelopment ? LOCAL_API_URL : PRODUCTION_API_URL;
const FALLBACK_API_URL = isDevelopment ? PRODUCTION_API_URL : LOCAL_API_URL;

async function fetchWithFallback(endpoint: string, options: RequestInit): Promise<Response> {
  try {
    return await fetch(`${PRIMARY_API_URL}${endpoint}`, options);
  } catch {
    return await fetch(`${FALLBACK_API_URL}${endpoint}`, options);
  }
}
```

## Validation

### Property-Based Tests

1. **Navigation Map Path Consistency**: All paths resolve to valid routes
2. **Module Category Consistency**: All modules have consistent structure
3. **Redirect URL Anchor Inclusion**: Section navigation includes anchors

### Manual Tests

- Week navigation (all 13 weeks)
- Topic navigation with anchors
- Highlight animation and fade
- Local backend connection
- Fallback to production
- Link fixes (navbar, footer)

## Related Decisions

- **ADR-003**: Gemini API Migration (affects backend implementation)
- **ADR-005**: Website Redesign Architecture (affects frontend structure)
- **ADR-006**: Pedagogical Framework (defines content structure for navigation)
- **ADR-007**: Base URL Strategy (affects link generation)

## References

- [Docusaurus Router Documentation](https://docusaurus.io/docs/api/misc/@docusaurus/router)
- [CSS Animations Best Practices](https://web.dev/animations/)
- [OpenAI Agents SDK Function Tools](https://github.com/openai/openai-agents-sdk)
- [React useLocation Hook](https://reactrouter.com/en/main/hooks/use-location)

## Notes

This decision significantly improves the chatbot's utility as a navigation tool. The combination of week-specific navigation, visual highlighting, and local backend support creates a powerful development and user experience.

The explicit navigation map approach, while requiring more entries, provides better reliability and testability than dynamic parsing. Future iterations could explore code generation for navigation entries if the map becomes unwieldy.

The local backend with fallback pattern should be considered for other API integrations in the project.
