# CFO + Auditor AI Review Loop with Supabase pgvector

- Status: accepted
- Deciders: Engineering, Finance, Audit
- Date: 2025-10-30
- ADR ID: ADR-001
- Tags: architecture, ai-agents, database, financial-controls

## Context and Problem Statement

The IKANISA/MoMo gateway operations suite requires automated daily financial close validation, SACCO float reconciliation, and tax compliance checking. Manual review processes are time-consuming, error-prone, and don't scale with transaction volume. We need an AI-powered system that can:

1. Validate double-entry accounting and transaction cut-off
2. Reconcile MoMo settlement with SACCO float accounts
3. Identify missing supporting documentation
4. Flag tax mapping gaps for compliance
5. Provide independent audit challenge to financial outputs
6. Generate audit trails for regulatory compliance

## Decision Drivers

- Need for daily automated financial controls execution
- Requirement for independent audit perspective (separation of duties)
- IFRS/regulatory compliance requirements for SACCO operations
- Scalability to handle growing transaction volumes
- Semantic search capability over financial documents and ledger entries
- Multi-tenant security isolation per organization
- Integration with existing Supabase infrastructure
- Explainability and audit trail for AI-generated recommendations

## Considered Options

1. **Dual-agent (CFO + Auditor) with pgvector RAG on Supabase**
2. Single AI agent with rule-based post-processing
3. Third-party financial review SaaS platform
4. Continue with manual review processes with basic automation

## Decision Outcome

Chosen option: "Dual-agent (CFO + Auditor) with pgvector RAG on Supabase", because it provides:

- Independent challenge loop (CFO proposes, Auditor challenges)
- Native integration with existing Supabase database
- Semantic search over ledger and documents via pgvector
- Full control over prompts, models, and data residency
- Cost-effective compared to SaaS alternatives
- Extensible architecture for future agent specialization

### Positive Consequences

- Automated daily close validation reduces manual effort by ~80%
- Faster identification of documentation gaps and reconciliation breaks
- Consistent application of tax rules via tax_maps table
- Comprehensive audit trail in controls_logs table
- RAG retrieval provides context-aware recommendations
- Multi-tenant RLS ensures data isolation between organizations
- OpenAPI-compatible REST APIs enable dashboard integration

### Negative Consequences

- Requires maintenance of agent prompts as business rules evolve
- Dependency on OpenAI API availability and rate limits
- Vector search performance degrades without proper index tuning
- Initial setup requires database schema changes and data migration
- Agent outputs require human validation for high-risk decisions

## Pros and Cons of the Options

### Dual-agent (CFO + Auditor) with pgvector RAG on Supabase

- Good, because separation of duties mirrors real-world CFO/Auditor relationship
- Good, because pgvector enables semantic search over financial text
- Good, because Supabase RLS provides tenant isolation
- Good, because schema changes are idempotent and versioned
- Good, because OpenAI models are continuously improving
- Bad, because prompt engineering requires iteration
- Bad, because vector index requires periodic maintenance
- Bad, because OpenAI API costs scale with usage

### Single AI agent with rule-based post-processing

- Good, because simpler architecture with fewer moving parts
- Good, because deterministic rules are more explainable
- Bad, because lacks independent challenge mechanism
- Bad, because rule maintenance becomes brittle at scale
- Bad, because no semantic search capability

### Third-party financial review SaaS platform

- Good, because outsources maintenance burden
- Good, because vendor may provide domain expertise
- Bad, because high recurring costs
- Bad, because data residency and compliance concerns
- Bad, because limited customization for IKANISA/SACCO specifics

### Continue with manual review processes with basic automation

- Good, because no architectural changes required
- Bad, because doesn't scale with transaction growth
- Bad, because human error risk remains high
- Bad, because slow feedback loops delay issue resolution

## Implementation Details

### Database Schema

Tables added to Supabase:
- `ledger_entries`: General ledger with org_id, date, account, debit/credit
- `support_docs`: Supporting documentation with OCR text for RAG
- `tax_maps`: Tax treatment rules per account/jurisdiction
- `controls_logs`: Audit trail of review executions and findings
- `embeddings`: Vector embeddings (1536-d) for semantic search

RPC function: `match_embeddings(p_org_id, query_vector, match_threshold, match_count)`

### Security Model

- Row-Level Security (RLS) enforces tenant isolation via JWT `org_id` claim
- Service role key used server-side for bulk operations (never exposed to client)
- Anon key used client-side with RLS enforcement
- All agent executions logged to `controls_logs` with full output details

### Agent Architecture

**CFO Agent**:
- System prompt defines daily close responsibilities
- Output schema: `{summary, status, issues[], proposed_entries[]}`
- Zod schema validation ensures structured JSON responses
- Temperature 0.2 for consistent outputs

**Auditor Agent**:
- System prompt defines independent challenge role
- Receives CFO output as context for challenge
- Output schema: `{exceptions[], risk_level, comments[]}`
- Focus on materiality, sampling, and control weaknesses

**RAG Pipeline**:
- OpenAI text-embedding-3-small (1536 dimensions)
- Hybrid retrieval: vector similarity + SQL filters (org_id, date range)
- IVFFlat index with 100 lists for <100k embeddings
- Similarity threshold 0.7 for relevance

### API Design

Next.js API routes under `/api/review/`:
- `POST /run`: Execute dual-agent review (returns CFO + Auditor outputs)
- `POST /missing-docs`: Find entries without supporting documents
- `POST /tax-risk`: Identify accounts missing tax mappings
- `POST /float-breaks`: Reconcile SACCO float vs MoMo settlement

All routes use zod validation and return typed JSON responses.

## Links

- Implementation: PR #XXX (this PR)
- Supabase pgvector docs: https://supabase.com/docs/guides/database/extensions/pgvector
- OpenAI embeddings: https://platform.openai.com/docs/guides/embeddings
- IFRS revenue recognition: https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/
- Related ADRs: (none yet, this is the first for finance review system)
