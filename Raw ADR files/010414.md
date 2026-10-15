# ADR 008: Cloud Service Provider and Infrastructure

## Context

[This GitHub repo](https://github.com/cloudcommunity/Cloud-Free-Tier-Comparison) provides a comprehensive comparison of free tiers offered by major cloud service providers. However, how much allowance is given in the free tier should probably not be the biggest consideration, over factors such as services offered, ease of use, and long-term pricing.

[Cloud Comparison Tool](https://cloudcomparisontool.com) lists services offered by major cloud service providers.

In [this blog post series](https://itnext.io/aws-vs-azure-vs-google-cloud-for-saas-startups-part-1-ce2f1b9aa78b), dated in 2022, author Charles Chen gives his opinions after working with Azure, AWS, and GCP. He notes that all three platforms have a startup program with generous amounts of credits. The benefits and drawbacks discussed in the following section draw from this series.

### Options

#### Azure

US$200 credit for 30 days, with many services having a free tier for 12 months or forever. Some relevant Azure services:

- Azure App Service
- Container Apps
- Azure Kubernetes Service
- Azure Database for PostgreSQL
- Azure Blob Storage

Independent on cloud infrastructure, we will be using [Pronunciation Assessment in Azure Speech Services](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-pronunciation-assessment).

Benefits of Azure:

- ease of connectivity between services offered
- Azure Functions, ease of use
- best free tier
- Microsoft owns both Azure and GitHub

Drawbacks of Azure:

- best experience only comes with C# and Visual Studio

#### AWS

AWS also offers many free tiers (12 months or always) as well as trials. Relevant AWS services:

- Amazon EC2, AWS Lambda
- Amazon Elastic Container Registry
- Amazon RDS
- AWS Amplify Hosting
- Amazon S3

Benefits of AWS:

- ecosystem, better community support, and as a result better local emulation
- developer talent
- Lambda, fast cold start time
- AppSync

Drawbacks of AWS:

- lack of coherence between services offered
- traps in free tier potentially costly

#### GCP

Benefits of GCP:

- small number of really easy-to-use services, reduced complexity
- Google Kubernetes Engine, ease of use, or alternatively Google Cloud Run
- Pub/Sub, Cloud Tasks, and Cloud Scheduler

Drawbacks of GCP:

- none mentioned

## Decision

We will use Microsoft Azure as our cloud service provider, since it has the overall best balance between pricing, service quality, and ease of use, as evidenced by the blog post series and other sources online.

## Status

Accepted.

## Consequences

This decision allows us to go ahead with setting up cloud deployment.