# [ADR-TECH-002] Infrastructure as Code (IaC) Tool Selection

## Context and Problem Statement
We need to select an Infrastructure as Code (IaC) tool to define, deploy, and manage our Serverless resources (Lambda, API Gateway, DynamoDB) on AWS.
The tool must support our "Serverless First" strategy and allow for reproducible environment deployments.

### Decision Drivers
* **Multi-cloud Support**: Must manage resources on AWS (Compute/Data) and Azure (Authentication).
* **Ecosystem Maturity**: Industry standard, wide module availability.
* **State Management**: Robust handling of remote state and locking.
* **Serverless Support**: Ease of packaging and deploying Lambda functions.

## Considered Options
* **AWS SAM** (Serverless Application Model) - AWS native, simple YAML.
* **AWS CDK** (Cloud Development Kit) - AWS native, imperative Python/TS.
* **Terraform** (OpenTofu) - Cloud-agnostic, declarative HCL.
* **Serverless Framework** - 3rd party tool.

## Decision Outcome
**Chosen Option**: **Terraform**

**Justification**:
While AWS SAM is excellent for pure AWS Serverless projects, our architecture explicitly depends on **Azure Entra ID** (`ADR-AUTH-002`).
Terraform allows us to define and manage both AWS and Azure resources in a single, unified codebase (Infrastructure as Code).
1.  **Unified Workflow**: `terraform apply` manages the entire stack (IdP config + AWS Compute).
2.  **Maturity**: Extensive providers for both AWS and Azure.
3.  **Python Support**: Although Terraform uses HCL, we can use `terraform-aws-modules/lambda` to handle Python dependency packaging elegantly.

### Positive Consequences
* **Single Source of Truth**: IAM, Database, and Identity Provider (Azure) all in one place.
* **Vendor Agnostic Core**: Familiar syntax and workflow regardless of cloud provider.
* **State Management**: Robust state locking via S3/DynamoDBBackend.

### Negative Consequences
* **Lambda Developer Experience**: "Local invoke" is not as native as SAM. (Mitigation: Use SAM CLI with Terraform hook or Unit Tests).
* **Boilerplate**: HCL can be more verbose than SAM for simple functions.
