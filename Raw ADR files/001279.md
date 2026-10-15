# Architecture Decision Record (ADR) - FTP 

## Title

FTP Server Implementation for Controlled Brute Force Attack Simulation

## Context

• Educational requirement to demonstrate common network service vulnerabilities

• Need for hands-on experience with penetration testing methodologies

• Requirement for controlled environment to practice ethical hacking techniques

• Must simulate real-world attack scenarios safely within lab environment

• FileZilla chosen as attack vector due to widespread enterprise usage


## Decision

Deploy an FTP server within the virtualized lab environment specifically configured for controlled brute force attack simulation using FileZilla as the attack platform.

## Rationale

• **Educational Value**: FTP remains common in enterprise environments despite security risks

• **Realistic Attack Vector**: Brute force attacks against FTP are frequently observed in real incidents

• **Controlled Environment**: Completely isolated within VirtualBox network preventing external impact

• **Tool Familiarity**: FileZilla is widely used, making attack simulation realistic

• **Logging Capabilities**: Excellent integration with Wazuh SIEM for attack detection analysis

• **Skill Development**: Provides hands-on experience with both offensive and defensive techniques


## Alternatives Considered

• **SSH Brute Force**: Rejected as secondary priority after FTP demonstration

• **HTTP/HTTPS Login Forms**: Rejected due to complexity for initial learning

• **SMB/NetBIOS Attacks**: Rejected due to Windows-specific limitations

• **Database Brute Force**: Rejected due to additional setup complexity

• **Remote Desktop Protocol (RDP)**: Rejected due to licensing and configuration complexity


## Consequences

### Positive

• Practical demonstration of common attack vectors

• Integration with SIEM for comprehensive attack detection learning

• Safe learning environment for penetration testing techniques

• Understanding of both attack methodologies and defensive measures

• Transferable skills applicable to real-world security assessments


### Negative

• Potential security risk if misconfigured or exposed outside lab environment

• Requires careful network isolation to prevent accidental external exposure

• May create false sense of security if students only test weak configurations

• Resource usage for additional services within virtual environment

• Ethical considerations requiring clear guidelines and supervision


### Mitigation Strategies

• Strict network isolation using VirtualBox internal networking

• Clear documentation of lab-only usage policies

• Regular security reviews of lab environment configuration

• Mandatory training on ethical hacking principles before access


## References

• [OWASP Penetration Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

• [NIST SP 800-115: Technical Guide to Information Security Testing](https://csrc.nist.gov/publications/detail/sp/800-115/final)

• [FileZilla Security Considerations](https://filezilla-project.org/security.php)

• [FTP Security Best Practices RFC 2577](https://tools.ietf.org/html/rfc2577)
