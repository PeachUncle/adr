# Title Deployment Topology Decision

### Date: Sept 30, 2024

### Status: Approved

### Deciders: Clear View Engineering Team



### Context and Problem Statement:

As the Clear View engineering team, we want to deploy our containerized microservices to a cloud environment using Amazon Web Services (AWS) with a lightweight containerization approach that doesn't rely on Kubernetes

We need to determine the deployment strategy for our Clear View HR application, which utilizes a microservices architecture. This decision involves selecting the target environment, containerization technology, and orchestration tools.

### Decision Drivers:

**Cloud-native approach**: Leverage the scalability and flexibility of a cloud environment.
**Simplicity and ease of management**: Avoid the complexity of Kubernetes for this project.
**Cost-effectiveness**: Minimize infrastructure costs while maintaining performance. As a non-profit, we dont have any Datacentres to deploy and also, the Data centres are CAPEX heavy
**Containerization**: Utilize container technology for consistency and portability.

### Alternatives Considered:

- **AWS ECS with Docker**: Deploy containerized services on AWS Elastic Container Service using Docker.
- **AWS EC2 with Docker**: Deploy containerized services directly on EC2 instances using Docker.
- **AWS ECS with Podman**: Deploy containerized services on AWS Elastic Container Service using Podman.
- **AWS EC2 with Podman**: Deploy containerized services directly on EC2 instances using Podman.


### Decision Outcome:

Go with AWS EC2 with Podman.

### Rationale:

**Simplicity**: Podman offers a daemonless architecture, simplifying container management compared to Docker.
**Lightweight**: Podman aligns with our goal of avoiding the complexity of Kubernetes.
**Cost-effectiveness**: Deploying directly on EC2 provides more control over instance types and costs compared to ECS.
**AWS Integration**: EC2 integrates seamlessly with other AWS services for networking, storage, and security.

### Implications:

**Increased operational overhead**: Managing containers on EC2 requires more manual configuration and monitoring compared to ECS.
**Scalability considerations**: Scaling might require more manual intervention or the use of AWS autoscaling features.

#### Further Considerations:

**Infrastructure as Code**: Utilize tools like AWS CloudFormation or Terraform to automate infrastructure provisioning.
**Monitoring and logging**: Implement robust monitoring and logging solutions for the EC2 instances and applications.
**Security**: Configure security groups and IAM roles to secure the EC2 instances and applications.

##### Notes:

This ADR documents the decision to deploy the Clear View  application on AWS EC2 using Podman for containerization. This approach prioritizes simplicity and cost-effectiveness while leveraging the benefits of a cloud environment