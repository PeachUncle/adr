# PRP Domain Management

- Status: [accepted]
- Deciders: [@aplybeah, @rocketnova, @microwavenby]
- Date: [2022-12-10]

Technical Story: [PRP-68](https://wicmtdp.atlassian.net/browse/PRP-68)
Tech Spec: [PRP Domain Management](https://wicmtdp.atlassian.net/browse/PRP-68)

## Context and Problem Statement

This project needs at least one DNS domain to host services under

Nava generally hosts all domains externally with Vercel which means that our standard domains are not in AWS / Route53.

## Decision Drivers <!-- optional -->

- Ability for the team to access the DNS for the hosted domain
- Ability for automation of DNS changes through Infrastructure-as-Code (Terraform)
- Minimizing multiple sources of truth for valid domains and DNS

## Considered Options

- Option 1 - External DNS - Keep DNS at Vercel
- Option 2 - Internal Subdomain DNS - Create a new subdomain for PRP, hosted in AWS
- Option 3 - New Domain - Register a new domain hosted in AWS

## Decision Outcome

The team preferred Option 2, but Vercel doesn't support subdomain nameservice delegation.

The business preferred using the navapbc.com domain, so we are choosing **[Option 1](#option-1---external-dns---keep-dns-at-vercel)**

## Pros and Cons of the Options

### Option 1 - External DNS - Keep DNS at Vercel

Summary: Keep the DNS registration at Vercel, adding appropriate subdomains for PRP

#### Pros/Cons

- Good, because Vercel remains single source of truth for DNS
- Bad, because DNS management for the project lives outside of Terraform
- Bad, because manual changes to DNS need to be made in Vercel
- Bad, because verification of the domain for SSL certificate issuance is manual
- Bad, because not all engineers on the team have Vercel access

### Option 2 - Internal Subdomain DNS - Create a new subdomain for PRP, hosted in AWS

Summary: Create a new subdomain, such as wic.navapbc.com, and make AWS the authority for that subdomain

- [AWS Documentation for setting up a subdomain in Route53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingNewSubdomain.html#decide-procedure-create-subdomain)

#### Pros/Cons

- Good, because we can manage permissions for DNS in AWS, rather than sharing access to Vercel (after setup)
- Good, because domain verification can be done automatically via ACM (SSL Certificate Service in AWS) dashboard
- Good, because DNS record management for subdomain can be managed / automated with Terraform
- Bad, because Vercel has no knowledge of records below the subdomain

### Option 3 - New Domain - Register a new domain hosted in AWS

Summary: Register a new domain, such as wic-demo-project.com

- Good, because all DNS for this domain is in AWS (single source of truth)
- Good, because IAM permissions can allow AWS users to manage DNS
- Good, because DNS record management for subdomain can be managed / automated with Terraform
- Good, because domain verification can be done automatically via ACM (SSL Certificate Service in AWS) dashboard
- Bad, because this may create trust or brand issues with partners (as an unknown domainj)
