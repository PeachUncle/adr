# Name
Project structure

## Status
Implemented

## Context
The project is facing challenges related to organizing the codebase and achieving a clear separation of data between different layers. It is important to address the following requirements:

- Prevent accidental data leaks: There is a need to enforce strict boundaries between layers to avoid unintended access to sensitive data.

- Implement an anti-corruption layer: An ACL is necessary to isolate and protect the core domain model from the influences of external agents from other layers. This layer ensures that the core domain remains independent and less likely to be deliberately or unintentionally affected by them.

- Avoid coupling between app validation logic and pure domain rules: Business validations and rules should be decoupled from application-specific logic to allow for better maintainability and flexibility. It is essential to have a clear separation between application-specific validation and the pure domain rules that govern the behavior of the business entities.

- Differentiate data representations in different layers: The project requires a clear structure that allows differentiation of different aspects and/or representations of the data associated with the business entities based on the corresponding layer. This separation of concerns enables easier maintenance, extensibility, and optimization of the system.

## Decision
It has been decided to adopt a modular project structure that adheres to the principles of DDD and CQRS. The proposed structure is as follows:


```shell
cmd/
  quanta/
    main.go                <- Entry point of the application
    
internal/
  app/
    app.go                 <- Application bootstrap and wiring
  config/
  core/
  log/
  system/
  grpc/
  http/
    cqrs-handler.go        <- HTTP request handlers
    rest-handler.go
  model/                   <- Thin business models
    model1.go
    model2.go
  service/                 <- Business services
    service1.go
    service2.go 
  event
    handlers/
      handlers1.go         <- Event handlers for updating Aggregates
    
  domain/
    model/
      entity/              <- Entities
        aggregate1.go
        entitity1.go
      vo/                  <- Value Objects
        vo1.go
      events/              <- Events related to aggregates
        event1.go
        event2.go
    service/
      service1.go          <- Domain services
      service2.go 
      
  infra/
    port/
      api/
        openapi/           <- OpenAPI
          type.go 
          api.go
    store/
        interface-r.go
        interface-w.go
        mem/
            memimpl-r.go
            memimpl-w.go
        mongo/
            mongoimpl-r.go
            mongoimpl-w.go
        pg
            pgimpl-r.go
            pgimpl-w.go
        
```

## Consequences
By adopting this project structure, several positive consequences are expected:

- Prevention of accidental data leaks: The clear separation of layers helps prevent unintended access to sensitive data by enforcing strict boundaries between them.

- Implementation of an anti-corruption layer: The project structure facilitates the implementation of an anti-corruption layer, allowing the core domain model to remain independent and isolated from external influences.

- Decoupling of app validation logic and pure domain rules: The separation of concerns between application-specific validation logic and pure domain rules enables easier maintenance, extensibility, and adaptability to changing business requirements.

- Differentiation of data representations in different layers: The proposed structure provides clear boundaries for different aspects and/or representations of data associated with the business entities, promoting better organization and maintainability.

## Date
May 28, 2023

