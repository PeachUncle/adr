# 2. html templating

Date: 2023-03-08

## Status

Accepted

## Context

In a htmx-architecture the backend-api sends pure html in reaction to user-actions which is used in the browser to update parts of the screen. This html is dynamically created based on the result of apllying the request to the current state. Composing the html "by hand" via string concatenation is way too tedious, so a templating-solution is needed to help with dynamically generating html.

## Considered

Hiccup, selmer

The templating needs for this project are pretty basic/standard, so only the community-standard options have been considered. When making a selection to choose from, two sources have been consulted. The demo-project of ctmx (see [ctmx demo-app](https://github.com/whamtet/ctmx-demo)) and the luminus-project (see [luminus templating options](https://luminusweb.com/docs/html_templating.html#templating_options)) which aims to provided sane-defaults for web-development in clojure. Both use Hiccup and/or Selmer. Luminus notes Enlive and Stencil a other popular options, but the already provided options seem to meet the needs of this project, so they haven't been considered but could be assest if there ever arises a need to reconsider this decision. 

[Hiccup](https://github.com/weavejester/hiccup) uses regular Clojure-datastructures to compose html-elements, which can be parsed to actual html once completed. This enables the use the full power of the langueage while manupulating the html-representations. 

[Selmer](https://github.com/yogthos/Selmer) is a more traditional templating-system inspired by Ruby's Django. It uses regular html-files with additional tags for dynamic content, which are filled when Selmer parses the template-files with some arguments. 

These options don't exclude each other and can be used in the same project side-by-side.

## Decision

Hiccup as default, with the option the use Selmer when the dynamic needs are very minimal and it feels like a more natural solution.

## Consequences

By using Hiccup the full power of clojure is available while composing html-elements dynamically is a huge benefit. As the options don't excluded each other there's still the option to use Selmer for mostly static-content (like error-pages) if this feels more natural. (This is the way the ctmx demo-app uses it aswell.)  

