# 007_code_formatting

## Context

Code formatting is a nice thing to have. It makes code more readable. Especially for me (Mark) when I'm not used to working with Java, Typescript, Javascript, React, etc. If code is properly formatted, it's easier to comprehend. For example, when method chaining is formatted to one method per line.

However, manually formatting code is boring and tedious.
I'm used to Visual Studio, where formatting can be done automatically.

Here, we use IntelliJ and VS Code. IntelliJ does have auto-formatting on save. VS Code doesn't seem to have auto-formatting.

Thus, it seems useful to use an extension that will auto-format code, at least for VS Code. IntelliJ only has Java, which is fairly readable for me. An opinionated auto-formatter is preferred, so that we don't have to have entire conversations about "how many spaces to use for indentation" and so on.

Various sources recommend using Prettier, since it has been around for 7 or so years. Wubbo pointed out it had 700 contributors (so that most of the bugs should've been found and resolved by now).
For example:
https://youtu.be/rpGJQz3KFKE?feature=shared&t=811

Prettier can be configured to "format on save". And it works out of the box.

A possible alternative would be BiomeJS. But this has only been around for about 3 years. And comparatively, far fewer projects use it (Prettier: 6.9 million, Biome: 2k).
Also, Biome apparently uses tabs instead of spaces, which is a bad thing for Git, according to Wubbo.

## Decision

We're going to use Prettier for code formatting in VS Code.
Prettier is also only available in IntelliJ Ultimate, so we can't even use it in Community Edition.

## How to install Prettier in VS Code

1. Go to the Extensions window (Ctrl + Shift + X).
2. Install "Prettier - Code formatter".
3. There is a config file in the root of frontend called ".prettierrc".
4. Go to VS Code's settings (Ctrl + ,).
5. Search for "Default formatter".
6. Select the option to use "Prettier - code formatter" as default. The list isn't alphabetically sorted.
   There doesn't seem to be a way to force this via config files.
7. There is a Prettier config file called ".prettierrc.json" in the root of frontend/src. Anything in this will override the default values of Prettier.
   Anything not listed will be the default values. (see https://prettier.io/docs/en/options)
   Using the config file is recommended, as that overrides local settings someone might have. (see https://prettier.io/docs/en/configuration)

## Status [Proposed, Accepted, Deprecated, Superseded]

Accepted

## Consequences

None that I can think of. It only changes formatting, which can easily be done with a different (or no) formatter in future, if Prettier no longer exists.
