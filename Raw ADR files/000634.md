# Making a decision on the key design patterns for the CMS

## Context and Problem Statement

The Complaint Management System (CMS) will need to support multiple large tenants from different industries such as banking and telecom and will need to integrate with external service such as emailing and messaging providers, while remaining maintainable as features and the system grows. The CMS will need to have clear seperation of concerns, with consistent creation of domain objects, including cross cutting type behaviour (e.g. logging & retries) without actually modifying the core logic of the system. The design will need to make testing easy and keep the service adaptable for future additions such as a Chatbot.

## Considered Options

* **Factory Method**
* **Abstract Factory**
* **Builder**
* **Adapter & Decorator**


## Decision Outcome

Chosen option: ***"Factory Method, Adapter, and Decorator"***, because these patterns collectively work together to make the code more modular, maintainable and flexible within the Complaint Service. The Factory Method was chosen to make a standardised way of creating Complaint objects, which will ensure that they are always instantiated in a valid state with all the proper fields, also keeping the logic out of the controller itself. 

The Adaptor was picked ti abstract away external dependencies such as emails, which will provide a clean interface (IEmailSender) that will allow the CMS to modularly integrate with different service providers (e.g. different external email service providers) without needing to make any significant code changes in the domain or application layers.

Finally, I chose the Decorator pattern to handle things such logging and retries, for the adapter and repository layers. This should allow me to dynamically add behaviour without altering existing classes or duplicating code. An example for this use would be handling logging and retries for the email sender.

### Consequences

* Good, because the Factory Method will enforce consistency and prevent invalid objects from being created. This should improve integrity and add seperation of concerns (e.g. Complaints Controller)

* Good, because the Adapter pattern will ensure that future integration with new communication services (e.g. Chatbot) will require less refactoring of core components.

* Good, because the Decorator will allow for better seperation of concerns, which should overall improve maintainability.

* Good, because using these three patterns together should support what is being asked for within the case study. Alongside the SOA architecture, these patterns should improve the systems extensibility and maintainability, which should overall lead to a well made system that is scalable and future proofed from the suggested future improvements for the system.

* Bad, because adding these patterns will add extra layers of abstractions and classes, meaning the system will become more complex and slow down future new developers learning the system.

* Bad, because if the Decorator pattern is used incorrectly, this will likely slow down and make testing more of a pain as loads of chains of Decorators could be hard to trace and debug for different requests. This could lower the overall quality of the system if not implemented correctly.
