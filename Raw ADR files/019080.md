# ADR-001: Business Domain and Platform Purpose

## Status

Accepted

## Context

We need to clearly define the business domain, target users, and core purpose of the platform to guide all architectural and development decisions. This clarity is essential for:

- Determining the appropriate scale and complexity of solutions
- Understanding user needs and access patterns
- Making technology choices that align with the platform's goals
- Establishing the scope of features and capabilities needed

## Decision

The platform is defined as a **Personal Portfolio Platform for Quantitative Finance** with the following characteristics:

### Primary Business Domain

- **Personal portfolio** for Tom Riddelsdell showcasing work and projects
- **Quantitative Finance** focus with emphasis on **Quantitative Index Strategies**
- **Open-source project hosting** for technical demonstrations
- **Professional networking** and collaboration facilitation

### Target User Personas

1. **Admins**:
   - Tom Riddelsdell (owner)
   - Future collaborators and contributors

2. **End Users**:
   - Potential employers evaluating Tom's work
   - Clients interested in quantitative finance expertise
   - Collaborators for research and development projects

3. **Forkers**:
   - Developers and enthusiasts who want to fork and build upon open-source projects
   - Academic researchers in quantitative finance
   - Financial technology professionals

### Core Business Processes

1. **Portfolio Presentation**: Provide a landing page summarizing interests and contact information
2. **App Onboarding**: Support deployment and showcasing of new quantitative finance applications
3. **User Access Management**: Configure and manage user permissions for different applications
4. **Project Demonstration**: Enable interactive demonstrations of quantitative strategies and tools

## Rationale

- **Focused Scope**: Clear domain focus prevents feature creep and maintains platform coherence
- **Professional Growth**: Aligns with career goals in quantitative finance and technology
- **Open Source Values**: Encourages collaboration and knowledge sharing in the finance technology community
- **Scalable Vision**: Personal platform that can grow into collaborative research environment
- **Technical Demonstration**: Provides real-world showcase of technical capabilities

## Architectural Implications

- **Scale**: Personal/small team scale - not enterprise-level complexity needed
- **Security**: Professional-grade security but not financial institution requirements
- **Performance**: Portfolio site performance expectations, not high-frequency trading requirements
- **Compliance**: Basic data protection compliance, not financial services regulation
- **Technology Choices**: Modern, demonstrable technologies that showcase technical expertise

## Business Rules and Constraints

- **Quality Over Quantity**: Focus on showcasing high-quality, well-documented projects
- **Open Source First**: Default to open-source unless specific privacy/IP concerns
- **Educational Value**: Projects should demonstrate learning and teaching capability
- **Professional Standards**: All content should meet professional presentation standards

## Consequences

- **Technology Stack**: Choices should demonstrate modern best practices and technical skill
- **User Experience**: Should reflect professional quality and attention to detail
- **Content Strategy**: Focus on quantitative finance applications and methodologies
- **Collaboration Model**: Open to collaboration but maintained with high standards
- **Growth Path**: Can evolve from personal portfolio to collaborative platform over time

## Success Metrics

- **Professional Opportunities**: Leads generated from portfolio showcase
- **Community Engagement**: Forks, stars, and contributions to open-source projects
- **Technical Demonstration**: Successful deployment and operation of quantitative applications
- **Knowledge Sharing**: Educational value provided to the quantitative finance community

## Alternatives Considered

- **Enterprise SaaS Platform**: Too complex and costly for the target scale
- **Simple Static Portfolio**: Too limited for demonstrating full technical capabilities
- **Academic Research Platform**: Too narrow focus, missing professional portfolio aspects
- **Financial Services Platform**: Too regulated and complex for the intended purpose

## Future Evolution

- **Collaborative Research**: May evolve to support multi-user research projects
- **Educational Platform**: Could expand to include tutorials and educational content
- **Consulting Business**: May grow to support client project showcases
- **Open Source Foundation**: Could become a hub for quantitative finance open source projects
