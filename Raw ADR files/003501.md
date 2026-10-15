# ADR-4: Library for State Management

**Status:** Accepted

## Context

The input validation for the attackers field is cumbersome and currently lives in multiple places. When trying to fix
it, I noticed, that the root of the problem is a two-way data flow: The validation that happens in the input-widget
depends on which attacking mode is selected, because it changes on "Sicherer Angriff". On the other hand, the "Sicherer
Angriff" widget also depends on the value that is provided in the input-widget, so it can do the calculations.

Currently, the input_validator is instantiated multiple times. The validation-logic is duplicated and in one case even
called manually.

The requirements for a proper solution are:

* The two input fields become red on invalid input.
* The two input fields display a short text about why the input is wrong.
* If one of the inputs is invalid, additionally a box with an explanation is displayed at the bottom of the page.
    * The text displayed on the box is adapted to the current problem.
* Whenever another attack mode is selected or one of the inputs is changed, the validation is triggered again.
* It should be an overall clean and simple solution.

## Considered Options

It is out of question that some improved form of state management is necessary here. These are the two considered
options:

### ChangeNotifier (with Provider package)

`ChangeNotifier` is Flutter's built-in state management solution that uses the observer pattern. It requires minimal
setup
and is included in the provider package, which is maintained by the Flutter team. It closely mirrors the existing
`StatefulWidget` pattern. State changes are triggered by calling `notifyListeners()`, which automatically rebuilds all
listening widgets. This approach works well for small to medium applications but can lead to over-rebuilding widgets
since granular control over which parts rebuild is limited.

### Riverpod

Riverpod is a modern, compile-safe alternative to Provider that eliminates common pitfalls like
`ProviderNotFoundException` by removing dependency on `BuildContext`. It offers better testability since providers can
be
easily mocked without widget trees. Riverpod provides fine-grained reactivity, allowing widgets to rebuild only when
specific pieces of state change, improving performance. The syntax is more declarative with features like auto-dispose,
family modifiers, and better DevTools integration. However, it has a steeper learning curve and introduces additional
concepts like `ConsumerWidget`, `ref`, and various provider types (`StateProvider`, `StateNotifierProvider`, etc.).

## Decision

The `ChangeNotifier` with Provider package will be used. This project is very simple and does not require the power of
`Riverpod`, so the simpler solution is sufficient.

First, the desired behavior will be tested for all possible scenarios. Then I will refactor the existing code.
Additionally, the validation logic will be decoupled from selecting the correct text to display in the infobox for
invalid states.
