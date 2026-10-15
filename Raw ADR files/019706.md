# ADR-015: Ansible Collection Distribution via Galaxy

**Status:** Accepted ✅  
**Date:** 2025-10-28  
**Decision Makers:** @tosin2013  
**Consulted:** Community, Ansible Best Practices  
**Informed:** Contributors, Users

## Context and Problem Statement

The Validated Patterns Ansible Toolkit currently distributes 7 production-ready Ansible roles through direct repository cloning or manual role extraction. While this works, it has limitations:

- **Discovery**: Users must know the GitHub repository URL
- **Installation**: Manual cloning or copying of individual roles
- **Versioning**: No semantic versioning for role updates
- **Dependencies**: No automatic dependency resolution
- **Updates**: Manual git pull or re-cloning required
- **Distribution**: Not available on Ansible Galaxy (the standard distribution platform)

As of 2024, **Ansible Collections** are the recommended distribution format for Ansible content, replacing standalone roles as the primary method for sharing roles, modules, plugins, and playbooks.

## Decision Drivers

* **Discoverability**: Make roles easily discoverable on Ansible Galaxy
* **Standard Distribution**: Follow Ansible ecosystem best practices (collections over standalone roles)
* **Ease of Installation**: Enable `ansible-galaxy collection install` workflow
* **Version Management**: Provide semantic versioning and dependency resolution
* **Backward Compatibility**: Maintain current installation methods (clone/fork)
* **Professional Distribution**: Align with enterprise Ansible practices
* **Future Extensibility**: Enable adding custom modules/plugins later
* **User Choice**: Support multiple installation methods

## Considered Options

### Option 1: Keep Current Distribution Only (Rejected)
- **Pros**: No changes needed, works today
- **Cons**: Not discoverable on Galaxy, manual installation, no versioning
- **Decision**: Rejected - doesn't follow Ansible best practices

### Option 2: Convert Entirely to Collection (Rejected)
- **Pros**: Clean collection-only structure
- **Cons**: Breaking changes for existing users, loses template repository benefits
- **Decision**: Rejected - too disruptive

### Option 3: Hybrid Distribution Model (Recommended) ✅
- **Pros**: 
  - Supports both Galaxy collection and direct clone/fork
  - No breaking changes
  - Users choose preferred method
  - Maintains template repository nature
- **Cons**: Slightly more complex repository structure
- **Decision**: **ACCEPTED** ✅

### Option 4: Separate Collection Repository (Rejected)
- **Pros**: Clean separation of concerns
- **Cons**: Maintenance overhead, split documentation, version sync issues
- **Decision**: Rejected - too much overhead

## Decision

**Adopt a Hybrid Distribution Model** supporting both:
1. **Ansible Galaxy Collection**: `tosin2013.validated_patterns_toolkit`
2. **Direct Repository Clone/Fork**: Current method (maintained)

### Collection Naming

**Collection Name**: `tosin2013.validated_patterns_toolkit`

**Rationale**:
- **Namespace**: `tosin2013` (personal Galaxy namespace, immediately available)
- **Name**: `validated_patterns_toolkit` (descriptive, matches repository)
- **Alternative considered**: `validated_patterns.toolkit` (requires namespace approval from Ansible Galaxy team)
- **Decision**: Use personal namespace for immediate availability

### Repository Structure

**Hybrid Structure** (maintains backward compatibility):

```
validated-patterns-ansible-toolkit/
├── README.md                           # Main repo README (updated with both methods)
├── CHANGELOG.md                        # Unified changelog
├── LICENSE                             # GPL-3.0
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── SUPPORT.md
│
├── collection/                         # NEW: Ansible Collection
│   ├── galaxy.yml                      # Collection metadata
│   ├── README.md                       # Collection-specific README
│   ├── CHANGELOG.rst                   # Collection changelog (Galaxy format)
│   ├── roles/                          # Roles (no validated_patterns_ prefix)
│   │   ├── prerequisites/
│   │   ├── common/
│   │   ├── operator/
│   │   ├── deploy/
│   │   ├── gitea/
│   │   ├── secrets/
│   │   └── validate/
│   ├── playbooks/                      # Example playbooks
│   │   ├── deploy_with_operator.yml
│   │   └── deploy_complete_pattern.yml
│   ├── plugins/                        # Future: custom modules/plugins
│   │   ├── modules/
│   │   ├── filter/
│   │   └── lookup/
│   ├── tests/
│   │   └── integration/
│   └── meta/
│       └── runtime.yml
│
├── ansible/                            # KEEP: Current structure (backward compat)
│   ├── roles/                          # Symlinks to collection/roles OR copies
│   │   ├── validated_patterns_prerequisites/
│   │   ├── validated_patterns_common/
│   │   └── ...
│   └── playbooks/
│
├── docs/                               # All documentation
├── quarkus-reference-app/              # Reference applications
├── tests/                              # Integration tests
└── scripts/                            # Build/utility scripts
```

### Installation Methods

**Method 1: Ansible Galaxy Collection** (NEW)
```bash
# Install from Galaxy
ansible-galaxy collection install tosin2013.validated_patterns_toolkit

# Use in playbook
---
collections:
  - tosin2013.validated_patterns_toolkit

roles:
  - tosin2013.validated_patterns_toolkit.prerequisites
  - tosin2013.validated_patterns_toolkit.common
  - tosin2013.validated_patterns_toolkit.deploy
```

**Method 2: Direct Repository Clone** (CURRENT - MAINTAINED)
```bash
# Clone repository
git clone https://github.com/tosin2013/validated-patterns-ansible-toolkit.git
cd validated-patterns-ansible-toolkit

# Use roles directly
ansible-playbook ansible/playbooks/deploy_with_operator.yml
```

**Method 3: Extract Individual Roles** (CURRENT - MAINTAINED)
```bash
# Copy specific role
cp -r ansible/roles/validated_patterns_prerequisites ~/my-project/roles/

# Use in playbook
roles:
  - validated_patterns_prerequisites
```

### Collection Metadata (galaxy.yml)

```yaml
namespace: tosin2013
name: validated_patterns_toolkit
version: 1.0.0
readme: README.md
authors:
  - Tosin Akinosho <tosin.akinosho@gmail.com>
description: >
  Production-ready Ansible roles for deploying Validated Patterns on OpenShift.
  Includes 7 roles for prerequisites, GitOps setup, deployment, secrets management,
  and validation. Reference implementation and reusable toolkit.
license:
  - GPL-3.0-or-later
tags:
  - openshift
  - validated_patterns
  - gitops
  - argocd
  - kubernetes
  - redhat
  - helm
  - deployment
dependencies:
  kubernetes.core: ">=2.3.0"
  community.general: ">=5.0.0"
repository: https://github.com/tosin2013/validated-patterns-ansible-toolkit
documentation: https://github.com/tosin2013/validated-patterns-ansible-toolkit/tree/main/docs
homepage: https://github.com/tosin2013/validated-patterns-ansible-toolkit
issues: https://github.com/tosin2013/validated-patterns-ansible-toolkit/issues
```

## Consequences

### Positive

1. **Discoverability** ✅
   - Listed on Ansible Galaxy
   - Searchable by tags (openshift, gitops, argocd)
   - Download statistics and community ratings

2. **Easy Installation** ✅
   - Single command: `ansible-galaxy collection install tosin2013.validated_patterns_toolkit`
   - Automatic dependency resolution
   - Version pinning support

3. **Professional Distribution** ✅
   - Follows Ansible best practices (2024)
   - Semantic versioning (1.0.0, 1.1.0, 2.0.0)
   - Proper dependency management

4. **No Breaking Changes** ✅
   - Current installation methods still work
   - Backward compatibility maintained
   - Users choose preferred method

5. **Future Extensibility** ✅
   - Can add custom modules later
   - Can add plugins (filters, lookups)
   - Can bundle playbooks and documentation

6. **Version Management** ✅
   - Users can pin to specific versions
   - Automatic updates available
   - Changelog tracking

### Negative

1. **Repository Complexity** ⚠️
   - Dual structure (collection/ and ansible/)
   - Need to maintain both
   - **Mitigation**: Use symlinks or build scripts

2. **Documentation Duplication** ⚠️
   - Collection README vs Repository README
   - **Mitigation**: Collection README references main docs

3. **Build Process** ⚠️
   - Need to build collection tarball
   - Need to publish to Galaxy
   - **Mitigation**: Automate with GitHub Actions

4. **Namespace Limitation** ⚠️
   - Using personal namespace (tosin2013) not org namespace
   - **Mitigation**: Can migrate to org namespace later if needed

## Implementation Plan

### Phase 1: v1.0.0 Release (Current - In Progress)
- ✅ Complete current release without collection
- ✅ Stabilize roles and documentation
- ✅ Gather user feedback

### Phase 2: Collection Preparation (v1.1.0 or Post-v1.0.0)
1. **Create Collection Structure** (2-4 hours)
   - Run `ansible-galaxy collection init tosin2013.validated_patterns_toolkit`
   - Create `collection/` directory
   - Move/symlink roles to `collection/roles/`
   - Create `galaxy.yml` with metadata

2. **Update Role Metadata** (2-4 hours)
   - Update all `meta/main.yml` files
   - Add proper galaxy_info (author, description, license)
   - Document dependencies
   - Add galaxy_tags

3. **Create Collection Documentation** (2-4 hours)
   - Collection README.md
   - CHANGELOG.rst (Galaxy format)
   - Role-specific documentation
   - Usage examples

4. **Build and Test** (4-8 hours)
   - Build collection: `ansible-galaxy collection build collection/`
   - Test installation locally
   - Test all roles work via collection namespace
   - Integration testing

5. **Publish to Galaxy** (1-2 hours)
   - Create Ansible Galaxy account (if needed)
   - Generate API token
   - Publish: `ansible-galaxy collection publish tosin2013-validated_patterns_toolkit-1.0.0.tar.gz`
   - Verify on Galaxy

6. **Update Documentation** (2-4 hours)
   - Update README.md with collection installation
   - Update MIGRATION-GUIDE.md
   - Create ADR-015 (this document)
   - Update CHANGELOG.md

7. **Automate Publishing** (4-8 hours)
   - Create GitHub Actions workflow
   - Automate collection build on release
   - Automate Galaxy publishing
   - Version bumping automation

**Total Estimated Effort**: 1-2 days

### Phase 3: Maintenance (Ongoing)
- Maintain both distribution methods
- Keep collection and repository in sync
- Publish updates to Galaxy with each release
- Monitor Galaxy download statistics and feedback

## Migration Path for Users

### For New Users
**Recommended**: Use Ansible Galaxy collection
```bash
ansible-galaxy collection install tosin2013.validated_patterns_toolkit
```

### For Existing Users
**No changes required** - current method continues to work
```bash
git clone https://github.com/tosin2013/validated-patterns-ansible-toolkit.git
```

**Optional**: Migrate to collection for easier updates
- See migration guide in documentation
- No breaking changes in playbooks

## Success Metrics

1. **Galaxy Downloads**: Track collection downloads
2. **GitHub Stars**: Monitor repository popularity
3. **Community Feedback**: Issues, discussions, PRs
4. **Installation Method**: Survey users on preferred method
5. **Version Adoption**: Track which versions are most used

## Alternatives Considered

### Alternative Namespace: validated_patterns.toolkit
- **Pros**: More professional, organization-level
- **Cons**: Requires namespace approval from Ansible Galaxy team, delays release
- **Decision**: Start with `tosin2013`, migrate later if needed

### Separate Collection Repository
- **Pros**: Clean separation
- **Cons**: Maintenance overhead, documentation split
- **Decision**: Rejected - hybrid model is better

## References

* [Ansible Collections Documentation](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
* [Migrating Roles to Collections](https://docs.ansible.com/ansible/latest/dev_guide/migrating_roles.html)
* [Distributing Collections](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_distributing.html)
* [Ansible Galaxy](https://galaxy.ansible.com/)
* [Collection Structure](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_structure.html)
* [Semantic Versioning](https://semver.org/)

## Decision Outcome

**Approved**: Hybrid distribution model with Ansible Galaxy collection `tosin2013.validated_patterns_toolkit`

**Timeline**: 
- v1.0.0: Current distribution (clone/fork)
- v1.1.0 or post-v1.0.0: Add Galaxy collection distribution
- Ongoing: Maintain both methods

**Next Steps**:
1. Complete v1.0.0 release
2. Create collection structure
3. Publish to Ansible Galaxy
4. Update documentation
5. Announce to community

---

**Status**: Accepted ✅  
**Implementation**: Planned for v1.1.0 or post-v1.0.0  
**Backward Compatibility**: Maintained ✅

