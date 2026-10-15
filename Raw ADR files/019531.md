<!-- Short descriptive title -->

# Forms and Validation Libraries

<!-- Date -->

_2021-11-23_

<!-- Summary -->

The app needs a consistent pattern for handling form state and basic validation.
Several libraries exist to solve this problem, this ADR aims to identify the
best suited for our purposes.

## Authors <!-- GitHub Username(s) -->

[@dauglyon](https://github.com/dauglyon/)

## Status <!-- Status of this ADR -->

Accepted

## Alternatives Considered <!-- Short list of considered alternatives, should include the chosen path -->

- [Formik](https://formik.org/)
- [React Hook Form](https://react-hook-form.com/)
- [React Final Form](https://final-form.org/react)
- In-house

## Decision Outcome <!-- Summary of the decision -->

React Hook Form best suits our need for a flexible solution, with basic
validation built in, while also being the smallest option. It also plays well
with ARIA and working with custom inputs without requring modification of their
implementation.

## Consequences <!-- Summary of the decision -->

React Hook Form _does not work with class components_. This may create
difficulting in moving code from other (older) react codebases into the app, if
we choose to do so. Having basic validation built into the form library doesnt
require a decision on complex validation at this stage (when we are still unsure
of our needs).

## Pros and Cons of the Alternatives <!-- List Pros/Cons of each considered alternative -->

### Formik (15kB)

- `+` Popular
- `+` Wrttien in TypeScript, tsx-friendly
- `+` Basic API is concise (when using HTML elements)
- `+` Good documentation
- `?` Validation features preference validation library `Yup`
- `-` Requires a significant amount of boilerplate when using custom input
  components not designed without Formik in mind (e.g. if we used a date-picker
  component from a library)
- `-` Straightforward use of custom input components requires modifying the
  component being used in the form, rather than wrapping it
- `-` More complicated features (e.g. custom validation) require lots of
  boilerplate.
- `-` Introduces react (anti?) pattern we don't use elsewhere
  ([Function as Child Components][])

### React Hook Form (8kB)

- `+` Very straightforward **react-hooks based API**
- `+` Wrttien in TypeScript, tsx-friendly
- `+` Thorough [documentation](https://react-hook-form.com/api/useform)
- `+` **Basic validation built in**.
- `+` Supports Yup, Zod, Joi, Superstruct, Vest, and custom validation through a
  single API (with helpers for each lib).
- `+` Uses `register` pattern which is straightforward for both html input
  elements, and components that mimic their APIs (onChange, etc)
- `+` Has a `Controller` component to wrap custom input components, making
  working with custom components pretty straightforward.
- `+` Requires fewer mounts than class-component libraries
- `+` Use of uncontrolled components makes accessibility (ARIA) more
  straightforward
- `-?` Newer to the scene, smaller community, but still quite popular
- `-` **Does not work within class components**

### React Final Form (26kB)

- `+` Flexible API for any sort of input component
- `-` Even basic examples end up pretty deeply indented/nested
- `-` Not react-based, introduces non-react observing/rendering into the app
- `-` Large in size, compared to other options considered
- `-` No builtin support for validation libraries

## References <!-- List any relevant resources about the ADR, consider using footnotes as below where useful -->

- [Function as Child Components][]

[function as child components]: https://reactpatterns.js.org/docs/function-as-child-component/
