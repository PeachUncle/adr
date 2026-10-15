---
status: "proposed"
date: "2024-11-22"
decision-makers: "@Ryangr0"
consulted: "@devops, @engineering, @product"
informed: "@developers, @security"
---

# Adoption of Internal Developer Platform

## Context and Problem Statement

Our development teams are experiencing challenges due to a fragmented information landscape and varying levels of knowledge about our infrastructure, workflows, and secrets. This leads to inefficiencies, dependencies on DevOps for routine tasks, and difficulties in maintaining standards across projects. We need a solution that centralizes information, streamlines workflows, and empowers developers to focus on delivering business value.

## Decision Drivers

- Need for a single point of entry for developers interacting with the platform.
- Desire to standardize and streamline project configurations and workflows.
- Requirement to reduce dependencies on DevOps for routine operations.
- Aim to improve developer productivity and reduce cognitive overload.
- Preference for a solution that integrates with existing tools and can be customized to our needs.

## Considered Options

- **Option 1:** Adopt [**Backstage**](https://backstage.io/) as our IDP.
- **Option 2:** Adopt [**Port.io**](https://port.io/) as our IDP.
- **Option 3:** Continue with the current setup and processes (status quo).
- **Option 4:** Develop a custom internal platform from scratch.

## Decision Outcome

Chosen option:
**Adopt Backstage as our Internal Developer Platform**, because it provides the flexibility, extensibility, and community support needed to address our challenges effectively.

### Consequences
- Good, because Backstage is open-source and customizable.
- Good, because it offers a wide range of community-supported plugins.
- Good, because it can be integrated with our existing tools and infrastructure.
- Bad, because it requires an initial setup effort.
- Bad, because there is a learning curve associated with adopting a new platform.
- Bad, because ongoing maintenance and updates are required.
- Bad, because it may lead to dependencies on a new platform.
- Bad, because it may require additional training for team members.
- Bad, because it may introduce new complexities to our workflows.

#### Mitigating circumstances
- A fair amount of documentation and community support available to assist with the setup and customization.
- @Ryangr0 has already set up a local instance of Backstage and is familiar with the platform
- @Ryangr0 is willing to lead the effort to onboard the team and provide necessary training.

## Pros and Cons of the Options

### **Option 1: Adopt Backstage**

**Description:** Adopt Backstage, an open-source Internal Developer Platform framework by Spotify, to centralize information and streamline developer workflows.

**Pros:**

- **Open Source and Customizable:** Being open-source, Backstage allows us to tailor the platform to our specific needs without licensing costs.
- **Plugin Ecosystem:** Access to numerous community-supported plugins (e.g., GitHub Actions, Sentry, Grafana) for extended functionality.
- **Active Community:** A strong community contributes to continuous improvement and support.
- **Flexible Integration:** Can integrate with our existing tools and infrastructure seamlessly.

**Cons:**

- **Initial Setup Effort:** Requires significant initial setup and customization.
- **Maintenance Responsibility:** We are responsible for ongoing maintenance and updates.
- **Learning Curve:** Team members will need to invest time to learn and adapt to the new platform.

### **Option 2: Adopt Port.io**

**Description:** Use Port.io, a platform that offers a developer portal and infrastructure management tools to centralize services and workflows.

**Pros:**

- **Feature-Rich Platform:** Provides a comprehensive set of tools out-of-the-box for service cataloging, environment management, and workflow automation.
- **User-Friendly Interface:** Designed for ease of use with a focus on user experience.
- **Managed Service:** Less overhead in terms of maintenance and updates compared to self-hosted solutions.

**Cons:**

- **Cost:** Licensing fees may be significant, especially as the team grows.
- **Less Customizable:** May not offer the same level of customization as an open-source solution.
- **Vendor Lock-In:** Dependence on a third-party provider for features and updates.

### **Option 3: Continue with Current Setup**

**Description:** Maintain the existing processes and tools without significant changes.

**Pros:**

- **No Immediate Effort:** No additional setup or training required.
- **Familiarity:** Teams continue using tools and processes they are accustomed to.

**Cons:**

- **Inefficiencies Persist:** Fragmented information and dependencies on DevOps remain unaddressed.
- **Scalability Issues:** Challenges may become more pronounced as the organization grows.
- **Lack of Standardization:** Divergence in standards and infrastructure solutions across teams continues.

### **Option 4: Develop a Custom Platform**

**Description:** Build a bespoke internal platform tailored to our specific needs from scratch.

**Pros:**

- **Fully Tailored Solution:** Platform can be designed to meet all unique requirements.
- **Complete Control:** Full ownership over features and functionalities.

**Cons:**

- **High Resource Investment:** Significant time and development effort required.
- **Maintenance Burden:** Ongoing responsibility for updates, bug fixes, and enhancements.
- **Delayed Benefits:** Longer time to realize advantages compared to adopting an existing solution.

## More Information

- [Backstage Official Documentation](https://backstage.io/)
- [Port.io Website](https://port.io/)
- [OpsLevel Website](https://www.opslevel.com/)
- [MADR Documentation](https://adr.github.io/madr/)
