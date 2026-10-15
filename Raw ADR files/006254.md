# ADR-0002. Use CC BY-SA 4.0 License for Documentation

Date: 2025-11-25

## Status

Accepted

## Context

The SciLifeLab Architecture Board documentation will be developed collaboratively across multiple institutions. Without explicit licensing, ownership and reuse rights are unclear.

We need a license that:

- Provides multi-institutional legal clarity
- Ensures governance improvements remain open
- Prevents proprietary capture of community standards
- Enables academic citation

## Decision

We will use the Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) license for this repository.

## Consequences

### Positive

- **Share-alike provision**: Any derivative works must be distributed under the same or compatible license, ensuring the documentation remains open
- **Attribution requirement**: Users must give appropriate credit, which helps maintain visibility of SciLifeLab's contributions
- **Wide adoption**: CC BY-SA 4.0 is widely recognized and understood in the open-source community (used by Wikipedia and many documentation projects)
- **Flexibility**: Others can freely use, adapt, and build upon our architectural decisions while keeping them accessible
- **Non-software focus**: CC licenses are specifically designed for creative works and documentation, making them more appropriate than software licenses (MIT, GPL, etc.)

### Negative

- **Not suitable for code**: Any code examples should be licensed separately under a software license
- **Compatibility considerations**: Share-alike requirement may limit how others can combine our documentation with other licensed content
- **No warranty disclaimer**: Users should be aware that architectural decisions are provided "as-is" without guarantees of suitability

- The license file (LICENSE) has been added to the repository root
- A license badge and information have been added to the README
- Future code repositories may need different licenses (e.g., MIT, Apache 2.0) appropriate for software

## References

- [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
