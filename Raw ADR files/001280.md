# Architecture Decision Record (ADR) - Virtual-Machine

## Title

VirtualBox Implementation for Network Simulation with ParrotOS and Windows 11

## Context

• Need for isolated testing environment to conduct security assessments safely

• Requirement to simulate real-world network scenarios without impacting production systems

• Budget limitations requiring cost-effective virtualization solution

• Must support multiple operating systems for comprehensive security testing

• Need for snapshot capabilities and easy environment replication


## Decision

Implement VirtualBox as the primary virtualization platform with ParrotOS and Windows 11 virtual machines for network simulation and security testing.

## Rationale

• **Cost-Effective**: Free, open-source virtualization platform

• **Cross-Platform Support**: Runs on Windows, macOS, and Linux host systems

• **Snapshot Functionality**: Easy rollback capabilities for testing scenarios

• **Operating System Selection**:

  - **ParrotOS**: Security-focused distribution with pre-installed penetration testing tools
  - **Windows 11**: Current enterprise standard requiring security assessment

• **Network Simulation**: Advanced networking features for creating complex topologies

• **Resource Efficiency**: Reasonable resource usage for multi-VM environments

## Alternatives Considered

• **VMware Workstation**: Rejected due to licensing costs and limited free features

• **Hyper-V**: Rejected due to Windows-only limitation and complexity

• **KVM/QEMU**: Rejected due to steep learning curve and Linux-only hosting

• **Physical Lab Equipment**: Rejected due to high costs and space requirements

• **Cloud-Based Labs**: Rejected due to ongoing costs and internet dependency


## Consequences

### Positive

• Safe, isolated testing environment preventing production system impact

• Cost-effective solution with no licensing fees

• Ability to quickly reset environments using snapshots

• Comprehensive tool availability through ParrotOS

• Realistic Windows 11 environment for current threat landscape testing


### Negative

• Resource consumption on host system (RAM, CPU, storage)

• Performance limitations compared to physical hardware

• Potential compatibility issues with some specialized security tools

• Limited by host system specifications for concurrent VM operations

• Manual setup and configuration requirements


## References

• [VirtualBox User Manual](https://www.virtualbox.org/manual/)

• [ParrotOS Documentation](https://docs.parrotlinux.org/)

• [Windows 11 Enterprise Security Features](https://docs.microsoft.com/en-us/windows/security/)