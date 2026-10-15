# 0004. Use TypeScript

## Date

2023-02-20

## Approved By

@danascheider

## Decision

We will use [TypeScript](https://typescriptlang.org) instead of ES6 JavaScript to build the next generation front end.

## Glossary

- **Static Typing:** A feature of (primarily) object-oriented languages where objects are assigned a type - the most basic examples being `string` or `number` - and functions expect arguments and return values of a defined type; this prevents numerous unexpected runtime errors
- **TypeScript:** A language, actually a superset of JavaScript syntax and functionality, that imposes static typing in development and compiles to JavaScript that can be run in the browser; TypeScript includes type checking in development environments as well as an optional compiler (other tools may also be used for compilation) to translate to JavaScript

## Context

We've had an open epic to migrate to TypeScript for a long time. While there is an established way to port a JavaScript code base to TypeScript, the process can be onerous and take time to see benefits. Now that we're doing a full rewrite, it makes more sense to introduce TypeScript from the beginning. The primary disadvantages to TypeScript are (1) the possibility for poorly organised projects to make finding type definitions difficult and (2) difficulty of integrating with third-party tools that don't provide types.

As TypeScript is becoming a standard in front-end development, more and more packages are providing TypeScript support. Most major projects, including React, Vite, Testing Library, and Storybook already provide out-of-the-box support for TypeScript.

Effectively, the decision to eventually use TypeScript for these reasons was made a long time ago.

## Considerations

Although, as mentioned above, the decision to use TypeScript had already been made in the past, we did consider whether now would be the right time to add it given we were already considering whether to use [Firebase](/docs/adrs/0001-use-firebase.md), another [React framework](/docs/adrs/0003-use-vite.md), and even a [library other than React](/docs/adrs/0002-use-react.md). Each of these would potentially involve a learning curve. Likewise, as our lead maintainer was not at all proficient in TypeScript, it would take a concerted effort to not only learn the language but also piece it all together.

Ultimately, we decided the upfront learning curve was worth it to reduce the amount of work we'd have to do later to port an existing JavaScript project to TypeScript. Doing it this way, we can start off with strict compiler options that enable TypeScript to be the most useful.

## Summary

Primarily because of the ease of adding TypeScript to a new project relative to porting over a project using plain JavaScript, it made sense to start off our frontend rewrite using TypeScript with all the configuration options we would ultimately want.
