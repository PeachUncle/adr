# Http4k as REST Framework

- Status: Accepted
- Deciders: Daniel
- Date: 2023-06-11
- Technical Story: Project Setup

## Context and Problem Statement

For the development of our RESTful web services, we need to decide on an appropriate web framework. The chosen framework should support the requirements of the project and the
skillset of the team.

## Considered Options:

- Http4k
- Ktor
- Spring Boot

## Decision Drivers:

- **Usability and learning curve**: How easy is it to use the framework and start developing in it?
- **Flexibility**: The ability to customize the behavior of the framework.
- **Performance**: The runtime efficiency of the framework.
- **Community and support**: Availability of tutorials, guides, and problem-solving resources.
- **Interoperability**: The ability of the framework to interoperate with other libraries and frameworks.

## Decision Outcome:

Chosen option: "Http4k", due to its flexibility, ease of testing because of its 'server as a function' concept, and compatibility with Kotlin. Specifically:

- Http4k provides a simple and uniform way to serve, consume, and test HTTP services.
- It provides a lot of flexibility with the 'server as a function' concept which makes it easier to test.
- Http4k is a lightweight framework and does not bloate the application.
- It is pure Kotlin and fits well with our tech stack.

## Consequences:

**Positive Consequences**

- Easy to implement and test HTTP-based applications due to 'server as a function' concept.
- Better efficiency and performance with a lean and focused feature set.

**Negative Consequences**

- The learning curve for new developers might be steep.
- The Http4k community is smaller compared to other options which might lead to fewer resources and support.

## Pros and Cons of the Options:

### Http4k

- Good, because it provides strong type-safety along with the simplicity and flexibility of functional programming.
- Good, because it is lightweight and does not impose extra dependencies.
- Bad, because it's less known and thus there's a steeper learning curve.

### Ktor

- Good, because it is also purely written in Kotlin and offers coroutine support out-of-the-box.
- Good, because it provides ample features and extensibility through plugins.
- Bad, because it might overly complicate things for simple use cases.

### Spring Boot

- Good, because it comes with a host of features and excellent community support.
- Good, because it reduces boilerplate code and simplifying deployment.
- Bad, because it can be heavy for simple applications and might enforces a particular way of doing things.

## Links:

- [http4k Documentation](https://www.http4k.org/)
- [Ktor Documentation](https://ktor.io/)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
