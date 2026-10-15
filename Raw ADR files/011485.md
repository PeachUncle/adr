# Role Operations

* Status: PENDING
* Creator: Vitor Pereira (1191244)
* Deciders: Group
* Date: 28/03/2024

## Context and Problem Statement

Where should the role operations be kept? 
Companion object? 
Module?

## Considered Options

Option 1 - Module
```scala
trait RoleOps[Role]:
    def isPresident(role: Role): Boolean
    def isAdvisor(role: Role): Boolean

object RoleService extends RoleOps[Role]:
    def isPresident(role: Role): Boolean = role match
        case President(_) => true
        case _ => false
    def isAdvisor(role: Role): Boolean = role match
        case Advisor(_) => true
        case _ => false
```

Option 2 - Companion Object
```scala
object Role:
    def isPresident(role: Role): Boolean = role match
        case President(_) => true
        case _ => false
    def isAdvisor(role: Role): Boolean = role match
        case Advisor(_) => true
        case _ => false
```

## Pros and Cons of the Options

### Option 1 - Module

* Good, because there is a clear separation between data model and its operations/behaviours. 
* Arguably Bad, because when creating a Viva, it depends on Role Service/Ops to validate the viva. This creates a coupling between the Viva model and the Role Operations. 
  * Opposing argument: there is no problem with using operations from another "entity" in a given entity's operations. 

### Option 2

* Bad, because it couples the data model with operations/behaviours.
* Good, because it's easier to find and work with.
* Arguably Good, because when creating a Viva, it depends on Role instead of RoleService. 
    * Opposing argument: at the end of the day it does not matter because its importing operations/behaviours.

## Decision Outcome

Chosen[Vitor] option 1, because we are aiming for clear separation between data model and its operations/behaviours.

### Positive Consequences

* clear separation between data model and its operations/behaviours which is better for maintainability, testing and possible parallelization.

### Negative Consequences

* n/a
