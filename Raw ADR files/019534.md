<!-- Short descriptive title -->

# Component Library Selection (Material UI)

<!-- Date -->

_2023-12-12_

<!-- Summary -->

In order to accelerate development and avoid custom implementations of common UI
components, a component library was desired. Several alternatives were
considered, looking at component availability, compatibility, developer ease,
and a decision was made in coordination with design.

## Authors <!-- GitHub Username(s) -->

@codytodonnell @dauglyon

## Status <!-- Status of this ADR -->

Accepted

## Alternatives Considered <!-- Short list of considered alternatives, should include the chosen path -->

- [Blueprint](https://blueprintjs.com/)
- [U.S. Web Design System (USWDS)](https://designsystem.digital.gov/)
- [Material UI](https://mui.com/material-ui/)

## Decision Outcome <!-- Summary of the decision -->

Added Material UI as a dependency.

## Consequences <!-- Summary of the decision -->

MUI is added with the intent to directly import components for use across the
app. Styles can be aligned to our custom components using the MUI ThemeProvider
component.

## Pros and Cons of the Alternatives <!-- List Pros/Cons of each considered alternative -->

### [Blueprint](https://blueprintjs.com/)

- `+` React component library optimized for building complex data-dense
  interfaces
- `+` Very popular and solid documentation
- `+` Accessibility-focused
- `+` Backed by Palantir
- `+` Many components for data inputs
- `+` Good complex data-table component with many features, potentially geared
  more towards interactive spreadsheet-like tables
- `+` Lots of useful, convenient components
- `+` Styling is all handled in CSS sheets with namespaced class names for the
  blueprint component classes
- `-` Low levels of configuration (hard to match our existing styles)
- `-` No planned mobile/ small-screen support

### [U.S. Web Design System (USWDS)](https://designsystem.digital.gov/)

- `-` Not implemented as a react library or otherwise easily compatible with our
  stack.

### [Material UI](https://mui.com/material-ui/)

- `+` Preferred visual styles
- `+` Upcoming headless component support
- `+` Widely compatible
- `+` Configuration does not require additional build steps or restrict styling
  options elsewhere.
- `+` Extensive library of react components that cater well to data-intensive
  interfaces
- `+` Very popular and well-documented
- `+` Accessibility-focused
- `+` Wide range of data input and data display components
- `+` Good complex data grid component with many out of the box features
- `+` Layout components to help build common layouts quickly and consistently
  across an app
- `+` “component” prop lets you control the html element used when an MUI
  component is rendered in the DOM
- `+` “sx” prop lets you easily override styles using CSS modules instead of
  inline styles
- `+` Comes with many styles out of the box
- `-` Style configuration is in JS, not SCSS
