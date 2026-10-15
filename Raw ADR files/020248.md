# TSDR-1004 UI Frameworks

## Status

Accepted, Proposed, Deprecated or Superseded (list DR)

## Context



## Decision

We want many UIs:
- Bare HTML
  - No JS no CSS (limited small CSS so just basic pretty. WORKS IF CSS OFF)
  - for low bandwidth, low power machines, Accessability
- full AJAX Site (htmx, js, or typescript)
  - Mostly so updates to forms and large column displays don't require a full page reload.

Website screen sizes to test on:
- small iOS (Iphone 5s? iOS 12) 
- small Android (what is smallest android?)
- tablet
- laptop
- med destop 19in
- massive screen > 22in

Web development will target small mobile screens first then scale up from there.
Advice says this is much easier than scaling down.

Browsers to test website on:
  - Chrome
  - Firefox
  - Edge
  - Safari (mac)
  - Internet Explorer
  - iOS web browser (what is it called?)
  - Android Chrome

TODO include versions of browser / operationg system / phone version in test device list

Minimal that this example should demonstrate:
- form validation
- large set of columns display and edit
- pagination of large column display

## Why

[Why your website should work without JavaScript.](https://www.reddit.com/r/webdev/comments/mfnxnj/why_your_website_should_work_without_javascript/)

## Notes

- [Complete-WebDev-Cheatsheet](https://github.com/SeiynJie/Complete-WebDev-Cheatsheet)
  - https://www.reddit.com/r/Frontend/comments/1j9g6f8/all_frontend_developers_lets_make_the_most/
  - Good listing of various resources
- https://www.reddit.com/r/webdev/comments/1k1b0oc/whats_the_one_web_dev_framework_or_library_you/
  - TODO list of good tech to check out
- https://medium.com/@william.b/i-built-a-raw-html-website-with-no-frameworks-heres-what-i-learned-407249be2137

## Comparisons

- [Is This Tech Dead?](https://www.isthistechdead.com/)
- [Solidjs vs svelte](https://www.reddit.com/r/solidjs/comments/11mt02n/solid_js_compared_to_svelte/)


## Other Possible Options

### htmx

- essays on htmx website
- HTMX + Alpine.js
  - seems to be a simi popluar combo
  - Alpine + Alpine-Ajax as an alternative to htmx?
  - https://www.reddit.com/r/htmx/comments/1kzncvs/htmx_alpine_is_a_breath_of_fresh_air/
- htmx + tailwind?
- https://go-monk.beehiiv.com/p/htmx-and-templ
- https://www.reddit.com/r/golang/comments/1g1k03p/i_found_the_best_web_dev_stack_for_golang/
  - templ, Alpine.js, tailwind
- https://www.reddit.com/r/htmx/comments/1jtv7m1/what_is_dead_may_never_die/
- https://www.reddit.com/r/htmx/comments/1jvrkjv/bootstrap_htmx_is_fucking_awesome/
- https://www.reddit.com/r/htmx/comments/1jvynk1/i_lost_sleep_reading_essays_on_the_htmx_website/
- htmx
  - [FULL Introduction To HTMX Using Golang](https://www.youtube.com/watch?v=x7v6SNIgJpE) by ThePrimeagen
  - specifically says he just started in go. Take with grain of salt.

### Solidjs


### Svelte

https://svelte.dev/

- https://www.reddit.com/r/sveltejs/comments/1j2h7du/is_there_anything_what_you_dont_like_in_sveltekit/
- https://www.reddit.com/r/sveltejs/comments/1jg56is/the_best_sveltekit_codebase_ive_ever_seen/
- https://www.reddit.com/r/sveltejs/comments/1kg91ai/daisyui_or_shadcn/
- https://www.reddit.com/r/sveltejs/comments/1juaepm/svelte_and_ai_coding/
- https://www.reddit.com/r/htmx/comments/1js5t7x/htmx_vs_sveltejs_what_are_pros_and_cons_of_both/
- https://www.reddit.com/r/sveltejs/comments/1kulk34/modern_ui_library/

### Typescript

- https://www.reddit.com/r/typescript/comments/1jrqmjl/once_you_learn_typescript_you_never_go_back_to/


## Not an Option

### Hotwire

- https://hotwired.dev/
- https://www.reddit.com/r/golang/comments/la1ar1/project_using_go_and_hotwire_turbo_to_build/
- pick over htmx if using Rails
- htmx is easier to pick up vs hotwire

### React

https://react.dev/

Controlled by Meta. Yes somethings are faster but it also requires more and more developers
to get things done. Quick to 80% but then it gets hard to get to 100%.

React bad. v19 rfc complex / married to next.js

- https://github.com/alan2207/bulletproof-react
- [React Native Isn't as Popular as You Think](https://www.youtube.com/watch?app=desktop&v=E3Yjx0fFeaA&t=1s)
  - in end of vid has sources of where pulled some stats from. worth looking up

### Vue

https://vuejs.org/

I've used it before. Could use again but it seems there are better options now.
lastest versions have multiple ways of doing things so it is still hard to find examples.
which also throws off AI.

## Others

- Angular
  - https://angularjs.org/
  - [why_do_enterprises / big_companies_use_angular](https://www.reddit.com/r/Frontend/comments/1kyd5g5/why_do_enterprisesbig_companies_use_angular/)
- Datastar instead of htmx?
  - too new
- [qor](https://github.com/qor/qor)
  - last release: 2022
  - example code? 
   - Admin - The core part of QOR system, will generate an admin interface and RESTFul API for you to manage your data
   - Publish - Providing a staging environment for all content changes to be reviewed before being published to the live system
   - Transition - A configurable State Machine: define states, events (eg. pay order), and validation constraints for state transitions
   - Media Library - Asset Management with support for several cloud storage backends and publishing via a CDN
   - Worker (Batch processing) - A process scheduler
   - Exchange - Data exchange with other business applications using CSV or Excel data
   - Internationalization (i18n) - Managing and (inline) editing of translations
   - Localization (l10n) - Manage DB-backed models on per-locale basis, with support for defining/editing localizable attributes, and locale-based querying
   - Roles - Access Control
