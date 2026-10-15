# ADR 003: 3-Tier Database Architecture for Offline Resilience

**📍 Navigation Path:** [AGOG Home](../../README.md) → [Project Spirit](../README.md) → [ADR](./README.md) → 3-Tier Database Architecture

## Status
**Accepted** - 2025-12-10

## Context

### The Manufacturing Reality: Internet Outages Are Not Acceptable

ADR 002 established that AGOG uses edge computing for equipment monitoring. However, it did not address a **CRITICAL customer requirement:**

> **"Manufacturing must continue even when the internet goes out."**

### Customer Pain Point

Print manufacturing is a 24/7 operation with tight deadlines:

```
Typical Scenario:
├─ Monday 8 AM: Internet outage (ISP maintenance)
├─ Duration: 2 hours
├─ Problem: Orders can't be entered, production stops
├─ Impact: $50,000 in lost production time
└─ Customer complaint: "We paid for an ERP that doesn't work when we need it!"
```

**Unacceptable Solution:** "Just wait for the internet to come back"

**Required Solution:** Full operational capability offline

### What Needs to Work Offline

**Critical Operations:**
1. ✅ Enter new orders
2. ✅ Update production status
3. ✅ Check inventory levels
4. ✅ View job schedules
5. ✅ Record quality checks
6. ✅ Equipment monitoring (from sensors)

**Can Wait for Internet:**
1. ⏳ Executive dashboards (global view)
2. ⏳ Cross-facility reports
3. ⏳ Email notifications to customers
4. ⏳ External integrations (shipping, payments)

### Why Cloud-Only Database Fails

```
❌ WRONG: Cloud-Only Database

Worker enters order → Internet DOWN
  ↓
Try to save to cloud database → ERROR: No connection
  ↓
Order lost, production stops, chaos

Problem: Single point of failure (internet connectivity)
```

### Why Edge-Only Database Fails

```
❌ WRONG: Edge-Only Database (No Cloud Sync)

Worker enters order → Saved to edge database ✓
  ↓
Remote worker (Philippines) needs to see order → Can't access
CEO (traveling) needs to see production → Can't access
Analytics for forecasting → No data

Problem: No remote access, no cross-facility visibility
```

## Decision

We will implement a **3-Tier Database Architecture** with near real-time replication:

### Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│  TIER 1: EDGE (Operational - Offline Capable)         │
│  "Day-to-day work happens here"                        │
├────────────────────────────────────────────────────────┤
│  PostgreSQL at each facility (local hardware)          │
│  ├─ Orders (last 30 days)                              │
│  ├─ Production logs (last 7 days)                      │
│  ├─ Inventory (current levels)                         │
│  └─ Equipment data (last 24 hours)                     │
│                                                         │
│  Workers connect locally: http://10.0.1.50:4000        │
│  ✅ WORKS OFFLINE (no internet required)               │
└────────────────────────────────────────────────────────┘
                    ↓ Near Real-Time Replication
┌────────────────────────────────────────────────────────┐
│  TIER 2: REGIONAL CLOUD (Aggregated - Multi-Tenant)   │
│  "Regional operations, remote workers, compliance"     │
├────────────────────────────────────────────────────────┤
│  PostgreSQL clusters per region (AWS/Azure)            │
│  ├─ US-EAST: Aggregates all US facilities             │
│  ├─ EU-CENTRAL: Aggregates all EU facilities (GDPR)   │
│  └─ APAC: Aggregates all APAC facilities (Sovereignty)│
│                                                         │
│  Remote workers connect: https://us.agog.io            │
│  ✅ Requires internet                                  │
└────────────────────────────────────────────────────────┘
                    ↓ Aggregated/Anonymized Data
┌────────────────────────────────────────────────────────┐
│  TIER 3: GLOBAL ANALYTICS (Executive Dashboards)       │
│  "For traveling executives, cross-region insights"     │
├────────────────────────────────────────────────────────┤
│  Global analytics database (likely US-EAST)            │
│  ├─ Aggregated KPIs from all regions                   │
│  ├─ Cross-facility trends and forecasts                │
│  └─ Executive dashboards (CEO, CFO, Board)             │
│                                                         │
│  Executives connect: https://global.agog.io            │
│  ✅ Requires internet                                  │
└────────────────────────────────────────────────────────┘
```

### Core Principles

**1. Edge as Source of Truth for Operational Data**
- Orders, production, inventory entered at edge
- Edge PostgreSQL is authoritative for facility operations
- Cloud is replica for redundancy and remote access

**2. Near Real-Time Replication (Not Real-Time)**
- Edge → Cloud: 1-5 second lag (normal)
- Edge → Cloud: Buffered during internet outage (sync when back)
- Acceptable: Executives don't need live-to-the-second data

**3. Regional Clouds Respect Data Sovereignty**
- EU facility data → EU-CENTRAL cloud (GDPR)
- China facility data → APAC cloud (Sovereignty)
- US facility data → US-EAST cloud

**4. Blue-Green Deployment Supports Edge**
- Edge agents connect to BOTH Blue and Green during deployment
- Dual-write ensures zero data loss during cutover
- Backward compatibility (DB schema) allows rollback

## Implementation

### Tier 1: Edge Database (Per Facility)

#### Hardware Requirements

**Small Facility (< 3 printers):**
```
├─ Intel NUC or Raspberry Pi 4 (8GB RAM)
├─ 256GB SSD
├─ Cost: ~$500-800
└─ Supports: 10-20 concurrent users
```

**Medium Facility (3-10 printers):**
```
├─ Mini PC (Intel i5, 16GB RAM)
├─ 512GB SSD
├─ Cost: ~$1,200-1,500
└─ Supports: 20-50 concurrent users
```

**Large Facility (10+ printers):**
```
├─ Server (Intel Xeon, 32GB RAM)
├─ 1TB SSD RAID
├─ Cost: ~$3,000-5,000
└─ Supports: 50-200 concurrent users
```

#### Software Stack (Docker Containers)

```yaml
# Edge facility docker-compose.yml

services:
  postgres-edge:
    image: postgres:16
    volumes:
      - edge-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: agog_edge
      POSTGRES_USER: agog_user
      POSTGRES_PASSWORD: ${EDGE_DB_PASSWORD}
    restart: always

  graphql-api:
    image: agog/edge-api:latest
    depends_on:
      - postgres-edge
    environment:
      DATABASE_URL: postgresql://agog_user:${EDGE_DB_PASSWORD}@postgres-edge:5432/agog_edge
      CLOUD_API_URL: https://us-east.agog.io
      FACILITY_ID: ${FACILITY_ID}
      TENANT_ID: ${TENANT_ID}
    ports:
      - "4000:4000"
    restart: always

  replication-agent:
    image: agog/edge-replicator:latest
    depends_on:
      - postgres-edge
    environment:
      EDGE_DB_URL: postgresql://agog_user:${EDGE_DB_PASSWORD}@postgres-edge:5432/agog_edge
      CLOUD_DB_URL: ${CLOUD_DB_URL}
      SYNC_INTERVAL: 5s
    restart: always

  equipment-agent:
    image: agog/edge-equipment:latest
    depends_on:
      - postgres-edge
    environment:
      DATABASE_URL: postgresql://agog_user:${EDGE_DB_PASSWORD}@postgres-edge:5432/agog_edge
    restart: always
    network_mode: host  # Access local equipment
```

#### Data Retention (Edge)

```sql
-- Keep only recent operational data on edge
-- Older data archived to cloud, deleted locally

-- Orders: Last 30 days
DELETE FROM orders
WHERE created_at < NOW() - INTERVAL '30 days';

-- Production logs: Last 7 days (detailed)
DELETE FROM production_logs
WHERE created_at < NOW() - INTERVAL '7 days';

-- Equipment data: Last 24 hours (real-time sensors)
DELETE FROM equipment_readings
WHERE timestamp < NOW() - INTERVAL '24 hours';
```

### Tier 2: Regional Cloud (Per Region)

#### Regional PostgreSQL Clusters

```yaml
# US-EAST Region (AWS RDS or Azure PostgreSQL)

Blue Environment:
  Primary: agog-us-east-blue-primary.postgres.database.azure.com
  Replicas:
    - agog-us-east-blue-replica-1 (read replica)
    - agog-us-east-blue-replica-2 (read replica)

  Schemas:
    - tenant_foo (Foo's US facilities: LA, Boston, NY)
    - tenant_bar (Bar's US facilities: Seattle, Chicago)
    - tenant_baz (Baz's US facilities: Denver, Atlanta)

  Storage: 1 TB (grows with tenant data)
  Retention: 2 years hot, archive to cold storage

Green Environment:
  Primary: agog-us-east-green-primary.postgres.database.azure.com
  (Used during blue-green deployments)
```

#### Replication Strategy (Edge → Regional)

```typescript
// Replication Agent (runs on edge computer)

class EdgeToCloudReplicator {
  private edgeDb: Pool;
  private cloudDb: Pool;
  private syncInterval = 5000; // 5 seconds
  private buffer: Transaction[] = [];

  async start() {
    setInterval(async () => {
      if (await this.isInternetAvailable()) {
        await this.syncToCloud();
      } else {
        console.warn('[Replicator] Internet down, buffering transactions');
        await this.bufferTransactions();
      }
    }, this.syncInterval);
  }

  private async syncToCloud() {
    try {
      // Get new transactions since last sync
      const transactions = await this.getNewTransactions();

      // Send to cloud
      for (const tx of transactions) {
        await this.cloudDb.query(tx.sql, tx.params);
      }

      // If we had buffered transactions, sync those too
      if (this.buffer.length > 0) {
        console.log(`[Replicator] Syncing ${this.buffer.length} buffered transactions`);
        for (const tx of this.buffer) {
          await this.cloudDb.query(tx.sql, tx.params);
        }
        this.buffer = [];
      }

      console.log(`[Replicator] Synced ${transactions.length} transactions to cloud`);
    } catch (error) {
      console.error('[Replicator] Sync failed:', error);
      await this.bufferTransactions();
    }
  }

  private async bufferTransactions() {
    // Store transactions locally until internet returns
    const transactions = await this.getNewTransactions();
    this.buffer.push(...transactions);

    console.log(`[Replicator] Buffer size: ${this.buffer.length} transactions`);
  }
}
```

### Tier 3: Global Analytics

#### Aggregation Strategy

```typescript
// Global Analytics Aggregator (runs in cloud)

class GlobalAnalyticsAggregator {
  async aggregateDailyKPIs() {
    // Runs nightly, aggregates from all regional clouds

    // Query each region
    const usData = await this.queryRegion('us-east');
    const euData = await this.queryRegion('eu-central');
    const apacData = await this.queryRegion('apac');

    // Aggregate cross-region
    const globalKPIs = {
      totalOrders: usData.orders + euData.orders + apacData.orders,
      totalRevenue: usData.revenue + euData.revenue + apacData.revenue,
      averageProductionTime: this.average([
        usData.avgProductionTime,
        euData.avgProductionTime,
        apacData.avgProductionTime
      ]),
      // ... more KPIs
    };

    // Store in global analytics DB
    await this.globalDb.query(
      'INSERT INTO daily_kpis (date, data) VALUES ($1, $2)',
      [new Date(), globalKPIs]
    );
  }

  private async queryRegion(region: string): Promise<RegionalKPIs> {
    // Query regional cloud
    // Returns only aggregated data (respects sovereignty)
  }
}
```

## Rationale

### Why 3 Tiers (Not 2, Not 1)?

**Why Not Just Cloud?**
- ❌ Single point of failure (internet)
- ❌ Cannot work offline
- ❌ Latency for local workers (Philippines → US-EAST = 200ms)

**Why Not Just Edge?**
- ❌ No remote worker access
- ❌ No executive dashboards
- ❌ No cross-facility analytics
- ❌ Data silos (no global view)

**Why Not Just Edge + Cloud (2 Tiers)?**
- ❌ Cross-region queries hit multiple regional clouds (slow)
- ❌ No pre-aggregated data for executives
- ✅ **3 Tiers solves this:** Global analytics tier pre-aggregates

### Why Edge as Source of Truth?

**Alternative: Cloud as source of truth, edge as cache**
```
❌ Cloud-First Model:
  ├─ Worker enters order → Sent to cloud first
  ├─ Cloud saves → Replicates back to edge
  └─ Problem: Fails when internet down
```

**Chosen: Edge as source of truth, cloud as replica**
```
✅ Edge-First Model:
  ├─ Worker enters order → Saved to edge immediately
  ├─ Edge syncs to cloud (when internet available)
  └─ Benefit: Works offline, syncs when back
```

### Why Near Real-Time (Not Real-Time)?

**Real-Time Replication:**
- Requires every edge transaction to wait for cloud confirmation
- Adds latency (50-200ms per transaction)
- Fails when internet intermittent

**Near Real-Time Replication:**
- Edge saves immediately (no latency)
- Replicator syncs every 5 seconds
- Buffers during internet outage
- Acceptable for operational needs

### Why Regional Clouds (Not Single Global Cloud)?

**Data Sovereignty Requirements:**
```
EU Facility (Frankfurt):
├─ Must store data in EU (GDPR Article 44)
├─ Cannot transfer to US without proper safeguards
└─ Solution: EU-CENTRAL region (Frankfurt, Dublin, Amsterdam)

China Facility (Shanghai):
├─ Must store data in China (Cybersecurity Law 2017)
├─ Cannot transfer outside China
└─ Solution: APAC region (Shanghai, Hong Kong)
```

**Latency Considerations:**
```
Worker in Frankfurt accessing US cloud:
├─ Latency: ~100-150ms (transatlantic)
├─ For operational work: Too slow

Worker in Frankfurt accessing EU cloud:
├─ Latency: ~10-20ms (local)
├─ For operational work: Acceptable
```

## Consequences

### Positive

✅ **Offline Resilience**
- Manufacturing continues during internet outages
- Edge database is authoritative for operations
- Data buffers locally, syncs when internet returns

✅ **Low Latency for Workers**
- Local workers access edge (< 5ms)
- Remote workers access regional cloud (< 50ms)
- Acceptable for operational work

✅ **Data Sovereignty Compliance**
- EU data stays in EU (GDPR)
- China data stays in China (Sovereignty)
- US data can stay in US

✅ **Global Executive Dashboards**
- CEO can see all facilities from anywhere
- Aggregated data respects sovereignty
- Pre-aggregated for fast queries

✅ **Scalability**
- Each facility independent (edge)
- Regional clouds aggregate facilities
- Global analytics aggregates regions

### Negative

❌ **Infrastructure Complexity**
- Must manage edge computers at each facility
- Must manage regional cloud databases
- Must manage global analytics database
- 3 tiers = 3x operational complexity

❌ **Replication Lag**
- Remote worker sees 1-5 second old data (normal)
- Remote worker sees stale data during internet outage
- Mitigation: Acceptable for operational needs

❌ **Conflict Resolution Complexity**
- Same order edited at edge AND cloud during outage
- Must resolve conflicts when syncing
- Mitigation: Edge wins (source of truth)

❌ **Hardware Costs**
- Edge computer per facility: $500-5,000
- Customer must purchase hardware
- Mitigation: Included in onboarding fee

❌ **Contractor Setup Required**
- Edge computer installation per facility
- Network configuration (firewall, VPN)
- Ongoing maintenance (updates, monitoring)
- Mitigation: Certified contractor network

### Mitigation Strategies

**For Infrastructure Complexity:**
- Docker standardization (same stack everywhere)
- Automated monitoring (Prometheus, Grafana)
- Remote management tools (SSH, Docker API)
- Certified contractor network for local support

**For Replication Lag:**
- UI indicators ("Last synced 3 seconds ago")
- Conflict resolution: Edge always wins
- Buffer size monitoring (alert if > 1000 transactions)

**For Hardware Costs:**
- Include in onboarding fee ($5k-20k)
- Offer hardware-as-a-service (monthly fee)
- Refurbished hardware for small customers

**For Contractor Setup:**
- Certified contractor training program
- Remote installation support (video call)
- Plug-and-play hardware (pre-configured)
- Monthly health checks (automated)

## Blue-Green Deployment Considerations

### Edge Dual-Connection During Deployment

```
Edge Agent at LA Facility:

Normal Operation (Blue is live):
├─ Primary: Blue environment (https://us-east-blue.agog.io)
└─ Secondary: None

During Deployment (Green being validated):
├─ Primary: Blue environment (https://us-east-blue.agog.io)
├─ Secondary: Green environment (https://us-east-green.agog.io)
└─ Dual-write: Sends data to BOTH Blue and Green

After Cutover (Green is now live):
├─ Primary: Green environment (https://us-east-green.agog.io)
├─ Secondary: Blue environment (rollback capability)
└─ Dual-write: Continues for 24-48 hours

After Stabilization:
├─ Primary: Green environment
└─ Secondary: None (Blue updated to match Green)
```

**Why Dual Connection?**
- ✅ Zero data loss during cutover
- ✅ Green receives all edge data for validation
- ✅ Rollback to Blue has all transactions (no data loss)
- ✅ Backward compatibility (DB schema) allows old edge code → new schema

## Monitoring & Alerting

### Edge Computer Health

```typescript
// Health checks for edge computers

interface EdgeHealth {
  facility_id: string;
  postgres_status: 'healthy' | 'degraded' | 'down';
  disk_usage: number;  // Percentage
  memory_usage: number;  // Percentage
  replication_lag: number;  // Seconds
  buffered_transactions: number;  // Count
  last_sync: Date;
  internet_status: 'connected' | 'disconnected';
}

// Alert thresholds
const ALERTS = {
  disk_usage: 80,  // Alert at 80% disk
  memory_usage: 85,  // Alert at 85% memory
  replication_lag: 300,  // Alert if lag > 5 minutes
  buffered_transactions: 5000,  // Alert if > 5000 buffered
  internet_downtime: 7200,  // Alert if down > 2 hours
};
```

### Regional Cloud Health

```typescript
// Health checks for regional clouds

interface RegionalHealth {
  region: 'us-east' | 'eu-central' | 'apac';
  environment: 'blue' | 'green';
  postgres_status: 'healthy' | 'degraded' | 'down';
  replication_lag: number;  // Seconds (for read replicas)
  query_latency_p95: number;  // Milliseconds
  active_connections: number;
  edge_facilities_connected: number;
  edge_facilities_total: number;
}

// Alert thresholds
const ALERTS = {
  postgres_status: 'degraded',  // Alert if not healthy
  replication_lag: 10,  // Alert if replica lag > 10 seconds
  query_latency_p95: 500,  // Alert if p95 > 500ms
  edge_connectivity: 0.95,  // Alert if < 95% facilities connected
};
```

## Data Retention & Archival

### Edge (Tier 1): Short-Term Operational

```sql
-- Automated cleanup (runs nightly on edge)

-- Orders: Keep 30 days
DELETE FROM orders
WHERE created_at < NOW() - INTERVAL '30 days'
  AND synced_to_cloud = true;  -- Only delete if synced

-- Production logs: Keep 7 days
DELETE FROM production_logs
WHERE created_at < NOW() - INTERVAL '7 days'
  AND synced_to_cloud = true;

-- Equipment readings: Keep 24 hours
DELETE FROM equipment_readings
WHERE timestamp < NOW() - INTERVAL '24 hours'
  AND synced_to_cloud = true;
```

### Regional (Tier 2): Medium-Term Historical

```sql
-- Automated archival (runs nightly on regional cloud)

-- Hot data: 2 years in PostgreSQL
-- Cold data: 2-7 years in S3/Blob Storage
-- After 7 years: Delete (compliance)

-- Archive old orders to S3
INSERT INTO s3_archive
SELECT * FROM orders
WHERE created_at < NOW() - INTERVAL '2 years';

DELETE FROM orders
WHERE created_at < NOW() - INTERVAL '2 years';
```

### Global (Tier 3): Long-Term Aggregated

```sql
-- Keep aggregated data for 10 years
-- No raw data (only summaries)

-- Automated archival (runs monthly)
DELETE FROM daily_kpis
WHERE date < NOW() - INTERVAL '10 years';
```

## Security Considerations

### Edge Computer Security

**Physical Security:**
- Edge computer in locked server room or closet
- Access restricted to authorized personnel
- Tamper-evident seals

**Network Security:**
- Firewall: Only allow outbound to cloud (inbound blocked)
- VPN/WireGuard tunnel to cloud (encrypted)
- No direct equipment→internet access (edge is gateway)

**Data Security:**
- PostgreSQL encrypted at rest (LUKS/BitLocker)
- Encrypted replication to cloud (TLS 1.3)
- Local backups encrypted

### Regional Cloud Security

**Network Security:**
- Private subnets (no public internet access)
- VPN gateway for edge connections
- DDoS protection (Cloudflare, Azure DDoS)

**Data Security:**
- PostgreSQL encrypted at rest (cloud provider managed)
- Encrypted backups (AES-256)
- Row-Level Security (multi-tenant isolation)

**Access Control:**
- No direct database access (only via API)
- MFA for cloud access
- Audit logging (every query logged)

## Testing Strategy

### Offline Resilience Testing

```bash
#!/bin/bash
# Test offline capability at edge

echo "Testing offline resilience..."

# 1. Start edge environment
docker-compose -f edge-docker-compose.yml up -d

# 2. Create test order (internet ON)
curl -X POST http://localhost:4000/graphql \
  -d '{"query":"mutation { createOrder(input: {customer: \"Test\"}) { id } }"}'

# 3. Verify synced to cloud
sleep 10
curl https://us-east.agog.io/api/orders/latest

# 4. Simulate internet outage
docker exec edge-replication-agent bash -c "iptables -A OUTPUT -d us-east.agog.io -j DROP"

# 5. Create order during outage
curl -X POST http://localhost:4000/graphql \
  -d '{"query":"mutation { createOrder(input: {customer: \"Offline Test\"}) { id } }"}'

# 6. Verify order saved locally
curl http://localhost:4000/graphql \
  -d '{"query":"query { orders { id customer } }"}'

# 7. Restore internet
docker exec edge-replication-agent bash -c "iptables -D OUTPUT -d us-east.agog.io -j DROP"

# 8. Wait for sync
sleep 30

# 9. Verify offline order synced to cloud
curl https://us-east.agog.io/api/orders/latest | grep "Offline Test"

echo "✅ Offline resilience test passed"
```

## Related Documentation

- [ADR 002: Multi-Tenant SaaS with Edge Architecture](./002-multi-tenant-saas-edge-architecture.md) - Overall architecture
- [Blue-Green Deployment](../../Standards/code/blue-green-deployment.md) - Deployment strategy
- [Database Standards](../../Standards/data/database-standards.md) - PostgreSQL best practices

## References

- **Database Replication:** PostgreSQL Logical Replication
- **Edge Computing:** Docker Swarm or Kubernetes at edge
- **Data Sovereignty:** GDPR Article 44, China Cybersecurity Law 2017
- **Conflict Resolution:** Operational Transformation, CRDTs

---

**Decision Made:** 2025-12-10
**Decision Makers:** Todd (Product Owner), AI Assistant (Technical Advisor)
**Review Date:** 2026-Q1 (after first production deployment with offline testing)

**Supersedes:** None (net new decision)
**Related:** ADR 002 (establishes edge computing, this defines database strategy)

[← Back to ADR Index](./README.md) | [ADR 002](./002-multi-tenant-saas-edge-architecture.md)
