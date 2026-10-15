# Architecture Design Record (ADR): Onboarding Kubernetes Event-Driven Autoscaling (KEDA) to Azure Kubernetes Service (AKS)

---

## **Context**

As part of our AKS deployment, there is a need for **event-driven autoscaling** to handle workloads that are triggered by external events, such as **Azure Service Bus queues**, **Cosmos DB**, or **Azure Storage Account** events. Currently, our AKS clusters scales based on manual intervention via product teams changes replica set size for pull requests. We intend to implement scaling through **Horizontal Pod Auto-Scaling** (HPA) on resource usage metrics like CPU and memory via another ADR (0027), but this does not address dynamic scaling based on external events.

Integrating **KEDA (Kubernetes Event-driven Autoscaling)** will allow AKS to scale workloads based on events from external sources such as message queues or storage events, providing more responsive scaling. This integration requires updates to the **AKS environment**, **Helm charts**, and **Terraform configuration**.

KEDA will be introduced alongside the **HPA** enablement to provide a comprehensive, hybrid scaling solution — **event-driven** scaling with KEDA and **resource-based** scaling with HPA.

### **Proof of Concept (PoC)**:
To validate the implementation, we will first create a **Proof of Concept (PoC)** to demonstrate KEDA's ability to scale workloads based on events from **Azure Service Bus**, **Cosmos DB**, and **Azure Storage Account**. The PoC will allow us to work closely with product teams to identify reusable use cases and to understand how event-driven scaling can improve operational efficiency.

---

## **Decision**

We will onboard **KEDA** (Kubernetes Event-driven Autoscaling) to AKS to allow scaling based on event-driven triggers such as **Azure Service Bus** messages, **Cosmos DB** events, or other custom metrics. This decision involves:

1. **KEDA Installation**:  
   We will install KEDA in our AKS environment and configure it to scale workloads based on external event sources (e.g., Azure Service Bus, Cosmos DB, and Storage Accounts).

2. **Helm Chart Updates**:  
   We will update **Helm charts** to include **ScaledObject** resources, which define the scaling rules based on event sources such as message queue length or database load.
   The **Helm charts** charts we will update are:
   - xxx-api
   - xxx-background-worker
   - xxx-cron-job
   - xxx-job

3. **Proof of Concept (PoC)**:  
   A **PoC** will be developed to test the integration of KEDA with **Azure Service Bus**, **Cosmos DB**, and **Azure Storage Account**. The PoC will help verify that KEDA scales workloads correctly in response to event-driven triggers.

4. **CI/CD Integration**:  
   The changes will be automated through our **CI/CD pipelines**, ensuring that KEDA configurations are applied across all environments without manual intervention.

5. **Secure Integration**:  
   We will ensure **secure integration** with services like **Cosmos DB**, **Service Bus**, and **Storage Accounts** by using **managed identities**, **Role-Based Access Control (RBAC)**, and **Azure Active Directory (AAD)**. This will ensure that only authorised services can trigger scaling events and that sensitive data remains protected during scaling operations.

6. **Testing and Monitoring**:  
   We will thoroughly test the event-driven scaling functionality in staging environments, using **Azure Monitor** and **Prometheus** to track and verify scaling events triggered by external sources.

---

## **Consequences**

### **Positive Consequences**:

1. **Responsive Event-Driven Scaling**:  
   KEDA enables **event-driven autoscaling**, which ensures that workloads scale based on actual demand, such as the number of messages in a queue or database load. This leads to more responsive and efficient handling of real-time events.

2. **Better Resource Management**:  
   Event-driven scaling helps prevent over-provisioning of resources during idle times and ensures that resources are allocated precisely when required, optimising both performance and cost.

3. **Flexibility in Scaling**:  
   By integrating both **KEDA** and **HPA**, we provide a flexible and granular autoscaling solution. While HPA manages resource utilisation-based scaling, KEDA will handle event-based scaling, covering a broader range of use cases.

4. **PoC for Reusable Use Cases**:  
   The **PoC** will allow us to work with product teams to identify and test reusable event-driven scaling use cases, making the solution adaptable across different applications and workloads.

5. **Secure Integration**:  
   By ensuring secure integration with services like **Cosmos DB**, **Service Bus**, and **Storage Accounts**, we guarantee that only authorised workloads are scaling based on event triggers. This reduces the risk of unauthorised access to sensitive resources.

### **Negative Consequences**:

1. **Complexity in Configuration**:  
   The configuration of KEDA with event sources such as **Azure Service Bus** and **Cosmos DB** may increase the complexity of the system. Careful management of event sources and their configurations is necessary to ensure proper scaling.

2. **Dependency on External Systems**:  
   The reliance on external event sources introduces potential risks, particularly if the event source (e.g., Azure Service Bus, Cosmos DB) experiences downtime. We need to ensure that our systems are resilient to such failures.

3. **Security Considerations**:  
   We need to ensure that appropriate **IAM** roles, **RBAC**, and **managed identities** are configured for KEDA to securely interact with external event sources without exposing sensitive data.

4. **Testing Efforts**:  
   Testing the event-driven scaling for multiple event sources (Service Bus, Cosmos DB, etc.) may require additional effort and coordination with product teams to validate the various use cases and ensure proper scaling behavior.

---

## **Next Steps**:

1. **Approval of the Design**:  
   Seek approval from the Architecture Advisory Forum (AAF) to proceed with the KEDA onboarding and event-driven scaling integration.

2. **Proof of Concept (PoC) Development**:  
   Develop the PoC to demonstrate KEDA’s capability to scale workloads based on event-driven triggers from **Service Bus**, **Cosmos DB**, and **Azure Storage Accounts**.

3. **Implementation and Rollout**:  
   Install KEDA in the AKS cluster, configure **ScaledObject** resources, and update Helm charts for deployment.

4. **Testing and Validation**:  
   Conduct thorough testing in a staging environment to ensure that event-driven scaling triggers and scales workloads correctly.

5. **Secure Integration Setup**:  
   Implement secure integration with **Cosmos DB**, **Service Bus**, and **Storage Accounts**, using **managed identities**, **RBAC**, and **AAD** for access control.

6. **Monitoring and Documentation**:  
   Set up monitoring to track KEDA scaling events and update documentation for team members on how to configure and monitor event-driven scaling.
