# OSDOP-237: Case events functionality

* Status: APPROVED
* Approved by: Dan Ashworth, Chris Tasker, Danny Betts

## Context and problem statement

We need a way to create a case event from the stored information.

The following information is stored and will need to be retrieved:

- Event type
- Event date
- Added by
- Nomination version
- Comment
- Files uploaded

The scope of this document will be to determine the best solution for mapping this stored data in a way that can be
passed to the frontend.

One aim is to investigate dynamic prompt text however this is not essential and is only to be considered should it be
low-effort to implement.

## Case events functionality

### Option 1: Builder pattern

To display the case event we could have a builder that allows us to customise event prompts:

```java
DisplayableCaseEvent.builder(
      caseEvent.getCreatedInstant()
      caseEvent.getCreatedBy(),
      caseEvent.getNominationVersion()
    ).withComment(caseEvent.getComment())
    .withCommentPrompt("Reason for decision")
    .withInstigatingUser(user)
    ...
```

Alternatively we could pass a CaseEvent object to handle field mapping internally and keep the builder solely for prompt
renames:

```java
DisplayableCaseEvent.builder(caseEvent)
    .withCommentPrompt("Reason for decision")
    ...
```

These builders would have suitable defaults should prompts not be provided.

We could then have a service dealing with rebuilding these case events for displaying on the frontend:

```java

@Service
class DisplayableCaseEventService {

  DisplayableCaseEvent getDisplayableCaseEvent(CaseEvent caseEvent) {
    return switch (caseEvent.type) {
      case CaseEventType.NOMINATION_DECISION -> getDisplayableCaseEventForDecisionType(caseEvent); 
      ...
    };
  }

  private DisplayableCaseEvent getDisplayableCaseEventForDecisionType(CaseEvent caseEvent) {
    return DisplayableCaseEvent.builder(caseEvent)
        .withCommentPrompt("Reason for decision")
        .build();
  }
  
  ...

}
```

#### Positives

- Easy to read and extend
- Suitable as events are immutable
- Can be easily implemented into tests and dev harnesses
- Easy to change event prompts

#### Negatives

- Potential to forget to call certain methods
    - Key data could be missing. Preventable by passing values into the `::builder()` method as arguments
- Not a pattern that's ordinarily used to create frontend views

### Option 2: Class per type

One option is to have an interface that defines prompts and records values. This is a verbose approach however would
ensure that all the data possible for the event are passed and not forgotten.

An example interface implementation would appear as:

```java
interface DisplayableCaseEvent {
  default String getCommentPrompt() {
    return "Comment";
  }

  @Nullable
  String getCommentValue();
  ...
}
```

We could then have an implementing class of

```java
class NominationDecisionCaseEvent implements DisplayableCaseEvent {

  private String commentValue;
  ...

  NominationDecisionCaseEvent(CaseEvent caseEvent) {
    this.commentValue = caseEvent.getComment();
    ...
  }

  @Override
  public String getCommentPrompt() {
    return "Reason for decision";
  }

  @Override
  @Nullable
  public String getCommentValue() {
    return commentValue;
  }
  
  ...

}
```

To determine which class to use, we'd have a service that uses a switch statement over the CaseEvent.type field.

```java

@Service
class CaseEventService {

  public List<CaseEventItem> getCaseEventsForNomination(Nomination nomination) {
    var caseEvents = ...
    return caseEvents.stream()
        .map(this::getDisplayableCaseEvent)
        .toList();

  }

  private DisplayableCaseEvent getDisplayableCaseEvent(CaseEvent caseEvent) {
    return switch (caseEvent.type) {
      case NOMINATION_DECISION:
        return new NominationDecisionCaseEvent(caseEvent);
      ...
    };
  }

}
```

#### Positives

- Easier to locate definitions
- Logic can be deferred to individual classes
    - Results in smaller tests for each type

#### Negatives

- Potential for a lot of classes
- Verbose

### Other considered options

- Having the CaseType enum store prompt text.
    - This wouldn't work well with the case events being dynamic as prompts would need to be declared despite not being
      used.

## Decision

Option 1, builder pattern, as we'd remove the need for multiple classes. 

Since the content is all related to displaying case events, and they're relatively small, it would make more sense to have them built up by a single service without
the overhead of additional files.

This also allows us to have, what I'd believe to be, a low-effort implementation for allowing dynamic prompts.