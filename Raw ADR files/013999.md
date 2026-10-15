# How to handle PWA Privileges in conversion to Teams Pattern

## Context and Problem Statement
PWA has a list of privs that we get from Fox. In Fox a team member can have many roles and each role can have many privs. A single priv can even span multiple roles.  
We're currently converting PWA to use the Teams Pattern, which does not include the concept of privileges. As part of this conversion we must decide how best to handle these privs. We have two main options:

- Expand the Teams Pattern to include privileges.
- Eliminate standalone privileges by checking for roles instead.


## Option 1: Add Privileges to Teams Pattern Model
This approach extends the existing Teams Pattern to include privileges:
- A dedicated privileges table would be introduced, mapping privileges to roles.
- Privilege checks would be refactored to work with the team patterns data model and services.

## Option 2: Role Groups
FCS faced a similar challenge and introduced "role groups" – collections of roles that collectively represent a privilege that spans multiple roles.
With this approach, instead of checking directly for a privilege, we would check whether a user is a member of a corresponding role group.

Below is a table mapping the key privileges that span multiple roles to their equivalent roles, along with usages in main (non-test) code:

| Privilege                 | Usages in main code | Roles needed in role group                                                                                                                                                                                                                                                            |
|---------------------------|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PWA_WORKAREA              | 3                   | Any Regulator Role, Any Organisation Role, Any Application Contacts Role, Any Consultee Role                                                                                                                                                                                          |
| PWA_APPLICATION_SEARCH    | 2                   | Any Organisation Role, Any Consultee Role, Regulator: TEAM_ADMINISTRATOR, ORGANISATION_MANAGER, PWA_MANAGER, CASE_OFFICER, AS_BUILT_NOTIFICATION_ADMIN, CONSENT_VIEWER; Organisation: TEAM_ADMINISTRATOR, APPLICATION_CREATOR, APPLICATION_SUBMITTER, AS_BUILT_NOTIFICATION_SUBMITTER |
| PWA_CONSENT_SEARCH        | 2                   | Regulator: CONSENT_VIEWER; Organisation: TEAM_ADMINISTRATOR, APPLICATION_CREATOR, APPLICATION_SUBMITTER                                                                                                                                                                               |
| PWA_CONSULTEE             | 3                   | Any Consultee Role                                                                                                                                                                                                                                                                    |
| PWA_ASBUILT_WORKAREA      | 1                   | Regulator: AS_BUILT_NOTIFICATION_ADMIN; Organisation: AS_BUILT_NOTIFICATION_SUBMITTER                                                                                                                                                                                                 |
| PWA_INDUSTRY              | 3                   | Any Organisation Role, Any Application Contacts Role                                                                                                                                                                                                                                  |

The rest of privileges can be mapped to roles one-to-one, therefore we would just check for the role.

## Decision Outcome
The preferred approach is Option 2: introducing role groups. It minimises refactoring while preserving consistency within the Teams Pattern.
