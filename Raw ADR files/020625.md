# ADR-001: Migration from ROADMAP.md to GitHub Issues

## Status
**Proposed** - Migration in progress

## Context
The Zenodotos project currently maintains a static `ROADMAP.md` file that lists planned features, completed features, and technical debt. This approach has several limitations:

- **Static nature**: The roadmap becomes outdated quickly and requires manual updates
- **Limited collaboration**: No built-in discussion or feedback mechanisms
- **Poor integration**: No connection to pull requests, releases, or development workflow
- **Maintenance burden**: Requires manual tracking of feature status and progress
- **No prioritization**: Features are listed but not prioritized or assigned
- **Limited visibility**: No easy way to see what's being worked on or planned

## Decision
We will migrate from maintaining a static `ROADMAP.md` file to using **GitHub Issues** for feature tracking and planning, while maintaining `CHANGELOG.md` for documenting completed features.

### New Workflow
- **Feature requests and planning** → GitHub Issues with labels and milestones
- **Completed features** → Documented in `CHANGELOG.md` following Keep a Changelog format
- **Release planning** → GitHub Milestones
- **Technical debt** → GitHub Issues with `technical-debt` label
- **Documentation** → Updated in README.md and contributing guidelines

## Rationale
This decision provides several benefits:

### **Better Collaboration**
- GitHub Issues enable discussions, comments, and feedback
- Multiple contributors can participate in feature planning
- Issues can be linked to pull requests for automatic tracking

### **Improved Workflow Integration**
- Issues automatically integrate with GitHub's project management features
- Labels and milestones provide better organization
- GitHub Actions can be triggered by issue events

### **Enhanced Visibility**
- Clear status tracking (open, in progress, closed)
- Assignees and due dates for accountability
- Search and filtering capabilities

### **Standard Practice**
- Follows industry best practices for open source projects
- Aligns with GitHub's ecosystem and tools
- Makes the project more accessible to new contributors

### **Reduced Maintenance**
- No manual synchronization between roadmap and actual work
- Automatic linking between issues and pull requests
- Built-in version control and history

## Consequences

### **Positive Consequences**
- **Improved collaboration**: Better discussion and feedback on features
- **Better organization**: Labels, milestones, and assignees provide structure
- **Enhanced visibility**: Clear status tracking and progress monitoring
- **Standard workflow**: Aligns with GitHub ecosystem and best practices
- **Reduced maintenance**: Less manual tracking and synchronization

### **Negative Consequences**
- **Learning curve**: Contributors need to learn GitHub Issues workflow
- **Migration effort**: Initial setup and migration of existing roadmap items
- **Potential fragmentation**: Features spread across multiple issues instead of one document
- **Dependency on GitHub**: Tied to GitHub's issue management system

### **Risks and Mitigations**
- **Risk**: Loss of historical roadmap information
  - **Mitigation**: Archive ROADMAP.md and create comprehensive migration documentation
- **Risk**: Issues becoming disorganized
  - **Mitigation**: Establish clear labeling and milestone conventions
- **Risk**: Reduced visibility for non-technical users
  - **Mitigation**: Maintain clear documentation in README.md about how to find planned features

## Implementation Plan

### **Phase 1: Analysis and Preparation**
- [x] Analyze current ROADMAP.md content
- [x] Categorize features (completed, planned, technical debt)
- [x] Design GitHub Issues structure and labels
- [x] Create migration documentation

### **Phase 2: Create GitHub Issues**
- [ ] Create labels for issue categorization
- [ ] Create milestones for version planning
- [ ] Convert planned features to GitHub Issues
- [ ] Convert technical debt items to GitHub Issues
- [ ] Organize issues with appropriate labels and milestones

### **Phase 3: Update Documentation**
- [ ] Update README.md to reference GitHub Issues
- [ ] Update contributing guidelines
- [ ] Create issue templates for feature requests
- [ ] Document the new workflow

### **Phase 4: Clean Up**
- [ ] Archive ROADMAP.md
- [ ] Remove references to ROADMAP.md from other documents
- [ ] Verify CHANGELOG.md completeness
- [ ] Finalize migration documentation

### **Phase 5: Validation**
- [ ] Test the new workflow with a sample feature
- [ ] Gather feedback from contributors
- [ ] Refine the process based on feedback

## Alternatives Considered

### **Alternative 1: Keep ROADMAP.md and Improve It**
- **Pros**: No migration effort, familiar to existing contributors
- **Cons**: Still static, limited collaboration, maintenance burden
- **Decision**: Rejected due to fundamental limitations

### **Alternative 2: Use GitHub Projects**
- **Pros**: Visual project management, kanban boards
- **Cons**: More complex, overkill for current needs
- **Decision**: Rejected - Issues provide sufficient functionality

### **Alternative 3: Use External Project Management Tools**
- **Pros**: Advanced features, integrations
- **Cons**: Additional complexity, external dependencies
- **Decision**: Rejected - GitHub Issues provide adequate functionality

### **Alternative 4: Hybrid Approach (ROADMAP.md + Issues)**
- **Pros**: Maintains familiar format while adding collaboration
- **Cons**: Duplication, synchronization challenges
- **Decision**: Rejected due to maintenance burden

## References
- [Keep a Changelog](https://keepachangelog.com/) - Standard for CHANGELOG.md format
- [GitHub Issues Documentation](https://docs.github.com/en/issues) - Official GitHub Issues guide
- [Architecture Decision Records](https://adr.github.io/) - ADR format and best practices

## Related Decisions
- None currently - this is the first ADR for the project

---

**Date**: 2025-01-27
**Author**: Project maintainers
**Reviewers**: TBD
