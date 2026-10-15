# 11. Authorisation Decision
Date: 13/11/2023
## Context and Problem Statement

What technology I will use to implement authorisation into my system (verifying what specific applications, files, or data a user has access to).

## Considered Options

* RBAC - Role based access control
* ABAC - Attribute based access control

## Decision Outcome

I considered two main solutions to authorisation for my Visa Processing System, RBAC and ABAC.

ABAC is focusing on the attributes and the several things that need to be alligned in order to access that material (clearance level, time, sensitivity, etc) which allows for a very specific and detailed approach to locking down resources which could be useful when dealing with sensitive data like this project will be doing. However, its also much more complex because of this and also takes a lot of time defining rules for each and every resource.

On the other hand RBAC focuses on the individual by assigning people to roles and based upon these roles they have access to different content the main advantage of this is the simplicity despite the security this provides to the sytem, its also fairly quick to setup. However there is the potential of having too many roles as the system expands and then this leads to several hundreds of roles to manage and decide who needs access to what with. (Okta, 2023)

In conclusion I believe that RBAC despite its potenital shortcoming is the much more straightforward and effective method of implementing authorisation for the visa processing system.

### Consequences

* RBAC provides a simple and quick way of setting up user authorisation in order to determing who has access to what within the system. 
* If a user needs access to another area of the system they can simply be assigned the role that grants this access so it makes administrative tasks much easier.

### References
Okta. (2023, September 15). RBAC vs. ABAC: Definitions & When to Use. Okta. Retrieved October 13, 2023, from https://www.okta.com/uk/identity-101/role-based-access-control-vs-attribute-based-access-control/
