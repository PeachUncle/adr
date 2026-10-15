# Setting affiliation and removing `affiliation` parameter

## Context

Patrons are given the ability to set their campus affiliation to either "Ann Arbor" or "Flint." If the affiliation is not set, then it defaults to either choice based on their associated campus or IP address. If neither are defined, then the affiliation defaults to Ann Arbor.

For a patron to set their campus affiliation, they would click the `Ann Arbor | Flint` button in the header. It would then open a `dialog` that confirms their decision to change their affiliation, or to proceed with the current affiliation.

When a campus affiliation is set, it defines what the default library their search results will be filtered through. If the patron's affiliation is set to Ann Arbor, the default library is set to "All libraries." If the patron's affiliation is set to Flint, the default library is set to "Flint Thompson Library."

Patrons have also been able to set their affiliation by defining the `affiliation` query parameter in the URL. To set it to "Ann Arbor," the parameter's value would be: `aa`. To set it to "Flint," the parameter's value would be: `flint`. This ends up being the equivalent of defining the `library` parameter as all it does is change the Library Scope.

* `affiliation=aa` functions the same as `library=All+libraries`.
* `affiliation=flint` functions the same as `library=Flint+Thompson+Library`.

Defining the `affiliation` parameter is repetitive and therefor unnecessary.

## Decision

We will no longer rely on the `affiliation` parameter to modify search results.

## Status

| Date       | Summary  |
|------------|----------|
| 2025-02-28 | Proposed |

## Consequences

1. Defining the `affiliation` parameter will no longer set the patron's campus affiliation, and will also not change the UI.
2. When an Ann Arbor affiliated patron goes to a Search URL with `affiliation=flint` and not `library=Flint+Thompson+Library` in the query string, they will see search results for "All libraries" and not for "Flint Thompson Library."
