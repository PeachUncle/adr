# ADR-010: Vertex AI RAG Engine Migration

**Status:** Accepted
**Date:** 2025-12-28
**Decision Makers:** TechTrend Federal - Digital Twin Team
**Category:** RAG Infrastructure
**Supersedes:** N/A (Evolutionary change)

---

## Context

RANGER initially implemented its NEPA knowledge base using the **Gemini AI Studio File Search API**. This approach worked well during early prototyping when using AI Studio API keys (`GOOGLE_API_KEY`).

However, as the architecture matured to production-ready Vertex AI (per ADR-006), we discovered:

1. **File Search API Not Available on Vertex AI** — The File Search API is exclusive to AI Studio and does not work with Vertex AI Application Default Credentials (ADC).
2. **Corpus Fragmentation** — AI Studio stores are not accessible from Vertex AI, creating isolated knowledge silos.
3. **Production Incompatibility** — File Search API is designed for developer prototyping, not production deployments with service accounts.
4. **Region Lock-in** — File Search API has limited region support; Vertex RAG supports us-central1.

---

## Decision

**Migrate all knowledge base infrastructure from Gemini File Search API to Vertex AI RAG Engine.**

All four knowledge base corpora now use Vertex AI RAG:
- **NEPA Regulations** (nepa_advisor)
- **Burn Severity Protocols** (burn_analyst)
- **Timber Salvage Standards** (cruising_assistant)
- **Trail Infrastructure Guidelines** (trail_assessor)

**File Search API code and configuration files are removed from the codebase.**

---

## Implementation

### New Workflow (`knowledge/` Directory)

**Centralized knowledge base management:**
```bash
# 1. Download documents from authoritative sources
python knowledge/scripts/1_download_documents.py

# 2. Sync PDFs to GCS bucket (gs://ranger-knowledge-base/)
python knowledge/scripts/2_sync_to_gcs.py

# 3. Create Vertex RAG corpora (one per agent)
python knowledge/scripts/3_create_corpora.py

# 4. Import documents into corpora
python knowledge/scripts/4_import_documents.py

# 5. Verify corpus health
python knowledge/scripts/5_verify_corpora.py
```

### Manifest-Driven Architecture

**Single source of truth:** `knowledge/manifest.yaml`
```yaml
project: "ranger-twin-dev"
location: "us-central1"
gcs_bucket: "ranger-knowledge-base"
embedding_model: "text-embedding-005"
```

All scripts read from the manifest, ensuring consistent configuration.

### Agent-Level Integration

**RAG query tools** (`agents/*/rag_query.py`):
- Updated to use `vertexai.preview.rag` API
- Load corpus resource IDs from `data/.vertex_rag_config.json`
- Default location: `us-central1`

---

## Files Deleted

**Legacy File Search setup scripts:**
- `agents/nepa_advisor/scripts/setup_file_search.py`
- `services/agents/nepa-advisor/scripts/setup_file_search.py`

**Orphaned AI Studio configuration files:**
- `agents/nepa_advisor/data/.file_search_store.json`
- `services/agents/nepa-advisor/.nepa_store_config.json`

---

## Consequences

### Positive

1. **Production-Ready** — Vertex RAG supports ADC, service accounts, and GCP IAM
2. **Unified Region** — All infrastructure in `us-central1` (Cloud Run, Cloud Build, RAG)
3. **Scalable** — GCS bucket approach supports multi-gigabyte document corpora
4. **Version Controlled** — Manifest tracks all 34 documents (16 Tier 1, 18 Tier 2)
5. **Auditable** — Corpus creation is scripted and reproducible

### Negative

1. **More Steps** — 5-step workflow vs. single File Search API setup script
2. **GCS Dependency** — Requires GCS bucket creation (minimal cost: ~$0.20/month)
3. **Initial Setup** — One-time corpus creation takes ~5 minutes per corpus

### Mitigations

| Risk | Mitigation |
|------|------------|
| Complex setup | Scripts are idempotent; documented in manifest header |
| GCS cost | Standard storage tier ($0.020/GB/month); total cost < $1/month |
| Regional restrictions | us-central1 supports RAG and all other RANGER services |

---

## Region Consolidation

As part of this migration, **all RAG infrastructure moved to us-central1**:

**Files updated:**
- `knowledge/manifest.yaml:18` — `location: "us-central1"`
- `agents/*/rag_query.py` — Default location fallback
- `agents/nepa_advisor/file_search.py` — Default location fallback
- `.env.example` — `VERTEX_AI_LOCATION=us-central1`
- `docker-compose.yml` — All agent services default to us-central1

This aligns with existing Cloud Run deployments in us-central1.

---

## Regional Migration (January 2025)

**Original Region:** us-central1
**New Region:** europe-west3 (Frankfurt)

**Migration Reason:**
Google Cloud restricted `us-central1` and `us-east4` Vertex AI RAG Engine to allowlist-only for new projects (effective December 2025). Migration to a generally available region was required for continued development and new corpus creation.

**europe-west3 Selection Criteria:**
- ✅ **General Availability (GA)** for Vertex AI RAG Engine
- ✅ **Gemini 2.0 Flash** support (answer generation model)
- ✅ **text-embedding-005** model availability
- ✅ **Equivalent SLA** and performance characteristics to us-central1
- ✅ **GDPR-compliant** EU region (future compliance benefit)
- ✅ **europe-west4** available as fallback GA region

**Architecture Decision:**
Created new GCS bucket `ranger-knowledge-base-eu` in europe-west3 to avoid cross-region latency during RAG operations. Original `ranger-knowledge-base` bucket in us-central1 remains as archived fallback.

**Files Updated (2025-12-28):**
- `knowledge/manifest.yaml:18` — `location: "europe-west3"`, `gcs_bucket: "ranger-knowledge-base-eu"`
- `agents/nepa_advisor/file_search.py:37` — Default location fallback
- `agents/burn_analyst/rag_query.py:34` — Default location fallback
- `agents/cruising_assistant/rag_query.py:34` — Default location fallback
- `agents/trail_assessor/rag_query.py:34` — Default location fallback
- `agents/nepa_advisor/.env.example:3` — `GOOGLE_CLOUD_LOCATION=europe-west3`
- `.env.example:20` — `VERTEX_AI_LOCATION=europe-west3`
- `docker-compose.yml:78,95` — All agent services default to europe-west3

**Migration Completed:** 2025-12-29

---

## Migration Status

**✅ Completed:**
- [x] Create `knowledge/` directory structure
- [x] Write 5-step pipeline scripts
- [x] Create manifest.yaml (34 documents, 4 corpora)
- [x] Update all agent RAG tools to Vertex API
- [x] Delete File Search legacy code
- [x] Consolidate region to us-central1

**🚧 In Progress:**
- [ ] Run corpus creation for all 4 agents
- [ ] Import documents to production corpora

---

## Future Considerations

**Vertex RAG Engine enhancements to explore in Phase 2+:**
- **Hybrid search** — Combine semantic + keyword search
- **Reranking** — Improve retrieval quality with reranker models
- **Custom embeddings** — Fine-tune embeddings on forestry domain
- **Multi-modal RAG** — Index diagrams, maps, and field photos

For now, standard Vertex RAG with text-embedding-005 meets Phase 1 needs.

---

## References

- [Vertex AI RAG Engine Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/rag-api)
- [ADR-006: Google-Only LLM Strategy](./ADR-006-google-only-llm-strategy.md) — Vertex AI migration
- [knowledge/manifest.yaml](../../knowledge/manifest.yaml) — Document inventory

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-28 | Migrate to Vertex RAG | File Search API incompatible with Vertex AI |
| 2025-12-28 | Region consolidation to us-central1 | Align with Cloud Run infrastructure |
| 2025-12-28 | Delete File Search code | No longer functional; technical debt |
| 2025-12-29 | Migrate to europe-west3 | us-central1 restricted to allowlist-only for new RAG projects |
