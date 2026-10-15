<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# ADR-0003: Use Python with Roundup Issue Tracker Toolkit

Date: 2025-11-15

## Status

Accepted

## Context

The Pasture Management System needs a foundation for implementing ITIL-inspired issue/change/CMDB management for homelab sysadmins. Key requirements include:

- Lightweight and suitable for small-scale homelab deployments
- Customizable to implement ITIL-inspired workflows
- Python-based to align with BDD demonstration objectives (Behave, Playwright)
- Self-hosted to maintain control and privacy
- Mature and stable codebase
- Multiple interfaces (Web UI, CLI, API) for comprehensive testing demonstrations

## Decision

We will use **Python 3.x with Roundup Issue Tracker Toolkit** as the foundation platform.

### Technology Stack

**Core Platform**:

- **Roundup Issue Tracker Toolkit**: Open-source issue tracking toolkit with extensive customization capabilities
- **Python 3.x**: Primary development language (3.9+ for modern features)

**BDD/Testing Stack**:

- **Behave**: Python BDD framework for Gherkin scenario execution
- **Playwright**: Modern browser automation for web UI testing
- **pytest**: Unit and integration testing framework
- **JUnit XML Reports**: Standardized test reporting with screenshots

**Additional Tools**:

- **Marpit**: Markdown presentations for BDD tutorials
- **C4 DSL (Structurizr)**: Architecture documentation
- **Pre-commit hooks**: Quality automation

### Roundup Toolkit Advantages

1. **Toolkit Architecture**: Designed for customization, not just configuration
1. **Multiple Interfaces**: Web UI, CLI, and API - perfect for comprehensive BDD demonstration
1. **ITIL Alignment**: Flexible schema allows modeling issue, change, and CMDB workflows
1. **Python Native**: Seamless integration with Python BDD ecosystem
1. **Lightweight**: Suitable for homelab scale deployments
1. **Mature**: Stable, long-term project with proven track record
1. **Self-hosted**: Full control and privacy for homelab sysadmins

### Testing Interface Coverage

The project will demonstrate BDD testing across three interfaces:

- **Web UI**: Playwright-based browser automation (English only, 1024x768 resolution)
- **CLI**: Command-line interface testing
- **API**: REST/XML-RPC API testing

This multi-interface approach provides comprehensive BDD demonstration value.

### Web UI Configuration

- **Language**: English only (simplifies BDD scenarios and reduces complexity)
- **Screenshot Resolution**: 1024x768 (standard for consistent test reports and documentation)
- **Browser**: Modern browsers via Playwright (Chromium, Firefox, WebKit)

## Consequences

**Positive:**

- Perfect alignment with Python BDD demonstration goals
- Roundup's toolkit nature enables real-world customization examples
- Three distinct interfaces provide comprehensive BDD testing demonstrations
- Customization capabilities enable ITIL workflow implementation
- Mature platform reduces infrastructure risk
- Self-hosted deployment maintains privacy and control
- Active community and documentation

**Negative:**

- Roundup learning curve for contributors unfamiliar with the platform
- Older web UI design may require customization for modern UX
- Smaller community compared to commercial issue trackers
- Custom development required for ITIL features (this is also the demonstration objective)

## Implementation Notes

### Development Environment

```bash
# Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Roundup and development dependencies
pip install roundup behave playwright pytest

# Initialize Roundup tracker instance
roundup-admin install -t classic tracker_data

# Configure tracker for ITIL workflows
# (Custom schema, templates, detectors)
```

### Project Structure

```
pasture-management-system/
├── tracker_data/          # Roundup tracker instance
├── customizations/        # ITIL workflow customizations
│   ├── schema/           # Data model extensions
│   ├── detectors/        # Business logic automation
│   └── templates/        # UI customizations
├── features/             # BDD scenarios
│   ├── issue_tracking/
│   ├── change_mgmt/
│   ├── cmdb/
│   └── step_definitions/
├── tests/                # Unit and integration tests
└── docs/                 # Diátaxis documentation
```

### Configuration Management

- Tracker configuration stored in version control
- Environment-specific settings in `.env` files (not committed)
- Initialization scripts for reproducible setup
- Docker/Podman containerization for deployment

## Validation Criteria

This decision will be validated through:

1. **Successful ITIL Implementation**: Issue, change, CMDB workflows functional
1. **BDD Coverage**: Comprehensive Gherkin scenarios across all three interfaces
1. **Performance**: Acceptable response times for homelab deployment
1. **Maintainability**: Customizations are maintainable and well-documented
1. **Educational Value**: Platform complexity is appropriate for BDD demonstration

## Related Decisions

- ADR-0001: Record architecture decisions
- ADR-0002: Adopt development best practices (establishes BDD-first approach)
- Future: ADR for specific ITIL workflow implementations
