# 8. Management of Visual Studio Code Settings

Date: 2024-06-13

## Status

Accepted

## Context

[Settings](https://code.visualstudio.com/docs/getstarted/settings) for Visual Studio Code can be configured at a user, or workspace level.
In both cases, they are stored in a `settings.json` file, either in an OS-dependent location in the user's home directory, or the workspace directory respectively.

We used to ship a Visual Studio Code workspace settings file in the research template at `.vscode/settings.json`. Some of these pertained to GitPod (another cloud based developer machine service we used to use), and others were for user convenience.

It is possible to specify user-level settings in the dev container configuration file `devcontainer.json` within the `customizations` property.

[ADR 3](https://github.com/opensafely-core/research-template-docker/blob/bcecb78838dfce8c9d708af194c51e4dce541c87/docs/adr/0003-use-of-devcontainer-directory.md) states our decision to place all of our dev container related configuration within the `.devcontainer` directory.

There are some settings which make the Python/ehrQL/OpenSAFELY CLI work properly in Codespaces(e.g. `python.analysis.extraPaths`, `python.terminal.activateEnvironment`, `python.defaultInterpreterPath`).

There are some settings which we believe make the Codespaces UI more pleasing (e.g. `window.autDetectColorScheme`, `extensions.ignoreRecommendations`).

There are some settings which we believe aid in the development workflow (e.g `files.autoSave`, `git.autofetch`)

## Decision

We will remove .vscode/settings.json from research template.

We will add Visual Studio Code settings that are required for the Codespaces environment to function effectively or that provides a good user experience for all users.

We will add these settings to `.devcontainer/devcontainer.json` in order to keep all codespaces/dev container config in one directory.

We will remove settings that we deem as no longer needed/GitPod related.

## Consequences

We are making some decisions about VS code configuration on users behalf.
Some of which are essential to the proper functioning of dev containers/Codespaces, others are in the name of minimising user surprise or ensuring a good baseline user experience.
Nonetheless this may result in a user experience that might not always be to the user's preference.


Users may still add a workspace settings file to their project's GitHub repository which will interact/override the user settings in ways we haven't tested.

Users connecting to a Codespace using Visual Studio Code rather than a browser will also see the influence of their local user settings, again in ways we are unable to test for.

We may encounter tech support requests that are a result of interactions of user-specified settings and those we ship in the research template.

Nonetheless it is important that we allow user configuration of settings on top of our baseline settings for reasons of accessiblity and supporting individual user needs.