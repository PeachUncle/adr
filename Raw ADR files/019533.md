<!-- Short descriptive title -->

# Tables to be implemented using the TanStack/Table library

<!-- Date -->

_2022-11-22_

<!-- Summary -->

Table functionality, state management, and rendering can be very complex when
accounting for things like sorting, pagination, and rendering dom elements
inside cells. This ADR explains the decision to use the headless
[TanStack/table][] library in our common Table component.

## Authors <!-- GitHub Username(s) -->

@dauglyon

## Status <!-- Status of this ADR -->

Accepted

## Alternatives Considered <!-- Short list of considered alternatives, should include the chosen path -->

- Hand-roll all table state management and features as needed.
- Enterprise solution like [AG Grid][]
- Component library like [adazzle/react-data-grid][]
- Headless Component library like [TanStack/table][]

## Decision Outcome <!-- Summary of the decision -->

Chose [TanStack/table][] to be used to manage the state and complicated logic
involved in creating a custom `<Table/>` component.

## Consequences <!-- Summary of the decision -->

Adds a dependency, and requires us to manage the styling and DOM of the Table
element, but allows for a lot of flexibility in usage without much code-bloat,
and allows easily isolating third-party code to a single component if we choose
to switch underlying libraries in the future.

## Pros and Cons of the Alternatives <!-- List Pros/Cons of each considered alternative -->

### Hand-roll the Table Component

- `+` Most customizable
- `+` No new dependencies
- `-` We have to handle all the tricky bits (sorting, conditional cell
  rendering, **types**, sensible defaults, re-rendering optimization)
- `-` Significantly increased dev time
- `-` Would need significant amounts of new documentation
- `-` Likely to be overfit to current usecase

### Enterprise Solution ([AG Grid][])

- `+` Lowest dev-time option
- `+` Includes pre-made components, styles, documentation
- `+` Document Import/export is built in
- `-` Significant dependency size (39.1 MB)
- `-` Certain features (like lazy-loading records) are limited to paid versions
- `-` Difficult to customize due to the complexity of the underlying library and
  licensing

### Component Library ([adazzle/react-data-grid][])

- `+` Relatively small (682 kB), with tree-shaking for unused features
- `+` No need to build and style our own component
- `+` virtualized scroll by default on large tables
- `+` CSV/XLS/PDF import/export
- `+/-` built-in context menu
- `-` No filtering capability
- `-` Limited style and rendering options
- `-` unclear accessibility considerations
- `-` poor documentation
- `-` relatively small dev community

### Headless Component Library ([tanstack/table][])

- `+` Most popular React table library (formerly called react-table)
- `+` Super small (14 kB), with tree-shaking for unused features
- `+` Can implement and import features as-needed
- `+` Can implement features not included in the library more easily, as we
  don't relinquish control over rendering
- `+` Library provides state management and rendering helpers
- `+` Can define our own component-level api (this makes any future refactoring
  more straightforward)
- `+/-` row/col virtualization is supported but not included
- `-` Increased initial dev-time needed to build and style the component
- `-` web documentation could use some work, but is being actively improved
- `-` somewhat complicated API
- `-` no CSV/XLS import/export
- `-` As of writing, tanstack/table@latest has a conflict with storybook's
  webpack config
  ([see issue #4500](https://github.com/TanStack/table/issues/4500)), this issue
  is marked critical, in active discussion, and there are reasonable workarounds

## References <!-- List any relevant resources about the ADR, consider using footnotes as below where useful -->

- [AG Grid][]
- [adazzle/react-data-grid][]
- [tanstack/table][]

[ag grid]: https://www.ag-grid.com/
[adazzle/react-data-grid]: https://github.com/adazzle/react-data-grid
[tanstack/table]: https://github.com/TanStack/table
