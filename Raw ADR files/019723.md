# ADR-004: Model Packaging as OCI Artifacts

**Status:** Accepted
**Date:** 2025-10-24
**Deciders:** Engineering Team, ML Engineering
**Context:** Local compute policy, multi-tier model deployment

---

## Context and Problem Statement

Vantage deploys AI models to **three compute tiers** with different requirements:

| Tier | Hardware | Model Format | Constraints |
|:--|:--|:--|:--|
| **Edge (Jetson)** | Jetson Orin NX (8 GB VRAM) | TensorRT (INT8/FP16) | Ultra-low latency, minimal power |
| **Workstation** | RTX 6000 Pro (48 GB VRAM) | ONNX / TensorRT / vLLM | Real-time inference, local LLMs |
| **Cloud** | RunPod DGX (80 GB VRAM) | PyTorch FP32/AMP | Training, large fusion models |

**Problems with current ad-hoc approach:**
- **No versioning:** Models stored as loose files in S3; unclear which version is deployed
- **No metadata:** Cannot query "does this model fit in 8 GB VRAM?" before pull
- **No rollback:** Broken model pushed → manual S3 restore
- **No provenance:** Cannot trace model → training run → dataset

**Need:** A standard packaging format with:
- Semantic versioning (`retina/seg:2.4.1`)
- Capability labels (`cv3`, `int8`, `vram:8gb`)
- Metadata (VRAM, input/output schema, training provenance)
- Atomic pull/rollback

---

## Decision

We adopt **OCI (Open Container Initiative) artifacts** to package models. OCI is the same format used for Docker images, supported by all major registries (Docker Hub, Harbor, AWS ECR, GitHub Packages).

### Why OCI?

- **Standard format:** Registries, tooling, and security scanning already exist
- **Layer deduplication:** Base layers (ONNX runtime, TensorRT) shared across models
- **Atomic pulls:** Download fails → no partial state
- **Multi-arch support:** Tag per target (`retina/seg:2.4.1-jetson`, `retina/seg:2.4.1-dgx`)
- **Provenance:** OCI manifests support SBOM (Software Bill of Materials)

### Model Artifact Structure

```
retina-segmentation:2.4.1-jetson  (OCI image)
├── manifest.json                  # OCI manifest
├── layers/
│   ├── tensorrt-base.tar.gz       # Layer 0: TensorRT runtime (shared)
│   ├── model-weights.tar.gz       # Layer 1: TensorRT engine
│   └── metadata.tar.gz            # Layer 2: Input/output schema, VRAM, provenance
└── config.json                    # OCI config with labels
```

### Metadata Schema

```json
{
  "name": "retina/seg",
  "version": "2.4.1",
  "variant": "jetson",
  "model": {
    "format": "tensorrt",
    "precision": "int8",
    "inputShape": [1, 3, 512, 512],
    "outputShape": [1, 128, 512, 512],
    "vramGB": 2.1,
    "latencyMs": 18
  },
  "capabilities": ["cv3", "int8", "retina"],
  "provenance": {
    "trainingRun": "wandb://vantage/retina-seg/runs/abc123",
    "dataset": "vantage-retina-v3 (n=5000, de-identified)",
    "trainedAt": "2025-10-20T12:00:00Z",
    "trainedBy": "ml-eng@vantage.health"
  },
  "deployment": {
    "targets": ["jetson-orin-nx", "jetson-agx-orin"],
    "minCudaVersion": "12.0",
    "minTensorRTVersion": "8.6"
  }
}
```

### Building a Model Artifact

```dockerfile
# Dockerfile.retina-seg-jetson
FROM nvcr.io/nvidia/tensorrt:23.10-py3 AS base

# Copy TensorRT engine
COPY models/retina_seg_int8.engine /models/

# Copy metadata
COPY metadata.json /models/

# Copy inference script
COPY infer.py /app/

CMD ["python", "/app/infer.py"]
```

```bash
# Build and push
docker build -t vantage/retina-seg:2.4.1-jetson -f Dockerfile.retina-seg-jetson .
docker push vantage/retina-seg:2.4.1-jetson

# Tag with capability labels
docker tag vantage/retina-seg:2.4.1-jetson vantage/retina-seg:latest-jetson
docker tag vantage/retina-seg:2.4.1-jetson vantage/retina-seg:cv3
```

### Pulling by Capability

```typescript
// packages/policy/src/model-registry.ts
export async function pullModel(capability: string, target: Target): Promise<ModelHandle> {
  // Query registry for capability label
  const tag = `${capability}-${target}` // e.g., "cv3-jetson"
  const image = `vantage/retina-seg:${tag}`

  // Pull OCI artifact
  await exec(`docker pull ${image}`)

  // Extract metadata
  const metadata = await exec(`docker run --rm ${image} cat /models/metadata.json`)
  return { image, metadata: JSON.parse(metadata) }
}
```

### Runtime: Model Runner Sidecar

Instead of embedding inference in every service, deploy a **model-runner sidecar** with gRPC API:

```protobuf
// packages/model-runner/proto/inference.proto
syntax = "proto3";

service Inference {
  rpc Infer(InferRequest) returns (InferResponse);
  rpc Health(HealthRequest) returns (HealthResponse);
}

message InferRequest {
  string model_name = 1;   // e.g., "retina/seg"
  bytes input_tensor = 2;  // Serialized tensor
  map<string, string> metadata = 3;
}

message InferResponse {
  bytes output_tensor = 1;
  float latency_ms = 2;
  string model_version = 3;
}
```

```yaml
# docker-compose.workstation.yml
services:
  model-runner:
    image: vantage/model-runner:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # For pulling models
      - /models:/models
    environment:
      - MODEL_REGISTRY=registry.vantage.health
    ports:
      - "50051:50051"  # gRPC
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Integration with Local Compute Policy

```typescript
// packages/workflows/src/activities/seg-workstation.ts
import { InferenceClient } from '@vantage/model-runner-client'

const client = new InferenceClient('localhost:50051')

export async function segWorkstation({ sessionId, captureId }: ActivityInput) {
  // Fetch image from local MinIO
  const image = await minio.getObject(`ring1/${captureId}.jpg`)

  // Call model runner sidecar
  const result = await client.infer({
    modelName: 'retina/seg',
    inputTensor: preprocessImage(image),
    metadata: { sessionId, captureId }
  })

  // Store segmentation mask
  await minio.putObject(`ring2/${captureId}_mask.png`, result.outputTensor)

  return { maskUrl: `ring2/${captureId}_mask.png`, latencyMs: result.latencyMs }
}
```

### Policy Integration

**Local Compute Policy (ADR-001) queries model metadata:**

```typescript
// packages/policy/src/execution-policy.ts
import { getModelMetadata } from './model-registry'

export async function decideTarget(ctx: Context): Promise<Target> {
  // Fetch model VRAM requirement
  const model = await getModelMetadata(ctx.model.name)

  // VRAM gate: model too large for workstation → cloud
  if (model.vramGB > ctx.vrams.workstation) return 'cloud'

  // ... other gates
}
```

---

## Consequences

### Positive

- **Versioned deployments:** Rollback via `docker pull vantage/retina-seg:2.4.0` (previous version)
- **Query before pull:** Policy checks VRAM in metadata before download
- **Provenance:** Metadata links model → training run → dataset (compliance requirement)
- **Standard tooling:** Harbor registry, Trivy scanning, OCI SBOM
- **Multi-tier support:** Same packaging format for Jetson, Workstation, Cloud (different variants)
- **Layer deduplication:** TensorRT base layer (2 GB) shared across all models

### Negative

- **OCI overhead:** Docker pull adds 5-10s latency vs direct S3 download
  - *Mitigation:* Pre-pull models during workstation enrollment; cache locally
- **Registry dependency:** If Harbor/ECR is down, cannot pull new models
  - *Mitigation:* Workstations cache last 3 model versions locally; can rollback offline
- **Large image sizes:** ONNX models can be 500 MB–2 GB
  - *Mitigation:* OCI layers + compression reduce transfers; zstd yields 3× compression

---

## Alternatives Considered

### Alternative 1: Store Models Directly in S3

**Pros:** Simple; fast download; no registry needed
**Cons:** No versioning, metadata, or rollback; manual provenance tracking

**Decision:** Rejected. OCI benefits outweigh small overhead.

### Alternative 2: Custom Model Registry (e.g., MLflow Model Registry)

**Pros:** ML-specific features (A/B testing, champion/challenger)
**Cons:** Another service to maintain; no standard tooling; not OCI-compatible

**Decision:** Rejected. OCI is industry standard; reuse container tooling.

### Alternative 3: Embed Models in Service Images

**Pros:** Single artifact (service + model)
**Cons:** Huge images (5 GB+); model update requires service redeploy

**Decision:** Rejected. Models update more frequently than code; separate concerns.

---

## Security Considerations

### Vulnerability Scanning

```bash
# Scan OCI image for CVEs (base layers)
trivy image vantage/retina-seg:2.4.1-jetson
```

### Signing

```bash
# Sign with Sigstore/Cosign
cosign sign vantage/retina-seg:2.4.1-jetson

# Verify signature before pull
cosign verify vantage/retina-seg:2.4.1-jetson
```

### SBOM (Software Bill of Materials)

```json
// Embed SBOM in OCI manifest
{
  "packages": [
    { "name": "tensorrt", "version": "8.6.1", "license": "NVIDIA" },
    { "name": "onnxruntime", "version": "1.16.0", "license": "MIT" },
    { "name": "opencv-python", "version": "4.8.1", "license": "Apache-2.0" }
  ]
}
```

---

## Related Decisions

- **ADR-001:** Local Compute Decision Policy (uses VRAM metadata to decide target)
- **Development Plan:** Week 2 (Model Registry & Packaging)

---

## References

- [OCI Artifacts Specification](https://github.com/opencontainers/artifacts)
- [Harbor Registry](https://goharbor.io/)
- [Trivy OCI Scanner](https://github.com/aquasecurity/trivy)
- [Sigstore/Cosign](https://www.sigstore.dev/)
- TensorRT: [NVIDIA TensorRT](https://developer.nvidia.com/tensorrt)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Vantage Engineering + ML Engineering
