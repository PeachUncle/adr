# ADR-001: Frontend Question Rendering Component Architecture

**Status**: Accepted
**Date**: 2025-10-22
**Deciders**: Development Team, Senior Frontend Architect Review
**Technical Story**: Refactoring to eliminate code duplication and data inconsistencies in questionnaire rendering

## Context and Problem Statement

The frontend codebase had significant code duplication in question rendering logic, with identical or similar code appearing in 5+ different components. This duplication led to:

1. **Critical bugs**: Submit button validation failing, data key mismatches causing data loss
2. **Maintenance burden**: Bug fixes required changes in multiple locations
3. **Inconsistency**: Different rendering behaviors across contexts
4. **Technical debt**: ~500+ lines of duplicate code

### Specific Issues Discovered

1. **RatingScale Bug**: Hardcoded `Stars="4"` in DynamicQuestionnaire.razor instead of reading from configuration
2. **Submit Button Validation Bug**: Validation state not updating when text fields were cleared
3. **Data Key Mismatch Bug**: QuestionnaireReviewMode using `"text_0"` keys while OptimizedTextQuestion using `"section_0"` keys
4. **Edit Dialog Data Corruption Bug**: EditAnswerDialog overwriting answers with wrong key format

## Decision Drivers

- **Data Integrity**: Prevent data loss and corruption bugs
- **Maintainability**: Single source of truth for question rendering
- **Consistency**: Same behavior across all contexts (edit, review, preview)
- **Performance**: Optimized components with proper lifecycle management
- **Developer Experience**: Clear patterns that are hard to misuse

## Considered Options

### Option 1: Continue with Inline Rendering (Status Quo)
- Keep duplicate rendering logic in each component
- Manually synchronize changes across all locations
- **Rejected**: Led to the bugs we discovered

### Option 2: Shared Helper Methods
- Extract helper methods to a shared service
- Each component still has rendering logic but uses shared helpers
- **Rejected**: Still allows drift, doesn't enforce consistency

### Option 3: Centralized Optimized Components (CHOSEN)
- Create canonical OptimizedQuestionRenderer component
- All contexts must use the centralized component
- Component handles all rendering and data management
- **Accepted**: Enforces single source of truth

## Decision Outcome

**Chosen option**: "Option 3: Centralized Optimized Components"

### Component Architecture

```
OptimizedQuestionRenderer (dispatcher)
├── OptimizedAssessmentQuestion
├── OptimizedTextQuestion
└── OptimizedGoalQuestion
```

Each component:
- Inherits from `OptimizedComponentBase`
- Handles its own configuration parsing
- Manages response state internally
- Provides lifecycle optimization via `HasStateChanged()`

### Data Format Standards

Standardized response keys to prevent mismatches:

| Question Type | Key Format | Example |
|--------------|------------|---------|
| Text (single) | `"value"` | `ComplexValue["value"]` |
| Text (multiple) | `"section_{index}"` | `ComplexValue["section_0"]` |
| Assessment Rating | `"rating_{key}"` | `ComplexValue["rating_communication"]` |
| Assessment Comment | `"comment_{key}"` | `ComplexValue["comment_communication"]` |
| Goal Description | `"Description"` | `ComplexValue["Description"]` |
| Goal Percentage | `"AchievementPercentage"` | `ComplexValue["AchievementPercentage"]` |
| Goal Justification | `"Justification"` | `ComplexValue["Justification"]` |

### Positive Consequences

✅ **Bug Prevention**: Data key mismatches impossible when using components
✅ **Code Reduction**: Eliminated ~500+ lines of duplicate code
✅ **Single Source of Truth**: Changes only need to be made once
✅ **Testability**: Test once in components instead of 5+ times
✅ **Consistency**: Same rendering and behavior everywhere
✅ **Performance**: Optimized lifecycle with proper change detection

### Negative Consequences

⚠️ **Migration Effort**: Existing components need refactoring (~40 hours estimated)
⚠️ **Learning Curve**: Developers must learn the new pattern
⚠️ **Backward Compatibility**: Old `"text_"` key format deprecated, needs migration layer

## Pros and Cons of the Options

### Option 1: Status Quo (Inline Rendering)

**Good**:
- No migration effort required
- Developers familiar with current approach

**Bad**:
- Critical bugs discovered (data loss, corruption)
- ~500 lines of duplicate code
- Maintenance nightmare
- Inconsistent behavior

**Risk Level**: 🔴 **CRITICAL** - Already causing production bugs

### Option 2: Shared Helper Methods

**Good**:
- Reduces some duplication
- Easier migration than full refactor
- More flexible for edge cases

**Bad**:
- Doesn't prevent drift
- Still allows inline rendering
- Key format mismatches still possible
- Configuration parsing still duplicated

**Risk Level**: 🟠 **HIGH** - Doesn't solve root cause

### Option 3: Centralized Components (CHOSEN)

**Good**:
- Eliminates all duplication
- Enforces single source of truth
- Prevents data key mismatches
- Easier to test and maintain
- Optimized performance

**Bad**:
- Requires migration effort
- Less flexible for edge cases
- Learning curve for developers

**Risk Level**: 🟢 **LOW** - Prevents entire class of bugs

## Links

- **Implementation PR**: #[TBD]
- **Bug Reports**:
  - Submit Button Validation Bug
  - Data Key Mismatch Bug (QuestionnaireReviewMode)
  - Edit Dialog Data Corruption Bug
- **Related Docs**:
  - CLAUDE.md Section 6 (Frontend Component Architecture)
  - Frontend Architecture Review Report (2025-10-22)

## Implementation Notes

### Completed Refactoring (As of 2025-10-22)

✅ **Phase 1**: Created Optimized components
- OptimizedQuestionRenderer.razor
- OptimizedAssessmentQuestion.razor
- OptimizedTextQuestion.razor
- OptimizedGoalQuestion.razor

✅ **Phase 2**: Refactored QuestionnaireCompletion.razor
- Removed ~216 lines of duplicate code
- Uses OptimizedQuestionRenderer

✅ **Phase 3**: Refactored DynamicQuestionnaire.razor
- Removed ~226 lines of duplicate code
- Fixed validation to match new key format
- Uses OptimizedQuestionRenderer

✅ **Bug Fixes**:
- Fixed RatingScale bug (hardcoded 4 stars)
- Fixed Submit button validation (now reactive)
- Fixed read-only rating visibility (ReadOnly vs Disabled)
- Fixed text question lifecycle (OnInitialized)

### Remaining Work

🔴 **CRITICAL - Sprint 1**:
- [ ] Fix QuestionnaireReviewMode.razor data key mismatch
- [ ] Fix EditAnswerDialog.razor data key mismatch
- [ ] Add backward compatibility migration layer

🟠 **HIGH - Sprint 2**:
- [ ] Extract QuestionConfigurationService (shared parsing)
- [ ] Refactor QuestionnaireReviewMode to use OptimizedQuestionRenderer
- [ ] Refactor EditAnswerDialog to use OptimizedTextQuestion
- [ ] Update PreviewTab to use shared service

🟡 **MEDIUM - Sprint 3**:
- [ ] Remove unused RenderYesNoQuestion() from DynamicQuestionnaire
- [ ] Add integration tests for all question types
- [ ] Document component usage patterns
- [ ] Add migration guide for old data format

## Validation

### How to Verify Compliance

1. **Component Usage**: All question rendering must use OptimizedQuestionRenderer
2. **Key Format**: All validation must use `"section_"` not `"text_"` keys
3. **No Duplication**: No `GetCompetenciesFromConfiguration()`, `GetRatingScaleFromQuestion()` duplicates
4. **Lifecycle**: Components must initialize in both OnInitialized() and OnParametersSet()
5. **Validation Updates**: Response changes must call UpdateProgress()

### Code Review Checklist

- [ ] Uses OptimizedQuestionRenderer (not inline rendering)
- [ ] Uses correct data key format (`"section_"` not `"text_"`)
- [ ] No duplicate configuration parsing
- [ ] Validation matches Optimized component keys
- [ ] Component lifecycle properly initializes data
- [ ] Progress/validation updates when responses change

## Notes

This ADR was created after a comprehensive architectural review revealed systemic duplication and data integrity issues. The decision was driven by actual production bugs, not theoretical concerns.

**Key Insight**: "Working code" isn't enough. Code must be maintainable, consistent, and prevent entire classes of bugs through architectural constraints.

---

**Last Updated**: 2025-10-22
**Next Review**: After Sprint 2 completion (estimated 2025-11-15)
