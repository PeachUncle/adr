# ADR-004: Enhanced Goal Model for Complete Lifestyle Coverage

**Status**: Accepted  
**Date**: 2025-01-07  
**Decision Makers**: Product Manager, Development Team  
**Supercedes**: Initial goal model in ADR-003

## Context

During validation of our generic goal system against real-world use cases, we discovered it only handled recurring goals well (e.g., "walk daily," "journal 3x/week"). Testing revealed five major goal patterns our users need:

1. **Milestone Goals**: "Write 50,000 words," "Save $5,000"
2. **Target Goals**: "Lose 20 pounds by June," "Run marathon by October"  
3. **Streak Goals**: "Meditate 100 days straight," "30-day sobriety"
4. **Limit Goals**: "Screen time under 2 hours," "Spend less than $200/month"
5. **Long-term Goals**: "Read 52 books this year," "Visit 12 countries"

Additionally, our AI analysis capabilities were limited by sparse activity data.

## Decision

Enhance the goal model to support five distinct goal patterns with rich contextual data for AI analysis.

## Key Changes

### 1. Goal Patterns
```typescript
goalPattern: 'recurring' | 'milestone' | 'target' | 'streak' | 'limit'
```

### 2. Flexible Targets
- Support for cumulative progress (no period reset)
- Target dates for deadline-based goals
- Direction (increase/decrease/maintain)
- Min/max ranges

### 3. AI Context Layer
Every activity now captures:
- Temporal context (time, day, season)
- Environmental factors (weather, location)
- Physical state (energy, sleep, stress)
- Social context (alone/with others)
- Subjective experience (mood, enjoyment, difficulty)

## Consequences

### Positive
- **100% Coverage**: Handles all common lifestyle goals
- **AI Intelligence**: 10x richer data for pattern recognition
- **User Delight**: Natural goal setting without constraints
- **Cross-insights**: "You read more when you exercise"
- **Predictive Power**: Accurate completion predictions

### Negative  
- **Complexity**: More goal pattern logic to implement
- **Migration**: Existing goals need pattern classification
- **UI Complexity**: Forms must adapt to patterns
- **Testing**: More edge cases to cover

### Neutral
- Database schema remains efficient (same table)
- API endpoints stay generic
- Frontend components need pattern awareness

## Examples

### Before: Limited Model ❌
```typescript
// Could only handle: "Walk 10k steps daily"
{
  target: { value: 10000, period: "day" },
  schedule: { frequency: "daily" }
}

// Couldn't handle: "Write 50k words total"
// Couldn't handle: "Lose 20 lbs by June"
// Couldn't handle: "100-day streak"
// Couldn't handle: "Limit to 2 hours"
```

### After: Complete Model ✅
```typescript
// Milestone: "Write 50k words"
{
  goalPattern: "milestone",
  target: { 
    value: 50000, 
    currentValue: 12000,
    direction: "increase" 
  }
}

// Target: "Reach 180 lbs by June"
{
  goalPattern: "target",
  target: { 
    value: 180,
    startValue: 200,
    targetDate: "2024-06-01",
    direction: "decrease"
  }
}

// Streak: "100 days of meditation"  
{
  goalPattern: "streak",
  target: { value: 1, period: "day" },
  progress: { targetStreak: 100, currentStreak: 47 }
}

// Limit: "Screen time under 2 hours"
{
  goalPattern: "limit",
  target: { 
    value: 120,
    period: "day",
    direction: "decrease",
    targetType: "maximum"
  }
}
```

## Implementation Plan

### Phase 1: Core Patterns (Days 1-3)
- Implement 5 goal patterns
- Update validation logic
- Create pattern-specific progress tracking

### Phase 2: AI Context (Days 4-5)
- Enhance activity model
- Add context collection UI
- Create context analysis service

### Phase 3: Migration (Days 6-7)
- Classify existing goals by pattern
- Update UI components
- Test all patterns thoroughly

## Success Metrics
- Support 100% of user-submitted goal types
- AI predictions within 15% accuracy
- Pattern-specific UI satisfaction >4.5/5
- Zero data loss during migration

## Alternatives Considered

### Option 1: Multiple Goal Tables
- **Pros**: Type-specific optimization
- **Cons**: Complex queries, poor UX

### Option 2: Keep Simple Model
- **Pros**: Easy implementation
- **Cons**: Users abandon app for lack of flexibility

### Option 3: Free-form Goals
- **Pros**: Ultimate flexibility
- **Cons**: No structure for AI analysis

## Review Date
- 2 weeks: Validate all patterns working
- 1 month: Assess AI prediction accuracy
- 3 months: Measure user satisfaction

## References
- [Goal Model Analysis](../features/core/goal-model-analysis.md)
- [Enhanced Design v2](../features/core/goal-system-design-v2.md)
- [Original Design](../features/core/goal-system-design.md)

## Approval
This enhancement is critical for product success and should be implemented before any feature-specific goals.

**Approved by**: Product Manager  
**Technical Lead**: Agreement on implementation approach
