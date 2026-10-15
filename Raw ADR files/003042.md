## ADR 10: Security vs. Open Data Flow Within the VPC
### Context
We are facing the decision of choosing between a secure communication approach using HTTPS for all data flows, both external and within the Virtual Private Cloud (VPC), and an open data flow approach using HTTP within the VPC.

### Decision
We choose to implement a combination of secure and open data flows within the VPC based on specific use cases and requirements.

### Decision Rationale
+ *HTTPS for External Communication:* We plan to use HTTPS for communication from the outside world to our gateway. This ensures data security and privacy when interacting with external clients, adhering to industry best practices for securing data in transit.
+ *HTTP Within VPC:*  Within the VPC, we intend to use HTTP for service-to-service communication. This decision is driven by the need to reduce the possible overhead of SSL/TLS handshakes between multiple service calls within the VPC. It can improve the efficiency of communication within the trusted network.
+ *HTTP/2 and HTTP/3:* For service communication within the VPC, we intend to leverage HTTP/2 or HTTP/3, which offer improvements in network packet transmission efficiency. These protocols can enhance the performance of service-to-service interactions.
+ *Cloud Provider Security:* Cloud providers, by default, guarantee data security within the VPC and their managed services. This shared security model ensures the integrity and availability of data within the VPC. However, we need to complement this by implementing Identity and Access Management (IAM)-based Access Control Lists (ACLs), addressing application vulnerabilities, ensuring compliance, and establishing robust data governance practices.

### Implications
+ *Mixed Protocols:* The mixed use of HTTPS and HTTP within the VPC requires careful network configuration to ensure that sensitive data is appropriately protected while taking advantage of performance optimizations.
+ *Security Monitoring:* We must implement robust security monitoring and auditing mechanisms to detect and respond to any security threats or vulnerabilities within the VPC.

### Alternatives Considered
We considered using HTTPS exclusively for all communication, both external and within the VPC, but this could introduce potential overhead due to SSL/TLS handshakes for internal service-to-service calls.

### Decision Outcome
This decision balances security and performance considerations by adopting a mixed approach. It ensures that external communication is secured with HTTPS while optimizing internal VPC communication with HTTP/2 or HTTP/3. It also relies on the security features provided by the cloud provider while addressing specific security and compliance concerns.
