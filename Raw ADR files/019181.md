## Title
Test doubles

## Status
Draft

## Context
When our application is depending on external sources or need to send out calls, 
these external sources are not available during test.

In order to test our application in isolation, these external sources need to be replaced with test doubles.

Test doubles in a broad sense are anything which replaces the 'real' behaviour with a 'test' behaviour.

### <span style="color:#4863A0;">Mocks</span>
  - use to verify interactions
  - setup responses per case
  - arbitrary
  - tedious/verbose (my bias perhaps :))
  - Pitfall: more easily leads to testing code coupling to code structure, making refactoring more difficult

### <span style="color:#4863A0;">Fakes, Stubs</span>
  - implements/extends an interface like any other class, usually a very simple 
  implementation which returns some predefined results. 
  - Implementation complexity may vary (we could have very dumb fakes, or more complex fakes)
  Usually it is in our best interest to keep the complexity rather low
  - A fake may expose some methods to configure common cases, so that the test can 
  setup behaviour in a more functional way
  - Pitfall: complexity may rise and may cause bugs
  - Pitfall: making the fake a swiss army knife to handle all possible cases increases complexity

### <span style="color:#4863A0;">Spies</span>
  - wrapper of an instance (usually a real instance, but can also be fake/stub, or even a mock though let me know when this is interesting!)
  - use to verify interactions
  - can also be used as a mock in certain conditions (doReturn("x").when(spy).getX())

<span style="color:#FF7900;">!!! Spring allows mixing mocks/fakes/spy beans in the application context, but we need to take care
<u>not</u> to create new beans per test so that the test application context can be reused.</span>

### <span style="color:#4863A0;">Proposed Setup</span>
- Fakes allow coarse control for the default behavior of the application
- Spies allow fine grained control when a test requires a special case which is only applicable in this particular case
- Wrapping fakes with spy allow not needing to create as much state in the fake when we want to verify which data it was called with.

We will implement fakes and load them into the application context as spies.
The spies are useful when we want to test edge cases, like exception handling for example.
While the fakes may stay simple and cover the most used cases using defaults.

## Decision

- Create Fake implementations for adapters, returning data based on the standard defaults.
- Load the fakes into the application context as Spy
- Tests needing fine-grained control will use the mock capability of the spy
- Tests not needing fine-grained control will use the fake as is

## Compliance

It is not possible to technically check when to use a fake or when 
mocking a return value using a spy is more suitable. 
This will be checked during code reviews / design.

- An ArchUnit test will check all test doubles have the annotation @ModuleTestDouble base on the package structure.
- A before test method listener will reset all @ModuleTestDouble annotated beans and validate they are setup as spy.

## Notes
- Author: Gert Wijns
- Changelog:
    - 0.1 initial proposed version on 2025-01-12
