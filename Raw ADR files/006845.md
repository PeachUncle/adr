# ADR 09: ESlint and Prettier for Static Code Analysis

[<- Back](../README.md)

## Context

Static code analysis is a valuable practice in software development because it
provides an automated way to review code, helping to catch bugs, errors, and
other potential problems before they make it into production. It enforces
coding standards and ensures consistency across the codebase, which is
especially important in larger projects or when working with a team. By
identifying issues early in the development process, static code analysis can
save time, reduce debugging efforts, and improve overall code quality.
Furthermore, it aids in maintaining the longevity and scalability of the code
making it more readable and maintainable for future developers or team members.

## Decision

We will use ESlint and Prettier for static code analysis.

The decision to use ESLint and Prettier for static code analysis is primarily
driven by the unique benefits they bring. ESLint is a highly flexible and
configurable linting utility that not only helps in identifying and reporting
on patterns found in ECMAScript/JavaScript code, but also aids in maintaining
code quality and ensuring code consistency. Its flexibility allows it to be
configured to suit specific coding guidelines and standards of a particular
project.

Prettier, on the other hand, is an opinionated code formatter that integrates
well with most editors and supports several languages. It helps in automatically
formatting the code to ensure it adheres to a consistent style. This eliminates
debates or inconsistencies over coding styles within a team, leading to cleaner,
more readable code.

Combining ESLint and Prettier brings the best of both worlds - ESLint's
flexibility in enforcing code quality rules, and Prettier's uncompromising
approach to code formatting. This combination helps to catch potential errors
before they're introduced into the codebase, enhancing overall code quality,
and reducing the time developers spend on discussing or fixing stylistic issues,
allowing them to focus more on problem-solving and building features.

### Setup

```bash
# Setup ESlint
#   How would you like to use ESLint? (style)
#   What type of modules does your project use? (import/export)
#   Which framework does your project use? (react)
#   Does your project use TypeScript? (no)
#   Where does your code run? (browser)
#   How would you like to define a style for your project? (guide)
#   Which style guide do you want to follow? (airbnb)
#   What format do you want your config file to be in? (JSON)
npm init @eslint/config

# Install ESLint and Prettier
npm install --save-dev eslint prettier

## Install other npm packages
npm install -D husky lint-staged prettier eslint-config-prettier

# Initialize the husky pre-commit script using the below command.
npx husky-init

# To automatically have Git hooks enabled after install, edit package.json
npm pkg set scripts.prepare="husky install"

# Try and make a commit
git commit -m "Keep calm and commit"
```

## Consequences

- Time to Set Up: Depending on the size and complexity of your project,
  setting up and configuring ESLint and Prettier can take some time. Also,
  if your project doesn't already adhere to the rules you set, correcting
  all existing linting and formatting errors might take significant effort.

- Learning Curve: For teams unfamiliar with these tools, there might be a
  learning curve to understand how they work and how to interpret and fix
  the issues they flag. Team members will also need to learn how to configure
  rules if needed.

- Potential for Disagreement: If team members have strong preferences for
  different coding styles, there might be disagreements over the rules set
  in ESLint and Prettier. Such debates can potentially hinder productivity.

- Integration with Existing Tools: Depending on the other tools and
  technologies in your stack, you might encounter some difficulties
  integrating ESLint and Prettier. However, both are widely used and have
  extensive community support, so solutions for common integration issues
  are often readily available.

- Slows Down Commit Process: Using ESLint and Prettier with a git commit
  hook can slow down the commit process, as each commit will be delayed by
  the linting and formatting process. However, this can be seen as a
  trade-off for ensuring that only quality code makes it into the codebase.

- Possible False Positives/Negatives: No tool is perfect. ESLint, for
  instance, might give false-positive or false-negative results in certain
  edge cases, especially with complex configurations and rules. These
  incidents, however, tend to be relatively rare.
