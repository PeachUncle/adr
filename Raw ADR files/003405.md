# ADR 003: Allure as Primary Reporting Tool

**Status:** Accepted  
**Date:** 2025-12-30  
**Decision Makers:** SDET Lead, QA Manager

## Context

The framework required comprehensive test reporting with:
- Rich visualizations
- Historical trends
- CI/CD integration
- Artifact attachments (screenshots, videos, logs)
- Multi-stakeholder audience (devs, QA, management)

Candidates evaluated:
- Allure Framework
- Extent Reports
- ReportPortal
- Built-in NUnit HTML reports

## Decision

We selected **Allure Framework** as the primary reporting solution.

## Rationale

### Why Allure?

1. **Rich Feature Set**
   - Timeline view (execution flow)
   - Trends (historical data)
   - Categories (bug vs infra failure)
   - Suites/Packages organization
   - Behaviors (BDD stories)
   - Test attachments (screenshots, videos, JSON, logs)

2. **CI/CD Native**
   - GitHub Actions plugin available
   - Azure DevOps integration
   - Jenkins plugin (official)
   - Static HTML output (hostable anywhere)

3. **BDD Integration**
   - Native SpecFlow support via Allure.SpecFlow
   - Gherkin steps displayed in reports
   - Tags/categories mapped automatically

4. **Extensibility**
   - Custom attachments
   - Link integration (JIRA, TMS)
   - Categories customization
   - Environment info injection

5. **Industry Standard**
   - Used by major companies (Google, Amazon)
   - Active community
   - Regular updates

### Why Not Extent Reports?

| Feature | Allure | Extent Reports |
|---------|--------|----------------|
| Historical Trends | ✅ Yes | ❌ No |
| CI/CD Plugins | ✅ Many | ⚠️ Limited |
| BDD Support | ✅ Native | ⚠️ Custom |
| Timeline View | ✅ Yes | ❌ No |
| Categories | ✅ Built-in | ⚠️ Manual |
| **Decision** | ✅ **Selected** | ❌ Rejected |

### Why Not ReportPortal?

- Requires infrastructure (database, backend service)
- More complex setup
- Overkill for current team size
- Additional maintenance overhead

### Why Not Built-in NUnit Reports?

- Minimal features (pass/fail only)
- No visualizations
- No artifact attachments
- Not stakeholder-friendly

## Implementation

### Configuration

```json
// allureConfig.json
{
  "allure": {
    "directory": "Reports/AllureResults",
    "linkTemplates": {
      "tc": "https://your-tms.com/testcase/{0}",
      "issue": "https://your-jira.com/browse/{0}"
    }
  },
  "categories": [
    { "name": "Product Bugs", "matchedStatuses": ["failed"] },
    { "name": "Test Infrastructure", "matchedStatuses": ["broken"] }
  ]
}
```

### Evidence Capture

```csharp
// Screenshots (configurable timing)
await AllureHelper.CaptureScreenshotIfConfiguredAsync(page, stepName, ScreenshotTiming.OnFailure);

// API Request/Response
AllureHelper.AttachRequestDetails("POST", url, headers, body);
AllureHelper.AttachResponseDetails(statusCode, headers, body);

// Video (full scenario)
await AllureHelper.AttachVideoAsync(page);
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Generate Allure Report
  run: |
    npm install -g allure-commandline
    allure generate Tests/bin/Release/net8.0/Reports/AllureResults -o Reports/AllureReport --clean

- name: Upload Allure Report
  uses: actions/upload-artifact@v4
  with:
    name: allure-report
    path: Reports/AllureReport
```

## Consequences

### Positive
- **Stakeholder-friendly**: Non-technical stakeholders can understand reports
- **Debugging efficiency**: Screenshots/videos attached automatically
- **Trend analysis**: Historical data helps identify flaky tests
- **Blame clarity**: Categories distinguish product bugs from test issues

### Negative
- **Learning curve**: Team needs to learn Allure concepts
- **Two-step process**: Generate results → Generate report (not real-time)
- **Storage**: Large reports (videos) consume CI/CD artifact storage

### Mitigation
- **Training**: Allure documentation sessions
- **Automation**: Scripts auto-generate reports
- **Retention**: Configure artifact retention (7 days for videos, 30 for reports)

## Evidence Configuration

### Screenshot Timing (Configurable)

```json
"ScreenshotOptions": {
  "BeforeStep": false,   // Debug mode only
  "AfterStep": false,    // Debug mode only
  "OnFailure": true      // Always enabled
}
```

**Rationale:**
- Before/After: Off by default (noise)
- OnFailure: Always on (critical evidence)

### Video Recording (Optional)

```json
"VideoEnabled": false  // Disabled by default (performance)
```

**Rationale:**
- Videos are large (storage cost)
- Enable only for:
  - Critical test runs
  - Debugging flaky tests
  - Production validation

## Alternatives Considered

| Tool | Cost | Features | CI/CD | Learning Curve | Decision |
|------|------|----------|-------|----------------|----------|
| Allure | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ **Selected** |
| Extent | Free | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ❌ Limited features |
| ReportPortal | Free/Paid | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ❌ Too complex |
| NUnit HTML | Free | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ Too basic |

## Future Enhancements

1. **Allure TestOps** (paid): Consider for enterprise features
2. **Custom widgets**: Test coverage, performance metrics
3. **Slack integration**: Notify on test failures
4. **Allure Docker Service**: Self-hosted report server

## References
- [Allure Framework Documentation](https://docs.qameta.io/allure/)
- [Allure .NET Integration](https://github.com/allure-framework/allure-csharp)
- [Allure GitHub Action](https://github.com/simple-elf/allure-report-action)
