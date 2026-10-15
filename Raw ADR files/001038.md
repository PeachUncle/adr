## ADR - Main Technology

[Back to table of contents](composite.md)

### Status
- Accepted

### Context
We need framework for building a scalable and maintainable web API for our project. The key requirements include:
- Cross-platform compatibility.
- Long-term support.
- Good and clear documentation.
- Integration with modern development tools and cloud services.

### SWOT

| **Strengths**                                             | **Weaknesses**                                 |
|-----------------------------------------------------------|------------------------------------------------|
| Cross-platform compatibility (Windows, macOS, Linux)      | Requires familiarity with .NET ecosystem       |
| High performance and scalability                          | Steep learning curve for new developers        |
| Rich documentation and community support                  | Initial setup and configuration can be complex |
| Strong integration with modern development tools          | Limited support for legacy systems             |

| **Opportunities**                                         | **Threats**                                               |
|-----------------------------------------------------------|-----------------------------------------------------------|
| Rising demand for cross-platform web applications         | Competition from other frameworks (e.g., Node.js, Django) |
| Increasing adoption in enterprise applications            | Rapid technology changes require constant updates         |
| Enhanced features for microservices and cloud-native apps | Security vulnerabilities in improperly configured APIs    |
| Strong support from Microsoft and frequent updates        | Dependency on Microsoft technologies                      |

### Decision
We have decided to use ASP.NET Core WEB API as the main framework to develop that microservice.
- ASP.NET Core is open-source and cross-platform, allowing flexibility in deployment.
- It integrates easily with Azure and other cloud services or public clouds.
- It's open-source, so it can be hosted in most hostings.
- The framework is maintained by Microsoft and have a large, active community, so it should have long support.
- Complete tools provided free of charge, even for commercial use (e.g. Visual Studio Code).

### Consequences

Positive:
- Team is experienced in this technology.
- Access to a wide range libraries and tools within the .NET ecosystem.
- Very good and clear documentation.
- Lot's of free tutorials all over the internet.

Negative:
- No opportunity to discover new technologies.