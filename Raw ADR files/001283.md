# Architectural software style

* Status: accepted
* Deciders: Jaime Ochoa de Alda Cerdan and Alejandro Garcia Prada
* Date: 2025-10-25

## Context and Problem Statement

The company needs a platform to manage purchasing processes, including customer management, orders, delivery routes, statistics, incidents, and payments via Stripe. The system must be scalable, secure, and capable of integrating with external services through HTTP.

## Decision Drivers

* RF-01 CRUD de datos personales
* RF-04 Actualizar estado del pedido
* RF-07 Comunicarse con servicio externo para datos de tráfico
* RF-10 Conectarse con la pasarela de pago

## Considered Options

* 0001-1-MVC
* 0001-2-3-tier-client-server-architecture
* 0001-3-RESTful-client-server-architecture

## Decision Outcome

Chosen option:  "0001-2-3-tier-client-server-architecture", because it's the decision that suits better with the most critical modules of the system: 
* The Client module (due to the handling of personal information)
* The Orders module (which requires the server to maintain state between the different processing phases)
* The Delivery and Routing module (because of its optimization algorithms and dependency on real-time logistics data)
* The Payments module (which integrates payments via Stripe and involves sensitive financial transactions).

### Positive Consequences

* Benefits asynchronous calls such as the ones made when needed real-time information.
* Ensures consistency and reliability across multi-phase operations, since the business layer can persist and recover state information if a transaction fails or needs to resume.
* Enhances security and data protection, since sensitive operations and data are isolated in the business and data layers.
* Supports load balancing and fault tolerance, since services in each tier can be distributed across multiple servers.


### Negative Consequences

* Increased latency due to multiple network hops between layers (client -> business logic -> data)
* State synchronization challenges, especially when horizontal scaling or load balancing the business logic layer that maintains partial state.


## Pros and Cons of the Options

### 0001-1-MVC

The MVC model (Model–View–Controller) is a way to organize the system in three parts:

* Model: Handles the data and business logic.
* View: Displays the information to the user.
* Controller: Connects the Model and View, managing user input and updating the View as needed.

More info: https://developer.mozilla.org/es/docs/Glossary/MVC

* Good, because it's very simple and has been used largely
* Good, because of clear responsibility separation
* Bad, because of limited scalability
* Bad, because of the difficulties integrating asynchronous processes

## 0001-2-3-tier-client-server-architecture

The three-tier client-server architecture is an extension of the traditional client-server model in which the system is organized into three distinct layers: presentation, business logic, and data.

* Presentation layer (Client): This layer handles user interaction and displays information. Clients can be web browsers, mobile apps, or desktop applications that request services from the server.

Business logic layer (Server): This layer processes requests, enforces rules, manages workflows, and maintains the state of complex operations such as orders, statistics, deliveries, incidents and payments. It acts as an intermediary between the presentation and data layers.

* Data layer (Database): Responsible for storing, retrieving, and managing persistent data. It is typically accessed exclusively by the business logic layer, ensuring data integrity and security.

More info: https://stackify.com/n-tier-architecture/

* Good, because it ensures sensitive data never reaches the client and maintains a higher level of security, such as the secret key for Stripe's API.
* Good, because of the separation between the client and the server which is essential for using Stripe. This is because Stripe strongly recommends all critical processes be made in the server-side of the application.
* Good, because client and server components can be scaled independently across multiple machines or instances to handle increased load efficiently.
* Bad, because The central server must handle all client requests, requiring proper load balancing and scaling resources
* Bad, because the performance depends heavily on the speed and stability of the network connection between client and server.
* Bad, because the centralized server can become overwhelmed with too many simultaneous requests, limiting scalability.

## 0001-3-RESTful-client-server-architecture

The RESTful client-server architecture is a distributed system design in which clients and servers communicate over standardized protocols (typically HTTP/HTTPS) using stateless requests. Clients request resources or services, and servers respond with representations of those resources, often in JSON or XML format.

More info: https://restfulapi.net/

* Good, because stateless communication allows high scalability, as servers do not need to track client sessions.
* Good, because it simplifies integration for multiple client types (web, mobile, third-party services).
* Bad, because transactional workflows require additional state management, such as tokens, databases, or orchestration services.
* Bad, because performance depends on network latency, as each request is independent.
* Bad, because handling delivery and routes is more complex, since the server is stateless.

