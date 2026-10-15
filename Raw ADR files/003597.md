# Adoption of GPG for encryption and Tar for compression for Phoenix

## Status
Accepted

## Context
Phoenix should support compressing and encrypting the files and folders it backs up to minimize disk and network utilization and ensure security since the data can be stored on a third party storage provider. In this context, we need to decide a mechanism to compress files and a mechanism to encrypt files. Given the complexity and the high risk associated with implementing custom encryption methods, and the availability of proven third-party solutions, we must choose between leveraging established third-party tools or developing in-house capabilities.

### Alternatives Considered:
- own encryption scheme
- GPG for encryption
- Fernet for encryption
- AES for encryption
- own compression scheme
- Tar for compression
- zip for compression
- 7z for compression

## Decision
In this context, we decide to use **GPG for encryption and Tar for compression** due to the following reasons:
- **Complexity and Risk of Custom Solutions**: Developing custom encryption methods is highly risky due to the potential for security flaws and vulnerabilities. Encryption requires careful implementation and continuous maintenance to protect against evolving security threats. Using established, widely-reviewed protocols like those provided by GPG mitigates these risks significantly.
- **Compliance and Trust**: Third-party tools like GPG are compliant with various regulatory standards and are trusted in the industry. This compliance is crucial for meeting legal and security standards. Tar and GPG are widely used in the *nix community.  
- **Community Support and Updates**: Tools like GPG and Tar have large communities and are regularly updated. This ongoing support reduces the risk of the tools becoming obsolete and ensures that security vulnerabilities are addressed promptly.  
- **Cost and Resource Efficiency**: Utilizing third-party tools reduces the need for extensive development and maintenance resources that would be required for custom solutions. This allows the team to focus on other critical aspects of the backup system.


## Consequences
### Advantages:
- **Security**: Leveraging well-established tools reduces the risk of security flaws.  
- **Maintenance**: Relying on third-party solutions with active community support and updates ensures that the system remains secure and functional over time.  
- **Compliance**: Using well-known, compliant tools helps in adhering to legal and regulatory requirements.  

### Disadvantages:
- **Dependence**: Dependency on external tools can pose risks if these tools are discontinued or if their licensing changes unfavorably.
- **Flexibility**: Using third-party tools may limit customization options compared to a custom solution.
- **Performance**: There may be some performance trade-offs, as third-party tools might not be optimized for all specific use cases of the backup system.
