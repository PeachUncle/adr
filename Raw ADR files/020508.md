# ADR 0004: Release Workflow Timeout and Performance SLA

**Status**: Accepted  
**Date**: 2026-01-05  
**Context**: Feature 003 - Automated Binary Release Pipeline  
**Related**: [spec.md](../../specs/003-automated-release-pipeline/spec.md), SC-003, T048a

## Context

The specification defines a performance requirement:

**SC-003**: Release must be published within **30 minutes** of merging to main branch.

To ensure this SLA is met, we need to:

1. Set appropriate GitHub Actions workflow timeouts
2. Provide safety buffer for cleanup and error handling
3. Prevent workflows from hanging indefinitely
4. Log clear error messages when timeout occurs

## Decision

### Workflow Timeout: 25 Minutes

The `create-release` job in `.github/workflows/release.yml` will have a **25-minute timeout**.

**Configuration**:

```yaml
create-release:
  name: Create GitHub Release
  needs: [calculate-version, build]
  runs-on: ubuntu-latest
  timeout-minutes: 25  # SLA: 30 minutes total, 5-minute buffer
```

### Rationale

1. **SLA Compliance**: 25 minutes + 5-minute buffer = 30-minute total
2. **Safety Margin**: Allows 5 minutes for:
   - GitHub Actions queue time
   - Artifact download delays
   - Network latency for Release API calls
   - Graceful error logging and cleanup
3. **Fail-Fast**: Prevents indefinite hangs if external service fails (e.g., Codacy, GitHub API)
4. **User Experience**: Users receive clear timeout error within SLA window

### Timeout Buffer Allocation

| Phase                    | Expected Duration | Timeout Allocation      |
| ------------------------ | ----------------- | ----------------------- |
| **Build Job** (parallel) | 10-15 minutes     | 20 minutes per platform |
| **Create Release Job**   | 8-12 minutes      | **25 minutes**          |
| **Total Pipeline**       | 18-27 minutes     | 30 minutes (SLA)        |
| **Buffer**               | -                 | **5 minutes**           |

### Breakdown of Create Release Job

| Step                     | Expected Time   | Notes                                 |
| ------------------------ | --------------- | ------------------------------------- |
| Checkout repository      | 10-30 seconds   | Fetch all history for release notes   |
| Download build artifacts | 1-2 minutes     | 4 platform binaries (~20-50 MB total) |
| Organize binaries        | 5-10 seconds    | Copy and rename files                 |
| Generate checksums       | 5-10 seconds    | SHA256 for all binaries               |
| Generate SBOM            | 30-60 seconds   | Anchore SBOM scan                     |
| Sign artifacts           | 10-20 seconds   | GPG signing                           |
| Generate release notes   | 10-30 seconds   | Parse commits since last tag          |
| Create Git tag           | 5-10 seconds    | Tag + push                            |
| Create GitHub Release    | 30-60 seconds   | Upload 8-10 files to Release API      |
| Release summary          | 5 seconds       | Generate workflow summary             |
| **Total**                | **3-6 minutes** | Under normal conditions               |

**Worst-Case Scenarios Covered by 25-Minute Timeout**:

- SBOM generation fails/retries (up to 5 minutes)
- GitHub API rate limiting (up to 10 minutes backoff)
- Artifact download slow network (up to 10 minutes)
- Multiple platform build retries (parallel, max 20 minutes)

## Alternatives Considered

### Alternative 1: No Timeout (Default GitHub Actions)

**Approach**: Use default 360-minute (6-hour) timeout

**Pros**:

- Never fails due to timeout
- Handles extreme edge cases

**Cons**:

- Violates SC-003 SLA requirement
- Workflows can hang indefinitely on failures
- Wastes GitHub Actions minutes
- Poor user experience (no feedback)

**Rejected**: Does not meet SLA requirement.

### Alternative 2: 15-Minute Timeout

**Approach**: Aggressive timeout to ensure fast feedback

**Pros**:

- Guarantees very fast failure detection
- Forces optimization of workflow

**Cons**:

- Too tight for edge cases (slow network, API rate limits)
- High risk of false positives (legitimate builds failing)
- No buffer for transient failures

**Rejected**: Too risky, may cause legitimate releases to fail.

### Alternative 3: 30-Minute Timeout (Exact SLA)

**Approach**: Set timeout exactly at SLA boundary

**Pros**:

- Matches SLA precisely

**Cons**:

- No buffer for cleanup/logging
- User receives timeout error exactly at SLA deadline (bad UX)
- No time for graceful degradation

**Rejected**: No safety margin for cleanup.

## Consequences

### Positive

- **SLA Guarantee**: Ensures releases complete within 30 minutes or fail clearly
- **Resource Efficiency**: Prevents runaway workflows from consuming GitHub Actions minutes
- **Clear Failures**: Timeout errors logged with context for debugging
- **Performance Accountability**: Forces workflow optimization to stay under 25 minutes

### Negative

- **Potential False Positives**: Legitimate releases may fail if external service is slow
- **Timeout Handling**: Requires careful error logging before timeout
- **Monitoring Required**: Need to track timeout frequency to identify systemic issues

### Error Handling

When timeout occurs:

1. **GitHub Actions Logs**: Workflow shows "timeout-minutes exceeded" error
2. **Step Summary**: Last completed step visible in workflow summary
3. **User Notification**: No release published, users check Actions tab for details
4. **Debugging**: Logs indicate which step timed out

**Example Timeout Log**:

```text
Error: The operation was canceled.
##[error]The action 'Create GitHub Release' has timed out after 25 minutes.
##[error]Workflow canceled by GitHub Actions (timeout-minutes: 25)
```

## Monitoring and Alerting

### Metrics to Track

1. **Average Release Duration**: Target < 20 minutes (80% of timeout)
2. **Timeout Frequency**: Target < 5% of releases
3. **Bottleneck Steps**: Identify slowest steps via workflow logs

### When to Re-evaluate Timeout

Re-evaluate timeout if:

- **> 5% of releases fail due to timeout** → Increase timeout or optimize workflow
- **Average duration > 20 minutes** → Optimize slow steps
- **SLA requirement changes** → Adjust timeout accordingly

## Implementation Notes

### Timeout Configuration

```yaml
# .github/workflows/release.yml
create-release:
  name: Create GitHub Release
  needs: [calculate-version, build]
  runs-on: ubuntu-latest
  timeout-minutes: 25  # SLA: 30 minutes total, 5-minute buffer
  steps:
    # ... release steps
```

### Build Job Timeout (Per Platform)

```yaml
# .github/workflows/build.yml
build:
  name: Build ${{ matrix.platform }}-${{ matrix.arch }}
  runs-on: ${{ matrix.os }}
  timeout-minutes: 20  # Per-platform timeout
```

**Rationale**: Builds run in parallel, so 20-minute individual timeout + 25-minute release timeout = max 45 minutes total (exceeds SLA if builds serialize, but they don't).

### Graceful Timeout Handling

```yaml
- name: Upload to GitHub Release
  timeout-minutes: 10  # Step-level timeout
  continue-on-error: false  # Fail job if timeout
```

## Testing

### Performance Test (T093)

```bash
# Measure time from main merge to release availability
time_start=$(git log -1 --format=%ct main)
time_release=$(gh release view --json publishedAt -q .publishedAt)
duration=$((time_release - time_start))

if [ $duration -gt 1800 ]; then
  echo "FAIL: Release took ${duration}s (> 30 minutes)"
  exit 1
fi
```

### Timeout Simulation

```bash
# Simulate slow SBOM generation
- name: Generate SBOM (with artificial delay)
  run: |
    sleep 600  # 10 minutes
    # ... actual SBOM generation
```

**Expected**: Workflow completes within 25 minutes or fails gracefully.

## References

- [GitHub Actions Timeout Limits](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idtimeout-minutes)
- [SC-003: Performance Requirements](../../specs/003-automated-release-pipeline/spec.md)
- [T048a: Configure timeout](../../specs/003-automated-release-pipeline/tasks.md)

## Review Schedule

This ADR should be reviewed:

- If timeout failures exceed 5% of releases
- If average release duration exceeds 20 minutes
- If SLA requirement changes (SC-003)
- Quarterly during performance reviews
