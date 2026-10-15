# Use Electron JS to Fulfill the Local-First Requirement

## Context and Problem Statement

We aim to provide a superior local-first user experience. Additionally, it's crucial that our team can quickly become proficient with the chosen technology. Which platform should we use to achieve these goals?

## Considered Options

-   Electron JS
-   Tauri
-   Progressive Web App (PWA)

## Decision Outcome

Chosen option: Electron JS, as it is best suited to our needs and the team's familiarity (details below).

### Consequences

-   Good, because we can leverage our existing web technology skills (HTML, CSS, JavaScript) from our labs.
-   Good, because Node.js backend can be integrated into the app, providing powerful local data processing and access to the vast Node.js package ecosystem.
-   Good, because Electron has excellent documentation which can expedite development and problem-solving.
-   Bad, because Electron applications tend to consume more memory, which might lead to performance issues in resource-constrained environments.

## Pros and Cons of the Options

### Electron JS

Homepage: <https://www.electronjs.org/>

-   Good, because it requires minimal setup, allowing us to get started quickly.
-   Good, because it can be adopted progressively, enabling a smoother transition and learning curve.
-   Good, because it provides Node.js API locally, extending the functionality and versatility of the application.
-   Bad, because it typically consumes a large amount of memory which could lead to performance issues, especially on older hardware.

### Tauri

Homepage: <https://tauri.app/>

-   Good, because it consumes significantly less memory than Electron, leading to more efficient resource usage.
-   Bad, because it requires knowledge of Rust for optimal local backend development, which may necessitate additional learning time for team members not familiar with the language.

### Progressive Web App (PWA)

Homepage: <https://web.dev/progressive-web-apps/>

-   Good, because it can be adopted progressively, enabling a smoother transition and learning curve.
-   Bad, because it depends on user action for installation. Users may opt not to install the PWA, resulting in a less optimal, browser-based experience. Additionally, PWA's functionality might be limited on certain platforms or browsers.
