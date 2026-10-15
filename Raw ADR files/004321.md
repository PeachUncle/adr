# ADR-012: Version Management Philosophy

## Status
Accepted

## Context
ToolVault's bundle-based architecture with timestamp versioning requires a clear philosophy for how users interact with tool versions. The system must balance getting users the latest improvements and bug fixes while supporting reproducibility requirements for scientific analysis. Bundle distributions include all historical commits, making legacy data available while encouraging adoption of improvements.

## Decision
We will implement a latest-by-default version management philosophy with the following characteristics:

### Default Behavior
- **Latest version priority**: Tools always use the newest available version by default
- **Automatic updates**: Users automatically benefit from bug fixes and improvements
- **Historical preservation**: All versions remain available in bundle distributions
- **Legacy data access**: Past data and tool versions always accessible for reproducibility

### User Pinning Options
- **Use newest**: Always use the most recent version (default behavior)
- **Use newest compatible**: Use latest version with compatible input/output schema
- **Use exact match**: Pin to specific timestamp version for guaranteed reproducibility

### Compatibility Determination
- **Schema-based compatibility**: Tools with matching input/output schemas are considered compatible
- **Automatic detection**: ToolVault compares schemas to determine compatibility
- **Breaking change identification**: Schema changes automatically trigger compatibility warnings
- **Metadata-driven decisions**: Bundle metadata drives compatibility assessments

### Version Storage Strategy
- **Complete historical archive**: Maintain all versions forever for full reproducibility
- **Bundle-included history**: All commits included in distributions eliminate separate version storage
- **No pruning**: Never remove old versions to ensure long-term analytical reproducibility
- **Accessible legacy**: Historical versions remain accessible through standard interfaces

### Breaking Change Management
- **Notification system**: Alert users when pinned versions become incompatible
- **Schema comparison**: Show detailed differences between incompatible versions
- **Migration assistance**: Provide clear information about what changed and why
- **User-controlled migration**: Users decide when and how to migrate to new versions

### User Interface Approach
- **Visible but simple**: Display current version with easy access to pinning options
- **Low-friction pinning**: Simple toggle to pin current version for critical workflows
- **Version transparency**: Clear indication of which version is being used and why
- **Advanced options available**: Detailed version controls accessible when needed

## Rationale

### Latest-by-Default Benefits
Using newest versions by default ensures users automatically receive bug fixes, performance improvements, and new features without requiring manual intervention or awareness of version management.

### Schema-Based Compatibility
Input/output schema matching provides objective, automated compatibility determination that aligns with ToolVault's metadata-driven architecture and user expectations.

### Complete Version Preservation
Maintaining all historical versions supports scientific reproducibility requirements while the bundle-based distribution makes this storage efficient.

### User-Controlled Pinning
Three pinning options (newest, newest compatible, exact match) provide flexibility for different reproducibility needs while maintaining simple defaults.

### Notification-Based Migration
Alerting users to compatibility breaks with schema comparison information enables informed migration decisions without forced upgrades.

## Consequences

### Positive
- **Automatic improvements**: Users get bug fixes and enhancements without manual updates
- **Flexible reproducibility**: Multiple pinning options support different reproducibility needs
- **Clear compatibility**: Schema-based determination provides objective compatibility rules
- **Complete history**: All versions preserved for long-term analytical reproducibility
- **Informed migration**: Schema comparison helps users understand breaking changes

### Negative
- **Storage overhead**: Keeping all versions increases bundle sizes over time
- **Potential disruption**: Automatic updates might change behavior unexpectedly
- **Migration burden**: Users must manually handle breaking changes when they occur
- **Complexity growth**: More versions create more potential configuration combinations

### Mitigation Strategies
- **Bundle efficiency**: Leverage bundle structure to minimize version storage overhead
- **Clear communication**: Provide transparent information about version changes and impacts
- **Migration tools**: Develop schema comparison and migration assistance features
- **Testing practices**: Encourage testing with latest versions before critical analyses

## Implementation Notes
- Version comparison will be based on tool input/output schema matching
- Bundle distribution will include complete version history efficiently
- User interface will provide simple pinning controls with advanced options available
- Breaking change notifications will include detailed schema comparison views
- Migration assistance will focus on schema difference visualization
- All pinning options will be persistable in user workflows and project configurations