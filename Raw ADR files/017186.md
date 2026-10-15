# 0003. Use Vite

## Date

2023-02-20

## Approved By

@danascheider

## Decision

We will use [Vite](https://vitejs.dev) as our build tool to replace Create React App.

## Glossary

- **Create React App (CRA):** A lightweight, React-based [framework](https://create-react-app.dev/) enabling React apps to be created quickly and easily
- **React:** A fully-featured [front-end JavaScript library](https://reactjs.org) enabling the use of an HTML-like syntax to create page components in isolation
- **Vite:** A lightweight framework and [build tool](https://vitejs.dev) that can replace both CRA and WebPack (a build tool on which CRA relies)

## Context

Several challenges have recently converged, pushing us to implement a full rewrite of the SIM front end. One of these was the realisation that Create React App, the lightweight framework we were using with React for the existing front end, may no longer be maintained or releasing new versions. Combined with challenges reimplementing our auth system [see context here](/docs/adrs/0001-use-firebase.md) and desire to migrate to [TypeScript](https://typescriptlang.org), a rewrite made sense. However, we still needed to choose a new framework.

[Vite](https://vitejs.dev) was the best option we were able to find.

## Considerations

We considered the following React-based frameworks in addition to Vite:

- [Next.js](https://nextjs.org)
- [Gatsby](https://gatsbyjs.com)

While each of these had certain convenient features, it was clear that they were overengineered relative to what we needed. We were looking for something that would allow us to manage most of the code in our app, providing only basic boilerplate and build utilities. These frameworks provided that but also extensive features we don't forsee needing, such as those pertaining to scalability (Next.js) when we don't except SIM to substantially scale, and those pertaining to cloud deployments (Gatsby), which are already easy with Firebase.

## Summary

Because of its fast and lightweight nature and ease of deployment to Firebase, we opted for Vite over Gatsby or Next.js.
