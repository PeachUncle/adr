# ADR-002: Evidence Blob Storage Architecture

**Status**: Accepted
**Date**: 2024-12-11
**Deciders**: Platform Architecture Team

## Context

Aegis ingests large volumes of evidence artifacts from CI/CD pipelines:

- **SBOM documents** (SPDX JSON, CycloneDX JSON) - 500KB to 50MB per build
- **Vulnerability scan results** (Grype JSON) - 100KB to 10MB per scan
- **Cosign signature bundles** - 5KB to 50KB per image
- **POA&M exports** (OSCAL JSON, CSV, DOCX) - 50KB to 5MB per export
- **Audit logs** (JSON) - 1KB to 100KB per log entry

**Volume estimates**:

- 1000 builds/day × 10MB average = **10GB/day** (3.65TB/year)
- Retention: 2 years minimum (FedRAMP requirement)
- Total storage: **7.3TB** for active data

**Requirements**:

- NIST 800-53 SC-8: Encryption at rest (AES-256)
- NIST 800-53 SC-13: FIPS 140-2 validated cryptographic modules
- Multi-cloud support (Azure Gov + AWS GovCloud)
- PostgreSQL database must NOT store large blobs (performance)
- Fast retrieval for POA&M generation (<500ms)
- Immutable storage (compliance evidence cannot be modified)
- Geographic redundancy (IL4/IL5 requirement)

## Decision

We will use **S3-compatible object storage** with the following architecture:

### 1. Storage Backend

**Production (Government Cloud)**:

- **AWS GovCloud**: S3-Gov buckets (`us-gov-west-1` + `us-gov-east-1` for DR)
- **Azure Government**: Azure Blob Storage with versioning enabled

**Development**:

- **Local**: MinIO (S3-compatible) for development and testing

### 2. Bucket Structure

```
aegis-evidence-{environment}-{region}
├── sbom/
│   └── {tenantId}/
│       └── {projectId}/
│           └── {buildId}/
│               └── sbom-{sha256}.spdx.json
├── scans/
│   └── {tenantId}/
│       └── {projectId}/
│           └── {buildId}/
│               └── grype-{sha256}.json
├── signatures/
│   └── {tenantId}/
│       └── {imageDigest}/
│           └── signature-{timestamp}.json
├── poam/
│   └── {tenantId}/
│       └── {exportId}/
│           ├── poam-{date}.oscal.json
│           ├── poam-{date}.csv
│           └── poam-{date}.docx
└── audit-logs/
    └── {tenantId}/
        └── {year}/
            └── {month}/
                └── {day}/
                    └── audit-{hour}.jsonl
```

**Example S3 URI**:

```
s3://aegis-evidence-prod-usgovwest1/sbom/550e8400-e29b-41d4-a716-446655440000/proj-123/build-456/sbom-abc123.spdx.json
```

### 3. Database Schema (PostgreSQL)

Store only **metadata** in PostgreSQL, not blob content:

```sql
CREATE TABLE evidence (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  project_name VARCHAR(255) NOT NULL,
  build_id VARCHAR(255) NOT NULL,
  image_digest VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL, -- 'SBOM' | 'VULNERABILITY_SCAN' | 'SIGNATURE'
  format VARCHAR(50), -- 'SPDX_2_3' | 'CYCLONEDX_1_4'
  s3_uri VARCHAR(512) NOT NULL, -- Full S3 path
  s3_bucket VARCHAR(255) NOT NULL,
  s3_key VARCHAR(512) NOT NULL,
  file_size_bytes BIGINT,
  sha256_checksum VARCHAR(64), -- For integrity verification
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT evidence_tenant_isolation CHECK (tenant_id IS NOT NULL)
);

CREATE INDEX idx_evidence_tenant_project ON evidence(tenant_id, project_name);
CREATE INDEX idx_evidence_s3_uri ON evidence(s3_uri);
CREATE INDEX idx_evidence_image_digest ON evidence(image_digest);
```

### 4. Encryption Configuration

#### AWS S3-Gov

```hcl
resource "aws_s3_bucket" "evidence" {
  bucket = "aegis-evidence-prod-usgovwest1"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = aws_kms_key.aegis.arn
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = true # Immutability requirement
  }

  lifecycle_rule {
    id      = "transition-to-glacier"
    enabled = true

    transition {
      days          = 90
      storage_class = "GLACIER" # Cost optimization
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = 730 # 2 years retention
    }
  }

  object_lock_configuration {
    object_lock_enabled = "Enabled" # Immutable storage (WORM)
  }

  replication_configuration {
    role = aws_iam_role.replication.arn

    rules {
      id     = "replicate-to-dr"
      status = "Enabled"

      destination {
        bucket        = aws_s3_bucket.evidence_dr.arn
        storage_class = "STANDARD_IA"
      }
    }
  }

  tags = {
    Compliance  = "NIST-800-53"
    FIPS        = "140-2"
    Environment = "prod-gov"
  }
}
```

#### Azure Blob Storage (Government)

```hcl
resource "azurerm_storage_account" "evidence" {
  name                     = "aegisevidenceprod"
  resource_group_name      = azurerm_resource_group.aegis.name
  location                 = "usgovvirginia"
  account_tier             = "Standard"
  account_replication_type = "GZRS" # Geo-zone redundant
  account_kind             = "StorageV2"

  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled       = true
    change_feed_enabled      = true # For audit trail
    last_access_time_enabled = true

    delete_retention_policy {
      days = 730
    }
  }

  identity {
    type = "SystemAssigned"
  }

  customer_managed_key {
    key_vault_key_id = azurerm_key_vault_key.aegis.id
  }

  tags = {
    Compliance  = "NIST-800-53"
    FIPS        = "140-2"
    Environment = "prod-gov"
  }
}
```

### 5. Access Control

#### S3 Bucket Policy (Least Privilege)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AegisAPIReadWrite",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws-us-gov:iam::123456789012:role/aegis-api-role"
      },
      "Action": ["s3:PutObject", "s3:GetObject", "s3:GetObjectVersion"],
      "Resource": "arn:aws-us-gov:s3:::aegis-evidence-prod-usgovwest1/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    },
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws-us-gov:s3:::aegis-evidence-prod-usgovwest1/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

### 6. Application Layer (Node.js SDK)

```typescript
import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
} from '@aws-sdk/client-s3';
import { createHash } from 'crypto';

export class EvidenceStorageService {
  private s3: S3Client;
  private bucket: string;

  async uploadSBOM(
    tenantId: string,
    projectId: string,
    buildId: string,
    sbomContent: string
  ): Promise<{ s3Uri: string; sha256: string }> {
    const sha256 = createHash('sha256').update(sbomContent).digest('hex');
    const key = `sbom/${tenantId}/${projectId}/${buildId}/sbom-${sha256}.spdx.json`;

    await this.s3.send(
      new PutObjectCommand({
        Bucket: this.bucket,
        Key: key,
        Body: sbomContent,
        ContentType: 'application/json',
        ServerSideEncryption: 'aws:kms',
        Metadata: {
          tenantId,
          projectId,
          buildId,
          sha256,
        },
      })
    );

    return {
      s3Uri: `s3://${this.bucket}/${key}`,
      sha256,
    };
  }

  async retrieveSBOM(s3Uri: string): Promise<string> {
    const { bucket, key } = this.parseS3Uri(s3Uri);

    const response = await this.s3.send(
      new GetObjectCommand({ Bucket: bucket, Key: key })
    );

    return (await response.Body?.transformToString()) ?? '';
  }
}
```

## Consequences

### Positive

✅ **Performance**: PostgreSQL queries remain fast (no large blob storage)
✅ **Scalability**: S3 scales infinitely, handles petabytes of data
✅ **Cost-effective**: S3 Glacier reduces storage costs by 90% after 90 days
✅ **Compliance**: Immutable storage (WORM), encryption at rest (FIPS 140-2)
✅ **Durability**: 99.999999999% (11 nines) with cross-region replication
✅ **Multi-cloud**: Same architecture works on Azure Blob Storage

### Negative

❌ **Network latency**: Retrieving blobs adds 50-200ms vs. database
❌ **Eventual consistency**: S3 replication has 1-5 second delay
❌ **Complexity**: Two systems to manage (PostgreSQL + S3)
❌ **Cost**: S3 API calls add operational cost (~$0.005 per 1000 requests)

### Neutral

⚖️ **Backup strategy**: S3 versioning provides point-in-time recovery
⚖️ **Data migration**: Moving between clouds requires bulk S3 copy (manageable with AWS DataSync)

## Alternatives Considered

### Alternative 1: Store blobs in PostgreSQL BYTEA column

**Rejected**: Degrades database performance. 10MB blob causes 10MB memory allocation per query. VACUUM becomes extremely slow.

### Alternative 2: MongoDB GridFS

**Rejected**: Adds another database to manage. No government cloud compliance story. Not FedRAMP authorized.

### Alternative 3: Distributed filesystem (GlusterFS, Ceph)

**Rejected**: Operational complexity too high. No managed service in government cloud. Kubernetes persistent volumes not designed for multi-TB datasets.

## Implementation Notes

- Use AWS SDK v3 (`@aws-sdk/client-s3`) for Node.js
- Implement retry logic with exponential backoff (S3 throttling)
- Pre-signed URLs for direct browser uploads (future feature)
- CloudWatch/Azure Monitor metrics for bucket access patterns
- Lifecycle policies automated via Terraform

## References

- NIST 800-53 Rev 5: SC-8 (Transmission Confidentiality), SC-13 (Cryptographic Protection), SC-28 (Protection of Information at Rest)
- [AWS S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [Azure Immutable Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)
- FedRAMP Rev 5 Control SC-28
