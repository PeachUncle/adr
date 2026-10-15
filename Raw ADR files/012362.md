# ADR 0002: Use React as the UI Library (with Server and Client Components)

## Status

Accepted

## Context

We needed to select a frontend UI library for building the user interface of the Meatbag app. The goals include:

- Building a modular and composable interface using components
- Managing both static (SSR) and dynamic (client-side) content
- Using the framework best supported by Next.js and the broader ecosystem
- Supporting long-term scalability with shared UI logic and reusability
- Enabling future adoption of **React Server Components (RSC)** for performance

## Decision

We chose **React** as the UI library for Meatbag.

Since Next.js (with the App Router) defaults to **Server Components**, this allows us to:

- Compose most UI as **Server Components** (by default), improving performance and reducing client bundle size
- Opt-in to **Client Components** only where interactivity or state is needed (by adding `'use client'` at the top of the file)
- Share logic across hooks, components, and layouts with minimal overhead
- Use modern React patterns like `useEffect`, `useContext`, and `useReducer` in Client Components

This supports both **short-term MVP delivery** and **long-term architectural flexibility**.

## Consequences

- All UI will be composed from functional React components
- We will default to **Server Components** (Next.js default), and only use **Client Components** where necessary for interactivity
- Developers must be aware of the difference between server and client components in the Next.js ecosystem
- We'll follow conventions like colocating styles (`.module.css`) and using hooks for logic abstraction

## Trade-offs

- React (with Server Components) introduces new mental models for devs, especially around what code runs on the server vs. client
- Some SSR-specific or RSC patterns may require learning and careful design
- We'll need to ensure consistency between server-rendered and client-rendered content, and be mindful of when to opt-in to client-side interactivity

---

_Created: 2025-06-20_
