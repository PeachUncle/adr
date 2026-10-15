# [ADR-0005] CMS Selection

## Status

Accepted

## Date

2023-06-20

## Context

As part of our MACH architecture implementation ([ADR-0001](0001-adopt-mach-architecture.md)), we need a Content Management System (CMS) to manage website content. The "Headless" aspect of MACH requires a CMS that can deliver content via APIs rather than being tightly coupled to the presentation layer.

Our requirements for the CMS include:
- Headless architecture with robust API capabilities
- User-friendly content authoring experience
- Flexible content modeling
- Support for various content types (text, images, videos, etc.)
- Version control and content workflows
- Role-based access control
- Performance and scalability
- Integration capabilities with our microservices architecture
- Active community and ongoing development

## Decision

We will use **Ghost CMS** as our headless CMS solution.

Ghost will be deployed in Kubernetes using a custom Helm chart, with the following configuration:
- Deployed in the `cms` namespace
- Configured with PostgreSQL as the database backend
- Set up with S3-compatible storage (MinIO) for media files
- Exposed through the Kong API Gateway
- Integrated with our authentication system

## Consequences

### Positive

- **API-First**: Ghost provides a comprehensive RESTful API for content delivery.
- **Developer Experience**: Ghost has excellent developer documentation and a clean API.
- **User Experience**: Ghost offers a modern, intuitive authoring interface.
- **Performance**: Ghost is lightweight and performs well under load.
- **Node.js Based**: Aligns with our backend technology stack.
- **Markdown Support**: Native support for Markdown simplifies content creation.
- **SEO Features**: Built-in SEO features help with content discoverability.
- **Active Community**: Ghost has an active community and regular updates.
- **Open Source**: Available under the MIT license with the option for a managed service.

### Negative

- **Limited Enterprise Features**: Some enterprise features may need to be custom-built.
- **Customization Complexity**: Deep customization can be challenging.
- **Plugin Ecosystem**: Smaller plugin ecosystem compared to some alternatives.
- **Learning Curve**: Team needs to learn Ghost's content model and API.
- **Integration Effort**: Requires integration work with our authentication and authorization systems.

## Alternatives Considered

### Contentful

**Pros**:
- Fully managed SaaS solution
- Robust API and SDK support
- Advanced content modeling
- Strong enterprise features
- Good performance and reliability

**Cons**:
- Subscription cost can be high at scale
- Vendor lock-in
- Limited customization of the authoring interface
- API rate limits on lower tiers

This option was rejected primarily due to cost concerns and the desire to avoid vendor lock-in.

### Strapi

**Pros**:
- Open-source and self-hostable
- Highly customizable
- GraphQL and REST API support
- Good content modeling capabilities
- Active community

**Cons**:
- Less mature than some alternatives
- Performance concerns at scale
- Admin UI can be slower
- Requires more development effort to customize

This option was strongly considered but rejected in favor of Ghost due to Ghost's better performance and more polished user experience.

### WordPress with Headless Configuration

**Pros**:
- Familiar to many content creators
- Vast plugin ecosystem
- Large community and resources
- Flexible content types with Advanced Custom Fields

**Cons**:
- Not designed as a headless CMS from the ground up
- Performance concerns
- Security considerations
- Technical debt and legacy code

This option was rejected because we preferred a CMS designed to be headless from the start.

### Custom-Built CMS

**Pros**:
- Tailored to our exact requirements
- Full control over features and implementation
- No licensing costs
- Deep integration with our systems

**Cons**:
- Significant development effort
- Ongoing maintenance burden
- No community support
- Reinventing the wheel

This option was rejected due to the development effort required and the availability of good open-source alternatives.

## References

- [Ghost API Documentation](https://ghost.org/docs/api/)
- [Ghost for Developers](https://ghost.org/docs/api/v3/javascript/content/)
- [Headless CMS Comparison](https://www.contentful.com/r/knowledgebase/headless-cms-comparison/)
- [JAMstack and Headless CMS](https://jamstack.org/headless-cms/)
- [Ghost on Kubernetes](https://github.com/bitnami/charts/tree/master/bitnami/ghost)
