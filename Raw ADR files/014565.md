# ADR-002: Analyzer Design - Progressive Intelligence Enhancement

**Status:** Accepted
**Date:** 2025-11-27
**Deciders:** Project Catalyst Team
**Technical Story:** Inverted Development Approach (Anthropic AI Recommended)

---

## Context

### Background

The project analyzer is the core intelligence component that examines projects and recommends relevant templates. The analyzer must balance accuracy, token efficiency, and maintainability while proving value quickly.

### Requirements

1. **Inverted Approach:** Prove utility with simple patterns before adding AI complexity
2. **Accuracy Target:** 95%+ pattern detection accuracy
3. **Token Efficiency:** Start at ~500 tokens, optimize to ~200 tokens cached
4. **local-memory Integration:** Strict project isolation enforced
5. **Scalability:** Handle any project size/language
6. **Maintainability:** Patterns should be easily updatable by community

### Anthropic AI Recommendation

**"Inverted Development":** Build and validate utility scripts manually first, document proven patterns with metrics, then build minimal analyzer for proven utilities, finally add contextual retrieval for optimization.

**Source:** Anthropic Documentation AI feedback (2025-11-27)

---

## Decision

### Chosen Approach: Three-Phase Progressive Enhancement

**Phase 1 (Weeks 5-6): Rule-Based Pattern Detection**
- YAML-defined detection patterns
- Deterministic confidence scoring
- No AI/ML required
- ~500 tokens per analysis

**Phase 2 (Weeks 7-8): local-memory Integration**
- Store analysis results with strict isolation
- Basic semantic search
- Pattern validation with real usage
- ~1,500 tokens per analysis

**Phase 3 (Weeks 9-10): AI-Powered Contextual Retrieval**
- Hybrid BM25 + semantic search
- 1-hour prompt caching
- Contextual embeddings
- ~200 tokens per cached operation

### Implementation Details

**Week 5-6: Rule-Based Analyzer**

```yaml
# assets/detection-patterns.yaml
patterns:
  - id: missing-gitignore
    type: file_absence
    check: .gitignore
    confidence: high
    severity: medium
    recommendation:
      template: git/gitignore
      reason: "Prevents accidental commits of sensitive files"

  - id: missing-ci
    type: directory_absence
    check:
      - .github/workflows
      - .gitlab-ci.yml
      - .circleci
    confidence: high
    severity: medium
    recommendation:
      template: ci-cd/github-actions
      reason: "Automated testing improves code quality"

  - id: missing-docs
    type: file_quality
    check: README.md
    criteria:
      min_lines: 50
      required_sections:
        - Installation
        - Usage
        - Contributing
    confidence: medium
    severity: low
    recommendation:
      template: documentation/README
      reason: "Comprehensive docs improve adoption"

  - id: no-license
    type: file_absence
    check: LICENSE
    confidence: high
    severity: high
    recommendation:
      template: setup/licenses
      reason: "Legal protection and clear usage terms"
```

**Confidence Scoring:**
```yaml
# assets/confidence-scoring.yaml
scoring:
  high:
    weight: 1.0
    conditions:
      - file_exists: exact match
      - directory_exists: exact match

  medium:
    weight: 0.7
    conditions:
      - file_quality: threshold met
      - pattern_match: 70%+

  low:
    weight: 0.4
    conditions:
      - file_quality: partial match
      - pattern_match: 40-70%
```

**Week 7-8: local-memory Integration**

```javascript
// Store analysis with MANDATORY isolation
async function storeAnalysis(analysisResults) {
  const params = createIsolatedParams({
    content: JSON.stringify({
      timestamp: Date.now(),
      patterns_detected: analysisResults.patterns,
      recommendations: analysisResults.recommendations,
      confidence_scores: analysisResults.scores
    }),
    tags: ['project-analysis', 'catalyst', 'pattern-detection'],
    importance: 8,
    source: 'project-catalyst-analyzer'
  });

  await mcp__local_memory__store_memory(params);
}

// Retrieve with basic search
async function getHistoricalAnalyses() {
  const params = {
    search_type: 'semantic',
    query: 'project analysis results',
    tags: ['project-analysis'],
    session_filter_mode: 'session_only',  // ⚠️ MANDATORY
    session_id: getProjectSessionId(),
    domain: getProjectName(),
    response_format: 'concise',
    limit: 5
  };

  return await mcp__local_memory__search(params);
}
```

**Week 9-10: Contextual Retrieval**

```javascript
// Hybrid search with contextual embeddings
async function getRecommendations(currentContext) {
  const params = {
    search_type: 'hybrid',  // BM25 + semantic
    query: currentContext.projectType + ' ' + currentContext.frameworks.join(' '),
    use_ai: true,
    tags: ['project-analysis', 'recommendations'],
    session_filter_mode: 'session_only',
    session_id: getProjectSessionId(),
    domain: getProjectName(),
    response_format: 'concise',
    limit: 5
  };

  const results = await mcp__local_memory__search(params);

  // Results cached for 1 hour (87% token reduction on repeat queries)
  return results;
}
```

---

## Considered Alternatives

### Alternative 1: AI-First Approach

**Pros:**
- More sophisticated from start
- Better context understanding
- Impressive demo

**Cons:**
- High token costs immediately (~5,000 tokens per analysis)
- Hard to debug/test (black box)
- Unproven patterns (no validation data)
- Violates "inverted approach" recommendation

**Why Not Chosen:**
Anthropic AI explicitly recommended proving utility first, then adding AI complexity. Starting with AI means high costs for unvalidated patterns.

### Alternative 2: Static Template List (No Analysis)

**Pros:**
- Zero token cost
- Simple implementation
- Fast execution

**Cons:**
- No intelligence/context awareness
- User overwhelmed with 40+ templates
- No value over manual browsing
- Doesn't justify "AI-powered" claim

**Why Not Chosen:**
Provides no differentiation. Users can browse templates themselves without a plugin.

### Alternative 3: External LLM API (OpenAI, etc.)

**Pros:**
- Potentially better models
- More control over prompts
- No MCP dependency

**Cons:**
- Requires API keys (user friction)
- External dependency (privacy concerns)
- Additional cost for users
- Violates local-memory integration goal

**Why Not Chosen:**
Claude Code's local-memory integration provides isolation, caching, and no external dependencies.

---

## Consequences

### Positive

1. **Proven Value Early:** Rule-based patterns work Week 6
2. **Deterministic Testing:** 95%+ accuracy achievable with rules
3. **Token Efficiency:** Start low, optimize progressively
4. **Community Extensible:** YAML patterns easy to contribute
5. **Data-Driven:** Phase 2 validates patterns with real usage
6. **Optimal Intelligence:** Phase 3 adds AI only where proven valuable

### Negative

1. **Manual Pattern Creation:** Rules require upfront research (mitigated: 15 MVP patterns initially)
2. **Limited Context Understanding:** Rules miss nuanced situations (mitigated: Phase 3 adds AI)
3. **Maintenance Burden:** Patterns need updates as best practices evolve (mitigated: community contributions)

### Risks

**Risk 1: Pattern Inaccuracy**
- **Impact:** False positives/negatives frustrate users
- **Probability:** Medium (rules miss edge cases)
- **Mitigation:** Confidence scoring, user feedback loop, Phase 3 AI enhancement

**Risk 2: Token Budget Exceeded**
- **Impact:** Expensive operations reduce adoption
- **Probability:** Low (phased approach controls costs)
- **Mitigation:** Token benchmarks at each phase, caching, progressive loading

---

## Implementation Notes

### Phase 1 Deliverables (Weeks 5-6)

**Files:**
- `skills/project-analyzer/SKILL.md`
- `skills/project-analyzer/assets/detection-patterns.yaml`
- `skills/project-analyzer/assets/confidence-scoring.yaml`
- `skills/project-analyzer/scripts/analyze-structure.py`
- `skills/project-analyzer/scripts/detect-patterns.py`

**Tests:**
- 20 unit tests for pattern detection
- 15 integration tests with sample projects
- Accuracy benchmark: 95%+ target

### Phase 2 Deliverables (Weeks 7-8)

**Features:**
- local-memory storage with isolation
- Historical analysis retrieval
- Pattern validation with usage data

**Tests:**
- 8 local-memory integration tests
- 100% isolation coverage tests

### Phase 3 Deliverables (Weeks 9-10)

**Features:**
- Contextual retrieval (hybrid BM25 + semantic)
- 1-hour prompt caching
- Token optimization validation

**Tests:**
- Token usage benchmarks
- Cache effectiveness tests
- Performance regression tests

---

## References

1. [Anthropic Contextual Retrieval Research](https://www.anthropic.com/news/contextual-retrieval)
2. [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
3. [ADR-001: Plugin Architecture](./001-plugin-architecture.md)
4. [ADR-004: Isolation Enforcement](./004-isolation-enforcement.md)
5. [ADR-005: Token Optimization](./005-token-optimization.md)

---

## Validation

### Success Criteria

**Phase 1 (Rule-Based):**
- ✅ 95%+ accuracy on 20 test projects
- ✅ ~500 tokens per analysis
- ✅ < 5 second execution time

**Phase 2 (Integrated):**
- ✅ All operations use session_only filtering
- ✅ Historical analyses retrievable
- ✅ ~1,500 tokens per analysis

**Phase 3 (Optimized):**
- ✅ ~200 tokens per cached operation
- ✅ 87% reduction vs Phase 1
- ✅ Hybrid search improves accuracy 5%+

### Metrics

- Pattern detection accuracy: 95%+
- False positive rate: < 5%
- Token usage progression: 500 → 1,500 → 200 (cached)
- User satisfaction: 80%+ (post-launch surveys)

---

**Last Updated:** 2025-11-27
**Related ADRs:** [ADR-001](./001-plugin-architecture.md), [ADR-004](./004-isolation-enforcement.md), [ADR-005](./005-token-optimization.md)
