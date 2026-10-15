# ADR-004: Secret Management Service Architecture

## Status
Proposed

## Context
Following ADR-002's secret management model and ADR-003's input processing rules, we need to define how the system architecture separates concerns between organizational management and secret handling while maintaining a unified interface for clients.

## Decision

### 1. Service Separation
The system is split into two main services:

#### Organization Service
* Entry point for all client interactions
* Manages metadata:
  - Paths
  - Labels
  - Tags
  - Names
* Handles all validations from ADR-003
* Stores reference to secrets via SecretID
* Coordinates with Secret Service for secret operations

#### Secret Service
* No direct client interaction
* Generates SecretID for new secrets
* Manages versions of secrets where each version has:
  - Unique version ID
  - Reference to fields (stored separately)
  - ActorID (creator/modifier)
  - CreatedAt timestamp
  - Optional ExpiresAt timestamp
  - Optional RevokedAt timestamp
* Provides storage operations:
  - Put: Create/update secret
  - Get: Retrieve specific/latest version
  - GetAll: Retrieve all versions
  - GetById: Retrieve by SecretID
  - Delete: Soft delete (new version with delete flag)
  - Destroy: Hard delete (specific/all versions)
  - Transaction: Atomic operations

### 2. Version Management
* Version increments ONLY occur for:
  - Field changes (secret content)
  - Flag changes:
    * ExpiresAt modification
    * RevokedAt modification
    * Deleted flag change
* Organizational metadata changes do not create new versions
* Separate audit logging for organizational changes (to be specified separately)

### 3. Creation/Update Flow
* Client Interface:
  - Single unified interface for all operations
  - Complete request structure required (as defined in ADR-003)
  - Internal service separation is opaque to clients

* Process Flow:
1. Organization Service validates request (per ADR-003)
2. For new secrets:
   - Start transaction in Secret Service
   - Create secret (generates SecretID, initial version)
   - Complete transaction
   - Store organizational metadata with SecretID
   - If organization storage fails, destroy secret
3. For updates:
   - Apply same validation rules as creation
   - System internally determines what needs updating
   - Version increments only for field/flag changes

## Consequences

### Positive
* Clear separation of concerns between organizational and secret management
* Unified client interface simplifies API usage
* Efficient storage through field reference system
* Versioning only when meaningful changes occur
* Strong validation maintained throughout all operations

### Negative
* Two-phase operations increase complexity
* Need to handle potential inconsistencies if operations fail
* All operations must pass through Organization Service

## Notes
* Audit logging system for organizational changes to be specified separately
* Error response format needs further specification
* Storage backend implementation details to be specified separately