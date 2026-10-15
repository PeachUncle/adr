## Context

Phase I.3 introduces synthetic data generation using teacher LLMs to rapidly expand and diversify the training dataset. This is fundamentally different from Phases I.1 and I.2:

- **Phase I.1**: Scraped existing DOT examples from documentation (real, high quality, limited scope)
- **Phase I.2**: Extracted DOT from FSM libraries (real code, limited availability)
- **Phase I.3**: Generate new DOT using teacher LLMs (synthetic, scalable, controllable diversity)

**Key Challenges:**
1. **Quality Control**: Ensuring synthetic DOT is valid and matches prompts
2. **Distribution Collapse**: Avoiding repetitive or formulaic generations
3. **Cost Management**: API calls can be expensive ($0.01-0.03 per generation)
4. **Synthetic Bias**: Teacher LLM may have idiosyncratic DOT style
5. **Semantic Validation**: Verifying generated graph matches intent

**Stakeholders:**
- Dataset consumers: Need diverse, high-quality training data
- Cost owners: Want to minimize API costs while maximizing quality
- Model trainers: Want to avoid overfitting to synthetic patterns

## Goals / Non-Goals

### Goals
- Generate 100-200 synthetic (NL → DOT) training pairs
- Achieve 90%+ Graphviz compilation success rate
- Cover 8-10 diverse domains (game AI, protocols, workflows, etc.)
- Maintain <$50 total API costs
- Ensure synthetic pairs are distinguishable (deduplication)
- Mix complexity: 30% simple, 50% medium, 20% complex

### Non-Goals
- **Not** replacing real data (synthetic should be ≤70% of final dataset)
- **Not** generating CODE_TO_DOT pairs (focus on NL→DOT only)
- **Not** fine-tuning our own generator (use existing teacher LLMs)
- **Not** manual review of every generation (automated quality filters)
- **Not** supporting local/open-source LLMs initially (cloud providers only)

## Decisions

### Decision 1: Teacher LLM Selection
**Choice**: Tiered approach with cloud and local models

**Primary (Cloud API - Validation Phase)**:
- **Gemini 2.5 Flash**: Fastest, cheapest for validation ($0.00001875/1K input)
- **Gemini 2.5 Pro**: Higher quality if Flash insufficient
- **Gemini 3 Pro Preview**: Latest model for comparison

**Secondary (Local via Ollama - Cost-Free Alternative)**:
- **Gemma 3:27b**: Google's open model, good for structured output
- **DeepSeek-R1:32b**: Reasoning-focused, may handle DOT logic well

**Rationale**:
- Gemini Flash: ~400x cheaper than GPT-4, perfect for validation
- Local models: Zero API cost, unlimited generations
- Multi-tier: Start cheap (Flash), escalate if needed (Pro)

**Pricing Comparison (Nov 2024):**
- Gemini 2.5 Flash: $0.00001875 per 1K input, $0.000075 per 1K output
- Gemini 2.5 Pro: $0.00125 per 1K input, $0.005 per 1K output
- GPT-4: ~$0.03 per 1K input, ~$0.06 per 1K output
- Ollama (local): $0 (compute only)
- Estimated cost per DOT: Flash $0.0001, Pro $0.005, GPT-4 $0.02

**Implementation**:
```python
providers = {
    'gemini-flash': GeminiGenerator(model='gemini-2.5-flash'),
    'gemini-pro': GeminiGenerator(model='gemini-2.5-pro'),
    'gemini-3': GeminiGenerator(model='gemini-3-pro-preview'),
    'ollama-gemma': OllamaGenerator(model='gemma3:27b'),
    'ollama-deepseek': OllamaGenerator(model='deepseek-r1:32b')
}
```

**Alternatives Considered**:
- OpenAI GPT-4: Too expensive for validation phase
- Claude 3.5 Sonnet: Good quality but expensive
- GPT-3.5: Inconsistent for structured output

### Decision 2: Quality Validation Strategy
**Choice**: Multi-stage validation (syntactic + semantic + deduplication)

**Stage 1 - Syntactic (Required)**:
```bash
echo "$dot" | dot -Tpng > /dev/null 2>&1
```
- Fast, deterministic
- Catches syntax errors immediately
- Zero API cost

**Stage 2 - Semantic (Optional, expensive)**:
Use cheaper LLM to validate:
```
Prompt: Does this DOT graph represent: "{original_prompt}"?
Graph: {generated_dot}
Answer yes/no and explain briefly.
```
- Uses GPT-3.5-turbo or Gemini Flash ($0.001 per check)
- Catches mismatches between prompt and output
- Optional based on budget

**Stage 3 - Deduplication (Required)**:
- Compute normalized DOT hash (ignore whitespace, comments)
- Check against existing dataset
- Reject if >90% structural similarity

**Rationale**:
- Syntactic validation is free and catches most errors
- Semantic validation is expensive but catches subtle issues
- Deduplication prevents dataset pollution

**Alternatives Considered**:
- Manual review: Doesn't scale, human bottleneck
- Only syntactic validation: Misses semantic errors
- Rule-based semantic checks: Hard to maintain, brittle

### Decision 3: Prompt Engineering Approach
**Choice**: Curated template library with few-shot examples

**Template Structure**:
```python
{
  "domain": "game-ai",
  "complexity": "medium",
  "template": """
    Create a DOT graph representing a combat AI state machine for a game character.
    
    Include these states: {states}
    Include these transitions: {transitions}
    
    Example DOT graph:
    {few_shot_example}
    
    Now create a similar graph for: {specific_prompt}
  """,
  "parameters": {
    "states": ["random", ["idle", "attack", "defend", "flee"]],
    "transitions": ["random", 3-6],
    "specific_prompt": ["generate"]
  }
}
```

**Benefits**:
- Controlled diversity through parameter randomization
- Few-shot examples improve quality
- Templates encode domain knowledge
- Easy to add new domains

**Initial Template Domains**:
1. Game AI (combat, dialogue, inventory)
2. Network protocols (TCP, HTTP, WebSocket)
3. Workflow automation (CI/CD, approvals)
4. UI navigation (app screens, menus)
5. Robotics (behaviors, tasks)
6. Database transactions (ACID, state)
7. E-commerce (checkout, order)
8. Document lifecycle (draft, review, publish)

**Alternatives Considered**:
- Zero-shot generation: Lower quality, more variability
- Fine-tuning generator: Too expensive, not needed
- Fully random prompts: Unpredictable quality

### Decision 4: Deduplication Strategy
**Choice**: Normalized DOT hashing with structural similarity threshold

**Implementation**:
```python
def normalize_dot(dot_string):
    # Remove whitespace, comments
    # Sort nodes alphabetically
    # Sort edges by source→target
    # Lowercase all identifiers
    return canonical_form

def similarity_score(dot1, dot2):
    nodes1, edges1 = parse_dot(dot1)
    nodes2, edges2 = parse_dot(dot2)
    
    node_overlap = len(nodes1 & nodes2) / max(len(nodes1), len(nodes2))
    edge_overlap = len(edges1 & edges2) / max(len(edges1), len(edges2))
    
    return (node_overlap + edge_overlap) / 2
```

**Thresholds**:
- Exact match (hash collision): Reject
- >90% similarity: Reject
- 70-90% similarity: Flag for manual review
- <70% similarity: Accept

**Alternatives Considered**:
- Graph isomorphism checking: Too expensive (NP-complete)
- String similarity (Levenshtein): Doesn't capture structural similarity
- No deduplication: Risk of repetitive dataset

### Decision 5: Complexity Distribution
**Choice**: Stratified sampling (30% simple, 50% medium, 20% complex)

**Complexity Definitions**:
- **Simple**: 2-5 nodes, 2-7 edges, no subgraphs
- **Medium**: 6-10 nodes, 8-15 edges, optional subgraphs
- **Complex**: 11+ nodes, 16+ edges, subgraphs/clusters required

**Rationale**:
- Simple: Foundation, easier to learn
- Medium: Most common real-world graphs
- Complex: Push model capabilities

**Implementation**:
```python
targets = {
    'simple': int(total_count * 0.3),
    'medium': int(total_count * 0.5),
    'complex': int(total_count * 0.2)
}
```

**Alternatives Considered**:
- Uniform distribution: May skew toward medium complexity
- Only complex graphs: Too hard, lower success rate
- Adaptive distribution: Over-engineering for initial dataset

### Decision 6: Cost Management
**Choice**: Budget-based generation with cost estimation and limits

**Implementation**:
```python
# Before generation
estimated_cost = count * avg_cost_per_generation[provider]
if estimated_cost > max_budget:
    raise BudgetExceededError(f"Estimated ${estimated_cost:.2f} > ${max_budget}")

# During generation
current_cost = sum(api_call_costs)
if current_cost > max_budget:
    logger.warning(f"Budget limit reached: ${current_cost:.2f}")
    break
```

**Budget Recommendations**:
- Development/testing: $5-10 (10-50 generations with Gemini)
- Initial dataset: $20-30 (100 with Gemini, 50 with GPT-4)
- Full dataset: $40-50 (200 mixed provider)

**Cost Optimization**:
1. Use Gemini for bulk generation (4x cheaper)
2. Use GPT-4 for complex/critical prompts
3. Batch API calls where possible
4. Cache successful generations
5. Minimize semantic validation (expensive)

**Alternatives Considered**:
- No budget limits: Could run up large bills accidentally
- Pre-pay tokens: Not available for all providers
- Local models: Quality not sufficient

## Risks / Trade-offs

### Risk 1: Synthetic Data Bias
**Severity**: HIGH
**Impact**: Model may learn teacher LLM's idiosyncrasies instead of general DOT semantics

**Mitigation**:
- Use multiple teacher LLMs (GPT-4 + Gemini) for diversity
- Limit synthetic to ≤70% of final dataset
- Include prompt engineering to encourage variety
- Monitor for repetitive patterns during generation
- Validation phase will compare synthetic vs real performance

**Trade-off**: More diversity sources = higher cost/complexity

### Risk 2: API Costs Overrun
**Severity**: MEDIUM
**Impact**: Could exceed budget, especially with semantic validation

**Mitigation**:
- Implement hard budget limits in code
- Pre-estimate costs before generation
- Default to cheaper provider (Gemini)
- Make semantic validation optional
- Monitor costs in real-time during generation

**Trade-off**: Strict budget may limit dataset size

### Risk 3: Low Generation Success Rate
**Severity**: MEDIUM
**Impact**: May need many retries, increasing costs and time

**Mitigation**:
- Strong few-shot prompts to guide LLM
- Start with simple complexity and progress
- Max 3 retries per prompt before giving up
- Log failures for prompt engineering improvements
- Test prompts on small batch before full generation

**Expected Success Rates**:
- Syntactic validation: 85-95% (first try)
- Semantic validation: 75-85% (if enabled)
- Overall: 70-80% useful generations

**Trade-off**: Higher quality filtering = fewer examples per dollar

### Risk 4: Semantic Validation Inaccuracy
**Severity**: LOW
**Impact**: Validation LLM may incorrectly reject good examples or approve bad ones

**Mitigation**:
- Make semantic validation optional (disabled by default)
- Use it selectively for complex generations only
- Human spot-check of flagged examples
- Syntactic validation is primary gate

**Trade-off**: Accepting some semantic mismatches vs cost of validation

### Risk 5: Distribution Imbalance
**Severity**: LOW
**Impact**: May over/under-generate certain domains or complexity levels

**Mitigation**:
- Stratified sampling with quotas
- Track generation statistics in real-time
- Stop generation when targets met for each category
- Post-generation analysis to verify distribution

**Trade-off**: Rigid quotas may waste good generations that don't fit

## Migration Plan

**N/A** - This is a new capability, no existing data to migrate.

**Integration Steps**:
1. Develop synthetic generator independently
2. Test on small batch (10-20 examples)
3. Validate quality against hand-crafted examples
4. Generate full dataset (100-200 examples)
5. Merge with existing streams (documentation + logic)
6. Run Phase I.4 deduplication on combined dataset

**Dataset Combination Strategy**:
```
Final Dataset = Documentation (44) + Logic (14) + Synthetic (100-200)
             = 158-258 total pairs
             
Composition:
- Real data: 58 pairs (22-37% of total)
- Synthetic: 100-200 pairs (63-78% of total)
```

**Quality Targets**:
- Compilation rate: >90% (same as real data)
- Domain coverage: 8-10 domains
- Complexity distribution: 30/50/20 split
- Deduplication: <5% near-duplicates

## Open Questions

1. **Should we generate any CODE_TO_DOT pairs synthetically?**
   - Initial answer: No, focus on NL_TO_DOT first
   - Reasoning: Harder to generate realistic code, higher validation complexity
   - Future: Could generate if needed for balance

2. **How to validate semantic correctness at scale?**
   - Option A: LLM-as-judge (expensive but thorough)
   - Option B: Heuristic checks (cheap but limited)
   - Option C: Human spot-checking (slow but gold standard)
   - Initial choice: Syntactic only, optional semantic for subset

3. **Should we use self-consistency sampling?**
   - Generate same prompt 3 times with different temperatures
   - Pick the one that appears most frequently or is highest quality
   - Trade-off: 3x cost but potentially higher quality
   - Initial answer: No, not cost-effective for first iteration

4. **How to handle prompt injection / jailbreaking?**
   - If teacher LLM generates malicious or nonsensical output
   - Mitigation: Validate output format strictly, use reputable providers
   - Initial answer: Trust OpenAI/Google content filtering

5. **Should we tune temperature/top_p for generation?**
   - Lower temperature (0.3-0.5): More deterministic, less creative
   - Higher temperature (0.7-0.9): More diverse, more errors
   - Initial choice: 0.7 for balance, may adjust based on quality
