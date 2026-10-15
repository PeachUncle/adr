# ADR-003: OSCAL-Native POA&M Generation Approach

**Status**: Accepted
**Date**: 2024-12-11
**Deciders**: Platform Architecture Team, Compliance Team

## Context

Plan of Action and Milestones (POA&M) is a critical FedRAMP deliverable for tracking security vulnerabilities and remediation progress. Traditional POA&M workflows involve manual Excel/Word document creation, which is error-prone and time-consuming.

**Current State**:

- Manual POA&M creation takes 2-4 hours per report
- Copy-paste errors lead to compliance findings
- No automated tracking of CVE → POA&M item linkage
- Excel templates incompatible with automation tools

**Requirements**:

- OSCAL 1.0.4 compliance (FedRAMP automation initiative)
- Map CVEs to POA&M items automatically
- Calculate risk scores using CVSS v3.1 + NIST 800-30
- Export to multiple formats: OSCAL JSON, CSV, DOCX
- Integration with FedRAMP automation platform
- Real-time POA&M updates as vulnerabilities are remediated

## Decision

We will implement **OSCAL-native POA&M generation** with automatic CVE mapping:

### 1. OSCAL POA&M Data Model

Use OSCAL 1.0.4 `plan-of-action-and-milestones` schema:

```json
{
  "plan-of-action-and-milestones": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "title": "Aegis POA&M - Tenant: Acme Corp",
      "last-modified": "2024-12-11T10:00:00Z",
      "version": "1.0",
      "oscal-version": "1.0.4"
    },
    "system-id": {
      "identifier-type": "https://fedramp.gov",
      "id": "F00000000"
    },
    "poam-items": [
      {
        "uuid": "cve-2024-1234-poam",
        "title": "CVE-2024-1234 in libssl 1.1.1",
        "description": "Critical vulnerability in OpenSSL library",
        "related-observations": [
          {
            "observation-uuid": "grype-scan-20241211"
          }
        ],
        "risk": {
          "status": "open",
          "characterization": {
            "facets": [
              {
                "name": "likelihood",
                "system": "https://fedramp.gov",
                "value": "high"
              },
              {
                "name": "impact",
                "system": "https://fedramp.gov",
                "value": "high"
              }
            ]
          }
        },
        "remediation-tracking": {
          "tracking-entries": [
            {
              "uuid": "remediation-1",
              "date-time-stamp": "2024-12-11T10:00:00Z",
              "title": "Upgrade libssl to 3.0.0",
              "description": "Update base image to Ubuntu 22.04 with OpenSSL 3.0"
            }
          ]
        }
      }
    ]
  }
}
```

### 2. Automatic CVE → POA&M Mapping

**Mapping Logic**:

```typescript
interface POAMGenerationRule {
  // Only create POA&M items for vulnerabilities meeting criteria
  severityThreshold:
    | VulnerabilitySeverity.HIGH
    | VulnerabilitySeverity.CRITICAL;

  // Calculate due date based on severity (NIST 800-40 guidance)
  dueDateDays: {
    CRITICAL: 30; // 30 days
    HIGH: 90; // 90 days
    MEDIUM: 180; // 180 days (optional)
    LOW: 365; // 365 days (optional)
  };

  // Risk level mapping (CVSS v3.1 → NIST 800-30)
  riskLevelMapping: {
    cvssScore: number;
    nistRiskLevel: 'very-high' | 'high' | 'moderate' | 'low';
  }[];
}

async function generatePOAMFromVulnerabilities(
  vulnerabilities: Vulnerability[],
  tenantId: string
): Promise<OSCALPOAMDocument> {
  const poamItems: POAMItem[] = [];

  for (const vuln of vulnerabilities) {
    if (vuln.severity === 'CRITICAL' || vuln.severity === 'HIGH') {
      const poamItem = {
        uuid: `cve-${vuln.cveId}-${uuidv4()}`,
        title: `${vuln.cveId} in ${vuln.packageName}@${vuln.packageVersion}`,
        description: vuln.description,

        // NIST 800-30 risk assessment
        risk: calculateRisk(vuln.cvssScore, vuln.severity),

        // Remediation steps
        remediationTracking: {
          trackingEntries: [
            {
              title: `Upgrade ${vuln.packageName} to ${vuln.fixedVersion}`,
              description: generateRemediationSteps(vuln),
              scheduledCompletionDate: calculateDueDate(vuln.severity),
            },
          ],
        },

        // Link to original vulnerability scan
        relatedObservations: [
          {
            observationUuid: vuln.evidenceId,
          },
        ],
      };

      poamItems.push(poamItem);
    }
  }

  return {
    'plan-of-action-and-milestones': {
      uuid: uuidv4(),
      metadata: generateMetadata(tenantId),
      poamItems,
    },
  };
}
```

### 3. Risk Score Calculation (NIST 800-30)

```typescript
function calculateRisk(
  cvssScore: number,
  severity: string
): RiskCharacterization {
  // NIST 800-30 Risk = Likelihood × Impact
  // CVSS Score → Likelihood mapping
  const likelihood =
    cvssScore >= 9.0 ? 'high' : cvssScore >= 7.0 ? 'medium' : 'low';

  // Severity → Impact mapping
  const impact =
    severity === 'CRITICAL' ? 'high' : severity === 'HIGH' ? 'medium' : 'low';

  // Risk matrix
  const riskMatrix = {
    'high-high': 'very-high',
    'high-medium': 'high',
    'high-low': 'moderate',
    'medium-high': 'high',
    'medium-medium': 'moderate',
    'medium-low': 'low',
    'low-high': 'moderate',
    'low-medium': 'low',
    'low-low': 'low',
  };

  const riskLevel = riskMatrix[`${likelihood}-${impact}`];

  return {
    status: 'open',
    characterization: {
      facets: [
        {
          name: 'likelihood',
          system: 'https://fedramp.gov',
          value: likelihood,
        },
        { name: 'impact', system: 'https://fedramp.gov', value: impact },
        { name: 'risk-level', system: 'https://fedramp.gov', value: riskLevel },
        {
          name: 'cvss-score',
          system: 'https://www.first.org/cvss',
          value: cvssScore.toString(),
        },
      ],
    },
  };
}
```

### 4. Export Formats

#### OSCAL JSON (Primary Format)

- Direct export of OSCAL data model
- Validated against OSCAL 1.0.4 JSON schema
- Compatible with FedRAMP automation tools

#### CSV (Legacy Compatibility)

```csv
POA&M Item ID,Weakness Name,Weakness Description,Severity,Remediation Plan,Scheduled Completion Date,Status
CVE-2024-1234,OpenSSL Vulnerability,Critical vulnerability in libssl,Very High,Upgrade to libssl 3.0.0,2025-01-15,Open
```

#### DOCX (Official POA&M Template)

- Use OpenXML SDK to generate Word documents
- FedRAMP POA&M template (OMB A-123)
- Populate tables with POA&M items

```typescript
import PizZip from 'pizzip';
import Docxtemplater from 'docxtemplater';

async function exportPOAMToDocx(poam: OSCALPOAM): Promise<Buffer> {
  const templatePath = './templates/fedramp-poam-template.docx';
  const content = await fs.readFile(templatePath);

  const zip = new PizZip(content);
  const doc = new Docxtemplater(zip, {
    paragraphLoop: true,
    linebreaks: true,
  });

  doc.render({
    systemName: poam.metadata.title,
    dateGenerated: new Date().toISOString().split('T')[0],
    poamItems: poam.poamItems.map((item) => ({
      id: item.uuid,
      weakness: item.title,
      description: item.description,
      severity: item.risk.characterization.facets.find(
        (f) => f.name === 'risk-level'
      )?.value,
      remediation: item.remediationTracking.trackingEntries[0]?.title ?? '',
      dueDate:
        item.remediationTracking.trackingEntries[0]?.scheduledCompletionDate ??
        '',
      status: item.risk.status,
    })),
  });

  return doc.getZip().generate({ type: 'nodebuffer' });
}
```

### 5. Continuous POA&M Updates

**Workflow**:

1. CI/CD pipeline uploads new vulnerability scan
2. Aegis worker processes scan results
3. New CVEs automatically create POA&M items
4. Fixed CVEs automatically update POA&M status to "closed"
5. ISSO receives email notification of changes
6. Updated OSCAL POA&M available via API

```typescript
// Automatic POA&M status update
async function updatePOAMStatus(
  cveId: string,
  tenantId: string
): Promise<void> {
  const latestScan = await getLatestVulnerabilityScan(tenantId);
  const cveStillPresent = latestScan.matches.some(
    (m) => m.vulnerability.id === cveId
  );

  if (!cveStillPresent) {
    await db.poamItem.update({
      where: { cveId, tenantId },
      data: {
        status: POAMStatus.CLOSED,
        closedDate: new Date(),
        closureRationale: 'CVE no longer detected in latest vulnerability scan',
      },
    });

    await sendNotification({
      to: await getISSOEmail(tenantId),
      subject: `POA&M Item Closed: ${cveId}`,
      body: `Vulnerability ${cveId} has been successfully remediated.`,
    });
  }
}
```

## Consequences

### Positive

✅ **Automation**: POA&M generation time reduced from 2-4 hours to <1 minute
✅ **Accuracy**: Eliminates copy-paste errors and manual tracking
✅ **Compliance**: OSCAL 1.0.4 compliance enables FedRAMP automation
✅ **Real-time**: POA&M updates automatically as vulnerabilities are fixed
✅ **Auditability**: Complete trail from CVE → Scan → POA&M item
✅ **Integration**: OSCAL JSON can be imported into GRC tools

### Negative

❌ **Learning curve**: ISSOs must understand OSCAL format
❌ **Validation complexity**: OSCAL schema validation adds processing overhead
❌ **Template maintenance**: FedRAMP DOCX template changes require updates
❌ **Risk calculation**: NIST 800-30 mapping may not align with org-specific risk frameworks

### Neutral

⚖️ **Legacy support**: CSV/DOCX exports maintain compatibility with non-OSCAL tools
⚖️ **Manual overrides**: ISSOs can manually adjust risk levels and due dates

## Alternatives Considered

### Alternative 1: Manual POA&M creation (status quo)

**Rejected**: Does not scale. Human error rate too high. No automation possible.

### Alternative 2: Custom JSON schema (not OSCAL)

**Rejected**: Not FedRAMP-compliant. Cannot integrate with gov automation tools. Reinventing the wheel.

### Alternative 3: Direct integration with GRC tools (Archer, ServiceNow)

**Rejected**: Vendor lock-in. Not all agencies use same GRC tool. OSCAL provides vendor-neutral format.

## Implementation Notes

- Use `oscal-js` library for OSCAL validation
- Store POA&M items in PostgreSQL with JSONB column for OSCAL data
- GraphQL query: `generatePOAM(tenantId: String, dateRange: DateRange): OSCALPOAMDocument`
- REST endpoint: `GET /api/v1/tenants/:id/poam/export?format=oscal|csv|docx`
- Scheduled job: Daily POA&M regeneration for all tenants

## References

- [OSCAL 1.0.4 Specification](https://pages.nist.gov/OSCAL/)
- [NIST 800-30 Rev 1: Risk Assessment](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf)
- [NIST 800-40 Rev 4: Patch Management](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-40r4.pdf)
- [FedRAMP POA&M Template](https://www.fedramp.gov/assets/resources/templates/FedRAMP-POAM-Template.xlsx)
- [FedRAMP Automation](https://automate.fedramp.gov/)
