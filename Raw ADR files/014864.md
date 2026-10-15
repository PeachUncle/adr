# 4. Adopt Apache License 2.0

Date: 2025-10-15

## Status

Accepted

## Context

The pytest-jux project requires an open source license that:

1. **Enables Enterprise Adoption**: Target users are system administrators, integrators, and infrastructure engineers in professional environments
2. **Protects Contributors**: Provides clear patent grants and liability protection
3. **Supports Cryptographic Code**: Plugin involves XML digital signatures and cryptographic operations
4. **Facilitates Integration**: Must work well with existing infrastructure tools (pytest, Ansible, PostgreSQL/SQLite)
5. **Encourages Contribution**: Clear, professional license that corporations trust
6. **Maintains Openness**: Remains free and open source while protecting all parties

### License Considerations for This Project

**Cryptographic Software**: The plugin generates and verifies XML digital signatures, which historically involved patent concerns (RSA, ECC). While many core algorithms are now patent-free, explicit patent grants protect users and contributors.

**Enterprise Context**: System administrators and integrators often work in corporate environments where:
- Legal departments scrutinize open source licenses
- Patent indemnification clauses are valued
- Permissive licenses are preferred over copyleft

**Infrastructure Integration**: The plugin integrates with:
- pytest ecosystem (MIT licensed)
- PostgreSQL and SQLite (PostgreSQL License and Public Domain)
- Python cryptography libraries (Apache 2.0 and BSD)
- Ansible playbooks (GPL but plugin is separate)

## Decision

We will adopt the **Apache License 2.0** for pytest-jux.

### License Choice Rationale

**Apache License 2.0 Advantages**:

1. **Explicit Patent Grant**: Section 3 grants patent rights to users, protecting against patent litigation
2. **Contributor Protection**: Contributors automatically grant patent licenses on their contributions
3. **Enterprise Acceptance**: Widely recognized and approved by corporate legal departments
4. **Professional Standard**: Used by major infrastructure projects (Kubernetes, Apache projects, Ansible core libraries)
5. **Clear Permissions**: Explicit grants for use, modification, distribution, and sublicensing
6. **Trademark Protection**: Clear separation of code license from trademark rights
7. **Liability Protection**: Strong disclaimers of warranty and liability

**Compatibility Analysis**:
- ✅ **pytest (MIT)**: Apache 2.0 is compatible with MIT (can integrate)
- ✅ **lxml (BSD)**: Compatible with permissive BSD license
- ✅ **signxml (Apache 2.0)**: Same license, perfect alignment
- ✅ **cryptography (Apache 2.0/BSD)**: Compatible
- ✅ **SQLAlchemy (MIT)**: Compatible with MIT
- ✅ **PostgreSQL/SQLite**: Compatible with both licenses

### Alternatives Considered

#### MIT License
**Pros**:
- Simpler, shorter license text
- pytest itself uses MIT
- Maximum permissiveness

**Cons**:
- No explicit patent grant (less protection for cryptographic code)
- No contributor patent protection
- Less clear for enterprise legal departments regarding patents

**Decision**: Rejected due to lack of patent protection for cryptographic software

#### BSD 3-Clause License
**Pros**:
- Simple, permissive
- Good academic/research reputation

**Cons**:
- No explicit patent grant
- Less commonly used in modern infrastructure projects
- Trademark clause less clear than Apache's

**Decision**: Rejected due to lack of patent protection

#### GPL v3 / AGPL v3
**Pros**:
- Strong copyleft protections
- Patent protection included

**Cons**:
- Copyleft restrictions limit enterprise adoption
- Incompatible with many proprietary infrastructure tools
- May complicate integration with commercial Ansible playbooks
- Creates licensing friction for system administrators
- AGPL's network copyleft particularly problematic for plugins

**Decision**: Rejected due to enterprise adoption barriers and copyleft restrictions

#### MPL 2.0 (Mozilla Public License)
**Pros**:
- File-level copyleft (compromise between permissive and GPL)
- Explicit patent grant

**Cons**:
- Less familiar to enterprise legal departments
- File-level copyleft adds complexity
- Not commonly used in Python infrastructure tools

**Decision**: Rejected due to complexity and limited ecosystem adoption

## Consequences

**Positive:**

- **Patent Protection**: Explicit patent grants protect users implementing XML signatures
- **Enterprise Trust**: Apache 2.0 is pre-approved by many corporate legal departments
- **Contributor Confidence**: Clear patent grants encourage professional contributions
- **Ecosystem Alignment**: Matches signxml and cryptography (key dependencies)
- **Professional Standard**: Signals mature, production-ready infrastructure tool
- **Clear Legal Framework**: Well-understood license with extensive case law and precedent
- **International Recognition**: Apache 2.0 widely accepted globally

**Negative:**

- **Longer License Text**: More verbose than MIT (but more explicit protections)
- **Attribution Requirements**: Must include NOTICE file and license in distributions (minimal burden)
- **Not Copyleft**: Modified versions can be closed-source (acceptable for infrastructure tools)

**Neutral:**

- **License Compatibility**: Must track dependency licenses (already required regardless of choice)
- **NOTICE File Maintenance**: Must maintain NOTICE file for attributions (standard practice)

## Implementation

### Files to Create/Update

1. **LICENSE file**: Full Apache License 2.0 text
2. **NOTICE file**: Copyright notices and attributions
3. **Source file headers**: Standard Apache 2.0 headers
4. **pyproject.toml**: Update license metadata
5. **README.md**: Add license badge and section

### Copyright Notice

```
Copyright 2025 Georges Martin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Source File Header Template

```python
# Copyright 2025 Georges Martin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

### NOTICE File Content

```
pytest-jux
Copyright 2025 Georges Martin

This product includes software developed as part of the pytest-jux project
(https://github.com/your-org/pytest-jux).

This software contains code derived from or inspired by:
- pytest (MIT License) - https://pytest.org/
- signxml (Apache License 2.0) - https://github.com/XML-Security/signxml
- cryptography (Apache License 2.0 and BSD) - https://cryptography.io/
```

## Validation Criteria

License adoption will be validated through:

1. **File Presence**: LICENSE and NOTICE files in repository root
2. **Source Headers**: All source files include Apache 2.0 header
3. **Metadata Accuracy**: pyproject.toml correctly declares Apache-2.0
4. **README Documentation**: License clearly stated in README.md
5. **Dependency Compatibility**: All dependencies compatible with Apache 2.0

## Related Decisions

- ADR-0001: Record architecture decisions
- ADR-0002: Adopt development best practices (establishes professional standards)
- ADR-0003: Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack (establishes dependency licenses)

## References

- Apache License 2.0: https://www.apache.org/licenses/LICENSE-2.0
- Apache License FAQ: https://www.apache.org/foundation/license-faq.html
- Open Source Initiative: https://opensource.org/licenses/Apache-2.0
- GitHub License Guide: https://choosealicense.com/licenses/apache-2.0/
- Python Packaging Guide on Licenses: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license
