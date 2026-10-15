<!-- based on this template: https://github.com/adr/madr/blob/develop/template/adr-template-minimal.md -->

# Testcoverage Generation Automation

## Context and Problem Statement

Generating testcoverage automatically has a lot of dependencies and challanges, that our toolchain can't fully predict and prevent. While configuring and preparing the target project is the users task by design, the assistance they need to provide in testcoverage generation would ideally be nonexistent. However, cmake (meson to some degree aswell) has a lot of ways to implement gcov usage and testexecution, which, because of time constraints we couldn't all account for. And even then, the user would have to provide the chosen specification. So the decision was wether to specialize on one build system and automate it as best as possible or try to be applicable to as many as we could. 

Note: The default configuration had to work on a simple setup without user input except the type of build system used.

## Considered Options

* Broad applicability
* Specialization for a single system

## Decision Outcome

We chose to support multiple build systems. Our toolchains philosphy is to make broaden the applicability of open source software to safety critical projects, therefore the specialization approach would misalign.  
Also, meson was fairly easy to automate as it has integrated testcoverage generation, which meant we had time for cmake and a general approach.
We chose cmake over make because our initial assumption was that we could modify a cmakelist.txt file in an automated way to enable testcoverage generation.

### Consequences

* The potentially has to provide arguments to the cmake build steps (/ meson setup step).
* The user has to implement gcov in cmake projects, if it isn't implemented yet. We provide a solution approach.
* The user can aquire linked documentation and coverage with any build system.

## Pros and Cons of the Options

### Specialization

* (+) The user doesn't need any understanding of the projects build system.
* (-) Our toolchain only supports a single build system. Which might make using a documentation generation tool and a testcoverage generation tool seperately the better option. 

### Broad applicability

* (+) Any project can have interlinked documentation and testcoverage. Providing a decent basis to decide its potential for safety critical software.
* (-) The user has to have rudimentary understanding of the projects build system, if our default settings don't work.

## More Information