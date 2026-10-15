# ADR-001: Primary Paper Selection and Architecture Scope

- **Date**: 2025-09-18
- **Status**: Accepted
- **Decision Makers**: Lead Architect, Director
- **Contributors**: Research Curator, Data Scout, Compliance Steward

## Context
We will reproduce and extend “Transforming LLMs into Cross-modal and Cross-lingual Retrieval Systems” (arXiv:2404.01616) as the anchor study for the Auto-Paper initiative. The paper demonstrates how a text-only LLM (PaLM 2 XXS) can be adapted into a dual-encoder retrieval system that aligns speech and text across 102 languages, despite training on paired speech-text data for only 21 languages. It achieves a 10% absolute improvement in Recall@1 over prior multilingual retrieval systems and leverages contrastive training with discretized audio tokens to support cross-modal alignment at scale.citeturn0search0

## Decision
- Adopt the paper’s multi-modal dual-encoder framework as the baseline implementation target for Phase 4.
- Treat the reported metrics (Recall@1 ≥35% on FLEURS, zero-shot BLEU improvements on S2TT with WikiMatrix augmentation) as core reproduction criteria.citeturn0search1
- Use the paper’s dataset mix (CoVoST 2 for training, FLEURS for evaluation, WikiMatrix augmentation) to drive Phase 2 dataset discovery and governance activities.citeturn0search1
- Track PaLM 2 XXS initialization plus audio token extensions as the architectural baseline; subsequent ablations (alternate encoders, translation mixtures) will be scoped after baseline parity.

## Rationale
- The study aligns directly with Auto-Paper goals: cross-modal retrieval, multilingual coverage, and limited reliance on scarce speech-labelled data.
- Reported improvements over mSLAM and earlier retrieval systems indicate meaningful research value and reproducibility potential.citeturn0search1
- Datasets are largely open (CC-BY/CC0/ShareAlike), enabling governance within our compliance framework, while highlighting specific legal checkpoints (MuST-C CC BY-NC-ND, VoxPopuli CC BY-SA) captured in risk logs.

## Consequences
- **Phase 2**: Dataset landscape must prioritize CoVoST 2, FLEURS, WikiMatrix, plus complementary corpora for robustness. Compliance has cleared MuST-C (internal-only) and VoxPopuli (share-alike) usage; manifest and README must embed NC-ND and CC BY-SA notices.
- **Phase 3**: Ingestion and preprocessing pipelines must support discrete audio token generation (k-means with 1024 clusters at 25 Hz) and language/modality prefixes compatible with PaLM-based tokenization.citeturn0search1
- **Phase 4**: Model implementation must initialize from a PaLM-family checkpoint (or equivalent open alternative if licensing restricts use) and implement bidirectional contrastive loss with spreadout regularization as described in the paper.citeturn0search1
- **Phase 5–6**: Training orchestration and evaluation need to capture Recall@1, WER, BLEU, and zero-shot S2TT metrics; logs must distinguish seen vs. unseen languages to mirror published breakdowns.citeturn0search1

## Follow-up Actions
- Lead Architect: Draft ADR addendum detailing fallback plans for SpeechCLIP and CLAP in case PaLM 2 access is restricted.
- Compliance Steward: Record legal guidance for MuST-C (NC-ND) and VoxPopuli (SA) in the compliance log and readiness report.
- Data Scout: Finalize dataset manifest entries for CoVoST 2, FLEURS, WikiMatrix, and candidate backups.
- Director: Ensure roadmap milestones reference ADR-001 when reviewing Phase 2 exit criteria.
