# ADR-002: Fallback Retrieval Architectures

- **Date**: 2025-09-19 (refresh)
- **Status**: Accepted (standby contingency)
- **Owner**: Lead Architect
- **Related ADRs**: ADR-001 (Primary Paper Selection)

## Context
ADR-001 selects “Transforming LLMs into Cross-modal and Cross-lingual Retrieval Systems” as the baseline. Legal review completed on 2025-09-18 approved the primary datasets (FLEURS, CoVoST 2, MuST-C v2, VoxPopuli, Multilingual LibriSpeech) with documented restrictions: MuST-C remains internal-only (CC BY-NC-ND), VoxPopuli/WikiMatrix require CC BY-SA share-alike, and AudioCaps/How2 operate feature-only under CC BY + YouTube ToS. Although the primary plan is green, we need a contingency in case redistribution limits or PaLM checkpoint access block key deliverables.

## Proposed Alternatives
1. **SpeechCLIP (Interspeech 2022)** – Dual encoder over AudioCaps/Clotho/SpokenCOCO with CLIP-style contrastive loss. Suitable for audio-text retrieval with public checkpoints; relies on CC-BY datasets plus MSCOCO licensing for SpokenCOCO.
2. **CLAP (ICASSP 2023)** – Large-scale audio-text contrastive pretraining (AudioSet, LAION-Audio). Offers open-source checkpoints and supports fine-tuning for multilingual retrieval when paired with translation corpora.

## Decision
- Adopt SpeechCLIP or CLAP as the fallback baseline if either condition holds:
  1. Compliance disallows distributing Phase 3/4 models trained on NC/SA corpora despite internal-use allowances.
  2. PaLM-family checkpoints or equivalent large multimodal models remain inaccessible for licensing or compute reasons by Phase 4 kickoff.
- Prioritize datasets with permissive licenses (AudioCaps, Clotho, Multilingual LibriSpeech, FLEURS public splits) to minimize legal overhead in the fallback path.

## Rationale
- Both alternatives have open implementations and proven retrieval metrics, enabling faster pivot.
- They can integrate with existing dataset landscape entries and share preprocessing pipelines (audio feature extraction, caption normalization).
- Maintains alignment with Auto-Paper’s cross-modal objectives while avoiding NC/SA complexities if required.

## Consequences
- **Data**: If fallback triggered, update dataset manifest to deprioritize MuST-C/VoxPopuli and elevate AudioCaps/Clotho/MLS. Compliance notices in README/manifest already reflect licensing as of 2025-09-19.
- **Model**: Training scripts must support CLIP-style dual encoders alongside PaLM-based architecture.
- **Evaluation**: Metrics shift toward audio-caption retrieval benchmarks (R@K, mAP) in addition to cross-lingual metrics.
- **Documentation**: Roadmap and backlog require updates; ADR-001 remains baseline but references ADR-002 for contingency.

## 2025-09-21 Legal Update
- Compliance meeting (2025-09-20) reaffirmed that NC/SA datasets remain internal-only but permissible for Phase 3 workflows; no additional restrictions introduced.
- Director captured fallback triggers in `docs/notes/planning/program-roadmap.md` and sprint backlog item now closed with this ADR reference.
- Status remains “Accepted”; revisit during the 2025-10-04 readiness review to confirm whether fallback activation is required.

## Follow-up Actions
- Monitor PaLM checkpoint availability; raise change request if access still blocked by Phase 4 planning review (2025-10-15 target).
- Prototype minimal SpeechCLIP training on AudioCaps once ingestion pipeline exists to estimate compute requirements (blocked on ingest sample run completion).
- Coordinate with Director to add conditional milestones in program roadmap and sprint backlog if fallback activated.
- Mirror updates in `docs/notes/compliance/compliance-readiness-report.md` whenever licensing guidance changes (owner: Compliance Steward).
