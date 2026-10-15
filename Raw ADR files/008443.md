# Third Party Libraries

[Return to index](https://cse210-group5.github.io/cse210-fa22-ucsd-group5/decisions/)

|  Status  | Confidence |   Date    |
| -------- | ---------- | --------- |
| Decided |    High    | 28-Oct-22 |

## Context and Problem Statement

There are numerous components of our system for which third party implementations might already exist. We need to reach an agreement regarding the use of third party libraries. 

<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* Simplicity: We want to avoid complexity in our code as much as possible
* Reliability: We want our application to be stable

## Considered Options

* Use no third party libraries
* Use some third party libraries, if necessary
* Use many third party libraries

## Decision Outcome

Chosen option: "Use some third party libraries, if necessary", because given the simple nature of our application we would rather implement components on our own. That would allow easier integration and reliability. We will use third party libraries if implementing the same functionality is needlessly complex or time consuming.

<!-- This is an optional element. Feel free to remove. -->
## Pros and Cons of the Options

### Use no third party libraries

<!-- This is an optional element. Feel free to remove. -->
<!-- {example | description | pointer to more information | …} -->

* Good, becasue we get complete control and understanding of our code
* Good, because we save time in reading complex or poorly maintained docs and focus on development
* Bad, because we will be wasting a lot of development effort in building existing things

### Use some third party libraries, if necessary

Balances the two other options ;eading to it being a good choice in the current setting

* Good, because we get strong control of our code
* Good, because we save time from reading bloated documentation
* Good, because we can choose to use libraries to avoid unnecessary time investment
* Bad, because might have to write more code for components which have been implemented by a library

### Use many third party libraries

* Good, because saves a lot of coding time and effort
* Bad, because takes complete control away from developers over the code.
* Bad, because promotes copy-paste coding rather actual understanding of the problem and solution.
