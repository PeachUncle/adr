---
status: "proposed"
date: {2024-10-10}
decision-makers: {Waris Ali, David  Ani, Connor Wright}
---

# Choice of Architectural Style used for the AML

## Context and Problem Statement

What architectural style will be used to create the framework for the AML?

## Considered Options

* Desktop/Database Application
* Microservice
* Three Tier Architecture

## Decision Drivers

* Scalability, the style chosen should be suitable for a growing system
* Ease of updates, if changes need to be made to the system then the architectural style chosen should be one that makes updating the system as simple as possible
* Development Time, the style that allows the system to be developed in the shortest time frame

## Pros and Cons of the Options

### Desktop/Database Application

* Good, because this will be less vulnerable than a web app 
* Good, because this can be tailored to the AML 
* Good, most features can work without internet access
* Bad, because working with external systems (e.g. stock procurement) will require more effort
* Bad as it isn't portable and makes accessibility harder

### Microservice

* Good, as they are more scalable with new components being able to be introduced without creating downtime for others
* Good as it is easier to identify and fix faults that appear
* Good as it allows for easier development with each developer having a fixed goal
* Bad as it increases complexity of the system
* Bad as it communication considerations increase 

### Three Tier Architecture

* Good as security can be tighter, with each layer having its own defences
* Good as this style tends to be more suited for large scale databases
* Bad as it can be much more costly both to create and mantain
* Bad as it will increase development time and complexity


## Decision Outcome

Chosen option: Microservice

### Consequences

* Good because it will allow us to focus on the different areas of the system more effeciently
* Good because it will be more cost effecient than mantaining a whole monolothic system
* Good as it will be more scalable
* Bad as it may increase the overall complexity of the system

### References

* Atlassian. (n.d.). 5 Advantages of Microservices [+ Disadvantages] | Atlassian. https://www.atlassian.com/microservices/cloud-computing/advantages-of-microservices
* Qa. (2023, July 17). Advantages and disadvantages of microservices architecture. https://www.qa.com/resources/blog/microservices-architecture-challenge-advantage-drawback/ 