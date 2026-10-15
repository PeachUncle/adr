# 3. Typescript Enabled solution

Date: 2023-11-18

## Status

Accepted

## Context

Enable typescript support for most tools in the project. `*.ts` files should become executable.

## Decision

added dependencies:

- typescript 5.xx
- ts-node
- @tsconfig/node18, https://github.com/tsconfig/bases
- @types/node

added additional types definitions:

- @types/webpack-dev-server
- Removed '@types/webpack' ref: https://webpack.js.org/blog/2020-10-10-webpack-5-release/#typescript-typings

## Consequences

To verify the configuration added small test script, that added additional dependencies:

- debug
- glob
- type-fest

tsconfig.json is not complete, and will require additional changes.

Notes:

- https://github.com/tsconfig/bases - contains configuration for react-app, cypress, node18, etc.
- We will continue using this package for other steps.

[Webpack Configuration](https://webpack.js.org/configuration/configuration-languages/)
[Webpack & Typescript](https://webpack.js.org/guides/typescript/)
[Webpack Integration](https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html#webpack)

- [x] Examine Project: https://github.com/hungtcs-lab/webpack-typescript-starter

[tsconfig-paths](https://github.com/dividab/tsconfig-paths) - https://www.npmjs.com/package/tsconfig-paths not included, but can be added later.
ref: https://webpack.js.org/configuration/configuration-languages/#typescript

resolution was found by [link](https://webpack.js.org/api/cli/#troubleshooting)

```bash
# test typescript configuration
yarn ts-node scripts/extract.src.dependencies.ts

# test webpack configuration
yarn build

# refresh types definitions
npx typesync
```

## Dependencies

```json
{
  "devDependencies": {
    "@tsconfig/node18": "^18.2.2",
    "@types/debug": "^4.1.12",
    "@types/node": "> ^18.0.0 <19.0.0",
    "@types/webpack-dev-server": "^4.7.2",
    "debug": "^4.3.4",
    "glob": "^10.3.10",
    "ts-node": "^10.9.1",
    "type-fest": "^4.8.1",
    "typescript": "^5.2.2"
  }
}
```

### References

- https://github.com/webpack/webpack-cli/issues/2458#issuecomment-1157987399
- https://generator.tsconfigdemystified.com/ - `tsconfig.json` online generator
- https://medium.com/extra-credit-by-guild/tsconfig-json-demystified-d8f333e578c1
- https://compat-table.github.io/compat-table/es6/
- https://www.manning.com/books/essential-typescript-5-third-edition
  - https://github.com/ManningBooks/essential-typescript-5/blob/main/Chapter%2020/reactapp/tsconfig.json
  - https://github.com/ManningBooks/essential-typescript-5/blob/main/Chapter%2021/End%20of%20Chapter/reactapp/tsconfig.json
- https://github.com/jeffijoe/typesync

## Debug Module Resolution

```bash
export NODE_DEBUG=module
yarn ts-node scripts/extract.src.dependencies.ts
```

refs:

- https://medium.com/@fengyu214/debugging-nodejs-resolve-algorithm-1a3fd6373c05
