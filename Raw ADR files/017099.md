# DECISION-001: Base Model Selection for Simplex Cognitive Models

**Status**: Approved
**Date**: 2026-01-08
**Decision Maker**: Engineering Team
**Related Task**: TASK-002-cognitive-models.md

---

## Context

Simplex Cognitive Hive AI requires a family of Small Language Models (SLMs) for different deployment tiers:

- **Divine Tier (30B)**: Cross-hive arbitration, complex reasoning
- **Hive Tier (7-8B)**: Primary specialist SLM per hive
- **Edge Tier (1-2B)**: Mobile/embedded/IoT inference
- **Embedding**: Semantic routing and memory recall

## Decision

### Selected Base Models

| Tier | Model | Parameters | Context | Quantization | License |
|------|-------|------------|---------|--------------|---------|
| Divine | **Qwen3-32B** | 32B | 128K | Q4_K_M, Q8_0 | Apache 2.0 |
| Hive | **Qwen3-8B** | 8.2B | 32K (128K w/YaRN) | Q4_K_M, Q8_0 | Apache 2.0 |
| Edge | **Qwen3-1.7B** | 1.7B | 32K | Q4_K_M, Q8_0 | Apache 2.0 |
| Embed | **nomic-embed-text-v1.5** | 137M | N/A | FP16 | Apache 2.0 |

### Why Qwen3 Over Qwen 2.5

The original task document recommended Qwen 2.5 models. We are updating to **Qwen3** (released April 2025) because:

1. **Newer architecture**: Qwen3 includes significant improvements over Qwen 2.5
2. **Thinking mode**: Native `/think` and `/no_think` modes for reasoning vs fast inference
3. **Better calibration**: Improved confidence calibration out of the box
4. **Same licensing**: Apache 2.0 maintained
5. **Model consistency**: All tiers use the same Qwen3 family for consistent behavior

### Model Specifications

#### Qwen3-8B (Hive Tier) - PRIMARY

```
Architecture:        qwen3
Parameters:          8.2B (6.95B non-embedding)
Layers:              36
Attention Heads:     32 (Q), 8 (KV)
Context Length:      32,768 native (131,072 with YaRN)
Embedding Dim:       4096
Quantization:        Q4_K_M (5.2 GB)
Capabilities:        completion, tools, thinking
```

**Features**:
- Thinking mode: Use `/think` for complex reasoning, `/no_think` for fast responses
- Tool calling support
- 128K extended context with YaRN rope scaling

#### Qwen3-32B (Divine Tier) - DEFERRED

- To be downloaded when AWS GPU instance is available
- Dense 32B model (not MoE)
- Requires ~18GB VRAM for Q4 inference

#### Qwen3-1.7B (Edge Tier) - PENDING

- Optimized for CPU/mobile inference
- Target: <100ms inference on Apple M1+

#### nomic-embed-text-v1.5 (Embedding) - PENDING

- Matryoshka embeddings (384 or 768 dimensions)
- Strong retrieval performance
- Ideal for semantic routing

## Alternatives Considered

### Divine Tier Alternatives

| Model | Pros | Cons | Decision |
|-------|------|------|----------|
| Mixtral 8x22B | MoE efficiency | Complex deployment, sparse | Rejected |
| Llama 3.1 70B | Strong performance | Too large, overkill | Rejected |
| DeepSeek-V2 | Very efficient | Origin concerns | Rejected |

### Hive Tier Alternatives

| Model | Pros | Cons | Decision |
|-------|------|------|----------|
| Mistral 7B v0.3 | Proven, simple | 32K context only | Fallback option |
| Llama 3.1 8B | Meta backing | Slightly larger | Not selected |
| Gemma 2 9B | Google quality | 8K context limit | Rejected |

## Infrastructure

### Current Setup

```
Ollama:     v0.13.5 installed
Platform:   macOS (Darwin 24.6.0)
Models:     qwen3:8b (Q4_K_M, 5.2GB) - INSTALLED
            qwen2.5:0.5b (397MB) - legacy
            tinyllama:latest (637MB) - legacy
```

### Model Storage

```
/Users/rod/code/simplex/models/
├── qwen3-8b/          # Hive tier metadata
├── qwen3-32b/         # Divine tier (pending)
├── qwen3-1.7b/        # Edge tier (pending)
└── nomic-embed/       # Embedding (pending)
```

Note: Actual model weights are managed by Ollama in `~/.ollama/models/`

### Performance Notes

- CPU inference on Qwen3-8B: ~1 token/second (expected for 8B on CPU)
- For production: GPU acceleration required
- Recommended: RTX 3090/4090 for Hive tier, A100 for Divine tier

## Next Steps

1. **Phase 2**: Fine-tune Qwen3-8B for Simplex context protocol
2. **Phase 3**: Add confidence calibration training
3. **Phase 4**: Create LoRA adapters for specialists
4. **Phase 5**: Set up AWS GPU instance for 32B model

## Verification

```bash
# Verify model is installed
ollama list | grep qwen3

# Test inference
ollama run qwen3:8b "What is 2+2?"

# API test
curl http://localhost:11434/api/generate \
  -d '{"model": "qwen3:8b", "prompt": "Hello", "stream": false}'
```

---

*Document generated as part of TASK-002 Phase 1 completion.*
