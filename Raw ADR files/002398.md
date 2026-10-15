# 7. Use ngnix gateway

Date: 2023-05-21

## Status

Accepted

## Context

In the context of designing Kwetter's architecture, we needed to select an appropriate user-facing API Gateway. We aimed
to find a solution that would efficiently handle and manage user calls to the backend services, ensuring scalability and
ease of integration.

## Decision

After careful consideration, we decided to test Kong API Gateway as a potential solution for Kwetter. We believed that
Kong's features and capabilities would align well with our requirements. However, after spending an extended amount of
time attempting to get Kong working, we encountered several challenges.

One of the main difficulties we faced was the lack of easy-to-understand tutorials or documentation. Despite the
promising features of Kong, the available resources were not sufficient to guide us through the implementation process
effectively. Additionally, we found that some of Kong's advanced features were only available as part of their premium
services, which did not align with our desire for an open-source and cost-effective solution.

Due to these challenges, we made the decision to switch to a simpler alternative for the user-facing API Gateway. We
opted to use a straightforward nginx ingress as a temporary solution. This choice allowed us to quickly set up the API
Gateway and proceed with the development process.

## Consequences

The decision to move away from Kong API Gateway and use nginx ingress instead had several consequences:

- Implementation Time: The time spent attempting to get Kong working was significant and could have been allocated to
other aspects of the project. The lack of clear tutorials or documentation slowed down the development process.

- Limited Features: By choosing nginx ingress, we have temporarily sacrificed some advanced features and functionalities
that Kong could have provided. However, we prioritized the need for a functional and easily deployable solution at this
stage of the project.

- Ongoing Evaluation: While we have settled on nginx ingress for now, we recognize that it may not be the final solution.
We will continue to explore alternative API Gateway options that better align with our requirements for scalability,
ease of use, and comprehensive documentation.

- Flexibility: The decision to switch to nginx ingress provides flexibility in the future to explore different API Gateway
solutions without being locked into one specific technology. This allows us to adapt to changing needs and leverage new
advancements in the API Gateway landscape.