# Error Handling by using Result4K

- Status: Accepted
- Deciders: [List everyone involved in the decision]
- Date: [YYYY-MM-DD e.g., 2023-01-01]
- Technical Story: [Description or ticket/issue URL]

## Context and Problem Statement

In our software development process, it is necessary to decide on how to handle errors. How should our program communicate failure situations?

## Considered Options:

- Using nulls
- Throwing exceptions
- Returning result objects with the help of Result4K library

## Decision Outcome:

Chosen option: "Returning result objects with the help of Result4K library", because it enforces explicit error handling and reduces the possibilities of unhandled exceptions,
thereby improving the overall robustness of our software product.

## Consequences:

**Positive Consequences**

- Makes error handling explicit, reducing the chances of unhandled failure cases.
- Coding to interfaces becomes easier with the use of Result4K as it uses sealed classes.
- Better maintains the flow of the program compared to throwing exceptions which are disruptive.

**Negative Consequences**

- Using Result4K result objects might introduce a slightly higher complexity in the codebase.
- Developers might require time to adapt to this non-traditional way of handling errors.

## Pros and Cons of the Options:

### Using nulls

- Good, because it's the simplest form of error indication.
- Good, because it's easy to check whether a value is null or not.
- Bad, because it may lead to NullPointer exceptions if not handled properly.

### Throwing exceptions

- Good, because exceptions provide detailed error information.
- Good, because it aborts the current operation as soon as any error occurs.
- Bad, because unhandled exceptions can cause the program to crash.

### Returning result objects (Result4K)

- Good, because it makes error handling explicit and forces the developer to deal with it.
- Good, because it provides a safer way to handle errors and allows for more control over the flow of the program.
- Bad, because it involves a higher level of complexity compared to nulls and exceptions.

## Links:

- [Result4K Library](https://github.com/npryce/result4k)
- [Exception Handling: Best Practices and Guidelines](https://www.oreilly.com/library/view/java-9-best/9781484225917/A457540_1_En_2_Chapter.html)
