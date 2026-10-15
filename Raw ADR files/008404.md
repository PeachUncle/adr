---
status: "{accepted}"
date: { 2025-05-18 }
decision-makers: { Ada He, Andrew Lam, Teoman Ozakan, Alexander Tataoian }
---

# Use Prettier and ESLint for In-editor Coding Style Enforcement

## Context and Problem Statement

How do we ensure that the code written for our project remains cohesive and unified in syntax and style from inception, with no syntax or variable errors? Automatic style enforcers and linters provide warnings and automatic code formatting within the editors, resolving this issues of unified styles. However, there are so many choices of linters and style enforces that each have their own specific rules, so we need to decide upon which ones to use as a team.

<!-- This is an optional element. Feel free to remove. -->

## Decision Drivers

- Is there extensive documentation that we can rely on?
- Do the tools have rulesets that enforce cleanliness in the basic categories we are concerned with (listed below)?
  - consistent whitespace and indentation
  - catch mismatched parentheses
  - catch misnamed variables
  - catch unused or useless variables or lines of code
  - readability (one line for each line of code, comment formatting)
- Do we want to have automated checking of any -ilities within the structure of our code (accessibility specific linters can enforce alt text and aria-labeling)?
- Are the tools easy to use?
- Do they work on save?
- Can we customize the rulesets?

## Considered Options

Linters:

- ESLint
- JSHint
- AxeLinter

Formatter:

- Prettier

## Decision Outcome

Chosen option: "ESLint", integrated with "Prettier" because the ESLint ruleset encompasses checking of our desired syntax consistency areas, and since we really want to have informative error messages that will help us with debugging syntax errors. We elect to use Prettier too, because Prettier does well at breaking up long statements over multiple lines in one consistent way.

### Consequences

- Good, because of confirmed coding style consistency in HTML, CSS, JS, and markdown across our development team
- Good, because of the productivity boost from automated style checking, so we don't have to go back and make edits ourselves
- Good, because of improved code readibility from prettier cross-line formatting
- Good, because of live time error warnings and syntax checking
- Bad, because the tools we're using may not be universal across industry and thus we may not be learning relevant tool usage
- Bad, because of the strict ESLint and Prettier auto rulesets; there may be a learning curve for setting custom flags

### Confirmation

To confirm implementation, leads will send the installation and setup guide to the team, and then check in with everyone individually to make sure that they have it set up.  
Additionally, Prettier checks and ESLint checks will be integrated with Github Actions to run on all pull requests, enforcing the style and flagging syntax errors in PRs, so anyone who forgets to integrate the tools into their editor will be forced to follow the style and correct syntax before we can merge the pull.

## Pros and Cons of the Options

### Linter: JSHint

[Demo JSHint](https://jshint.com/)

- Good, because it's intended to be beginner friendly
- Good, because it has clear and extensive documentation
- Good, because its options reference is concise (very simple and straightforward to use and read)
- Neutral, because it's open source and there is a large user community
- Neutral, because configuration is manual
- Bad, because the error messages aren't clear/ easy to parse

### Linter: ESLint

[ESLint Ruleset](https://eslint.org/docs/latest/rules/)

- Good, because it has extensive documentation
- Good, because it has a detailed options/ rules reference (reading through it is a bit more involved than for JSHint though, because you have to click into individual rules to see more information)
- Good, because the error statements are very clear
- Good, because there is an automated configuration option with npm for intializing the config folder
- Neutral, because it has a lot of presets
- Neutral, because it integrates well with code formatters

### Linter: AxeLint

- Good, because it makes sure we're considering screen reader compatibility and accessibility early in development with HTML
- Good, because it's an accessible in-editor extension
- Neutral, because it integrates with code formatters
- Bad, because it sometimes throws false positives (missing that some code is inaccessible, or flagging code that includes the right labels)
- Bad, because integrating it with pull requests through Github Actions (using to check across files outside of VSCode) requires paid trial
- Bad, because it requires configuration that fully manual

### Code formatter: Prettier

- Good, because it enforces consistent across coding languages: markdown, CSS, HTML too alongside JS
- Good, because it automatically corrects formatting issues
- Bad, because it has a strict ruleset and will flag down any code not fititng the ruleset
  - we may not like the way it formats things 100%, and then we have to customize flags
- Neutral: it works well with linters, fixing style so linter can focus on errors

## More information

### Implementation Guide

1. Install Prettier and ESLint extensions from VSCode
2. Follow the instructions listed in the [integration guide](https://blog.logrocket.com/using-prettier-eslint-javascript-formatting/#eslint-vs-prettier-initial-configuration-basic-usage)
