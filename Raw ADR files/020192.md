# 14. CJS and ESM modules mix

Date: 2023-12-06

## Status

Accepted

## Context

Some tools can not be executed in the project root due to conflict of CJS and ESM modules.

## Decision

- [x] downgrade glob to 7.xx version
- [ ] replace glob by `fast-glob`

## Consequences

Root-cause: https://github.com/isaacs/node-glob/issues/566

Learn the things:

- `npm ls {package-name}` - show the tree of dependencies for the package
- `yarn why {package-name}` - show why dependency is installed and who requests it

```diff
{
  "devDependencies": {}
-   "glob": "^10.3.10",
+   "glob": "^7.1.7",
  },
  "@comments resolutions": {
    "glob": "^7.xx - this is the last known version of the package that does not break the string-width, strip-ansi and wrap-ansi packages. Keep them CJM instead of ESM."
  },
+  "resolutions": {
+    "glob": "^7.1.7"
+  }
}
```

`glob` tool was reserved for future use, so we are ok to downgrade it.

## Diagnostics

### Solution 1: re-link esm modules to cjs versions

```json
{
  // force esm modules to be replaced by links to cjs modules
  "resolutions": {
    "**/string-width": "link:./mocks/node_modules/string-width",
    "**/strip-ansi": "link:./mocks/node_modules/strip-ansi",
    "**/wrap-ansi": "link:./mocks/node_modules/wrap-ansi"
  }
}
```

Do the installation of the packages: `yarn install --force --refresh-files`

`npm ls string-width` will show the following tree:

```diff
  webpack.config@1.0.0-alpha /Users/o.kucherenko2/workspace/githubs/webpack.config
  ├─┬ concurrently@8.2.2
  │ └─┬ yargs@17.7.2
  │   ├─┬ cliui@8.0.1
  │   │ ├── string-width@4.2.3 deduped -> ./mocks/node_modules/string-width
  │   │ └─┬ wrap-ansi@7.0.0 invalid: "^8.1.0" from node_modules/@isaacs/cliui -> ./mocks/node_modules/wrap-ansi
+ │   │   └── string-width@4.2.3 deduped invalid: "^5.1.2" from node_modules/@isaacs/cliui -> ./mocks/node_modules/string-width
  │   └── string-width@4.2.3 -> ./mocks/node_modules/string-width
  └─┬ glob@10.3.10
    └─┬ jackspeak@2.3.6
      └─┬ @isaacs/cliui@8.0.2
+       ├── string-width@4.2.3 deduped invalid: "^5.1.2" from node_modules/@isaacs/cliui -> ./mocks/node_modules/string-width
        └─┬ wrap-ansi-cjs@npm:wrap-ansi@7.0.0
+         └── string-width@4.2.3 deduped invalid: "^5.1.2" from node_modules/@isaacs/cliui -> ./mocks/node_modules/string-width

```

Correct sub-project resolution tree:

```
npm ls string-width
tools@0.1.0 /Users/o.kucherenko2/workspace/githubs/webpack.config/mocks
├─┬ @mocks-server/main@4.1.0
│ ├─┬ @mocks-server/core@4.0.2
│ │ └─┬ update-notifier@5.1.0
│ │   └─┬ boxen@5.1.2
│ │     ├─┬ ansi-align@3.0.1
│ │     │ └── string-width@4.2.3 deduped
│ │     ├── string-width@4.2.3 deduped
│ │     └─┬ widest-line@3.1.0
│ │       └── string-width@4.2.3 deduped
│ └─┬ @mocks-server/plugin-inquirer-cli@4.0.0
│   └─┬ inquirer@8.2.4
│     ├── string-width@4.2.3 deduped
│     └─┬ wrap-ansi@7.0.0
│       └── string-width@4.2.3 deduped
└─┬ concurrently@8.2.2
  └─┬ yargs@17.7.2
    ├─┬ cliui@8.0.1
    │ └── string-width@4.2.3 deduped
    └── string-width@4.2.3

```

### Solution 2:

Apply resolutions from step #1, install the dependencies... rollback the resolutions, install the dependencies again. Dependencies tree will be correct after that.

```diff
webpack.config@1.0.0-alpha /Users/o.kucherenko2/workspace/githubs/webpack.config
├─┬ concurrently@8.2.2
│ └─┬ yargs@17.7.2
│   ├─┬ cliui@8.0.1
│   │ ├── string-width@4.2.3 deduped
│   │ └─┬ wrap-ansi@7.0.0
│   │   └── string-width@4.2.3 deduped
│   └── string-width@4.2.3
└─┬ glob@10.3.10
  └─┬ jackspeak@2.3.6
    └─┬ @isaacs/cliui@8.0.2
+     ├── string-width@5.1.2
      ├─┬ wrap-ansi-cjs@npm:wrap-ansi@7.0.0
      │ └── string-width@4.2.3 deduped
      └─┬ wrap-ansi@8.1.0
+       └── string-width@5.1.2 deduped
```

## References

- https://github.com/yarnpkg/yarn/issues/4812
- https://classic.yarnpkg.com/en/docs/selective-version-resolutions/
