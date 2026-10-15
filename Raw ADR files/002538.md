# Decision 006: Program ↔ Occupation Mapping Strategy (Revised)

**Date:** 2025-11-12  
**Status:** Accepted  
**Deciders:** [Project Lead / Data Architect]

## Context

The core challenge is to link Hawai'i Program Data (scraped program descriptions) with National Occupation Data (O*NET SOC codes) to enable powerful search, recommendation, and skill-gap analysis features. Since the program descriptions do not contain explicit O*NET codes, an automated, intelligent process is required to establish these high-quality relationships in the `program_occupation` association table. The goal of this revision is to reduce the upfront cost associated with large LLM calls.

## Options Considered

1. **Option A: Runtime Vector Similarity Search (RAG at the Front-End)**
   - Pros: Always Fresh, Simple Data Model
   - Cons: High Latency for front-end features, High Cost on every request, Inconsistent Results for structural features

2. **Option B: Manual Mapping/Rule-Based Heuristics**
   - Pros: Fastest Runtime, Low Operational Cost
   - Cons: Low Accuracy, High Maintenance, Not Scalable

3. **Option C: Two-Stage LLM Bridge (Offline Ingestion/Batch Job)**
   - Description: Use a powerful generative LLM (GPT-4/Claude 3) in a one-time batch job to analyze each Program description and explicitly return 5-10 O*NET codes
   - Pros: Highest Accuracy (LLM acts as an expert human labeler), Low Runtime Latency (relationships are stable database joins), Enables Structural Features (Recommendations, Skill Gap Analysis)
   - Cons: High Upfront LLM Cost during the batch ingestion phase

4. **Option D: Vector Similarity Mapping (Reduced LLM Cost)**
   - Description: Use a general-purpose, high-quality embedding model (e.g., Sentence-BERT, BGE) to embed Program Descriptions and O*NET Occupations (Title + Description + Top Skills). Then, use Cosine Similarity to find the top K closest Occupation vectors for each Program vector, and save these links to the `program_occupation` table
   - Pros: Significantly Lower Upfront Cost (embedding model is much cheaper than a generative LLM), Highly Scalable Batch Process (vector models are fast for this task)
   - Cons: Lower Accuracy for Intent/Nuance (relies purely on semantic overlap; misses professional intent), Still requires a separate step to extract structured metadata (degree_type, institution_id)

## Decision

We chose a **Hybrid Vector + Generative LLM Approach** (A Refined Option C).

This strategy uses the low-cost, high-speed benefits of Vector Similarity (Option D) as a filtering and pre-processing step, while reserving the expensive, high-accuracy Generative LLM (Option C) for the final, critical task of validation and precision linking.

### The Refined Ingestion Process:

1. **Initial Ingestion**: Programs are loaded, and mandatory structured fields (institution_id, degree_type, etc.) are extracted via a Rule-Based or Cheap LLM Task (e.g., a simple one-shot LLM model)

2. **Vector Filtration (Low Cost)**: Embed all Program Descriptions and all O*NET Occupations. Use Cosine Similarity to identify the Top 50 O*NET codes for each Program

3. **Generative LLM Validation (Targeted Cost)**: Send the Program description along with the list of Top 50 Vector-Identified O*NET codes to the expensive Generative LLM

4. **Final Prompt**: The LLM's task is now only to review and refine the provided list: "From this list of 50 O*NET codes, identify the 10 most relevant to the program description and return only those 10 codes."

5. **Final Link**: Store the LLM's final 10 validated codes in the `program_occupation` table

This Hybrid Approach drastically reduces the cost of Option C by preventing the LLM from having to search across the entire O*NET catalogue (~1000 codes) and focuses its power only on a highly relevant subset.

## Consequences

- **Positive:**
  - Cost Reduction: Dramatically lower upfront LLM costs compared to Option C
  - High Accuracy Maintained: The generative LLM still provides the final, human-quality check for the structural links
  - Performance: All runtime structural features (joins) remain fast
  - Flexibility: Establishes a vector infrastructure that can be immediately reused for the runtime RAG pipeline

- **Negative:**
  - Increased Code Complexity: Requires integrating and chaining both the embedding model and the generative LLM into the ingestion pipeline

- **Neutral:**
  - Requires a small amount of extra time to tune the vector similarity threshold for the initial "Top 50" filter

## Implementation Notes

- **When:** Data Ingestion Phase, after Program records are created
- **Where:** A new ingestion module: `app/data/processor/hybrid_program_mapper.py`
- **How:**
  1. **Embed**: Use a common embedding model to generate vectors for all Program and Occupation records
  2. **Vector Store Batch Query**: Use a vector database index to quickly find the top 50 closest Occupation vectors for each Program
  3. **Generative LLM Call**: Call the powerful LLM, providing the Program description and the list of the top 50 filtered O*NET codes
  4. **Upsert**: Insert the LLM's final, curated list into the `program_occupation` table