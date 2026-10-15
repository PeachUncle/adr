<!-- Short descriptive title -->

# UI Refresh General Architecture

<!-- Date -->

*2021-10-19*

<!-- Summary -->

The new UI refresh needed basic decisions around infrastructure.
Typescript/React was the framework desired. State management was also
discussed; Redux was chosen due to its focus on app-level state, and its
popularity. This ADR covers the architectural decisions made to support those
frameworks.

## Authors <!-- GitHub Username(s) -->

[@dauglyon](https://github.com/dauglyon)

## Status <!-- Status of this ADR -->

Accepted

## Alternatives Considered <!-- Short list of considered alternatives, should include the chosen path -->

- Create React App (CRA)
- Manual React Setup
- Other react bootstrapping solutions

## Decision Outcome <!-- Summary of the decision -->

Create React App (CRA) was chosen to bootstrap the repo. The typescript
template will be used, and redux added post-hoc.

## Consequences <!-- Summary of the decision -->

Using CRA allows fast initial setup, but adds some "magic" to the repo. We felt
this was a good trade-off for initial development. CRA also offers `eject`[^1]
which allows for it to be removed as a dependency (though doing so also removes
many of its benefits, such as not maintaining the webpack config). There is
also a large dev community for CRA.

## Pros and Cons of the Alternatives <!-- List Pros/Cons of each considered alternative -->

### Create React App (CRA)

- `+` Fast and easy setup
- `+` Large dev community, with existing tools and documentation
- `+` Low flexibility (allows us to focus more on development over bikeshedding)
- `-` Low flexibility (if we run into a unique react issue we need to solve, we
      may need to `eject`[^1])

### Manual React Setup

- `+` Almost completely customizable
- `-` Complicated configurations and decisions around bundling, css loading,
      etc. Best practices unclear.
- `-` Would be KBase-specific, and perhaps even repo-specific, adding to
      required onboarding.

### Other react app-bootstrapping solutions

- `+` Some, such as Snowpack, have faster and/or more intuitive setup
- `-` Smaller dev community
- `-` may not have long-term viability

## References <!-- List any relevant resources about the ADR, consider using footnotes as below where useful -->

- [CRA](https://create-react-app.dev/)
- ["What Does Create-React-App Actually Do?" - Andrew Mc](https://levelup.gitconnected.com/what-does-create-react-app-actually-do-73c899443d61)
- ["In search of CRA alternatives" - bobae kang](https://bobaekang.com/blog/in-search-of-cra-alternatives/)
- ["Don’t eject your Create React App" - Adam Laycock](https://medium.com/curated-by-versett/dont-eject-your-create-react-app-b123c5247741)
[^1]: [CRA Eject](https://create-react-app.dev/docs/available-scripts/#npm-run-eject)
