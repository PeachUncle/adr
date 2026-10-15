# Title: Git and Github for source code management

## Status
Accepted

## Date
December 5, 2022

## Deciders
DevOps Committee

## Context
We have multiple software projects that we develop and maintain. These projects can involve collaboration among different teams within TTS. Contributors to our projects include developers, designers, contractors and project managers. To support these projects, we need a reliable and efficient platform for storing and managing git based projects that provides the necessary features and integrations to support our current development workflow, as well as our future directions.

## Decision Drivers
- Git is the Source Code Management (SCM) tool of choice in TTS
- Availability of features such as code review, pull requests, and CI/CD
- Ease of use and learning curve for team members
- Integration with other tools and services we use
- Support and community resources available
- Desire to not self-host our Source Code Mangement system
- Cost

## Considered Options
- Github
- Gitlab
- Bitbucket

## Decision Outcome
After discussing both Github, Gitlab and Bitbucket in various forums, and using both Gitlab and Github for extending periods of time in various parts of TTS, we have decided to use Github. Here are the main reasons behind this decision:

### Availability of features
Github offers a set of features that we require for our software projects, such as code review, pull requests, and CI/CD. While Gitlab offers similar functionality, we found that Github's implementation was a bit more polished and had a more extensive integration ecosystem that we could take advantage of in the future. Additionally, Github has a large and active community of developers that provides a wealth of resources and support.

### Ease of use and learning curve
We found that Github has a more user-friendly interface and a shallower learning curve for our team members. The tool is intuitive and easy to navigate, which helps us streamline our development workflow and reduce the learning curve for new team members.

### Integration with other tools and services
Github integrates well with a wide range of other tools and services that we use, such as CI/CD pipelines, project management tools, and documentation systems. This integration allows us to potentially automate many aspects of our development workflow.

### Support and community resources
Github has a large and active community of developers that provides a wide array of training resources and support. This community has created many plugins, integrations, and workflows that we can leverage to improve our development processes. Additionally, Github provides support and documentation resources, which should make it easy to troubleshoot issues and get help when needed.

### Cost
Currently, we have an on prem installation of Gitlab which is "free". We also have an Github Organization set up, with unlimited private repos which is also free.  With a driver of this decision being a desire to move to the cloud, and integrate with our SSO for easier onboarding, either option will likely cost more than we spend today.

While both Github and Gitlab offer free and paid plans, we found that Github's pricing model combined is more suitable for our needs. 

## Consequences
By choosing Github over Gitlab for source code storage platform, we anticipate the following consequences:

- Easier onboarding for new team members
- Integration with Tufts SSO
- Integration with other tools and services, which allows us to automate more aspects of our development workflow
- Reduced learning curve for our team members
- Access to a large and active community of developers and support resources

However, this decision may have some drawbacks, such as:

- Dependence on a single source code management platform
- A degree of lock-in to a specific ecosystem of tooling
- No viable control over the Github's development roadmap
- A long horizon of needing to continue to support the on-prem Gitlab until projects are migrated.
- Real potential for Gitlab to be a source of technical debt until we dedicate resource to migrate projects.

