# 0005-{Choosing ESLint for our Linter}

Status: Accepted <br>
Date: 2023-05-20 <br>
Deciders: Joseph Del Val <br>
Consulted: Internet <br>
Informed: Andrew Onozuka, Alex Tahan, Vivin Vinil, Julia Poon, Jacob Felts, Yuantian Zhou, Leo Lee, Abhimanyu Srivastava, Merrick Qiu

## Context and Problem Statement

We needed to decide on a linter so that we could enforce our code style.
Ideally, we wanted something which could potentially change alongside us, and something that could easily be used while we write our code.
Finally, it should also be easy to use, as we should not spend an extraordinary amount of time figuring out how to use a linter.

<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* Adaptability
* Ease of Use
* Able to enforce style as we write code.

## Considered Options

* ESLint
* JSHint

## Decision Outcome

Chosen option: ESLint because
ESLint has a more streamlined installation process, which adds to ease of use. And while both are adaptable and allow for changeing rules, ESLint's documentation is better. Finally, ESLint has a VSCode extension, letting us enforce style as we write code.

<!-- This is an optional element. Feel free to remove. -->
### Consequences

* Good, because we now have a linter to enforce code style. Plus, it works as you write code, and we can change the style whenever necessary.

<!-- This is an optional element. Feel free to remove. -->
## Pros and Cons of the Options

### ESLint

<!-- This is an optional element. Feel free to remove. -->

* Good, because it enforces code style
* Good, because you can configure it whenever
<!-- use "neutral" if the given argument weights neither for good nor bad -->
* Good, because the documentation is easily readilbe
* Good, because it has a VSCode extension
* Bad, because requires a bit of setup

### JSHint

* Good, because it enforces code style
* Good, because you can configure it whenever
* Bad, because requires a bit of setup
* Bad, because documentation is less clear
* Bad, because it doesn't have a VSCode extension.

<!-- This is an optional element. Feel free to remove. -->
## More Information

Here is ESLint's documentation:

https://eslint.org/docs/latest/rules/

And here is JSHint's:

https://jshint.com/docs/options/

To install ESLint, run the following commands in the root of the project directory:

`npm init -y`

`npm install eslint --save-dev`

`./node_modules/.bin/eslint --init`

In the config file, under rules, you should set "camelcase":"error