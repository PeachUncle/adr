---
id: 002
status: "proposed"
supersedes: null
superseded_by: null
---

# Decision Record 002: Domain Management Approach

## Context

We need to establish a domain management strategy for the game platform infrastructure. The domain will be used to provide human-readable access to game servers and services, replacing the need for users to remember IP addresses. This decision impacts user experience, learning opportunities, and the overall architecture of our platform.

This is part of a developer course where students will be the primary implementers, with instructor backing. The work will be done during weekly social time, so the approach should balance learning value with practical implementation. Students should be able to put this experience on their CVs and include it in their portfolios, making the technical depth and real-world applicability important considerations.

## Decision

We need to choose between three domain management approaches:

### 1. IP-based routing

This approach uses direct IP addresses for accessing game servers and services. Users would connect directly to server IPs (e.g., `123.456.789.0:25565` for Minecraft) without any domain name resolution.

**Note:** Dead simple but very limited in learning value and trust chain establishment. While functional, it provides minimal educational benefit and poor user experience.

**Pros:**

- Zero setup time and configuration overhead
- No domain registration or DNS management required
- No ongoing costs
- Simple to understand and debug
- No external dependencies
- No learning curve for domain concepts
- **Immediate availability** - can start using right away
- **Zero maintenance** - no ongoing domain management required

**Cons:**

- **Poor user experience** - difficult to remember IP addresses
- **No learning opportunities** - missing DNS, domain management, trust chains
- **Limited portfolio value** - no modern networking or domain administration skills
- **No professional practices** - real-world systems use domains
- **Scaling challenges** - IP changes require manual updates everywhere
- **No SSL/TLS learning** - certificates require domain names
- **No service discovery** - harder to implement load balancing and failover
- **Not user-friendly** - requires sharing IP addresses with players
- **No security features** - no SSL/TLS, no domain-based security policies
- **Poor integration** - doesn't work well with modern infrastructure automation

### 2. Student-owned domain

This approach involves leasing or using a domain name owned by one of the students. The team would register a domain through a registrar and manage DNS records for the game platform services.

**Note:** Straightforward approach with some ownership complexity. Provides good learning value but introduces potential contention around domain ownership within the group.

**Pros:**

- **Good learning value** - DNS management, domain administration, SSL certificates
- **Portfolio relevance** - real-world domain and DNS experience
- **Full control** - complete ownership of domain and DNS records
- **Professional practices** - industry-standard domain management
- **SSL/TLS capabilities** - enables HTTPS and secure connections
- **User-friendly** - memorable domain names for services
- **Manageable complexity** - straightforward domain registration and DNS setup
- **Real-world experience** - students learn actual domain management workflows
- **Quick setup** - domain registration and DNS configuration in hours
- **Low maintenance** - basic DNS record management

**Cons:**

- **Ongoing costs** - domain registration and renewal fees (~$10-15/year)
- **Ownership contention** - potential issues with domain ownership within group
- **Student dependency** - domain tied to individual student's account
- **Transfer complexity** - difficult to transfer ownership if student leaves
- **Limited governance** - no formal process for domain management decisions
- **Risk of loss** - domain could be lost if student account is compromised
- **Setup complexity** - requires domain registration and initial DNS configuration
- **Security risks** - domain tied to student account, potential for compromise
- **Limited scalability** - manual DNS management doesn't scale with infrastructure automation

### 3. Course subdomain delegation

This approach uses a subdomain delegated from one of the course's owned domains. The instructor would delegate a subdomain (e.g., `games.course.edu`) to the student team through full NS delegation and DS registration, providing them with complete DNS zone administration while maintaining institutional oversight.

**Note:** Instructor recommended approach. Provides real governance and learning about zone administration and chain of custody/trust. Balances learning value with institutional control and support.

**Pros:**

- **Excellent learning value** - zone delegation, DNS administration, trust chains
- **Real governance** - proper domain management processes and procedures
- **Chain of custody** - understanding of DNS delegation and trust relationships
- **Institutional backing** - course-supported infrastructure and support
- **No ownership issues** - clear institutional domain ownership
- **Professional practices** - enterprise-level domain management
- **SSL/TLS support** - proper certificate management with institutional backing
- **Portfolio value** - advanced DNS and domain administration skills
- **No ongoing costs** - domain and DNS management provided by course
- **User-friendly** - memorable domain names for services
- **Learning progression** - builds from basic DNS to advanced zone administration
- **Enterprise integration** - works seamlessly with infrastructure automation
- **Advanced security** - DNSSEC, proper certificate management, security policies
- **Inherited security policies** - automatically inherits DNSSEC and DMARC from parent domain

**Cons:**

- **Institutional dependency** - requires course/instructor coordination
- **Setup complexity** - initial delegation and zone configuration
- **Governance overhead** - formal processes for domain changes
- **Limited autonomy** - some decisions may require institutional approval
- **Steeper learning curve** - more advanced DNS concepts and zone administration
- **Ongoing coordination** - some changes require institutional approval
