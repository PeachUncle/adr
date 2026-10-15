# 9. Enable CSS styles support

Date: 2023-11-21

## Status

Accepted

## Context

React App should be able to use CSS styles. we need support of several CSS related tools/languages/frameworks:

- [x] CSS
- [x] SASS, SCSS
- [x] SASS, SCSS - modules
- [x] vanilla CSS modules

## Decision

1. Use normalize.css to reset browser styles to a consistent baseline

```bash
# install latest normalize.css
curl -O https://raw.githubusercontent.com/necolas/normalize.css/master/normalize.css
```

2. make `global.css` file for demoing the usage of CSS styles

## Consequences

- [x] import of CSS file make it embedded into HTML `<header/>` section. It become a part of final HTML file.
- `style-loader` is used for Injecting CSS into the DOM.
- `css-loader` is used for Interprets `@import` and `url()` like `import/require()` and will resolve them.
- `mini-css-extract-plugin` is used for extracting CSS into separate files. It creates a CSS file per JS file which contains CSS. It supports On-Demand-Loading of CSS and SourceMaps.
- `css-minimizer-webpack-plugin` is used for minifying CSS.

- [x] additional types definition are required for CSS modules support `typings/style.modules.d.ts`

- `postcss-loader` is used for processing CSS with PostCSS. It is a tool for transforming styles with JS plugins. These plugins can lint your CSS, support variables and mixins, transpile future CSS syntax, inline images, and more.

```bash
yarn add --dev postcss-loader postcss postcss-flexbugs-fixes postcss-preset-env postcss-cli
```

- [x] configure vanilla CSS modules support

### References

- https://huantao.medium.com/how-to-host-fonts-and-icons-locally-with-webpack-f5e3d0704bd4
- https://github.com/necolas/normalize.css
- https://webpack.js.org/plugins/mini-css-extract-plugin/
  - https://github.com/webpack-contrib/mini-css-extract-plugin
- https://webpack.js.org/plugins/css-minimizer-webpack-plugin/
- https://stackoverflow.com/questions/40382842/cant-import-css-scss-modules-typescript-says-cannot-find-module
- https://www.npmjs.com/package/typescript-plugin-css-modules
- https://github.com/postcss/postcss
  - https://webpack.js.org/loaders/postcss-loader/
  - plugin: `postcss-flexbugs-fixes` is used for fixing flexbox issues
  - plugin: `postcss-preset-env` is used for converting modern CSS into something most browsers can understand, determining the polyfills you need based on your targeted browsers or runtime environments
  - https://github.com/postcss/postcss-cli
  - https://github.com/postcss/postcss-load-config
- https://vanilla-extract.style/
  - https://vanilla-extract.style/documentation/integrations/webpack/

## Dependencies

```json
{
  "dependencies": {
    // vanilla css modules
    "@vanilla-extract/css": "^1.14.0"
  },
  "devDependencies": {
    "css-loader": "^6.8.1",
    "style-loader": "^3.3.3",
    "mini-css-extract-plugin": "^2.7.6",
    "css-minimizer-webpack-plugin": "^5.0.1",
    // sass, scss
    "sass": "^1.69.5",
    "sass-loader": "^13.3.2",
    // postcss
    "postcss": "^8.4.31",
    "postcss-cli": "^10.1.0",
    "postcss-flexbugs-fixes": "^5.0.2",
    "postcss-loader": "^7.3.3",
    "postcss-preset-env": "^9.3.0",
    // vanilla css suport in webpack
    "@vanilla-extract/webpack-plugin": "^2.3.1"
  }
}
```
