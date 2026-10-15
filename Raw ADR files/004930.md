---
title: "ADR-0003: Configurable Status Management"
date: "2025-10-07"
status: "Proposed"
tags:
  - architecture
  - configuration
  - workflow
modules:
  - src/
summary: >-
  Implement configurable status management to support organization-specific ADR workflows and external system integration.
---

# ADR-0003: Configurable Status Management

## Status

Accepted

## Context

The ADR Toolkit currently enforces a hard-coded set of statuses (`accepted`, `approved`, `proposed`, `draft`, `rejected`, `deprecated`, `superseded`) which creates limitations for organizations with different workflow requirements. GitHub issue #9 identified a discrepancy between the README's claim that the validator "accepts a configurable set of statuses" and the actual implementation that uses a fixed allow-list.

### Problem Statement

Different organizations have varying ADR lifecycle processes:

- **Enterprise environments**: Need custom approval workflows (`under-review`, `pending-approval`, `escalated`, `on-hold`)
- **Regulated industries**: Require compliance statuses (`compliance-review`, `security-approved`, `audit-required`)
- **Agile teams**: Use iterative statuses (`backlog`, `in-progress`, `blocked`, `ready-for-review`)
- **Integration requirements**: Need to map ADR statuses to external systems (JIRA, Confluence, governance tools)

The current hard-coded approach forces organizations to adapt their established processes to the tool rather than the tool adapting to their workflows.

### Current Impact

1. **Limited adoption**: Organizations cannot use the tool without changing their established processes
2. **Integration friction**: No way to map statuses to external systems (JIRA, Confluence)
3. **Incorrect documentation**: README promises configurability that doesn't exist
4. **Workflow misalignment**: Tool doesn't support organization-specific decision lifecycles

## Decision

We will implement **Configuration-Driven Status Management** using a `.adrx.config.json` file that allows organizations to:

1. **Define custom statuses** with workflow properties (active, digest inclusion, approval requirements)
2. **Configure validation rules** (summary limits, required fields, workflow enforcement)
3. **Enable integration hooks** for JIRA, Confluence, and other systems
4. **Maintain backward compatibility** with existing hard-coded defaults

### Implementation Approach

- **Configuration format**: JSON schema-validated `.adrx.config.json` file
- **Hierarchical lookup**: Project → workspace → global → built-in defaults
- **Zero breaking changes**: Existing behavior preserved when no config present  
- **IDE support**: JSON schema for autocomplete and validation
- **Programmatic access**: Configuration API for tooling integration

### Key Features

1. **Custom Status Definitions**:
   ```json
   {
     "statuses": {
       "draft": { "active": true, "includeInDigest": false },
       "security-review": { "active": true, "includeInDigest": false, "requiresApproval": true },
       "implemented": { "active": false, "includeInDigest": true }
     }
   }
   ```

2. **Workflow Integration**:
   ```json
   {
     "integrations": {
       "jira": {
         "statusMapping": { "security-review": "In Security Review" },
         "webhookUrl": "https://company.atlassian.net/webhook"
       }
     }
   }
   ```

3. **Validation Customization**:
   ```json
   {
     "validation": {
       "summaryLimit": 500,
       "strictWorkflow": true,
       "requiredFields": ["title", "status", "summary", "owner"]
     }
   }
   ```

## Consequences

### Positive

- **Increased adoption**: Organizations can use the tool without changing established processes
- **Better integration**: Native support for JIRA, Confluence, and other systems
- **Workflow enforcement**: Optional strict workflow validation based on organization needs
- **Future extensibility**: Foundation for advanced features (approval workflows, notifications)
- **Developer experience**: JSON schema provides IDE support and validation
- **Backward compatibility**: Existing users experience no breaking changes

### Negative

- **Implementation complexity**: Requires refactoring validation, artifact generation, and CLI logic
- **Configuration overhead**: Organizations must define and maintain configuration files
- **Testing complexity**: Must test various configuration combinations and edge cases
- **Documentation burden**: Need comprehensive configuration documentation and examples

### Migration Strategy

1. **Phase 1**: Implement configuration loading with fallback to current behavior
2. **Phase 2**: Refactor validation and artifact generation to use configuration
3. **Phase 3**: Add CLI commands for configuration management (`adrx config init`, `adrx config validate`)
4. **Phase 4**: Implement integration hooks (JIRA, Confluence webhooks)

### Implementation Impact

**Files to modify**:
- `src/adr.ts`: Status validation and artifact generation logic
- `src/config.ts`: New configuration loading and validation module
- `src/constants.ts`: Make status sets configurable
- `src/cli.ts`: Add configuration commands and pass config to operations
- `templates/`: Add default configuration template

**New functionality**:
- Configuration schema validation
- Hierarchical config file lookup
- Status workflow enforcement
- Integration webhook support
- CLI configuration management commands

## References

- [GitHub Issue #9: Validator configuration README claims vs actual implementation](https://github.com/lordcraymen/adr-toolkit/issues/9)
- [ADR-0001: Automated NPM Releases](ADR-0001-automated-npm-releases-with-semantic-release.md)
- [ADR-0002: English as Primary Language](ADR-0002-english-as-primary-language-for-documentation-and-comments.md)
- [MADR Documentation: Status Management](https://adr.github.io/madr/)
- [JSON Schema Specification](https://json-schema.org/)