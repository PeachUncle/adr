# ADR-0002: Rule-based vs ML-based Tag Extraction Approach

**Status**: Accepted
**Date**: 2025-08-05
**Context**: Travel Memory Journal needs to automatically extract meaningful tags from natural language memory descriptions to enhance searchability and organization.

## Problem Statement
How should we implement automatic tag extraction from travel memory descriptions while maintaining local-only processing, fast performance (<30s for memory addition), and reliable results?

## Decision Drivers
- **Business Requirements**: Enhance memory searchability, organize experiences by themes/activities
- **Technical Constraints**: Local-only processing, no external APIs, lightweight dependencies
- **Team Constraints**: MVP timeline (<1 hour), simple implementation and maintenance
- **Non-Functional Requirements**: Memory addition <30s, reliable tag quality, minimal resource usage

## Options Considered

### Option 1: Rule-based Tag Extraction (Recommended)
**Pros**:
- Predictable and deterministic results
- Fast execution with minimal computational overhead
- Easy to debug, test, and customize for travel domain
- No external dependencies or model files
- Transparent logic that users can understand
- Perfect alignment with MVP timeline
- Can be enhanced incrementally with domain-specific rules

**Cons**:
- Limited to predefined patterns and keywords
- May miss nuanced or creative descriptions
- Requires manual curation of travel-related terms

**Implementation Effort**: S (Small)
**Operational Complexity**: Low

### Option 2: Local ML Model (spaCy/NLTK)
**Pros**:
- More sophisticated natural language understanding
- Better handling of varied sentence structures
- Potential for higher accuracy with diverse inputs
- Can identify entities, sentiment, and context

**Cons**:
- Significant dependency overhead (100MB+ model files)
- Slower processing time, may exceed 30s requirement
- Complex setup and potential model loading delays
- Harder to debug and customize for travel domain
- Overkill for MVP scope

**Why Not Chosen**: Adds significant complexity and dependencies that conflict with our lightweight, fast MVP goals

### Option 3: Hybrid Approach
**Pros**:
- Combines reliability of rules with ML sophistication
- Fallback mechanisms for edge cases

**Cons**:
- Increased complexity for marginal benefit
- Still requires ML dependencies and setup
- Harder to test and maintain

**Why Not Chosen**: Complexity doesn't justify benefits for initial implementation

## Decision
We will use **Rule-based Tag Extraction** for the MVP implementation.

**Rationale**: Rule-based extraction perfectly aligns with our MVP timeline, zero-dependency philosophy, and performance requirements. We can achieve 80% of the value with 20% of the complexity by focusing on travel-specific keywords and patterns.

## Consequences
**Positive**:
- Fast, predictable performance within 30s requirement
- Zero external dependencies or model downloads
- Easy to customize for travel-specific terminology
- Transparent and debuggable tag generation
- Users can understand and predict tag behavior
- Simple testing and quality assurance

**Negative**:
- May miss tags from creative or unusual descriptions
- Limited to predefined travel vocabulary
- Requires manual maintenance of keyword lists

**Implementation Notes**:
- Create travel-specific keyword dictionaries (locations, activities, emotions, food, transport)
- Implement simple NLP preprocessing (tokenization, stemming, stop word removal)
- Use regex patterns for common travel phrases ("went to", "ate at", "stayed in")
- Allow manual tag addition/override for missed cases
- Track tag extraction quality to guide future improvements

## Travel Domain Keywords
**Categories to include**:
- **Activities**: hiking, sightseeing, museum, beach, shopping, dining
- **Transportation**: flight, train, bus, taxi, rental car, walking
- **Accommodation**: hotel, hostel, airbnb, camping, resort
- **Food**: restaurant, street food, local cuisine, breakfast, dinner
- **Experiences**: cultural, adventure, relaxation, nightlife, nature
- **Emotions**: amazing, beautiful, disappointing, exciting, peaceful

## Future Evolution
- Monitor tag quality and user feedback
- Consider ML upgrade if rule-based approach proves insufficient
- Implement tag suggestion feature for user validation
- Add location-specific keyword expansion based on common destinations