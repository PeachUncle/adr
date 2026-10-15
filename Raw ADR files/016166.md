# Use Layered Architecture

## Context
In order to facilitate effective development, applications need to be built with an architectural structure that defines 
component roles, responsibilities and modular boundaries. The chosen structural style should fit the needs of the particular application and the value it provides while enabling code legibility and making the application as easy to navigate as possible.  

## Decision
For the Slot Manager Service we will use a Layered Architectural Style. There are many ways to express this style, but we will express it by defining the following three layers:
- Web Layer
- Service Layer
- Data Layer

The Web Layer (sometimes referred to as the Presentation Layer) will contain components that provide access to the application from external sources. The Web Layer will contain REST APIs, User Interfaces and Event Producers and Consumers as necessary. The Web Layer should be as thin as possible, containing no more than access logic, validation logic and conversion or presentation logic.  

The Service Layer (sometimes referred to as the Application Layer) will contain components that provide capabilities to components in the Web Layer. The Service Layer should be agnostic of the interfaces used to access the application. In other words, the Service Layer should not be aware of REST APIs or User Interfaces (though it can be aware of things like User Roles and User Scenarios). Components in the Service Layer cannot depend on components in the Web Layer. Components in the Service Layer access components in the Data Layer and perform operations on them as well as operation between them. The Service Layer should be as thin as possible.

The Data Layer will contain components that access and operate on data stored in the database. The Data Layer should be agnostic of the Service Layer and Web Layer. The Data Layer cannot depend on either one. Entities and other Domain Objects in the Data Layer should contain both state and behavior. In other words, they should contain Business Logic when that logic is owned by the particular Entity, Domain Object or Aggregate and there are no dependencies outside those boundaries. Otherwise, there is risk of implementing that logic in the Service Layer and that leads to what is known as an Anemic Domain Model. 

The Layers will be represented in the application as packages. 
- `com.zoomcare.slots.web`
- `com.zoomcare.slots.service`
- `com.zoomcare.slots.data`

## Rationale
- Layered architecture is a well known, conventional pattern. The majority of Java developers will likely have experience with it, so getting to know the application will require a smaller learning curve. 
- Layered architecture is simple. The rules regarding dependencies and separation of concerns is easy to follow, adding little to no cognitive load. 
- Layered architecture provides structural guidelines that help manage scope and complexity while making the code easier to read and navigate, providing boundaries that guide overall design by encouraging certain kinds of encapsulation.
- Layered architecture decouples the application logic from the APIs that provide access to it from the outside, making the application more flexible and adaptable to external demands.
- Using the name 'Web Layer' is conventional and consistent with the vocabulary used by the Spring Framework.
- Using the name 'Service Layer' is conventional.
- Using the name 'Data Layer' is conventional and consistent with the vocabulary used by the Spring Framework.

## Status
**Accepted**

## Consequences
- Developers can proceed with their work using established and familiar patterns that enable rather than obstruct their efforts.
- Developers can spend less time and effort making sense of how things are put together while investing more effort in the value their work provides. 
- The application becomes more flexible because of the decoupling and isolation between components and their well-defined roles and responsibilities. 

However...
- Architects Mark Richardson and Neal Ford say that Layered Architecture is a technically partitioned architecture as opposed to a domain partitioned architecture. So, Layered Architecture "a domain-driven design does not work as well with the layered architectural style.". While it is true that Layered Architecture is technically partitioned, domain modules can still be implemented within each layer and much of domain-driven design can still be observed. Furthermore, by organizing things in that manner, we are enforcing every domain module to adere to the same standards, which in turn makes them more consistent and that makes things easier to comprehend because it reduces the effects of context-switching.
