# Architectural Decision Record (ADR): Use of React Hook Form

## Context

To efficiently manage forms in the application, we decided to use **React Hook Form** as the primary solution for form handling.

## Decision

**Date**: 24/03/2025

The application will use **React Hook Form** for form handling due to the following reasons:

- **Performance**: Lightweight and optimized, it minimizes unnecessary re-rendering of components, resulting in better performance.
- **Simple API**: Provides an intuitive API that makes integration with UI components and form validation straightforward.
- **State Management**: Eliminates the need to manually manage the state of inputs, reducing code complexity.
- **Validation Integration**: Easy support for validation libraries like Yup, allowing for robust and customizable validations.

## Implementation

### Installation

To install React Hook Form, run:

```sh
pnpm add react-hook-form
```

### Usage

#### Example Form with React Hook Form

```tsx
import React from 'react';
import { useForm } from 'react-hook-form';

interface FormData {
  name: string;
  email: string;
}

function MyForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>();

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Name</label>
        <input {...register('name', { required: true })} />
        {errors.name && <span>This field is required</span>}
      </div>
      <div>
        <label>Email</label>
        <input {...register('email', { required: true })} />
        {errors.email && <span>This field is required</span>}
      </div>
      <button type='submit'>Submit</button>
    </form>
  );
}
```

### Best Practices

- Use **React Hook Form** to simplify form handling and reduce the amount of required code.
- Perform data validation directly with the methods provided by React Hook Form or use libraries like Yup for more complex validations.
- Keep form components separate and reusable to promote code maintainability and clarity.
- Leverage the state management capabilities of React Hook Form to optimize performance and avoid unnecessary re-renders.

## Status

**Accepted**

## Consequences

- All future forms within the application should prioritize the use of **React Hook Form**.
- Developers must follow best practices to ensure efficient and maintainable form handling.
