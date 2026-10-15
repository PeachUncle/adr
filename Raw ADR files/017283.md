# Architecture Design Record (ADR): Onboarding Horizontal Pod Autoscaling (HPA) to Azure Kubernetes Service (AKS)

---

## **Context**

The **Azure Kubernetes Service (AKS)** environment currently lacks dynamic autoscaling based on resource metrics like **CPU** and **memory**. This has resulted in inefficient use of resources, with manual intervention required for scaling. The integration of **Horizontal Pod Autoscaling (HPA)** is necessary to automatically adjust the number of pods based on these metrics, allowing for more efficient resource allocation.

In our case, HPA is needed to scale workloads based on **CPU** and **memory utilisation**. Given the need for dedicated scaling functionality, it is also necessary to create a **dedicated NodePool with taints** to ensure only specific workloads requiring autoscaling are scheduled on the new NodePool.

Additionally, HPA’s performance can be further enhanced by ensuring that **Job** and **CronJob** Kubernetes resources are properly configured to use cpu/memory request's and limit's on the resources. By setting appropriate resource requests and limits, we ensure that HPA can more accurately determine when to scale these tasks, improving both performance and efficiency.

---

## **Decision**

We will enable **Horizontal Pod Autoscaling (HPA)** in **AKS** for scaling workloads based on **CPU** and **memory** utilisation. To facilitate this, we will implement the following changes:

1. **Dedicated NodePool with Taints**:  
   We will create a dedicated **NodePool with taints** to specifically schedule pods that require autoscaling via HPA. This will ensure that workloads that need to scale based on load or resource utilisation are isolated and managed independently from other workloads.

2. **Helm Chart Updates**:  
   We will update **Helm charts** to include **HorizontalPodAutoscaler** resources for the services requiring autoscaling, specifying scaling metrics and limits.
   The **Helm charts** charts we will update are:
   - xxx-api
   - xxx-background-worker
   - xxx-cron-job
   - xxx-job

3. **Job and CronJob Resource Requests and Limits**:  
   We will update the **Job** and **CronJob** Kubernetes resources in the Helm chart templates to include appropriate **resource requests** and **limits** for **CPU** and **memory**. This is critical as HPA relies on these resource configurations to make scaling decisions. By providing these values, we ensure that HPA performs optimally, particularly when jobs or cron jobs are initiated.
   The default settings for requests and limits are as follows, but will be user configurable:
   - CPU Request: 25m
   - CPU Limit: **TBD during testing as we do not currently set this on any resources in the current templates**
   - Memory Request: 128Mi
   - Memory Limit: 512Mi

4. **CI/CD Integration**:  
   The changes will be incorporated into our **CI/CD pipelines** to automate deployment and management of HPA configurations across all environments.

5. **Monitoring and Alerting**:  
   We will ensure that **Azure Monitor** or **Dynatrace** is used to track and alert on scaling events triggered by HPA, ensuring that scaling activities are visible and issues can be flagged early.

---

## **Consequences**

### **Positive Consequences**:

1. **Improved Scalability**:  
   The introduction of HPA will enable AKS to automatically adjust to fluctuating workloads, scaling pods up or down based on CPU and memory usage. This will help to ensure optimal performance and responsiveness without manual intervention.

2. **Cost Efficiency**:  
   Dynamic scaling will lead to better resource utilisation, reducing over-provisioning and ensuring that we only use the compute resources necessary to meet demand, leading to cost savings.

3. **Operational Efficiency**:  
   By automating the scaling process, the operational burden on teams will be reduced. The system will be able to scale without needing human intervention, improving overall productivity.

4. **Dedicated Workload Isolation**:  
   The new **NodePool with taints** ensures that only specific workloads are scheduled for autoscaling. This isolation prevents other, non-scaling workloads from consuming resources on the dedicated pool.

5. **Better Performance for Jobs and CronJobs**:  
   By including resource requests and limits for **Job** and **CronJob** resources in Helm charts, we ensure that HPA can accurately scale these tasks when they are initiated, improving efficiency and scaling responsiveness.

### **Negative Consequences**:

1. **Complexity of Configuration**:  
   The addition of a dedicated **NodePool with taints** and the update of **Helm charts** may increase the complexity of the AKS configuration. The taints configuration will need to be carefully managed to avoid misallocation of workloads.

2. **Testing and Validation Efforts**:  
   While HPA is being added to existing services, proper testing and validation are required to ensure that scaling occurs correctly based on resource consumption. This might require additional testing efforts and monitoring to ensure correct scaling behavior in real-time.

3. **Security Considerations**:  
   The new configuration must ensure that the appropriate **Role-Based Access Control (RBAC)** and **managed identities** are in place to prevent unauthorized workloads from being scheduled on the autoscaling node pool.

---

## **Next Steps**:

1. **Approval of the Design**:  
   Seek approval from the Architecture Advisory Forum (AAF) for the proposed HPA implementation.

2. **Implementation and Rollout**:  
   Create the new NodePool with taints, update Helm charts, and apply the changes through Terraform and the CI/CD pipeline.

3. **Validation and Testing**:  
   Test the implementation in non-production environments, simulating varying load conditions to verify that HPA triggers scaling as expected.

4. **Monitoring and Documentation**:  
   Set up appropriate monitoring and alerting to ensure HPA is working as expected, and update documentation to provide clear guidance on how to use and manage HPA in AKS.
