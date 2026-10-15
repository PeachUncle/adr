# 11. Prevent js files part 2

Date: 2024-07-19

## Status

Rejected

## Context

See: [6. Prevent .js files](./0006-prevent-js-files.md)

This needs more thought because the build requires some of the files to be translated, for example:

```
Error: Cannot find module '/home/ben/sauce/Signal-Desktop/ts/scripts/generate-dns-fallback.js'
```

## Decision

### Do nothing: not worth it

It turns out the build requires quite a few typescript files to be transpiled, which means adding lots of cases to the build.

This means there is still going to be lots of noise _and_ it more to maintain in the build.

I went through a few cycles of adding transpilation for missing files and ended up with something like

```js
async function transpileAll() {
  return Promise.all[
    (transpile("ts/types"),
    transpile("ts/scripts"),
    transpile("ts/util"),
    transpile("ts/logging"),
    transpileFile("ts/environment.ts"))
  ];
}
```

and I wasn't finished.

### Something else to try

Bundle the build into a single file and call it from there, that way you don't need the files on disk.

## Notes

### Default build to "no js"

```shell
npm run build:esbuild
```

The `js` file output can be prevented by editing the config file and setting `write` to false.

```js
// scripts/esbuild.js
```

### Make sure build stll works

The build requires that some files _are_ transpiled, you can tell by running the build:

```shell
npm run generate && npm run start

> signal-desktop@7.19.0-alpha.1 generate
> npm-run-all build-protobuf build:esbuild build:dns-fallback build:icu-types build:compact-locales sass get-expire-time copy-components


> signal-desktop@7.19.0-alpha.1 build-protobuf
> npm run build-module-protobuf


> signal-desktop@7.19.0-alpha.1 build-module-protobuf
> pbjs --target static-module --force-long --no-typeurl --no-verify --no-create --no-convert --wrap commonjs --out ts/protobuf/compiled.js protos/*.proto && pbts --no-comments --out ts/protobuf/compiled.d.ts ts/protobuf/compiled.js


> signal-desktop@7.19.0-alpha.1 build:esbuild
> node scripts/esbuild.js


> signal-desktop@7.19.0-alpha.1 build:dns-fallback
> node ts/scripts/generate-dns-fallback.js

node:internal/modules/cjs/loader:1148
  throw err;
  ^

Error: Cannot find module '/home/ben/sauce/Signal-Desktop/ts/scripts/generate-dns-fallback.js'

```

#### Allow certain directories to output js

```js
/*

  Transpile all `.ts` files in <dir> to `.js`.

  The `.js` file is written next to its `.ts` counterpart.

*/
async function transpile(dir) {
  const app = await esbuild.context({
    ...nodeDefaults,
    format: "cjs",
    entryPoints: glob
      .sync(`${dir}/**/*.ts`, {
        nodir: true,
        root: ROOT_DIR,
      })
      .filter((file) => !file.endsWith(".d.ts")),
    outdir: path.join(ROOT_DIR, dir),
    write: true,
  });

  if (watch) {
    await Promise.all([app.watch()]);
  } else {
    await Promise.all([app.rebuild()]);
    await app.dispose();
  }
}

async function transpileFile(file) {
  const app = await esbuild.context({
    ...nodeDefaults,
    format: "cjs",
    entryPoints: [file],
    outdir: path.join(ROOT_DIR, path.dirname(file)),
    write: true,
  });

  if (watch) {
    await Promise.all([app.watch()]);
  } else {
    await Promise.all([app.rebuild()]);
    await app.dispose();
  }
}

async function transpileAll() {
  return Promise.all[
    (transpile("ts/types"),
    transpile("ts/scripts"),
    transpile("ts/util"),
    transpile("ts/logging"),
    transpileFile("ts/environment.ts"))
  ];
}
```

## Consequences

What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.
