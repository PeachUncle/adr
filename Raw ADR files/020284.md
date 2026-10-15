# Parameter Validation

- Status: [accepted]
- Deciders: [@rocketnova, @microwavenby, @aplybeah]
- Date: [2022-12-08]

Technical Story: [PRP-51](https://wicmtdp.atlassian.net/browse/PRP-51)
~Tech Spec:~

## Context and Problem Statement

What tools should we use to parse, validate, and transform data coming into the API?

### Additional reading

The author of Zod, Colin McDonnell, wrote a [good, if biased essay](https://colinhacks.com/essays/zod) about his reasons for creating Zod against other existing options.

Former Navanaut Kat Tipton did some [some research](https://hackmd.io/BWuD10WsSS-cKHQHpS6nXw?view) that is still available as well

## Decision Drivers <!-- optional -->

- Typescript compatibility
- Validating form data from the frontend
- Transforming form data into JSON for storage

## Considered Options

- [Zod](https://zod.dev)
- [AJV](https://ajv.js.org)
- [Yup](https://github.com/jquense/yup)
- [io-ts](https://gcanti.github.io/io-ts/)
- [joi](https://joi.dev/api/?v=17.7.0)

## Decision Outcome

We're selecting **Option 1 - Zod** for this project

- Zod has excellent type inference support, and is Typescript native
- Custom validation functions (`.refine` and `.superrefine`) can create multiple issues and error codes for a field with complex validation needs
- Zod has great documentation
- `remix-validated-form` has excellent support for Zod, and provides form data validation and data parsing from one Zod schema

## Pros and Cons of the Options

### Option 1 - Zod

[Zod Documentation](https://zod.dev)

- Good, because it's Typescript native
- Good, because it does error handling
- Good, because it infers types from schema
- Good, because it is well-adopted
- Good, because it has great documentation
- Good, because validation can be chained in-line
- Good, because the helper `remix-validated-form` supports it
- Bad, because it has a proprietary schema definition
- Bad, because it has one maintainer

### Option 2 - AJV

[AJV documentation](https://ajv.js.org)

- Good, because you can use standard JSON schema / JSON types to validate data
- Good, because it has typescript support
- Good, because it validates very fast
- Bad, because adding custom validation code requires defining new keywords
- Bad, because any customization is likely outside the supported standards (like ajv-keywords)
- Bad, because there are feature and performance differences between versions of JSON schema

### Option 3 - Yup

[Yup source / documentation](https://github.com/jquense/yup)

- Good, because it has conditional schema behavior
- Good, because it supports inline custom validation
- Good, because the helper `remix-validated-form` supports it
- Bad, because it doesn't support Union or Intersections of its schemas
- Bad, because it has inferred [types that don't align with Typescript](https://github.com/DefinitelyTyped/DefinitelyTyped/issues/42360)
- Bad, because it has a proprietary schema definition

### Option 4 - io-ts

[io-ts documentation](https://gcanti.github.io/io-ts/)

- Good, because it's typescript native
- Good, if you prefer functional programming
- Bad, if you do not want to use functional programming, or mix functional and declarative
- Bad, because having optional properties is cumbersome and requires defining and intersecting two types
- Bad, because it is not easy to use

### Option 5 - joi

[Joi documentation](https://joi.dev/api/?v=17.7.0)

- Good, because it's javascript native
- Bad, because there are multiple ways to define schema (one of which needs to be `.compile`-ed)
- Bad, because the documentation is not easy to use
- Bad, because there is no built-in Typescript type inference
