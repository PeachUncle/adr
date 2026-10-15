# architectural_decision_record 

As an architect I want to document architectural decisions in the code repository 

## Status
Accepted

## Decision 

We will use a dotnet tool: [dotnet adr](https://github.com/endjin/dotnet-adr)

## Rationale 

Given:
- We do not have any knowledge
- We do not have any experience
- There are no acceptance criteria
- Decision should be made as fast as possible.

With the dotnet adr tool we have a tool we can integrate into Visual Studio, producing an architectural decision record in the documentation folder. It has exactly what we need and no more. 

### Rejected alternatives

There were only two serious solutions found on the internet. ArchUnit (or something comparable for dotnet) and dotnet adr.

#### ArchUnit

It checks the architecture using "unit tests" (heavy airquotes, architecture is not a unit, nor does it resemble anything close to a unit test).
You can create rules, like layer_dependencies_are_respected. These rules look like (unit) tests and work alike. So whenever you run the tests, it tests if the layer dependencies are respected.

You are very flexible in the creation of rules, you can write tests for anything, like there_should_be_no_nullable_properties_in_classes.
Like in behaviour-driven design, the tests and code are your documentation.

These rules hurt flexibility. 
Say I need for some reason, a diverging pattern in a certain piece of code. I would have to rework the architecture tests, and make an exception for that piece of code.

It overlaps with sonarAnalyzer and Visual studio code analyzers.
Code style checking is already handled by using an editor.config. We do not need that option. It may create a risk of having two places where code style is checked.

It does not recored decision-making proces
Implementing a rule does not give me the reason why I made that decision. And which options did not make it. 

Hard to read.
As an architect I need to explain to people why we made certain decisions. It is much easier having a record that show the decision, than having the code as documentation and reading files with rules to puzzle back the decision made.

So Archunit does not answer the need we have.


## Consequences

### Advantages

We have a nice decision record documentation
It is in the code repo.

### Disadvantages

Compared to a central wiki, only a limited amount of people have access to the repositories. So it is hidden from the management team and other architects
It could grow wild, anything could be an architectural decision (like this one).
Markdown invites you to use a lot of text instead of pictures or short clear tests.
You can go wild on the templates, becoming much to elaborate to be clear.