# 17. Package Bundling Strategy

Date: 2021-06-25

## Status

Accepted

## Context

The JS bundle that our end-users download typically contains more than what they need. To optimise this, the
conversation-components and sunco-js-client libraries should be available in a format that enables us to optimise this
by sending the bare minimum down the wire.

[RFC: Package bundling strategy](https://docs.google.com/document/d/1aHqZxeO_pW81l1Y1mJOQ8ul7oh63Iu4Ygh5AGUtHpv8/edit?usp=sharing)

## Decision

Use Babel instead of bundlers like Webpack or Rollup to simply transpile our src directories, keeping their folder and
file structure intact. By not bundling the packages into a single file, the bundlers for the apps consuming these
packages have an easier time determining which code split bundle to place different parts of the package into.When

using bundlers like Webpack and Rollup, we noticed that the apps consuming the packages tended to put the whole package
into one of the app's bundles. Even though different parts of the app were code split and used different parts of the
package.

## Consequences

- conversation-components, sunco-js-client and future packages will be built using Babel rather than Webpack
- The dist folder of each package will contain many files rather than one large bundle
- Consumers will have to include their own loaders to handle files that we previously handled with webpack
- Consumers can reduce their app size by relying on tree shaking
- Packages will be limited in functionality by what is supported by Babel - see "Limited by Babel" for more context

### Limited by Babel

Usually you would have both Babel and either Webpack or Rollup. By just using Babel for building our package we are
limiting ourselves to only Babel's features. This means we may have to look for alternative ways of handling things we
normally would have used a Webpack loader or plugin for.

One immediate example is how image file types are handled. Instead of using a webpack loader, we had to find a babel
solution with [babel-plugin-inline-react-svg](https://github.com/airbnb/babel-plugin-inline-react-svg)
and [babel-plugin-inline-import-data-uri](https://www.npmjs.com/package/babel-plugin-inline-import-data-uri).

Although a solution could be found for images, one of the packages hasn't been touched in 4 year and there's no
guarantee we won't face other issues in the future.

## Alternative solutions considered

Please read
the [RFC: Package bundling strategy](https://docs.google.com/document/d/1aHqZxeO_pW81l1Y1mJOQ8ul7oh63Iu4Ygh5AGUtHpv8/edit?usp=sharing)
for more information.

- Bundle with Webpack, single entry point
- Bundle with Webpack, multiple entry points
- Bundle with Rollup using es plugin, single entry point
- Bundle with Rollup using es plugin, multiple entry points

Rollup with multiple entry points got the closest to what we want, but we decided that managing all the entry points was
more effort than was worth it, especially since with Babel we don't have to worry about that and get the same/better
outcome in terms of file size + code splitting.
