# ADR 04: Test-Driven Development with Code Coverage

[<- Back](../README.md)

## Context

We want to ensure our software is working as expected at all times.

## Decision

We will follow the Test-Driven Development (TDD) approach and track code coverage.

Test-driven Development (TDD) is a software development technique that uses a
short, iterative cycle of development and testing, with the primary goal being
the specification and validation of the software's behavior. The process begins
by writing a test for a specific functionality or feature, which initially
fails as the code to implement that functionality has not been written yet.
Following the "red-green-refactor" principle, the developer then writes the
minimal necessary code to make the test pass (going from a "red" or failing
test, to a "green" or passing one), and subsequently refactors this code to
meet the necessary standards of readability, maintainability, and efficiency,
without breaking the test. This cycle continues with each new feature, ensuring
the codebase is always in a functioning state. TDD is underpinned by the
philosophy that the cost of fixing a bug increases the longer it remains
undetected, which motivates developers to catch bugs early in the development
cycle. It also aids in the creation of a detailed specification, which is often
represented by the suite of tests themselves.

Code coverage is a quantitative measure used in software testing to describe
the degree to which the source code of a program has been tested. It is an
integral part of understanding the effectiveness of our test suite, providing
metrics on the extent of our tests' reach within our codebase. This measure is
usually expressed as a percentage, indicating how much of the total codebase is
covered by the tests. The main types of coverage include statement (or line)
coverage, branch coverage, function (or method) coverage, and condition
coverage. Statement coverage measures the percentage of statements that have
been executed by tests, branch coverage measures the decision points (like IF,
WHILE), function coverage indicates the functions that were called, and
condition coverage checks if both the true and false conditions have been
executed. Code coverage helps identify untested parts of a codebase, which
could be potential areas for bugs to lurk. However, it's important to note that
while high code coverage can be a positive sign, it does not guarantee the
absence of defects or the completeness of testing - it simply indicates the
code that has been executed during testing.

The sub-decisions associated with this ADR include:

- We will use Jest for our unit tests.
- We will use Cypress for our integration tests.
- We will use ESLint and Prettier for our linting / static code analysis.
- We will use Codecov for our code coverage.

## Consequences

- Development may be slower due to the write-test-first approach.
- Higher confidence in the quality of the software.
- Need to invest in a tool for tracking code coverage.
