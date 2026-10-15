# Use custom annotations for restricting access to endpoints

* Deciders: cwood
* Date: 19/03/2020

## Context and Problem Statement

We need to restrict access to controller endpoints (primarily app form-based ones at the moment) to those users 
who have access to the application (or other entity) that is to be shown or edited. 

Assuming a user has access to the entity we are working with, we need to be able to distinguish between user roles
and what permissions the user has for the entity in question.

## Decision Drivers

* testability (to ensure fewer bugs)
* compactness (as little boilerplate as possible)
* flexibility (usable in more than one scenario without rewriting/copying the whole thing)

## Considered Options

* Spring Security (granted authorities/roles)
* Spring Security ACL
* Spring Security Decision Voters/Managers
* Custom annotations/argument resolvers that call off to our own auth services
* Context helper/service.withDetail call similar to those used in ASF/IRS

## Decision Outcome

Use custom annotations/argument resolvers because they strike the right balance between abstraction and usability. They allow us
to make use of some of the Spring MVC features and tidy up the controllers without requiring a lot of overhead as in the case of 
Spring ACLs. 

We can access the rules we've defined on the controllers in other areas of the application code to avoid duplication and the 
pattern should work for other domains quite easily, for example case management. They can also be easily tested.

## Pros and Cons of the Options

### Spring Security (granted authorities/roles)

* Bad because it is overly simplistic and doesn't easily apply to domain objects. Roles are used to signify a role
similar to a team role, and granted authorities can be considered as specific privileges. Kind of similar to our
portal resource type model, with roles and system privs granted to users in those roles. As we would need to pair
this option with another (as the portal augments the team model with security object rules) in order to provide
domain object security, we may as well go for one option that combines everything we might want instead, as we already
have the PWA app contact model to provide the role structure. 

### Spring Security ACL

* Good, it meets the required goal of checking permissions for a user on an object
* Bad, it's heavyweight, complex, requires several additional database tables to store its information (which includes qualified
class names) and requires constant update of the Access Control Entries which define who has which permissions to access what.
This would mean whenever we update any team/contact information we would also have to update the ACLs/ACEs for relevant entities,
same when creating new ones. 

### Spring Security Decision Voters/Managers

* Good, used in conjunction with a custom authorisation service, they could meet our goal
* Bad, Spring Decision Voters are required to return an enum value (either access granted, denied or abstaining), meaning all of
the work done to identify whether or not the current user can access the object (and what privileges they have on it) is thrown
away, meaning any services that later act on the object have to re-query this information

### Custom annotations/argument resolvers that call off to our own auth services
* Good, flexible (can use class-level or method-level annotations for different purposes), easy to exclude any checks we don't 
want to make on our route
* Good, using an argument resolver reduces boilerplate in the controller methods
* Good, allows us to build an application context with common data rather than just returning a detail record 
* Bad, reliant on annotations being used on controllers and properly tested, can't set at MVC/route security level

### Context helper/service.withDetail call similar to those used in ASF/IRS
* Good, allows us to build an application context with common data rather than just returning a detail record or a yes/no authorised
answer
* Bad, clogs up controller methods with boilerplate
* Bad, can require passing lots of null parameters if we only want one of the checks, or having lots of overloaded methods