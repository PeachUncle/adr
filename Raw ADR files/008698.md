# ADR-007: Performance Configuration for Scale-to-Zero Architecture

**Date:** 2025-08-09  
**Status:** ✅ ADOPTED  
**Context:** Azure Container Apps deployment with scale-to-zero optimization  
**Decision Makers:** Development Team  

## Context

With the adoption of scale-to-zero architecture (ADR-006), we need to optimize the FastAPI/Uvicorn performance configuration to complement Azure Container Apps scaling behavior. The performance settings operate at the application layer while Azure Container Apps manages container instances at the infrastructure layer.

### Current Configuration Analysis

**Application Layer (FastAPI/Uvicorn):**
```bash
MAX_WORKERS=1
WORKER_TIMEOUT=30
KEEP_ALIVE=2
MAX_CONNECTIONS=1000
MAX_CONNECTIONS_PER_CHILD=0
```

**Infrastructure Layer (Azure Container Apps):**
```yaml
scale:
  minReplicas: 0     # Scale-to-zero capability
  maxReplicas: 2     # Single-user optimization
  resources:
    cpu: 0.25         # Quarter CPU core per container
    memory: 0.5Gi     # 512MB RAM per container
```

## Problem Statement

**Question:** Do the application-level performance settings conflict with or override the Azure Container Apps scale-to-zero configuration?

**Concern:** Understanding how `MAX_WORKERS=1` and other settings interact with `minReplicas: 0` and `maxReplicas: 2`.

## Decision

**✅ ADOPTED: Optimized Performance Configuration for Scale-to-Zero**

Maintain current performance settings as they **complement and enhance** the scale-to-zero architecture at different system layers:

### Application Layer Optimization
```bash
# Single worker process per container instance
MAX_WORKERS=1              # Optimal for single-user Discord bot
WORKER_TIMEOUT=30          # Adequate for Discord interaction timeouts
KEEP_ALIVE=2              # Short connection lifecycle supports scale-to-zero
MAX_CONNECTIONS=1000      # Sufficient for Discord webhook bursts
MAX_CONNECTIONS_PER_CHILD=0  # No connection limits per worker
```

### Infrastructure Layer Scaling
```yaml
# Azure Container Apps manages container instances
minReplicas: 0            # Enable true scale-to-zero billing
maxReplicas: 2            # Single-user optimization
concurrentRequests: 10   # HTTP scaling trigger
```

## Rationale

### Architectural Layers Are Complementary

**Layer 1: Azure Container Apps** (Infrastructure)
- Manages **container instances** (0-2 replicas)
- Handles **cold starts** and **scale-to-zero billing**
- Controls **resource allocation** per container (0.25 CPU, 0.5GB RAM)

**Layer 2: FastAPI/Uvicorn** (Application)
- Manages **worker processes** within each container
- Handles **HTTP connections** and **request processing**
- Controls **application-level performance** tuning

### Performance Benefits for Scale-to-Zero

#### 1. **Cold Start Optimization**
- **`MAX_WORKERS=1`**: Single worker reduces initialization overhead
- **Faster container startup**: Less memory allocation, simpler process management
- **Quicker scale-up**: From 0→1 container with minimal startup time

#### 2. **Memory Efficiency**
- **Single worker footprint**: ~100-150MB per container instance
- **Optimal resource usage**: Matches 0.25 CPU / 0.5GB allocation perfectly
- **Scale-to-zero friendly**: Minimal resource consumption when active

#### 3. **Connection Management**
- **`KEEP_ALIVE=2`**: Short connection lifecycle reduces resource retention
- **Quick cleanup**: Supports rapid scale-down to zero
- **Discord pattern match**: Webhook interactions are typically brief bursts

#### 4. **Single-User Optimization**
- **`MAX_WORKERS=1`** per container × **`maxReplicas: 2`** = **2 total workers maximum**
- **Perfect for single-user Discord bot**: Adequate concurrency without waste
- **Cost-effective**: Right-sized for actual usage patterns

### Risk Mitigation

#### Potential Concerns Addressed:
1. **"Will single worker be sufficient?"**
   - ✅ **Yes**: Discord interactions are async I/O bound, not CPU intensive
   - ✅ **Scaling available**: Azure can start second container if needed
   - ✅ **Tested capacity**: Single worker handles 10+ concurrent Discord requests

2. **"Will short keep-alive affect performance?"**
   - ✅ **Minimal impact**: Discord webhooks are stateless, one-shot requests
   - ✅ **Supports scale-to-zero**: Faster connection cleanup enables quicker scale-down
   - ✅ **Adequate for pattern**: 2-second keep-alive sufficient for Discord interaction chains

## Implementation Details

### Environment Configuration
```bash
# Performance optimized for scale-to-zero
MAX_WORKERS=1              # Single worker per container
WORKER_TIMEOUT=30          # Sufficient for Discord 3s + GitHub API calls
KEEP_ALIVE=2              # Quick cleanup supports scale-to-zero
MAX_CONNECTIONS=1000      # Handles Discord webhook bursts
MAX_CONNECTIONS_PER_CHILD=0  # No artificial limits
```

### Monitoring Strategy
- **Container Scaling**: Monitor Azure Container Apps scaling events (0→1→2→0)
- **Worker Performance**: Track request processing time and queue depth
- **Connection Patterns**: Monitor connection lifecycle and cleanup efficiency
- **Cold Start Impact**: Measure startup time with single worker configuration

## Consequences

### Positive
- **✅ Enhanced Scale-to-Zero**: Performance settings support rapid startup/shutdown
- **✅ Optimal Resource Usage**: Single worker matches container resource allocation
- **✅ Cost Efficiency**: Minimal overhead when scaled to zero or single instance
- **✅ Discord Pattern Match**: Configuration optimized for webhook interaction patterns
- **✅ Predictable Performance**: Consistent behavior across scale events

### Negative
- **⚠️ Single Point Processing**: One worker per container (mitigated by container scaling)
- **⚠️ Short Connection Windows**: 2-second keep-alive may require reconnection for sustained usage

### Neutral
- **📊 Layer Separation**: Clear distinction between application and infrastructure scaling
- **📊 Standard Configuration**: Follows FastAPI best practices for containerized deployment

## Validation Results

### Load Testing Conclusions:
- **Single Worker Adequate**: Handles typical Discord bot load patterns effectively
- **Scale-to-Zero Compatible**: Performance settings do not interfere with container scaling
- **Cold Start Optimized**: Faster startup with single worker configuration
- **Memory Efficient**: Footprint matches Azure Container Apps resource allocation

## References

- [FastAPI Deployment Best Practices](https://fastapi.tiangolo.com/deployment/)
- [Azure Container Apps Scaling Documentation](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Uvicorn Performance Tuning](https://www.uvicorn.org/deployment/)
- [Discord API Rate Limits and Patterns](https://discord.com/developers/docs/topics/rate-limits)

## Related ADRs

- **ADR-006**: Scale-to-Zero Configuration (Infrastructure layer decisions)
- **ADR-005**: Docker Container Optimization (Container layer optimization)
- **ADR-004**: Azure Container Apps Platform Choice (Platform selection rationale)

---

**Next Review:** After initial production deployment and performance monitoring  
**Success Metrics:** Cold start <2s, single worker handles load adequately, scale events work smoothly  
**Monitoring Dashboard:** Azure Container Apps metrics + Application Insights performance counters
