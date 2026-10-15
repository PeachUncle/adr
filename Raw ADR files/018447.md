# Architectural Decision Record (ADR): Use of @tanstack/react-table

## Context

To efficiently manage and display tabular data in the application, we decided to use **@tanstack/react-table** as the primary solution for building data tables.

## Decision

**Date**: 24/03/2025

The application will use **@tanstack/react-table** for rendering tables due to the following reasons:

- **Flexible Table Structure**: Provides a powerful API for building highly customizable tables with various features.
- **Performance**: Built with performance in mind, it can handle large datasets efficiently with features like lazy loading and virtualization.
- **Headless Design**: Allows developers to create custom table components without being tied to a specific UI framework.
- **Extensibility**: Easily integrates with other libraries and supports features like sorting, filtering, and pagination.

## Implementation

### Installation

To install the library, run:

```sh
pnpm add @tanstack/react-table
```

or

```sh
yarn add @tanstack/react-table
```

### Usage

#### @tanstack/react-table Example

```tsx
import React from 'react';
import { useTable } from '@tanstack/react-table';

const data = [
  { id: 1, name: 'John Doe', age: 28 },
  { id: 2, name: 'Jane Smith', age: 34 },
  // more data...
];

const columns = [
  {
    Header: 'ID',
    accessor: 'id', // accessor is the "key" in the data
  },
  {
    Header: 'Name',
    accessor: 'name',
  },
  {
    Header: 'Age',
    accessor: 'age',
  },
];

function UserTable() {
  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable({ columns, data });

  return (
    <table {...getTableProps()}>
      <thead>
        {headerGroups.map((headerGroup) => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map((column) => (
              <th {...column.getHeaderProps()}>{column.render('Header')}</th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map((row) => {
          prepareRow(row);
          return (
            <tr {...row.getRowProps()}>
              {row.cells.map((cell) => (
                <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
```

### Best Practices

- Use **@tanstack/react-table** for building tables to take advantage of its performance and flexibility.
- Structure your data and columns effectively to utilize the features offered by the library.
- Implement pagination and sorting for better user experience, especially with larger datasets.
- Keep the table logic separate from presentation to maintain a clean architecture.

## Status

**Accepted**

## Consequences

- All future table implementations should prioritize **@tanstack/react-table**.
- Developers must adhere to best practices for building efficient and maintainable table components.
