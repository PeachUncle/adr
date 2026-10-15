> **🟢 [ACTIVE]** — Architecture Decision Record  
> **Canon Code:** ADR_003  
> **Version:** 1.0.0  
> **Purpose:** Kernel tech stack decision (Hono vs Next.js)  
> **Plane:** A — Governance (ADR)  
> **Date:** 2025-12-12

---

# ADR_003: Kernel Tech Stack Decision - Hono vs Next.js

**Decision:** ✅ **HONO** (Recommended)  
**Status:** **FINAL**

---

## Executive Summary

After analyzing PRD requirements, performance benchmarks, and architectural constraints, **Hono is the clear choice** for the AIBOS Kernel. This decision is supported by:

1. **PRD Explicit Recommendation:** "Hono (recommended for high throughput)"
2. **Performance Requirements:** < 50ms latency, 10,000 events/second target
3. **Benchmark Evidence:** Hono ~394k req/sec vs Next.js ~150ms TTFB
4. **Architectural Fit:** Pure API service, no frontend needs
5. **Deployment Flexibility:** Multi-runtime support (Node, Bun, Edge)

---

## Requirements Analysis

### From PRD_KERNEL_01:

| Requirement | Target | Criticality |
|-------------|--------|-------------|
| **Latency** | < 50ms (p95) for metadata queries | 🔴 **CRITICAL** |
| **Throughput** | 10,000 events/second | 🔴 **CRITICAL** |
| **Service Type** | Standalone API (REST + RPC) | 🔴 **CRITICAL** |
| **Deployment** | Docker/K8s or serverless | 🟡 **IMPORTANT** |
| **Framework** | High-performance, lightweight | 🔴 **CRITICAL** |

### Silent Killer Frontend Requirements:

- **Ultra-Fast Queries:** < 50ms response time (prevents UI lag)
- **High Concurrency:** Multiple frontend instances querying simultaneously
- **Edge Deployment:** Potential for edge deployment for global latency

---

## Evidence-Based Comparison

### 1. Performance Benchmarks

| Metric | Hono | Next.js API Routes | Winner |
|--------|------|-------------------|--------|
| **Requests/Second** | ~394,000 req/sec | ~6,600 req/sec* | ✅ **Hono (60x faster)** |
| **TTFB (Time to First Byte)** | < 10ms | ~150ms | ✅ **Hono (15x faster)** |
| **Memory Footprint** | ~5MB | ~50MB+ | ✅ **Hono (10x smaller)** |
| **Cold Start** | < 5ms | ~200-500ms | ✅ **Hono (40-100x faster)** |

*Estimated based on Next.js TTFB and typical Node.js performance

**Evidence Source:**
- Hono: Microservice Solutions benchmark (394k req/sec)
- Next.js: Johal.in study (150ms TTFB, 40% improvement with App Router)

### 2. Architectural Fit

| Aspect | Hono | Next.js | Winner |
|--------|------|---------|--------|
| **Pure API Service** | ✅ Designed for APIs | ⚠️ Full-stack framework | ✅ **Hono** |
| **Frontend Overhead** | ✅ None | ❌ React, SSR, etc. | ✅ **Hono** |
| **Bundle Size** | ✅ ~50KB | ❌ ~2MB+ | ✅ **Hono** |
| **Standalone Deployment** | ✅ Native | ⚠️ Possible but heavy | ✅ **Hono** |
| **Edge Runtime Support** | ✅ Cloudflare, Deno, Bun | ⚠️ Node.js only | ✅ **Hono** |

### 3. PRD Alignment

| PRD Requirement | Hono | Next.js | Match |
|-----------------|------|---------|-------|
| "High throughput" | ✅ 394k req/sec | ⚠️ ~6.6k req/sec | ✅ **Hono** |
| "Lightweight" | ✅ ~5MB footprint | ❌ ~50MB+ | ✅ **Hono** |
| "Standalone API" | ✅ Pure API framework | ⚠️ Full-stack | ✅ **Hono** |
| "Fast API framework" | ✅ Explicitly recommended | ⚠️ Not optimized for APIs | ✅ **Hono** |

### 4. Silent Killer Frontend Requirements

| Requirement | Hono | Next.js | Winner |
|-------------|------|---------|--------|
| **< 50ms Response** | ✅ Typical < 10ms | ⚠️ ~150ms TTFB | ✅ **Hono** |
| **High Concurrency** | ✅ 394k req/sec | ⚠️ Limited by Node.js | ✅ **Hono** |
| **Edge Deployment** | ✅ Native support | ❌ Node.js only | ✅ **Hono** |
| **Micro-Actions** | ✅ Fast enough for inline edits | ⚠️ May cause UI lag | ✅ **Hono** |

---

## Decision Matrix

### Scoring (1-5, 5 = Best):

| Criterion | Weight | Hono | Next.js | Weighted Hono | Weighted Next.js |
|-----------|--------|------|---------|---------------|------------------|
| **Performance** | 30% | 5 | 2 | 1.50 | 0.60 |
| **Architectural Fit** | 25% | 5 | 2 | 1.25 | 0.50 |
| **PRD Alignment** | 20% | 5 | 2 | 1.00 | 0.40 |
| **Deployment Flexibility** | 15% | 5 | 3 | 0.75 | 0.45 |
| **Team Familiarity** | 10% | 3 | 5 | 0.30 | 0.50 |
| **TOTAL** | 100% | - | - | **4.80** | **2.45** |

**Winner:** Hono (4.80 vs 2.45) - **96% higher score**

---

## Risk Analysis

### Hono Risks & Mitigations:

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Team Learning Curve** | Low | Hono uses Web Standards API (familiar), simple syntax |
| **Ecosystem Maturity** | Low | Hono is production-ready, used by major companies |
| **Documentation** | Low | Excellent docs, active community |

### Next.js Risks:

| Risk | Impact | Why It Matters |
|------|--------|----------------|
| **Performance Gap** | 🔴 **HIGH** | 60x slower - cannot meet < 50ms requirement |
| **Unnecessary Overhead** | 🟡 **MEDIUM** | React/SSR not needed for pure API |
| **Deployment Complexity** | 🟡 **MEDIUM** | Heavier container, slower cold starts |

---

## Final Recommendation: **HONO**

### Reasoning:

1. **Performance is Non-Negotiable:**
   - PRD requires < 50ms latency
   - Hono: ~10ms typical, Next.js: ~150ms TTFB
   - **Hono is 15x faster** - critical for Silent Killer Frontend

2. **Architectural Purity:**
   - Kernel is a **pure API service** - no frontend needs
   - Hono is designed for APIs, Next.js is designed for full-stack
   - **Right tool for the job**

3. **PRD Explicit Recommendation:**
   - PRD states: "Hono (recommended for high throughput)"
   - This recommendation is based on performance requirements
   - **Follow the specification**

4. **Future-Proof:**
   - Edge deployment support (Cloudflare, Deno, Bun)
   - Multi-runtime compatibility
   - **Deployment flexibility**

5. **Monorepo Benefits:**
   - Shared `packages/schemas` ensures type safety
   - Shared `packages/shared` for utilities
   - **Consistency through packages, not framework**

### Trade-offs Accepted:

- **Team Learning:** Minimal - Hono uses Web Standards API
- **Ecosystem:** Sufficient - Hono has mature ecosystem
- **Consistency:** Achieved through shared packages, not framework

---

## Implementation Plan

### Phase 1: Initialize "DNA" (`packages/schemas`)
- Create package structure
- Define Kernel API types (from PRD)
- Export Zod schemas for validation
- Shared between Kernel and Web

### Phase 2: Initialize "Brain" (`apps/kernel`)
- Create Hono server
- Set up Drizzle ORM
- Implement health check endpoint
- Implement first metadata endpoint

---

**Decision:** ✅ **HONO**

**Confidence Level:** 🔴 **VERY HIGH** (96% decision matrix score, PRD recommendation, performance evidence)

**Next Action:** Initialize `packages/schemas` and `apps/kernel` with Hono.
