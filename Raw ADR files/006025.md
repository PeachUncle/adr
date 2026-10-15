# ADR-005: Infrastructure

## Status
Accepted

## Context
Infrastructure decisions for deployment, storage, and operations of the accounting application.

## Decisions

### 5.1 Document Storage
**Decision:** Dual implementation selectable by config - Local FS (MVP) + S3-compatible (Production).

**Implementations:**
1. **Local Filesystem (MVP/development)**
   - Profile: `storage.type=local`
   - Simple, zero external dependencies

2. **S3-Compatible Storage (Production)**
   - Profile: `storage.type=s3`
   - Works with: MinIO, AWS S3, GCP Cloud Storage

**Storage Optimization:**
- Image compression: 80% quality on upload
- Thumbnail generation for preview
- PDF optimization on upload
- Max per upload: 10 MB
- Supported formats: JPG, PNG, PDF, Excel, CSV

**Security:**
- ClamAV virus scanning on upload
- Reject infected files with error message

### 5.2 Cloud Hosting
**Decision:** Local Indonesian providers or DigitalOcean; avoid big cloud unless requested.

**Preferred Providers:**
- Indonesian: IDCloudHost, Biznet Gio, Dewaweb
- Global (budget): DigitalOcean
- Avoid: AWS, GCP (unless client specifically requests)

**Rationale:**
- Cost control for mid-range pricing strategy
- Data residency compliance (Indonesia)
- Big cloud overkill for target market

**Deployment:**
- Single VPS per instance (MVP)
- Docker Compose
- Can co-locate multiple instances for cost efficiency

### 5.3 Multi-Currency
**Decision:** Rupiah only for Phase 1.

**When Multi-Currency NOT Needed:**
- Pay foreign services via IDR credit card
- Receive foreign payments via PayPal auto-convert
- All bank accounts are in IDR

**When Multi-Currency IS Needed (Phase 2):**
- Own USD/foreign currency bank account
- Invoice in USD with payment to USD account

**Rationale:**
- Most target users (photographers, online sellers) use IDR only
- Simplifies Phase 1 significantly

### 5.4 Transaction Numbering
**Decision:** Per transaction type with yearly reset - `{TYPE}-{YYYY}-{seq}`

**Format Examples:**
- SAL-2025-00001 (Sales)
- PUR-2025-00001 (Purchase)
- EXP-2025-00001 (Expense)
- JNL-2025-00001 (General Journal)

**Implementation:**
- Separate sequence per transaction type
- Sequence resets each fiscal year
- Width configurable (default 5 digits)
- Faktur Pajak follows DJP rules (separate system)

**Rationale:**
- Easy to identify transaction type from number
- Organized for audit and reporting

### 5.5 Business Model
**Decision:** Monthly subscription, mid-range pricing.

**Target Market:**
- IT Services / Consulting
- Photography / Videography
- Online Seller / Marketplace

**Pricing:**
- Model: Monthly subscription
- Range: Rp 200k - 500k/month
- Goal: Cover hosting expenses per instance

**Bookkeeper Support:**
- Separate credentials per client
- No shared dashboard across clients
- Complete data isolation per instance

### 5.6 DevSecOps Tools
**Decision:** Standard toolchain for development, testing, and security.

| Purpose | Tool |
|---------|------|
| Local Development | Docker Compose |
| Infrastructure as Code | Ansible, Pulumi |
| Functional Testing | Playwright |
| Performance Testing | K6 |
| Security Scanning | SonarQube, OWASP tools, Trivy |

### 5.7 Capacity Planning
**Decision:** Optimized configuration for 2GB VPS (s-1vcpu-2gb tier).

**Memory Budget Allocation:**

| Component | Allocation | Configuration |
|-----------|------------|---------------|
| JVM Heap | 768 MB | Fixed -Xms768m -Xmx768m |
| JVM Metaspace | 128-192 MB | Class metadata |
| PostgreSQL | ~256 MB | shared_buffers + connections |
| OS/Buffers | ~512 MB | Page cache, kernel |

**JVM Configuration:**
- GC: G1GC (optimal for heaps <4GB, lower pause than ZGC)
- Heap regions: 4 MB
- GC pause target: 200 ms
- String deduplication enabled
- GC logging to `/var/log/<app>/gc.log`

**PostgreSQL Configuration:**
- Version: 18 (from PGDG repository)
- shared_buffers: 128 MB (6% of RAM for shared server)
- effective_cache_size: 384 MB
- work_mem: 4 MB
- random_page_cost: 1.1 (SSD)
- Aggressive autovacuum (5% scale factor)

**Nginx Configuration:**
- Rate limiting: 10 req/s per IP, burst 20
- Gzip compression: level 5
- Keepalive: 65s timeout, 1000 requests
- SSL: TLS 1.2/1.3, HSTS enabled
- Security headers: X-Frame-Options, CSP, X-Content-Type-Options

**Rationale:**
- G1GC chosen over ZGC for better memory efficiency on small heaps
- Fixed heap sizing prevents resize pauses
- PostgreSQL tuned for OLTP rather than analytics
- Rate limiting prevents abuse without affecting normal usage

**Scaling Path:**
- 2GB: Single user, light usage (current config)
- 4GB: Increase heap to 1.5GB, shared_buffers to 256MB
- 8GB+: Consider ZGC, larger connection pools

## Consequences
- Deployments are simple and cost-effective
- Storage can scale from local dev to production without code changes
- Indonesian hosting ensures data residency compliance
- Transaction numbers are human-readable and audit-friendly

## References
See [Historical Discussion](../archive/decisions-historical.md) for detailed Q&A and alternatives considered.
