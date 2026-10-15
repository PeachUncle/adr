# Decision 005: Occupation-Program Association Strategy

**Date:** 2025-11-17  
**Status:** Accepted  
**Deciders:** Development Team

## Context

The UH Pathfinder application needs to recommend relevant University of Hawaii programs to users based on their RIASEC interest assessment results, which produces a list of 20 occupation recommendations. We need a scalable, accurate method to associate 887 O*NET occupations with 344 UH programs without manual curation.

The challenge: How do we create meaningful occupation→program associations that:
- Scale to handle all occupation-program combinations (887 × 344 = 305,128 comparisons)
- Provide high-quality, semantically relevant matches
- Can be computed and stored statically (pre-computed rather than real-time)
- Don't require expensive LLM API calls or manual mapping
- Leverage existing program embeddings infrastructure

## Options Considered

### 1. Direct Vector Similarity (Occupation → Program)
Embed all occupations and compute cosine similarity directly against all program embeddings.

**Pros:**
- Simple, straightforward approach
- Single similarity computation per pair
- Uses existing program embeddings

**Cons:**
- 305,128 comparisons per full run
- No semantic grouping or filtering
- May produce lower-quality matches across disparate fields
- Computationally intensive without optimization

### 2. LLM-Based Text Generation
Use LLM to analyze occupation descriptions and generate program recommendations via prompts.

**Pros:**
- Could provide rich, contextual reasoning
- Natural language explanations possible

**Cons:**
- Expensive: 887 occupations × 344 programs = $$$$ in API costs
- Non-deterministic results
- Rate limiting concerns
- Requires prompt engineering and validation
- Not scalable for future updates

### 3. Manual Curation
Expert-driven mapping of occupations to programs.

**Pros:**
- Highest potential accuracy
- Domain expertise applied

**Cons:**
- Extremely time-consuming (887 × 344 potential links to review)
- Not scalable or maintainable
- Human bias and inconsistency
- Doesn't adapt to new programs/occupations

### 4. Two-Stage Vector Hierarchy (Occupation → Pathway → Program)
Introduce pathways (Hawaii Career Pathways - 29 categories across 9 sectors) as an intermediate semantic layer. First map occupations to pathways, then search programs only within matched pathways.

**Pros:**
- Reduces computation: 887 × 29 + filtered comparisons (~42K total vs 305K)
- Leverages existing domain structure (Hawaii Career Pathways)
- Better semantic grouping (e.g., "Machinist" → "Transportation/Automotive" pathways → relevant programs)
- Local embeddings (sentence-transformers) = zero API cost
- Deterministic and reproducible
- Easy to tune with thresholds

**Cons:**
- Two-stage process adds complexity
- Requires embedding pathways separately
- May miss cross-domain matches if pathway filtering too strict
- Depends on pathway quality/completeness

## Decision

**We chose Option 4: Two-Stage Vector Hierarchy (Occupation → Pathway → Program)**

### Rationale

1. **Cost Efficiency**: Using local sentence-transformers (all-MiniLM-L6-v2) eliminates API costs entirely while providing good semantic understanding.

2. **Computational Efficiency**: Reduces comparisons from 305K to ~42K (86% reduction) by filtering programs through pathway matches:
   - Stage 1a: Embed 29 pathways with sector context
   - Stage 1b: Embed 887 occupations with O*NET descriptions  
   - Stage 1c: Compute 887 × 29 = 25,723 comparisons (fast matrix operation)
   - Stage 2: For each occupation, only compare against programs in matched pathways (~48 programs avg per occupation)

3. **Semantic Quality**: Pathways act as a domain-informed filter. Example:
   - "Machinist" (occupation) → matches "Automotive Maintenance", "Aviation Maintenance", "Marine Maintenance" pathways → only searches programs in those pathways
   - This prevents nonsensical matches like "Machinist" → "Culinary Arts" programs

4. **Tunable Precision**: Two threshold parameters allow fine-tuning:
   - Pathway threshold: 0.25 (controls occupation→pathway matching breadth)
   - Program threshold: 0.3 (controls final program match quality)
   - Max programs per occupation: 20 (caps association count)

5. **Results Validation**: Dry run showed high-quality matches:
   - 847/887 occupations matched to pathways (95.5%)
   - 638/887 occupations matched to programs (71.9%)
   - 5,687 total associations (avg 8.9 programs per matched occupation)
   - Sample matches confirmed semantic relevance

6. **Maintainability**: Simple Python script with clear stages, easy to re-run when programs/occupations updated.

## Consequences

### Positive
- **Zero ongoing costs**: No API fees, runs locally
- **Fast execution**: ~10-15 seconds for full pipeline including embeddings
- **High quality matches**: Semantic similarity + domain structure yields relevant results
- **Scalable**: Easy to re-run with updated data, thresholds adjustable
- **Transparent**: Clear similarity scores for debugging/validation
- **Database-backed**: Associations stored in `program_occupation_association` table for fast queries

### Negative
- **249 unmatched occupations** (28%): Some occupations too specialized or distant from UH program offerings
  - Mitigation: These occupations simply won't show program recommendations in UI
- **Pathway dependency**: Quality depends on pathway definitions and structure
  - Mitigation: Hawaii Career Pathways are well-established and maintained
- **Local model limitations**: sentence-transformers may miss nuanced semantic relationships vs. larger models
  - Mitigation: Can upgrade to Voyage AI or other cloud embeddings later if needed (already padded to 1024-dim)

### Neutral
- Requires `occupation` table to be populated first (new prerequisite)
- Two-stage process is conceptually more complex than direct matching
- Embedding model is cached in memory (minor RAM overhead)

## Implementation Notes

### When
- Implemented: November 17, 2025
- Run frequency: On-demand when programs or occupations change (not real-time)

### Where
- **Scripts**:
  - `data_pipeline/processor/populate_occupations.py` - Populates `public.occupation` table from RIASEC + O*NET data
  - `data_pipeline/processor/build_occupation_associations.py` - Main association builder
- **Database**:
  - `public.occupation` table - 887 occupation records with O*NET codes
  - `public.program_occupation_association` table - 5,687 associations
  - `public.vector_chunks` - 344 program embeddings (already existed)
- **Models**:
  - `src/models/public_schema/occupation.py` - Occupation model with RIASEC + career fields
  - `src/models/public_schema/associations.py` - Association table definition

### How
1. **One-time setup** (completed):
   ```bash
   # Populate occupation table
   python3 -m data_pipeline.processor.populate_occupations
   
   # Build associations
   python3 -m data_pipeline.processor.build_occupation_associations
   ```

2. **Architecture**:
   - **Embeddings**: Local sentence-transformers (all-MiniLM-L6-v2), 384-dim → padded to 1024-dim
   - **Similarity**: Cosine similarity computed via NumPy (efficient matrix operations)
   - **Storage**: PostgreSQL with composite PK (program_id, occupation_onet_code)
   - **Foreign Keys**: Enforced referential integrity to programs and occupation tables

3. **Configuration Parameters**:
   ```python
   PATHWAY_SIMILARITY_THRESHOLD = 0.25    # Min score for occupation→pathway match
   PROGRAM_SIMILARITY_THRESHOLD = 0.3     # Min score for occupation→program match
   MAX_PROGRAMS_PER_OCCUPATION = 20       # Cap on associations per occupation
   BATCH_SIZE = 32                         # Embedding batch size
   ```

4. **Performance Metrics** (from production run):
   - Pathway embeddings: 29 items, <1 second
   - Occupation embeddings: 887 items, ~4 seconds (6.4 it/s)
   - Pathway matching: 887 × 29 similarity matrix, instant
   - Program matching: 41,976 filtered comparisons, ~2 seconds
   - Database insert: 5,687 associations, ~1 second
   - **Total runtime: ~10 seconds**

5. **Future Enhancements**:
   - Add similarity_score column to association table for ranking
   - Implement GET `/api/v1/occupations/{onet_code}/programs` endpoint
   - Consider upgrading to Voyage AI embeddings for higher quality (1024-dim native)
   - Add confidence scores based on pathway match strength
   - Monitor usage to identify occupations with no good matches

## Related Decisions
- [Decision 003: Skills Matching Retrieval](003-skills-matching-retrieval.md) - Original embedding strategy
- [Decision 004: Skills Matching Strategy](004-skills-matching-strategy.md) - Skills-based matching (complementary approach)

## References
- Hawaii Career Pathways: https://www.hawaiipublicschools.org/TeachingAndLearning/HighSchool/CareerPathways
- O*NET Database: https://www.onetcenter.org/
- sentence-transformers documentation: https://www.sbert.net/
