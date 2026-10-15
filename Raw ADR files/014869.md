# ADR-0009: Adopt REUSE/SPDX License Identifiers

**Status**: Accepted
**Date**: 2025-10-20
**Decision Makers**: Georges Martin
**Related**: ADR-0004 (Apache License 2.0), ADR-0005 (Security Framework), ADR-0008 (OpenSSF Best Practices)

## Context

pytest-jux source files currently use traditional 14-line Apache License 2.0 copyright headers in every file. While legally correct and compliant, these headers are:

1. **Verbose**: 14 lines of boilerplate before actual code
2. **Not Machine-Readable**: Requires human parsing or complex regex to extract license information
3. **Harder to Maintain**: Multiple copyright holders or years require updating full text
4. **Not Industry Standard**: Modern OSS projects use SPDX identifiers (Linux kernel, KDE, curl, git, etc.)

The REUSE specification (https://reuse.software/) provides a standardized, machine-readable way to declare copyright and licensing using SPDX identifiers. REUSE is:

- **Adopted** by: KDE, Free Software Foundation Europe, curl, git, and hundreds of projects
- **Recommended** by: OpenSSF Best Practices Badge, EU Cyber Resilience Act compliance
- **Required** for: Some corporate procurement processes and government contracts
- **Compatible** with: SPDX SBOM generation (planned Sprint 6)

## Decision

**Adopt REUSE/SPDX license identifiers for all source files.**

### New Header Format

**Before (14 lines)**:
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

"""Module docstring."""
```

**After (2 lines)**:
```python
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Module docstring."""
```

### Implementation Details

1. **SPDX-FileCopyrightText**: Machine-readable copyright declaration
2. **SPDX-License-Identifier**: Machine-readable license identifier (`Apache-2.0`)
3. **Full License**: Remains in `LICENSE` file (required by Apache 2.0)
4. **Compliance**: Follows REUSE Specification 3.0

### Affected Files

- All Python source files (31 converted)
- Total line reduction: ~372 lines of boilerplate removed

## Alternatives Considered

### 1. Keep Traditional Headers

**Pros**:
- Already in place (no work required)
- More explicit for human readers
- Familiar to developers

**Cons**:
- Not machine-readable
- 14 lines of boilerplate per file
- Not aligned with modern OSS practices
- Harder to maintain with multiple contributors

**Decision**: Rejected - Benefits of SPDX outweigh familiarity

### 2. SPDX Identifiers Only (No Copyright Text)

```python
# SPDX-License-Identifier: Apache-2.0
```

**Pros**:
- Even more minimal (1 line)
- Used by some projects

**Cons**:
- Missing copyright holder information
- Not REUSE-compliant
- Loses legal clarity

**Decision**: Rejected - Copyright holder should be explicit

### 3. Hybrid (SPDX + Partial License Text)

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Georges Martin
#
# Licensed under the Apache License 2.0.
# See LICENSE file for full license text.
```

**Pros**:
- More familiar transition
- Includes copyright

**Cons**:
- Still 4-5 lines
- Not REUSE-compliant
- Redundant with SPDX-FileCopyrightText

**Decision**: Rejected - Not fully REUSE-compliant

## Consequences

### Positive

1. **Reduced Boilerplate**: 372 lines of copyright headers removed
2. **Machine-Readable**: Tools can automatically extract license information
3. **REUSE-Compliant**: Can validate with `reuse lint` tool
4. **SBOM-Ready**: SPDX identifiers integrate with SBOM generation (Sprint 6)
5. **Industry Standard**: Aligns with modern OSS practices
6. **Easier Maintenance**: Multiple copyright holders/years easier to manage
7. **OpenSSF Alignment**: Supports Best Practices Badge requirements

### Negative

1. **Familiarity**: Some developers may be unfamiliar with SPDX format
2. **Tooling**: Pre-commit hooks may need updates (future)
3. **Git History**: Large one-time change affecting many files

### Neutral

1. **Legal Status**: No change - still Apache 2.0 licensed
2. **Full License Text**: Still required in `LICENSE` file
3. **Copyright Holder**: No change - Georges Martin

## Validation

### REUSE Compliance

Project can be validated with:

```bash
pip install reuse
reuse lint
```

Expected result: REUSE-compliant (when fully implemented)

### SPDX SBOM Integration

SPDX identifiers enable automatic license detection in:
- SBOM generation (CycloneDX, SPDX)
- GitHub dependency graph
- License compliance tools
- Security scanners

## Migration Notes

### One-Time Conversion

All 31 Python files converted in a single commit using automated script (`convert_to_reuse.py`).

### Future Files

New files should use REUSE header format:

```python
# SPDX-FileCopyrightText: YYYY Author Name <email@example.com>
# SPDX-License-Identifier: Apache-2.0
```

### Multiple Copyright Holders (Future)

If contributions are accepted:

```python
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-FileCopyrightText: 2026 Jane Doe <jane@example.com>
# SPDX-License-Identifier: Apache-2.0
```

### File Contributors (Optional)

For significant contributions to specific files:

```python
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-FileContributor: Jane Doe <jane@example.com>
# SPDX-License-Identifier: Apache-2.0
```

## References

### REUSE Specification

- **REUSE Homepage**: https://reuse.software/
- **REUSE Spec 3.0**: https://reuse.software/spec/
- **REUSE Tutorial**: https://reuse.software/tutorial/

### SPDX

- **SPDX Homepage**: https://spdx.dev/
- **SPDX License List**: https://spdx.org/licenses/
- **Apache-2.0**: https://spdx.org/licenses/Apache-2.0.html

### Tools

- **reuse-tool**: https://github.com/fsfe/reuse-tool (validation)
- **licensee**: https://github.com/licensee/licensee (GitHub's license detector)
- **scancode**: https://github.com/nexB/scancode-toolkit (license scanning)

### Adopters

- **Linux Kernel**: https://www.kernel.org/doc/html/latest/process/license-rules.html
- **KDE**: https://community.kde.org/Policies/Licensing_Policy
- **curl**: https://github.com/curl/curl/blob/master/REUSE.toml
- **git**: https://github.com/git/git (SPDX identifiers)

### OpenSSF Best Practices

- **License Clarity**: https://www.bestpractices.dev/en/criteria/0#license_location
- **SBOM Requirements**: Support for machine-readable license detection

## Implementation Timeline

- **2025-10-20**: ADR created and accepted
- **2025-10-20**: All 31 Python files converted to REUSE format
- **Future (Sprint 6)**: Add `reuse lint` to CI/CD pipeline
- **Future (Sprint 6)**: SPDX identifiers used in SBOM generation

## Compliance Checklist

- [x] ADR documented
- [x] 31 Python source files converted
- [x] LICENSE file unchanged (Apache 2.0 full text retained)
- [x] NOTICE file unchanged
- [x] CHANGELOG.md updated
- [ ] `reuse lint` validation (future - requires reuse-tool installation)
- [ ] CI/CD integration (future - Sprint 6)

## Success Criteria

1. ✅ All source files use SPDX identifiers
2. ✅ 372+ lines of boilerplate removed
3. ⏳ REUSE-compliant (validated with `reuse lint`)
4. ⏳ SBOM generation includes license data (Sprint 6)
5. ⏳ No legal or compliance issues

## Notes

This change is **non-breaking**:
- License unchanged (Apache 2.0)
- Copyright holder unchanged (Georges Martin)
- Legal protections unchanged
- Only format is different (machine-readable)

This prepares pytest-jux for:
- Sprint 6: OpenSSF Best Practices Badge
- Sprint 6: SBOM generation with license compliance
- Future: EU Cyber Resilience Act compliance
- Future: Corporate/government procurement requirements

---

**Adopted**: 2025-10-20
**Author**: Georges Martin
**Impact**: Low (format only, no legal/functional change)
**Effort**: Completed (automated conversion)
