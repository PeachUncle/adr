# ADR 004: Disaster Recovery Plan - Tested & Practiced

**📍 Navigation Path:** [AGOG Home](../../README.md) → [ADRs](./README.md) → ADR 004: Disaster Recovery Plan

**Status:** Accepted
**Date:** 2025-12-10
**Deciders:** Engineering Team, Operations Team
**Related:** [ADR 002](./002-multi-tenant-saas-edge-architecture.md), [ADR 003](./003-3-tier-database-offline-resilience.md)

---

## Context

**Customer confidence requires demonstrable disaster recovery, not just documentation.**

Large enterprise customers (Fortune 500 manufacturing) require:
1. **Tested DR plan** - Must be smoke tested, not just theoretical
2. **Practiced procedures** - Team must execute drills regularly
3. **Measurable RTO/RPO** - Recovery Time Objective, Recovery Point Objective
4. **Automated failover** - Manual processes are too slow and error-prone
5. **Regional redundancy** - Single region failure cannot take down global system

**Current Risk:** Multi-region architecture (US-EAST, EU-CENTRAL, APAC) with edge facilities means multiple failure modes:
- Regional cloud failure (AWS outage, Kubernetes cluster crash)
- Database corruption or deletion
- Edge facility offline (internet, power, hardware)
- Network partition (split brain)
- Human error (bad deployment, accidental deletion)

**This ADR defines our disaster recovery strategy with TESTABLE, PRACTICED procedures.**

---

## Decision

### 1. Recovery Time Objectives (RTO)

**Tier 1 (Critical - Manufacturing Facilities):**
- **RTO:** 0 seconds (offline-capable, no recovery needed)
- **Failure Mode:** Internet outage, cloud unavailable
- **Solution:** Edge PostgreSQL databases continue operations independently

**Tier 2 (High - Regional Cloud Services):**
- **RTO:** 15 minutes (automated failover to secondary region)
- **Failure Mode:** Regional cloud outage (AWS us-east-1 down)
- **Solution:** Multi-region active-active with DNS failover

**Tier 3 (Medium - Global Analytics):**
- **RTO:** 1 hour (executive dashboards, non-operational)
- **Failure Mode:** Global aggregation database down
- **Solution:** Rebuild from regional backups

### 2. Recovery Point Objectives (RPO)

**Tier 1 (Edge):**
- **RPO:** 0 seconds (edge is source of truth)
- **Backup:** Continuous replication to regional cloud (5-second lag)

**Tier 2 (Regional Cloud):**
- **RPO:** 5 minutes (transaction logs)
- **Backup:** PostgreSQL WAL archiving + Point-in-Time Recovery (PITR)

**Tier 3 (Global Analytics):**
- **RPO:** 1 hour (acceptable for analytics)
- **Backup:** Hourly snapshots to S3/GCS

### 3. Multi-Region Active-Active Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Global DNS (Route53 / Cloud DNS)               │
│  Health checks every 10s → Automatic failover if region down   │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────▼─────┐        ┌─────▼────┐        ┌─────▼────┐
    │ US-EAST  │        │ EU-CENT  │        │   APAC   │
    │ (Active) │        │ (Active) │        │ (Active) │
    └──────────┘        └──────────┘        └──────────┘
         │                    │                    │
    ┌────▼─────┐        ┌─────▼────┐        ┌─────▼────┐
    │ Blue+Grn │        │ Blue+Grn │        │ Blue+Grn │
    │ Postgres │        │ Postgres │        │ Postgres │
    └──────────┘        └──────────┘        └──────────┘
         │                    │                    │
    ┌────▼─────┐        ┌─────▼────┐        ┌─────▼────┐
    │   Edge   │        │   Edge   │        │   Edge   │
    │ LA Facil │        │ Frankfurt│        │ Shanghai │
    └──────────┘        └──────────┘        └──────────┘
```

**Key Properties:**
- Each region independently operational (no cross-region dependencies for operations)
- Edge facilities route to geo-closest region (LA→US-EAST, Frankfurt→EU-CENTRAL, Shanghai→APAC)
- If primary region down, edge auto-fails to secondary region (LA→EU-CENTRAL if US-EAST down)
- Global analytics queries all healthy regions (tolerates 1-2 region failures)

### 4. Automated Failover Mechanisms

#### Regional Failover (Cloud)

**DNS Health Checks:**

```yaml
# Route53 Health Check Configuration
HealthCheck:
  Type: HTTPS
  ResourcePath: /health
  FullyQualifiedDomainName: api.us-east.agog.com
  Port: 443
  RequestInterval: 10  # seconds
  FailureThreshold: 3   # 30 seconds to detect failure

RoutingPolicy:
  Type: Failover
  Primary: us-east.agog.com
  Secondary: eu-central.agog.com
  HealthCheckId: !Ref HealthCheck
```

**Result:** If US-EAST unhealthy for 30 seconds, DNS automatically routes traffic to EU-CENTRAL

#### Edge Failover (Facility to Cloud)

**Edge Agent Configuration:**

```typescript
// Edge agent tries regions in order
const REGION_PRIORITY = [
  { name: 'US-EAST', url: 'https://api.us-east.agog.com', primary: true },
  { name: 'EU-CENTRAL', url: 'https://api.eu-central.agog.com', primary: false },
  { name: 'APAC', url: 'https://api.apac.agog.com', primary: false }
];

async function getActiveRegion() {
  for (const region of REGION_PRIORITY) {
    try {
      const response = await fetch(`${region.url}/health`, { timeout: 5000 });
      if (response.ok) {
        console.log(`Connected to ${region.name}`);
        return region;
      }
    } catch (err) {
      console.warn(`${region.name} unavailable: ${err.message}`);
    }
  }

  // All regions down - edge continues in offline mode
  console.error('All cloud regions unavailable. Operating offline.');
  return null;
}
```

**Result:** Edge tries US-EAST → EU-CENTRAL → APAC. If all fail, operates offline.

### 5. Disaster Scenarios & Recovery Procedures

#### Scenario 1: Regional Cloud Failure (US-EAST Down)

**Detection:**
- Route53 health checks fail for 30 seconds
- PagerDuty alert: "US-EAST region unhealthy"
- Grafana dashboard: Red status for US-EAST

**Automated Response:**
1. DNS failover routes new traffic to EU-CENTRAL (30 seconds)
2. Edge facilities (LA) reconnect to EU-CENTRAL (10-15 seconds)
3. Load balancers mark US-EAST backends as down (5 seconds)

**Manual Recovery (When US-EAST Returns):**

```bash
# 1. Verify US-EAST healthy
curl https://api.us-east.agog.com/health
# Expected: {"status":"healthy","region":"us-east"}

# 2. Re-enable health check
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://enable-us-east.json

# 3. Gradual traffic shift (10% → 50% → 100%)
# Wait 10 minutes between each step to monitor
./scripts/dr/gradual-failback.sh --region us-east --increments 10,50,100

# 4. Verify edge facilities reconnect
./scripts/dr/verify-edge-connectivity.sh --region us-east

# 5. Check replication lag
./scripts/dr/check-replication-lag.sh --region us-east
# Expected: < 5 seconds lag
```

**RTO:** 15 minutes (automated failover: 1 min, manual failback: 14 min)
**RPO:** 5 seconds (last transaction before failure)

---

#### Scenario 2: Database Corruption or Deletion

**Detection:**
- Application errors: "relation 'orders' does not exist"
- PostgreSQL logs: "corrupted page detected"
- Backup validation fails

**Recovery Procedure:**

```bash
# 1. Identify corruption extent
psql -U agogsaas_user -d agogsaas -c "SELECT * FROM pg_stat_database"

# 2. Stop Blue environment (prevent further corruption)
kubectl scale deployment backend-blue --replicas=0

# 3. Restore from Point-in-Time Recovery (PITR)
# Restore to 5 minutes before corruption detected
export RESTORE_TIME="2025-12-10 14:55:00"

# 4. Provision new PostgreSQL instance
./scripts/dr/provision-postgres.sh \
  --region us-east \
  --environment blue-recovery \
  --restore-time "$RESTORE_TIME"

# 5. Verify restored data
psql -U agogsaas_user -h postgres-blue-recovery.internal -d agogsaas \
  -c "SELECT COUNT(*) FROM orders WHERE created_at > '$RESTORE_TIME'"
# Expected: 0 (no orders after restore time)

# 6. Switch Blue to use recovered database
kubectl set env deployment/backend-blue \
  DATABASE_URL="postgresql://...@postgres-blue-recovery.internal:5432/agogsaas"

# 7. Scale back up
kubectl scale deployment backend-blue --replicas=3

# 8. Verify traffic serving
curl https://api.us-east.agog.com/graphql -d '{"query":"{ __typename }"}'

# 9. Rebuild replication from Blue → Green
./scripts/dr/setup-replication.sh --source blue-recovery --target green
```

**RTO:** 45 minutes (PITR restore: 30 min, verification: 10 min, cutover: 5 min)
**RPO:** 5 minutes (transaction logs)

**Data Loss:** 5 minutes of transactions (between last WAL archive and corruption)

---

#### Scenario 3: Edge Facility Hardware Failure

**Detection:**
- Edge health check timeout (60 seconds)
- Facility reports: "Server not responding"

**Recovery Procedure:**

```bash
# 1. Verify edge truly down (not network issue)
ssh facility-admin@la-facility.agog.com "systemctl status agog-edge"
# Connection timeout → hardware failure confirmed

# 2. Mark facility as offline in cloud
curl -X POST https://api.us-east.agog.com/admin/facilities/facility-la-001/mark-offline \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Block cloud users from editing LA data
# (Automatic - see Conflict Resolution Strategy)

# 4. Dispatch replacement hardware to facility
# Options:
#   - Hot spare on-site (swap in 30 minutes)
#   - Ship from warehouse (24-48 hours)
#   - Temporary cloud-only mode (remote workers only)

# 5. When replacement arrives, restore from cloud
# Edge database syncs FROM cloud (reverse of normal direction)
./scripts/edge/provision-edge.sh \
  --facility-id facility-la-001 \
  --restore-from-cloud us-east \
  --full-sync

# 6. Verify edge operational
curl http://edge-la-001.local:4010/health
# Expected: {"status":"healthy","facilityId":"facility-la-001"}

# 7. Mark facility back online
curl -X POST https://api.us-east.agog.com/admin/facilities/facility-la-001/mark-online \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**RTO:**
- Hot spare available: 30 minutes
- Shipped replacement: 24-48 hours
- Temporary cloud-only mode: 5 minutes (no edge, remote workers access cloud directly)

**RPO:**
- Edge had synced within last 5 seconds before failure → 5 seconds of data loss
- If edge offline for extended period before failure → depends on last successful sync

---

#### Scenario 4: Network Partition (Split Brain)

**Detection:**
- Edge can reach internet but not cloud API
- Cloud can reach internet but not edge
- Both sides think the other is down

**Recovery Procedure:**

```bash
# 1. Detect split brain
# Edge logs: "Cloud unreachable, continuing offline"
# Cloud logs: "Edge facility-la-001 unreachable, marked offline"

# 2. Verify partition (not outage)
# From edge:
ping google.com  # Success
ping api.us-east.agog.com  # Failure

# From cloud:
ping 1.1.1.1  # Success
ping edge-la-001.vpn.agog.com  # Failure

# 3. Check VPN tunnel
ipsec statusall | grep "facility-la-001"
# tunnel{1}:  BROKEN

# 4. Restart VPN tunnel
ipsec restart facility-la-001-tunnel

# 5. Verify connectivity restored
ping edge-la-001.vpn.agog.com  # Success

# 6. Edge auto-reconnects (within 30 seconds)
# Watch edge logs:
docker logs -f agog-edge-api

# Expected:
# "Reconnected to cloud (US-EAST)"
# "Syncing buffered changes... 47 changes"
# "Sync complete"

# 7. Verify no duplicate data
./scripts/dr/check-duplicates.sh --facility facility-la-001 --since "last 2 hours"
# Expected: 0 duplicates (edge uses idempotent sync)
```

**RTO:** 5 minutes (VPN restart: 2 min, edge reconnect: 30 sec, sync: 2 min)
**RPO:** 0 seconds (edge buffered all changes, no data loss)

---

#### Scenario 5: Bad Deployment (Application Bug)

**Detection:**
- Error rate spike in Grafana
- PagerDuty alert: "Error rate > 5%"
- Customer reports: "Cannot create orders"

**Recovery Procedure:**

```bash
# 1. Identify bad deployment
kubectl get deployments -n production
# backend-green   3/3   3   3   5m   ← Recently deployed

# Check error logs
kubectl logs -n production deployment/backend-green --tail=100 | grep ERROR

# 2. Immediate rollback: Switch traffic from Green → Blue
./infrastructure/scripts/switch-to-blue.sh

# Expected output:
# "Updating load balancer to route to Blue..."
# "Health check: Blue is healthy"
# "DNS updated: api.agog.com → Blue"
# "Rollback complete. Green still running for investigation."

# 3. Verify traffic serving from Blue
curl https://api.agog.com/health
# Expected: {"status":"healthy","environment":"blue"}

# 4. Monitor error rate drop
# Grafana dashboard should show error rate drop within 60 seconds

# 5. Investigate Green environment (still running)
kubectl exec -it deployment/backend-green -- /bin/sh
# Debug issue without affecting production

# 6. Fix issue, redeploy to Green
# ... fix code ...
docker build -t agog-backend:v1.3.1 .
kubectl set image deployment/backend-green backend=agog-backend:v1.3.1

# 7. Test Green again
curl https://green.agog.com/graphql -d '{"query":"{ __typename }"}'

# 8. Gradual traffic shift Blue → Green
./scripts/dr/gradual-cutover.sh --from blue --to green --increments 10,50,100
```

**RTO:** 2 minutes (load balancer switch: 30 sec, DNS propagation: 60 sec, verification: 30 sec)
**RPO:** 0 seconds (Blue database has all transactions via replication)

---

### 6. Monthly DR Drills (Tested & Practiced)

**CRITICAL:** DR plan must be PRACTICED, not just documented.

#### Drill Schedule

| Drill | Frequency | Scenario | Success Criteria |
|-------|-----------|----------|------------------|
| **Regional Failover** | Monthly | Simulate US-EAST down | Traffic routes to EU-CENTRAL in < 15 min, RTO met |
| **Database PITR** | Monthly | Restore DB to 1 hour ago | Successful restore, RPO < 5 min |
| **Edge Offline** | Weekly | Disconnect edge from cloud | Edge operates offline, syncs on reconnect |
| **Bad Deployment Rollback** | Monthly | Deploy intentionally broken code | Rollback to Blue in < 2 min |
| **Network Partition** | Quarterly | Break VPN tunnel | Detect + fix split brain in < 5 min |
| **Full Disaster** | Annually | Entire region loss simulation | Recover all services, data intact |

#### Drill #1: Regional Failover (Monthly)

**Script:** `./scripts/dr/drill-regional-failover.sh`

```bash
#!/bin/bash
# DR Drill: Simulate US-EAST Region Failure
# Purpose: Verify automated failover to EU-CENTRAL
# Expected RTO: 15 minutes

set -e

echo "===== DR DRILL: Regional Failover ====="
echo "Simulating US-EAST region failure..."
echo ""

# 1. Record baseline metrics
echo "[1/7] Recording baseline metrics..."
BASELINE_ERRORS=$(curl -s https://api.agog.com/metrics | jq '.errors_per_min')
BASELINE_LATENCY=$(curl -s https://api.agog.com/metrics | jq '.latency_p95')
echo "  Baseline error rate: $BASELINE_ERRORS errors/min"
echo "  Baseline P95 latency: $BASELINE_LATENCY ms"

# 2. Mark US-EAST unhealthy (simulated failure)
echo "[2/7] Marking US-EAST as unhealthy..."
START_TIME=$(date +%s)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://configs/dr-drill-fail-us-east.json
echo "  ✓ US-EAST marked unhealthy"

# 3. Wait for DNS failover (should happen in 30 seconds)
echo "[3/7] Waiting for DNS failover to EU-CENTRAL..."
sleep 30

# 4. Verify traffic routing to EU-CENTRAL
echo "[4/7] Verifying traffic routes to EU-CENTRAL..."
for i in {1..10}; do
  REGION=$(curl -s https://api.agog.com/health | jq -r '.region')
  if [ "$REGION" == "eu-central" ]; then
    echo "  ✓ Traffic routed to EU-CENTRAL"
    break
  fi
  sleep 5
done

if [ "$REGION" != "eu-central" ]; then
  echo "  ✗ FAILED: Traffic still routing to US-EAST after 1 minute"
  exit 1
fi

# 5. Verify edge facilities reconnect
echo "[5/7] Verifying edge facilities reconnect to EU-CENTRAL..."
EDGE_LA_REGION=$(curl -s http://edge-la-001.local:4010/status | jq -r '.connected_region')
if [ "$EDGE_LA_REGION" == "eu-central" ]; then
  echo "  ✓ LA edge reconnected to EU-CENTRAL"
else
  echo "  ✗ WARNING: LA edge not connected to EU-CENTRAL (got: $EDGE_LA_REGION)"
fi

# 6. Monitor error rate and latency
echo "[6/7] Monitoring error rate and latency..."
sleep 60  # Wait 1 minute for metrics to stabilize

CURRENT_ERRORS=$(curl -s https://api.agog.com/metrics | jq '.errors_per_min')
CURRENT_LATENCY=$(curl -s https://api.agog.com/metrics | jq '.latency_p95')
echo "  Current error rate: $CURRENT_ERRORS errors/min"
echo "  Current P95 latency: $CURRENT_LATENCY ms"

ERROR_INCREASE=$(echo "$CURRENT_ERRORS - $BASELINE_ERRORS" | bc)
LATENCY_INCREASE=$(echo "$CURRENT_LATENCY - $BASELINE_LATENCY" | bc)

if (( $(echo "$ERROR_INCREASE > 10" | bc -l) )); then
  echo "  ✗ WARNING: Error rate increased by $ERROR_INCREASE errors/min"
else
  echo "  ✓ Error rate acceptable"
fi

if (( $(echo "$LATENCY_INCREASE > 100" | bc -l) )); then
  echo "  ✗ WARNING: Latency increased by $LATENCY_INCREASE ms"
else
  echo "  ✓ Latency acceptable"
fi

# 7. Restore US-EAST (end drill)
echo "[7/7] Restoring US-EAST to healthy state..."
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://configs/dr-drill-restore-us-east.json
echo "  ✓ US-EAST restored"

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
echo ""
echo "===== DRILL COMPLETE ====="
echo "Total failover time: $TOTAL_TIME seconds"
echo "RTO target: 900 seconds (15 minutes)"

if [ $TOTAL_TIME -le 900 ]; then
  echo "✓ RTO MET"
else
  echo "✗ RTO MISSED (took $TOTAL_TIME sec, target 900 sec)"
fi
```

**Success Criteria:**
- Traffic routes to EU-CENTRAL within 15 minutes
- Edge facilities reconnect automatically
- Error rate increase < 10 errors/min
- Latency increase < 100ms

---

#### Drill #2: Database Point-in-Time Recovery (Monthly)

**Script:** `./scripts/dr/drill-database-pitr.sh`

```bash
#!/bin/bash
# DR Drill: Database Point-in-Time Recovery
# Purpose: Verify ability to restore from backup
# Expected RTO: 45 minutes, RPO: 5 minutes

set -e

echo "===== DR DRILL: Database PITR ====="

# 1. Create test data
echo "[1/5] Creating test data..."
psql -U agogsaas_user -h postgres-blue.internal -d agogsaas << EOF
INSERT INTO orders (id, customer, created_at)
VALUES (uuid_generate_v7(), 'DR Drill Test Order', NOW());
EOF
TEST_ORDER_ID=$(psql -U agogsaas_user -h postgres-blue.internal -d agogsaas -tAc \
  "SELECT id FROM orders WHERE customer = 'DR Drill Test Order'")
echo "  Created test order: $TEST_ORDER_ID"

# 2. Record restore point (5 minutes ago)
RESTORE_TIME=$(date -u -d '5 minutes ago' '+%Y-%m-%d %H:%M:%S')
echo "[2/5] Restore point: $RESTORE_TIME"

# 3. Create more data (simulate transactions after restore point)
sleep 10
psql -U agogsaas_user -h postgres-blue.internal -d agogsaas << EOF
INSERT INTO orders (id, customer, created_at)
VALUES (uuid_generate_v7(), 'After Restore Point', NOW());
EOF
echo "  Created post-restore-point order"

# 4. Restore database to RESTORE_TIME
echo "[3/5] Restoring database to $RESTORE_TIME..."
START_TIME=$(date +%s)

# Provision recovery instance
./scripts/dr/provision-postgres.sh \
  --region us-east \
  --environment blue-recovery \
  --restore-time "$RESTORE_TIME"

END_TIME=$(date +%s)
RESTORE_DURATION=$((END_TIME - START_TIME))
echo "  ✓ Database restored in $RESTORE_DURATION seconds"

# 5. Verify test order exists in restored DB
echo "[4/5] Verifying test data..."
FOUND=$(psql -U agogsaas_user -h postgres-blue-recovery.internal -d agogsaas -tAc \
  "SELECT COUNT(*) FROM orders WHERE id = '$TEST_ORDER_ID'")

if [ "$FOUND" -eq 1 ]; then
  echo "  ✓ Test order found in restored database"
else
  echo "  ✗ FAILED: Test order NOT found"
  exit 1
fi

# Verify post-restore-point data is NOT in restored DB
POST_RESTORE_COUNT=$(psql -U agogsaas_user -h postgres-blue-recovery.internal -d agogsaas -tAc \
  "SELECT COUNT(*) FROM orders WHERE customer = 'After Restore Point'")

if [ "$POST_RESTORE_COUNT" -eq 0 ]; then
  echo "  ✓ Post-restore-point data correctly excluded"
else
  echo "  ✗ WARNING: Found $POST_RESTORE_COUNT post-restore-point orders (expected 0)"
fi

# 6. Cleanup
echo "[5/5] Cleaning up..."
./scripts/dr/destroy-postgres.sh --environment blue-recovery
psql -U agogsaas_user -h postgres-blue.internal -d agogsaas << EOF
DELETE FROM orders WHERE customer IN ('DR Drill Test Order', 'After Restore Point');
EOF
echo "  ✓ Cleanup complete"

echo ""
echo "===== DRILL COMPLETE ====="
echo "Restore duration: $RESTORE_DURATION seconds"
echo "RTO target: 2700 seconds (45 minutes)"

if [ $RESTORE_DURATION -le 2700 ]; then
  echo "✓ RTO MET"
else
  echo "✗ RTO MISSED"
fi
```

---

### 7. Backup Strategy

#### Tier 1 (Edge)

**Method:** Continuous replication to regional cloud

```typescript
// Edge replication agent runs every 5 seconds
setInterval(async () => {
  const changes = await getUnsynced Changes();
  if (changes.length > 0) {
    await syncToCloud(changes);
  }
}, 5000);
```

**Backup Location:** Regional cloud PostgreSQL (US-EAST, EU-CENTRAL, or APAC)
**Retention:** 30 days on edge, 2 years in cloud

#### Tier 2 (Regional Cloud)

**Method:** PostgreSQL Write-Ahead Logging (WAL) + S3 archiving

```yaml
# PostgreSQL configuration
archive_mode: on
archive_command: 'aws s3 cp %p s3://agog-backups-us-east/wal/%f'
wal_level: replica
max_wal_senders: 10
```

**Backup Schedule:**
- **WAL archiving:** Continuous (every transaction)
- **Full backup:** Daily at 2 AM UTC
- **Incremental backup:** Every 6 hours
- **Retention:** 90 days

**Backup Location:**
- Primary: S3 (US-EAST)
- Replica: S3 Cross-Region Replication → EU-CENTRAL

#### Tier 3 (Global Analytics)

**Method:** Hourly snapshots

```bash
# Cron job: Every hour
0 * * * * /scripts/backup-global-analytics.sh
```

**Backup Location:** S3 with lifecycle policy (30 days hot, 365 days glacier)

---

### 8. Monitoring & Alerting

#### Health Check Endpoints

**Regional Cloud:**

```bash
GET https://api.us-east.agog.com/health

Response:
{
  "status": "healthy",
  "region": "us-east",
  "environment": "blue",
  "database": {
    "status": "connected",
    "replication_lag": "0.3s"
  },
  "edge_facilities": {
    "facility-la-001": "online",
    "facility-nyc-002": "online"
  }
}
```

**Edge:**

```bash
GET http://edge-la-001.local:4010/health

Response:
{
  "status": "healthy",
  "facilityId": "facility-la-001",
  "connected_region": "us-east",
  "buffered_changes": 0,
  "last_sync": "2025-12-10T14:59:55Z",
  "disk_free": "87%"
}
```

#### PagerDuty Alerts

| Alert | Severity | Trigger | Response |
|-------|----------|---------|----------|
| Regional cloud down | P1 (Critical) | Health check fail 3x (30 sec) | Page on-call engineer |
| Database replication lag > 1 min | P2 (High) | Lag threshold exceeded | Page database team |
| Edge facility offline > 1 hour | P3 (Medium) | No sync for 60 min | Email facility manager |
| Backup failure | P2 (High) | Daily backup job failed | Page on-call engineer |

#### Grafana Dashboards

**DR Readiness Dashboard:**
- Last successful backup (all regions)
- Replication lag (Blue → Green, Edge → Cloud)
- Health check status (all regions, all facilities)
- DR drill results (pass/fail, RTO/RPO metrics)

---

### 9. Compliance & Audit

#### SOC 2 Type II Requirements

- **DR plan documented:** ✓ This ADR
- **DR plan tested:** ✓ Monthly drills with automated scripts
- **Backups verified:** ✓ Daily backup validation job
- **RTO/RPO defined:** ✓ See section 1
- **Incident response:** ✓ PagerDuty integration

#### Annual Audit Checklist

- [ ] DR drills completed monthly (12 drills per year minimum)
- [ ] Backup restoration tested successfully
- [ ] RTO/RPO targets met in 90% of drills
- [ ] Incident postmortems documented
- [ ] DR plan reviewed and updated

---

## Consequences

### Positive

1. **Customer Confidence:** Demonstrable DR builds trust with enterprise customers
2. **Reduced Downtime:** Automated failover achieves 15-minute RTO
3. **Data Safety:** 5-minute RPO ensures minimal data loss
4. **Team Readiness:** Monthly drills keep team practiced
5. **Compliance:** Meets SOC 2, ISO 27001 requirements

### Negative

1. **Infrastructure Cost:** Multi-region active-active is expensive (~3x single region)
2. **Complexity:** More moving parts, more failure modes
3. **Maintenance:** Monthly drills require engineer time
4. **Latency:** Cross-region calls add 100-200ms latency

### Mitigation

- **Cost:** Offset by higher enterprise contract values (Fortune 500 customers)
- **Complexity:** Automated scripts reduce human error
- **Maintenance:** Drills automated, require ~2 hours/month engineer time
- **Latency:** Geo-routing minimizes cross-region calls (LA→US-EAST, Frankfurt→EU-CENTRAL)

---

## References

- [ADR 002: Multi-Tenant SaaS Edge Architecture](./002-multi-tenant-saas-edge-architecture.md)
- [ADR 003: 3-Tier Database Offline Resilience](./003-3-tier-database-offline-resilience.md)
- [Conflict Resolution Strategy](../../docs/CONFLICT_RESOLUTION_STRATEGY.md)
- [Blue-Green Deployment Guide](../../README_BLUE_GREEN_DEPLOYMENT.md)

---

[⬆ Back to top](#adr-004-disaster-recovery-plan---tested--practiced) | [🏠 AGOG Home](../../README.md) | [📚 ADRs](./README.md)
