# ADR-0023: ECS Deployment

## Status

Accepted

Date of decision: 2024 Q4

## Context and Problem Statement

With our application deployed in ECS running on Fargate, we need a way of deploying new versions/images of the
application code.

New images will be built by CI and published to ECR, but there are a few options for promoting a new image into
a deployed ECS cluster

## Considered Options

* Single 'latest' image always used
* Task definition (in infra repo) is updated with each release
* Task definition (in infra repo) is updated by application repo CI with each release
* Task definition (in application repo) is updated with each release
* Task definition is ignored by Terraform and image is updated directly by CI via the CLI
* CodeDeploy is used to deploy new images

## Decision Outcome

Task definition (in infra repo) is updated by application repo CI with each release because it allows all infrastructure
code to be kept together in one place while still allowing the task definition to be updated independently of the rest
of the infrastructure.

## Pros and Cons of the Options

### Single 'latest' image always used

In addition to publishing images with application versions, a "latest" version is published (overwritten) with each
deploy.

ECR Task Definition uses this "latest" version, and is triggered to update the service by CI pipelines.

* Good, because no infrastructure deployments need to happen for code-only releases
* Good, because it minimises deployment complexity
* Good, because there is no risk of terraform state drift
* Bad, because it prevents the enforcement of immutable application images
* Bad, because rollbacks become much harder to achieve

### Task definition (in infra repo) is updated with each release

Every time a new application version is published, the infra terraform is applied, with an updated
image value for the application Task Definition.

* Good, because it allows for immutable image enforcement in ECR
* Bad, because it couples infrastructure deployment to application deployment, nullifying the benefits
  of [ADR 18](./0018-infrastructure-repository.md)
* Good, because rollbacks are easy to achieve

### Task definition (in infra repo) is updated by application repo CI with each release

Every time a new application version is published, the CI in the application repo calls a Github action from the infra
repo to update the task definition (and only the task definition) via terraform. Combined with this, the wider
infrastructure uses the task definition as a datasource to ensure that any infrastructure-only deployment does not
change the version of the application that is deployed.

* Good, because it allows for immutable image enforcement in ECR
* Good, because it maintains the benefits of a separate infra repo described
  in [ADR 18](0018-infrastructure-repository.md)
* Good, because rollbacks are easy to achieve
* Good, because almost all of the infrastructure concerns remain together
* Neutral, because it slightly complicates the deployment of a new environment from scratch, but this can be mitigated
  with good documentation

### Task definition (in application repo) is updated with each release

Task Definition terraform code is moved to the application repo. It refers to the infra created as part of the infra
repo
(i.e. the ECR repository, and the ECS cluster)

Every time a new application version is published, the application terraform is applied, with an updated
image value for the application Task Definition.

* Good, because it allows for immutable image enforcement in ECR
* Good, because it maintains the benefits of a separate infra repo described
  in [ADR 18](0018-infrastructure-repository.md)
* Good, because rollbacks are easy to achieve
* Bad, because the terraform code for ECS becomes separated and harder to work with
* Bad, because it moves some infrastructure concerns (non-image elements of the task definition) away from the rest of
  the
  infrastructure repo)

### Task definition is ignored by Terraform and image is updated directly by CI

Task Definition is defined in terraform, but is ignored via ignore_changes. Terraform will create the task definition in
the
first instance, but will never update it.

CI pipeline will directly update the task definition's image property (e.g. via AWS CLI) to trigger deployments of new
application versions.

* Good, because it allows for immutable image enforcement in ECR
* Good, because it maintains the benefits of a separate infra repo described
  in [ADR 18](0018-infrastructure-repository.md)
* Good, because rollbacks are easy to achieve
* Bad, because terraform state drift becomes a risk
* Bad, because changing non-image properties of task definitions (e.g. CPU allocation) becomes harder to achieve

### CodeDeploy is used to deploy new images

CodeDeploy is used to deploy new images to the applications. It has support for advanced roll-out patterns such as
blue-green deployments and canary releases.

* Good, because it allows for immutable image enforcement in ECR
* Good, because it maintains the benefits of a separate infra repo described
  in [ADR 18](0018-infrastructure-repository.md)
* Good, because rollbacks are easy to achieve
* Good, because more advanced deployment patterns like blue-green deployments become easily available
* Bad, because enabling blue-green deployments will increase the service cost
* Bad, because terraform management of task definitions will still be a complex problem to solve
* Bad, because additional complexity is added (such as configuration files for CodeDeploy)
