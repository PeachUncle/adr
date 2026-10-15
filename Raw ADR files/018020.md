# ADR 0006 — Configurable Audio File Retention Strategy

**Status:** Proposed  
**Date:** 2025-11-04  
**Tags:** #adr #architecture #retention #auditing #storage #compliance

---

## 📘 Context

### Current State
The current system immediately deletes uploaded audio files after successful transcription completion (see `transcription.worker.ts` lines 38-45). This approach prioritizes privacy and storage efficiency but creates several limitations:

### Problem Statement
• **No Audit Trail**: Cannot verify transcription accuracy against original audio
• **Limited Debugging**: Cannot investigate transcription quality issues or errors
• **Compliance Gaps**: Many regulations require retaining source data for audit purposes
• **No Re-processing**: Cannot re-transcribe with different models or settings
• **Data Recovery**: Cannot recover transcription results if database records are corrupted/lost

### Forces Driving Decision
• **Auditing Requirements**: Need to verify transcription accuracy and content
• **Compliance Needs**: Legal/medical applications often require source data retention
• **Quality Assurance**: Sample transcriptions for quality control and training
• **Customer Disputes**: Resolve disagreements about transcription content
• **Storage Costs**: Audio files are 100-1000x larger than text transcriptions
• **Privacy Concerns**: Retaining user audio longer than necessary
• **Data Minimization**: GDPR and privacy principles favor minimal data retention

---

## 💡 Decision

Implement a **configurable audio file retention strategy** that provides flexibility for different use cases while maintaining privacy-focused defaults.

### Core Strategy
1. **Configurable Retention Period**: Environment-based retention duration (default: 0 days = immediate deletion)
2. **Tiered Retention Options**: Support immediate, short-term, and long-term retention
3. **Automated Cleanup**: Periodic jobs to delete expired files
4. **Database Tracking**: Track retention metadata and deletion status
5. **Feature Flag**: Enable/disable retention per environment

### Implementation Approach
```typescript
// Environment Configuration
const AUDIO_RETENTION_DAYS = parseInt(process.env.AUDIO_RETENTION_DAYS || '0');
const AUDIO_CLEANUP_INTERVAL_HOURS = parseInt(process.env.AUDIO_CLEANUP_INTERVAL_HOURS || '24');
const AUDIO_RETENTION_ENABLED = process.env.AUDIO_RETENTION_ENABLED !== 'false';
```

### Database Schema Changes
```sql
ALTER TABLE transcriptions ADD COLUMN audio_file_retention_until TEXT;
ALTER TABLE transcriptions ADD COLUMN retain_audio_file INTEGER DEFAULT 0;
ALTER TABLE transcriptions ADD COLUMN audio_file_deleted_at TEXT;
```

### Retention Tiers
| Tier | Duration | Use Case | Storage Impact |
|------|----------|-----------|---------------|
| Immediate | 0 days | Privacy-focused, default | Minimal |
| Short-term | 7-30 days | Debugging, QA | Moderate |
| Long-term | 1+ years | Compliance, legal | High |

---

## 🧩 Rationale

### Why Configurable Retention?

| Option | Pros | Cons |
|--------|------|------|
| **Current (Immediate Deletion)** | ✅ Privacy-focused<br>✅ Minimal storage<br>✅ Simple implementation | ❌ No audit trail<br>❌ Limited debugging<br>❌ Compliance gaps |
| **Permanent Retention** | ✅ Complete audit trail<br>✅ Full compliance<br>✅ Maximum flexibility | ❌ High storage costs<br>❌ Privacy concerns<br>❌ Unbounded growth |
| **Configurable Retention** | ✅ Flexible for different needs<br>✅ Compliance when required<br>✅ Cost control<br>✅ Gradual migration | ⚠️ Increased complexity<br>⚠️ Requires cleanup jobs<br>⚠️ Storage monitoring needed |

### Key Benefits
• **Flexibility**: Different environments have different requirements
• **Compliance**: Meet regulatory requirements when needed
• **Cost Control**: Default to deletion, enable retention when required
• **Gradual Migration**: Phase in retention without breaking changes
• **Audit Capability**: Verify transcription accuracy and resolve disputes

### Trade-offs
• **Storage Growth**: Need to plan for 10-100x storage increase
• **Operational Overhead**: Cleanup jobs and monitoring required
• **Complexity**: Additional configuration and database fields
• **Security**: Need proper access controls for retained audio

---

## ⚙️ Consequences

### Positive Consequences
• **Audit Trail**: Complete record of original audio and transcription
• **Compliance Ready**: Can meet regulatory requirements when needed
• **Debugging Support**: Investigate quality issues and errors
• **Re-processing**: Re-transcribe with different models/settings
• **Quality Assurance**: Sample transcriptions for training and QA
• **Customer Service**: Resolve disputes about transcription content

### Negative Consequences
• **Storage Costs**: Significant increase in storage requirements
• **Privacy Impact**: Retaining user audio longer than necessary
• **Operational Complexity**: Need cleanup jobs and monitoring
• **Security Concerns**: Additional data to protect and control
• **Backup Overhead**: Audio files included in backup processes

### Neutral Consequences
• **Configuration Management**: Need to manage retention policies per environment
• **Database Changes**: Additional fields and queries for retention tracking
• **Monitoring Requirements**: Storage usage and retention compliance tracking
• **Documentation**: Need clear retention policies and procedures

### Implementation Requirements
• **Database Migration**: Add retention fields to transcriptions table
• **Cleanup Jobs**: Periodic deletion of expired files
• **Storage Monitoring**: Track disk usage and growth patterns
• **Configuration Management**: Environment-specific retention policies
• **Security Controls**: Access controls for retained audio files

---

## 🔮 Future Evolution

### Phase 1 (Immediate - 1 week)
• Basic configurable retention with environment variables
• Database schema updates
• Simple cleanup job implementation

### Phase 2 (Short-term - 1 month)
• Advanced retention policies (per-user, per-job-type)
• Storage monitoring and alerting
• External storage integration (S3/MinIO)

### Phase 3 (Long-term - 3 months)
• Selective retention based on content analysis
• Automated archival to cold storage
• Advanced compliance reporting

### Triggers for Re-evaluation
• **Storage Costs**: Become prohibitive for current approach
• **Regulatory Changes**: New requirements for audio retention
• **Customer Requirements**: Increased demand for audit capabilities
• **Technology Changes**: New storage solutions or compression methods
• **Scale Issues**: Current approach doesn't scale with usage

---

## 📋 Implementation Checklist

### Database Changes
- [ ] Add `audio_file_retention_until` column
- [ ] Add `retain_audio_file` column  
- [ ] Add `audio_file_deleted_at` column
- [ ] Update repository methods for retention fields
- [ ] Create migration script

### Application Changes
- [ ] Add environment variable configuration
- [ ] Update worker to respect retention policy
- [ ] Implement cleanup job scheduler
- [ ] Add storage monitoring
- [ ] Update API responses with retention info

### Operations
- [ ] Define retention policies per environment
- [ ] Set up storage monitoring and alerts
- [ ] Create backup procedures for retained audio
- [ ] Document cleanup and recovery procedures

### Testing
- [ ] Unit tests for retention logic
- [ ] Integration tests for cleanup jobs
- [ ] Performance tests for storage impact
- [ ] Security tests for audio file access

---

**Related ADRs:**  
- [0005-service-failure-recovery.md](./0005-service-failure-recovery.md) - Service failure recovery and data consistency
- [0004-job-enqueu-process.md](./0004-job-enqueu-process.md) - Job enqueue process and database persistence
- [0001-database-location.md](./0001-database-location.md) - Database location and ownership

**Supersedes:** none  
**Superseded by:** none