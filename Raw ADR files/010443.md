# Licence schedule timeline structure
* Author: Ryan Middleton
* Status: proposed

## Context and problem statement

We need to determine how we are going to structure the data that makes up the licence schedule timeline view.

A licence Schedule is made up of the following items:
- Terms
- Phases (within terms)
- Rates (within either a term directly or within a phase within a term)
- Work programme activities (within either a term directly or within a phase within a term)
- Schedule events (within either a term directly or within a phase within a term)

Terms and phases are duration based and have determined start and end dates.

Rates have start dates and their end dates are determined by the next rate start date or the end of the licence.

Work programme activities and schedule events can be attached to terms or phases or have a defined date.

We need to be able to filter rates, work programme activities and schedule events from the licence schedule.

For each item we need to show what it is, dates and duration (if applicable), and comments (if they exist).

## Option 1 - Flat schedule structure
The first option is to have a single list of identical objects, each one holding all the display data for the items in the schedule.

The display logic would be driven either by the event type being added to the objects or potentially creating interfaces for each type.

### Pros
- Filtering event types in a single list is easy

### Cons
- Using a single 'one size fits all' object can make messy code as each event type will use the object differently
- A flat list makes it more difficult to drive display logic as there is no defined structure

## Option 2 - Nested schedule structure
The second option is to have a hierarchical structure, with the top level objects being the terms.

All the other timeline events could be children to the term. A phase could also be a parent to the other events.

All the events that can be children would implement an interface, both the term and phase accepting a list of children.

### Pseudocode example:

```java
import java.time.LocalDate;
import java.util.List;

record Schedule(List<Term> terms) {
}

record Term(List<TermItem> termItems) {
}

interface TermItem {
}

record Phase(List<TermItem> termItems) implements TermItem {
}

record Rate(LocalDate startDate, LocalDate endDate) implements TermItem {
}

var schedule = new Schedule(
    List.of(
        new Term(
            List.of(
                new Rate(LocalDate.of(), LocalDate.of()),
                new Rate(LocalDate.of(), LocalDate.of())
            )
        ),
        new Term(
            List.of(
                new Phase(
                    List.of(
                        new Rate(LocalDate.of(), LocalDate.of()),
                        new Rate(LocalDate.of(), LocalDate.of())
                    ) 
                )
            )
        )
    )
);
```

### Pros
- Each object has the exact fields required for each event type, which makes code cleaner and logic easier
- The defined structure makes it easier to drive display logic

### Cons
- Filtering event types in multiple places is complicated 

## Decision outcome
The decision is to use a nested structure for the schedule (Option 2).