# Authentication

- Status: [accepted]
- Deciders: [@aplybeah, @rocketnova, @microwavenby]
- Date: [2023-03-01]

Technical Story: [PRP-67](https://wicmtdp.atlassian.net/browse/PRP-67), [PRP-176](https://wicmtdp.atlassian.net/browse/PRP-176)

Tech Spec: [Authentication](https://navasage.atlassian.net/wiki/spaces/MWDP/pages/561021069/Tech+Spec+Authentication)

## Context and Problem Statement

The PRP site needs some form of authentication for service of documents and recertification information to WIC staff during the course of the demonstration.

What authentication solution should we use for PRP?

## Decision Drivers

- Serve under 100 users with accounts
- Single role for administrators
- OpenID Connect Provider
- **NO** Single Sign-on / Federation
- **NO** User profile data
- **NO** Multi-factor Authentication

## Considered Options

- Remix In-app authentication
- AWS Cognito
- Auth0
- SuperTokens

## Decision Outcome

Due to new decision drivers (We now need an OpenID Connect Provider), the team has updated this decision to utilize **[Option 2](#option-2---aws-cognito)** AWS Cognito for the following reasons:

- Good, because Cognito is in our AWS private cloud and is FedRAMP and SOC 2 compliant, so we don’t need to alter our security/compliance plan
- Good, because we don’t need to deploy or self-host another tool
- Good, because it can function as an OpenID Connect Provider, which is required to integrate with Lowdefy
- Good, because it will be free for the number of users we anticipate for the pilot

Although we previously preferred **[Option 4](#option-4---supertokens)** over the rest as a second choice, SuperTokens is unfortunately not an OpenID Connect Provider.

## Pros and Cons of the Options

### Option 1 - Internal Session-based Authentication

Utilizing remix-auth or the appropriate package and tooling for the selected platform

- Use session-based authentication, storing the session in an encrypted browser cookie
- Use email + password based logins, stored in the platform’s Postgres database

#### Pros/Cons

- Good, because this solution requires no procurement
- Good, because there are no integrations required
- Good, because there are no additional costs above platform hosting (database and app servers)
- Bad, because there are limited features included (without additional development)
- Bad, because there is limited higher security functionality (ID Proofing, MFA, etc)
- Bad, because users need to be manually provisioned (to ensure only WIC staff have access)

### Option 2 - AWS Cognito

Utilize AWS Cognito to provide authenticated sessions for a single authorized role

#### Pros/Cons

- Good, because we expect to require no user profile data
- Good, because having a single role without grants means bearing a valid JWT can mean access to the portal
- Good, because there is a simple UI to manage user accounts
- Good, because the team has experience building Cognito-backed software
- Good, because it is inexpensive and can scale
- Good, because Cognito is an OpenID Connect Provider
- Bad, because it has limited MFA functionality and flexibility
- Bad, because more robust user flows require custom server-side code / development
- Bad, because we also have experience with the limitations of Cognito
- Bad, because role functionality does not exist without custom development
- Bad, because user profile storage is fixed at the Cognito pool creation (adding or changing fields for a user requires deployment of a new Cognito pool and migrating all of its existing users)

### Option 3 - Auth0

Auth0 is an industry leader in authentication solutions

The platform is free to use for up to 7000 users

#### Pros/Cons

- Good, because Auth0 is an industry leader in auth
- Good, because Auth0 is free for under 7000 users
- Good, because Auth0 has a user management dashboard
- Good, because other teammates at Nava have experience
- Good, because Auth0 is an OpenID Connect Provider
- Bad, because this team has no Auth0 experience
- Bad, because there is no open source / self-hosted option
- Bad, because larger scale gets expensive quickly
- Bad, because it is not FedRAMP certified at this time

### Option 4 - SuperTokens

Use SuperTokens to provide sessions, and desired features

SuperTokens has customizeable user login flow, including passwordless, social logins, MFA and more

#### Pros/Cons

- Good, because SuperTokens has flexible, pre-made “recipes” for auth flows
- Good, because SuperTokens is free for 5000 users hosted in the cloud
- Good, because SuperTokens can be self-hosted
- Good, because SuperTokens has a pre-built frontend for UI
- Good, because SuperTokens has great React documentation
- Good, because SuperTokens is open source
- Bad, because the team has no experience with SuperTokens
- Bad, because SuperTokens is a newcomer to the industry
- Bad, because SuperTokens is not an OpenID Connect Provider
