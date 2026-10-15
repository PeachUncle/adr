# ADR-0023: ECR Deployment

## Status

Accepted

Date of decision: 2024-12-15

## Context and Problem Statement

New application images will be published to ECR. We need to decide how many image repositories 
will exist within ECR, and where they will be hosted. 

## Considered Options

* ECR repository per-environment
* Single ECR repository in production AWS Account
* Single ECR repository in dedicated AWS Account

## Decision Outcome

ECR repository per-environment, because it allows maximal isolation of environments, 
while minimising complexity and effort. 

## Pros and Cons of the Options

### ECR Repository per-environment

Each environment (int, test, prod) will have a dedicated ECR repository, defined in Terraform.
Images will be pushed to all repositories by CI pipelines after images have been built and scanned.

* Good, because it allows complete isolation of environments
* Good, because it minimises complexity
* Good, because it minimises development effort
* Bad, because it makes it more difficult to enforce promotion of images between environments

### Single ECR Repository in production account

Only one ECR account will exist, in the production AWS account. Images will be deployed to all 
environments from this central repository

* Good, because it engenders promotion of images between environments
* Bad, because it creates additional complexity by breaking down assumptions about environment isolation
* Bad, because it creates additional complexity of cross-account IAM permissions
* Bad, because it reduces isolation of environments 
* Bad, because it slows down development, as the production account wil not exist until later in the development process 

### Single ECR Repository in dedicated AWS Account

A dedicated AWS account will be crated which hosts the ECR repository. Images will be deployed to all 
environments from this central repository

* Good, because it engenders promotion of images between environments
* Good, because it does not require access controls to production from lower environments
* Bad, because it creates additional complexity by breaking down assumptions about environment isolation
* Bad, because it creates additional complexity of cross-account IAM permissions
* Bad, because it slows down development, as the additional account may not be created before development on ECR begins 
