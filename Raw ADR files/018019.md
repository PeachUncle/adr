# ADR-0005: Service Failure Recovery and Data Consistency

### ADR Details

Title: "Service Failure Recovery and Data Consistency"  
Number: 0005  
Status: Draft  
Date: 2025-11-04  
Tags: #adr #architecture #failure #recovery #data-consistency #risk

### Context

Problem Statement:

• Current architecture has API Gateway as single point of failure during transcription processing
• Whisper service operates independently and continues processing even if API Gateway crashes
• No recovery mechanisms for partial failures during active transcription
• Risk of orphaned transcript files and stuck job states
• Data inconsistency between database records and file system

Forces Driving Decision:

• Need for reliable job tracking across service failures
• Requirement for data consistency between database and file system
• Prevention of resource waste from orphaned files
• Operational need for manual recovery procedures
• System reliability and maintainability concerns

### Current Failure Scenarios

#### Scenario 1: API Gateway crashes BEFORE calling Whisper service
- **State**: Job status = 'processing' in database
- **Consequence**: Job remains in 'processing' state indefinitely
- **Recovery**: Worker restart → BullMQ retries job (if configured) → processes again

#### Scenario 2: API Gateway crashes DURING Whisper service transcription
- **State**: Whisper service continues processing independently (stateless)
- **Consequence**: 
  - Whisper completes transcription and saves file to `shared/transcripts/`
  - Worker never receives response to update database
  - Job remains stuck in 'processing' state
  - Transcript file becomes "orphaned" (exists but not tracked)

#### Scenario 3: API Gateway crashes AFTER Whisper response, BEFORE DB update
- **State**: Whisper response received, but database not updated
- **Consequence**: 
  - Transcript file exists
  - Job status remains 'processing'
  - No metadata (language, confidence, duration) saved

### Decision

**Immediate Mitigation Strategy:**

1. **Document Current Limitations** - Acknowledge and document existing risks
2. **Add Manual Recovery Procedures** - Provide operational guidance
3. **Implement Basic Monitoring** - Add visibility into failure states
4. **Plan Future Enhancements** - Design comprehensive recovery mechanisms

**Future Recovery Strategy (To be implemented):**

1. **Job Timeout & Recovery**
   - Implement job timeout mechanism (configurable, e.g., 30 minutes)
   - Add status cleanup for stuck 'processing' jobs
   - Periodic job health checks

2. **Idempotent Operations**
   - Make Whisper service calls idempotent
   - Check if transcript already exists before processing
   - Prevent duplicate file creation

3. **Cleanup Mechanisms**
   - Periodic cleanup of orphaned transcript files
   - Database reconciliation processes
   - Resource monitoring and alerts

4. **Improved Error Handling**
   - Add transaction-like behavior across service boundaries
   - Implement compensation patterns
   - Better logging for debugging

5. **Health Checks**
   - Service health monitoring
   - Dependency health checks
   - Graceful degradation

### Rationale

**Why Immediate Mitigation:**
- Current system is functional but has known reliability issues
- Documentation provides immediate operational guidance
- Allows teams to work around limitations while comprehensive solution is developed
- Maintains development velocity while improving reliability

**Why Future Recovery Strategy:**
- Addresses root causes of data inconsistency
- Provides automated recovery capabilities
- Reduces operational overhead
- Improves system reliability and maintainability

### Consequences

**Positive Consequences:**

• **Risk Awareness**: Teams understand current limitations and failure modes
• **Operational Guidance**: Clear procedures for handling failures
• **Foundation for Improvement**: Documented path to better reliability
• **Better Monitoring**: Visibility into system health and failure states

**Negative Consequences:**

• **Increased Complexity**: Recovery mechanisms add system complexity
• **Operational Overhead**: Requires monitoring and maintenance
• **Development Effort**: Implementation time and resources
• **Performance Impact**: Additional checks and monitoring may affect performance

**Neutral Consequences:**

• **Documentation Overhead**: Requires ongoing maintenance of recovery procedures
• **Testing Requirements**: Need comprehensive failure scenario testing
• **Training Needs**: Team education on new recovery procedures

### Risk Assessment

**High Risk:**
- Production systems with long transcription jobs
- High-volume environments with frequent uploads
- Systems with limited disk space

**Medium Risk:**
- Development environments (manual cleanup possible)
- Low-volume systems (infrequent occurrences)

**Low Risk:**
- Systems with very short transcription times
- Environments with robust monitoring

### Implementation Timeline

**Phase 1 (Immediate - 1 week):**
- Document current limitations
- Add manual recovery procedures
- Implement basic monitoring

**Phase 2 (Short-term - 1 month):**
- Implement job timeout mechanisms
- Add idempotent operations
- Create cleanup processes

**Phase 3 (Long-term - 3 months):**
- Comprehensive error handling
- Advanced monitoring and alerting
- Automated recovery systems

### References

- [ADR 0001 - Database Location](./0001-database-location.md)
- [ADR 0004 - Job Enqueue Process](./0004-job-enqueu-process.md)
- [ARCHITECTURE_OVERVIEW.md](../ARCHITECTURE_OVERVIEW.md)
- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)