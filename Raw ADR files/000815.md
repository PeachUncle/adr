# 008 - Application of Value Objects for Data Consistency

**Reporter:** Rafał Karaś

## Context

The decision concerns the modeling of data in the project's entities. The key aspect is to maintain data consistency and guard against errors resulting from incorrect values.

## Considered Options

- **Option #1** - Use of primitive data types in entities.
- **Option #2** - Use of Value Objects for specific data, instead of primitive types.

## Decision

After a thorough analysis of the available options, the decision has been made to go with **Option #2**, which is the use of Value Objects for specific data, instead of primitive types, in the project's entities.

This decision is based on the following reasons:
1. **Maintaining Data Consistency:** Value Objects allow the definition of semantic types specific to the domain, increasing data consistency in entities.
2. **Protection Against Errors:** Value Objects enable validation at the type level, safeguarding against the introduction of incorrect data.
3. **Better Representation of Business Logic:** Value Objects are an excellent tool for representing business logic related to data, making the code more understandable and maintainable.

## Expected result

Adopting Value Objects for specific data in entities will allow the maintenance of data consistency, protection against errors, and better representation of business logic in the data model.

Impact on:
- **Organization:** It will facilitate the management of data consistency in the project.
- **Standardization:** It will provide a consistent approach to data modeling using Value Objects.
- **Concrete Solution:** It will improve the quality of the data model, enabling a clearer representation of business reality.

Potential negative consequences:
- The need for adaptation for individuals who have not worked with Value Objects before. However, this is not a significant problem, as the concept is straightforward and well documented.

## Links

- [Value Objects in .NET](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects)
