# Architectural Decision Record (ADR): Use of @tanstack/react-query

## Context

To efficiently manage server state and data fetching, we decided to use **@tanstack/react-query** as the primary solution for handling asynchronous data in the application.

## Decision

**Date**: 24/03/2025

The application will use **@tanstack/react-query** for data fetching and caching due to the following reasons:

- **Efficient Data Fetching**: Provides built-in caching, background updates, and request deduplication.
- **Automatic Refetching**: Keeps data fresh with automatic background refetching.
- **Optimistic Updates**: Improves UX by updating UI before server response.
- **Simplified API**: Reduces boilerplate code compared to traditional state management solutions.

## Implementation

### Installation

To install the library, run:

```sh
pnpm add @tanstack/react-query
```

or

```sh
yarn add @tanstack/react-query
```

### Usage

#### @tanstack/react-query Example

```tsx
import { useQuery } from '@tanstack/react-query';

const fetchUsers = async () => {
  const response = await fetch('https://api.example.com/users');
  return response.json();
};

function Users() {
  const { data, error, isLoading } = useQuery(['users'], fetchUsers);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error loading users</p>;

  return (
    <ul>
      {data.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Best Practices

- Use **@tanstack/react-query** to fetch and cache data before rendering components.
- Avoid unnecessary state management by leveraging **react-query’s caching** and invalidation features.
- Use **query invalidation** after mutations to keep data consistent.
- Implement **pagination and background fetching** when dealing with large datasets.

## Status

**Accepted**

## Consequences

- All future data fetching logic should prioritize **@tanstack/react-query**.
- Developers must adhere to best practices for managing server state efficiently.
