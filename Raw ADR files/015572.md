# 7. Limited support for Stata in Codespaces

Date: 2024-06-10

## Status

Accepted

## Context

Stata is a proprietary data analysis-focussed programming language available on a comercially-licensed basis.

The Bennett Institute has purchased such a license to enable researchers to write analysis code in Stata in both the secure environment and their own development environments.

This license key is distributed via a private respository in the OpenSAFELY GitHub organisation.
Its presence is not explicitly revealed to users, and management of this key requires little to no manual user intervention.
This is with the aim of minimising the risk of this key being distributed and used outside of OpenSAFELY studies.

Stata has been used in several OpenSAFELY studies and remains a popular choice of language for epidemiological studies.

Stata is not used in any core OpenSAFELY infrastruture or tools, and the Bennett Institute tech team has little familiarity with the language and its ecosystem.

StataCorp provides an IDE/enhanced editor for Stata called the [Do File Editor](https://www.stata.com/features/overview/do-file-editor/), we are unsure of how often this is used by our users.
There is a third-party VS Code extension called [Stata Enhanced](https://marketplace.visualstudio.com/items?itemName=kylebarron.stata-enhanced) which provides Stata syntax highlighting, we have not tested this extension.


## Decision

We will ensure the required licensing infrastructure for Stata actions to be run via the OpenSAFELY CLI works in Codespaces.

We will not install the Stata executable(s), Do File Editor or any other Stata tooling in the research template codespace image.

## Consequences

The research template dev container configuration has been specified with read permissions to the private repository containing the Stata license key.
This change introduces a dialogue to the user during codespace startup to authorise these permissions.
Every member of the OpenSAFELY GitHub organisation has the correct permissions to make such an authorisation.

Codespace users will not be able to run Stata code interactively directly within the Codespace, using the first-party Stata tools.
R is the most frequently used programming language for analytical code in OpenSAFELY studies, and so we decided to prioritise the user experience for R development over Stata.
Adding Stata and its tooling to the research template image was deemed to be too much complexity for our initial development initiative, especially given our unfamiliarity with it.


They may have a diminished user experience using VS Code or RStudio to edit their Stata files compared to using the Stata Do File Editor.
They will be able to run Stata interactively via `opensafely exec ...` and Stata pipeline actions via `opensafely run ...`.
