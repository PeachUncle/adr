# ADR-006: Privacy-Preserving Metadata Model

## Status
Proposed

## Context
Following our secret management model (ADR-002), input processing (ADR-003), service architecture (ADR-004), and encryption architecture (ADR-005), we need to define how to maintain rich organizational structures and searchability while preserving privacy. The challenge is to support path hierarchies, labels, and searching without exposing business context or organizational structure.

## Decision

### 1. Path Segment Privacy
```plaintext
PathSegment {
    id: uuid,
    parent_id: uuid,          // Structural relationship
    owner_id: uuid,           // User/Organization
    
    // Encrypted content
    name_encrypted: {         // e.g., "payments" encrypted
        iv: bytes,
        ciphertext: bytes,
        tag: bytes
    },
    
    // Search/uniqueness support
    name_hmac: string        // HMAC using org_secret
}
```

### 2. Label Privacy

#### 2.1 Label Structure
```plaintext
Label {
    id: uuid,               // Unique identifier
    
    // Encrypted content
    key_encrypted: {        // e.g., "environment" encrypted
        iv: bytes,
        ciphertext: bytes,
        tag: bytes
    },
    value_encrypted: {      // e.g., "production" encrypted
        iv: bytes,
        ciphertext: bytes,
        tag: bytes
    },
    
    // Search support
    label_hmac: string,    // HMAC(key + value)
    key_hmac: string,      // HMAC(key)
    value_hmac: string     // HMAC(value)
}
```

### 3. HMAC-Based Search and Uniqueness

#### 3.1 Reference String Format
```plaintext
Format:    <path>:<labels>:<name>
Path:      Underscore-separated segments
Labels:    Comma-separated key-value pairs
Name:      URL-safe secret name

Examples:
project1_app2:env=prod,region=us-east-1:postgres-main
project2_app2:region=us-east-1,env=prod:redis-cache  // Note: different label order, same HMAC

Constraints:
- Path segments: [a-zA-Z0-9-_]+
- Label keys:    [a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9] or [a-zA-Z0-9]
                 Maximum length: 63 characters
- Label values:  [a-zA-Z0-9][a-zA-Z0-9-_.]*[a-zA-Z0-9] or [a-zA-Z0-9]
                 Maximum length: 63 characters
- Secret name:   [a-zA-Z0-9-_.]+

Valid label examples:
Keys:           Values:
- env           - prod
- app-name      - v1.2.3
- service123    - us-west-2

Invalid label examples:
Keys:           Values:
- -env          - .prod
- env-          - prod.
- app.name      - -test
```

#### 3.2 HMAC Generation
```plaintext
// Path segment HMAC (normalized path segment)
HMAC_segment = HMAC(
    key: org_secret,
    message: segment_name
)

// Label HMAC (normalized key and value)
HMAC_label = HMAC(
    key: org_secret,
    message: key_name + value
)

// Label key HMAC (normalized key)
HMAC_key = HMAC(
    key: org_secret,
    message: key_name
)

// Label value HMAC (normalized value)
HMAC_value = HMAC(
    key: org_secret,
    message: value
)

// Secret name HMAC
HMAC_name = HMAC(
    key: org_secret,
    message: secret_name
)

// Uniqueness HMAC (combines all components)
HMAC_unique = HMAC(
    key: org_secret,
    message: concatenate(
        [path_segment_hmacs] +                    // Order preserved from path
        [sorted_label_hmacs_by_key] +            // Labels always sorted by key for HMAC
        name_hmac
    )
)
```

### 4. Implementation Requirements

#### 4.1 Client-Side Operations
* Validate input against Kubernetes-style label constraints
* Generate HMACs for paths, labels, and names
* Encrypt segments and labels
* Process search terms
* Handle label normalization and validation

#### 4.2 Server-Side Operations
* Store encrypted segments and labels
* Maintain structural relationships
* HMAC-based lookups
* Uniqueness enforcement
* Access control

### 5. Metadata Privacy

#### 5.1 Visible to Server
* Path structure (parent/child relationships)
* HMAC values
* Timestamps and versions
* Access control information

#### 5.2 Protected Information
* Path segment names
* Label keys and values
* Business context
* Organizational structure
* Relationships between secrets

## Consequences

### Positive
* Complete metadata privacy
* Maintained searchability
* Efficient hierarchical navigation
* Support for rich organizational structure
* No business context leakage
* Strong uniqueness guarantees
* Kubernetes-compatible label constraints
* Clear validation rules

### Negative
* Additional client-side computation
* Complex HMAC management
* Increased storage requirements
* Need for org_secret management
* Stricter label constraints may require data migration

## Notes
* org_secret management detailed in ADR-007
* Consider HMAC rotation strategy
* Cache strategies for frequently accessed paths
* Migration path for existing systems
* Consider impact of label constraints on existing data
* Monitor HMAC computation performance