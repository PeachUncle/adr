### ADR 02: Service-Based Architecture selected for ClearView

- **Title**: Service-Based Architecture selected
- **Status**: Accepted
- **Context**:  
  As ClearView’s system is designed to reduce bias in candidate selection through anonymized matching of CVs to job advertisements, the chosen architecture must support key priorities such as scalability, fault-tolerance, cost-efficiency, and evolvability. Based on these characteristics, we have decided to use a **Service-Based Architecture (SBA)** rather than a monolithic or microservices architecture. SBA is a middle ground between a monolith and microservices, where we separate the system into logical services that can evolve and scale independently.

- **Decision**:  
  The **Service-Based Architecture** was selected for ClearView to balance key priorities, specifically:
  1. **Cost**: SBA allows the system to scale at a lower operational cost compared to a fully microservices-based architecture, which can be resource-intensive due to the large number of independently deployable services.
  2. **Fault-Tolerance**: Services are logically separated, so failures in one service (e.g., skill matching, resume parsing) won’t take down the entire system. This aligns with the fault-tolerance requirement.
  3. **Scalability**: While not as granular as a microservices architecture, SBA still enables scalability for critical services that need to grow independently (e.g., candidate and employer services). It provides enough flexibility to scale key services without the overhead of managing dozens of microservices.
  4. **Evolvability**: SBA strikes a balance between simplicity and evolvability. Each service can evolve independently, allowing the system to adapt to future changes in business needs or requirements.

- **Consequences**:
  - **Positive**:
    - **Cost-Efficient**: Service-based architecture is less costly to implement and maintain than microservices while still providing a modular structure for independent scaling.
    - **Improved Fault-Tolerance**: Logical separation of services ensures that individual service failures do not affect the entire system, improving overall reliability.
    - **Modularity and Maintainability**: Services are decoupled, which allows ClearView to develop, maintain, and deploy different parts of the system separately, improving flexibility and evolvability over time.
    - **Scalability**: SBA provides sufficient scalability for the anticipated system load, allowing critical services to scale without introducing the operational overhead of a full microservices architecture.

  - **Negative**:
    - **Increased Complexity**: The introduction of multiple services leads to increased complexity in terms of service orchestration, monitoring, and managing inter-service communication. Unlike monolithic architectures, service-based architectures require more sophisticated DevOps practices.
    - **Operational Overhead**: Managing services independently adds some operational overhead, requiring careful orchestration, especially in deployments, logging, and error handling.
    - **Reduced Scalability Compared to Microservices**: While SBA provides good scalability for ClearView’s expected scale, it is less flexible than a full microservices or event-driven architecture, which allows for even finer-grained scaling and resiliency. This trade-off is acceptable for now, given the lower expected traffic and emphasis on cost control.
    - **Potential Limitations in Future Evolvability**: If ClearView grows faster than expected, transitioning from a service-based to a full microservices architecture might introduce additional complexity and refactoring.