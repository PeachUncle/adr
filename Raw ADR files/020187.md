# ADR 004: GraphQL Schema Design

## Status

Accepted

## Context

In this project, GraphQL is used as the API layer to manage data between microservices and the front-end. The schema design plays a key role in ensuring the API remains flexible, maintainable, and easy to extend over time. Since this repository serves as a reference for best practices, we aim to establish guidelines that promote clear, efficient, and scalable GraphQL usage.

This ADR outlines the best practices we’ll follow for GraphQL schema design, ensuring both clients and servers operate in sync, and focusing on business-driven requirements.

## Decision

### 1. **Schema-First Approach with Centralized Design**

We will adopt a **schema-first approach** where the schema is the primary source of truth for both the server and client. The schema will be centrally designed and maintained to ensure consistency across the entire project.

- **No Code Generation via Introspection**: We will not rely on introspection-based code generation for the client. Both the client and server will generate code directly from the schema. This ensures that the API contract is explicit and does not depend on runtime introspection, minimizing discrepancies and ensuring full control over the schema.

- This centralized schema design will prevent drift between what the server expects and what the client consumes.

### 2. **Principle of Least Privilege: Business-Driven Fields**

We will expose only the fields that are **necessary for business purposes**. This extends beyond security considerations and includes minimizing unnecessary data exposure to reduce cognitive load and complexity for consumers.

For instance:
- If the business case only requires a movie’s title and release date, we will not expose other fields like budget or director, even if they are available in the database.

This tight focus ensures that the API is streamlined, avoids over-fetching, and remains aligned with business goals.

### 3. **Pagination with Connections**

We will use the **Connection** pattern for all fields that return lists of data, following Relay-style pagination. This ensures that the API can efficiently handle large datasets and allows clients to navigate data incrementally.

Example:
```graphql
type MovieConnection {
  edges: [MovieEdge]
  pageInfo: PageInfo
}

type MovieEdge {
  node: Movie
  cursor: String
}

type PageInfo {
  hasNextPage: Boolean
  hasPreviousPage: Boolean
}
```
Connections help avoid over-fetching and ensure that clients have an easy way to paginate through large datasets.

### 4. **Generalized Queries with Filters and Selectors**

We will avoid creating single-purpose queries. Instead, we will expose generalized queries that accept **filters and selectors** to retrieve specific data based on client requirements.

For example, instead of creating separate queries like `getTopMovies` or `getMoviesByGenre`, we will provide a single `movies` query that accepts filters:
```graphql
type Query {
  movies(filter: MovieFilter, sortBy: MovieSort, pagination: PaginationInput): MovieConnection
}
```
- **Filters**: Allow clients to request subsets of data, such as movies from a specific genre or within a date range.
- **Selectors**: Support sorting by fields like popularity, release date, or alphabetical order.

This approach ensures the API remains flexible while preventing query overload and minimizing redundancy in the schema.

### 5. **Mutations Return Acted-Upon Entities**

All mutations will return the entities they acted upon, providing immediate feedback to the client and reducing the need for follow-up queries. This enables a more efficient interaction model where the client gets all necessary data directly from the mutation response.

For example:
```graphql
mutation {
  createReview(input: ReviewInput) {
    id
    movie {
      id
      title
    }
    rating
    comment
  }
}
```
By returning the entity that was created or updated, we ensure the client has immediate access to the relevant data without needing to issue additional queries.

### 6. **Error Handling Using Error Union Lists and Interfaces (Stage 6a)**

Following **Marc-André Giroux’s "Stage 6a" approach** to error handling, we will represent errors using **error union types** combined with an interface for standardization. This method allows both successful results and errors to be returned as part of the same response, offering flexibility and clarity to the client.

Each mutation or query will return either the desired result or an error type, allowing for structured error handling on the client side. For example:
```graphql
union CreateReviewResult = Review | CreateReviewError

interface Error {
  code: String!
  message: String!
}

type CreateReviewError implements Error {
  code: String!
  message: String!
  field: String
}

mutation {
  createReview(input: ReviewInput): CreateReviewResult
}
```
This approach allows clients to handle errors in a consistent manner while getting structured responses. Errors will contain a `code` and `message` to aid in debugging and handling (e.g., validation errors, authorization issues).

By using union types for error handling, the client always receives predictable data structures and can react appropriately to both success and failure scenarios.

### 7. **Input Types for Mutations**

Wherever possible, we will encapsulate mutation arguments using **input types**. This simplifies mutation signatures and provides flexibility for extending or modifying arguments in the future.

For example:
```graphql
input ReviewInput {
  movieId: ID!
  rating: Int!
  comment: String!
}

mutation {
  createReview(input: ReviewInput): Review
}
```
Using input types improves code maintainability and allows for easier modifications to the mutation without breaking the schema.

## Consequences

- **Positive**:
	- A clear and business-driven schema will result in a more streamlined API that is aligned with actual needs and easier to consume.
	- Error handling with union types and interfaces allows for consistent, flexible error reporting that scales well with different types of failures.
	- Pagination with connections and generalized queries provides flexibility without cluttering the schema with specific-use queries.
	- Returning acted-upon entities from mutations simplifies client logic and improves efficiency.

- **Negative**:
	- Strictly adhering to these practices will require additional development effort upfront, particularly in setting up the schema, error handling, and batching.
	- Developers will need to familiarize themselves with the error handling approach, which may have a learning curve.
