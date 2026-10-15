# Calculating dates of a licence schedule and work programme
* Author: Ryan Middleton
* Status: accepted

## Context and problem statement

We need to be able to calculate the dates on a licence schedule and work programme.

A licence schedule is defined by the following rules:
* A licence schedule is made up of 1-3 (very occasionally 4) terms.
* A term can be made up of 0-3 phases.
* Various events (rates, schedule events, work programme activities) can be added either at a specific date, or attached to a term or phase.
* Terms and phases cannot overlap each other. When a term ends, the next term must start immediately afterward without any gaps.
* The length of a term or phase is defined by a duration, with the start date being either the start of the licence or the end of the previous term/phase.

We also need to be able to recalculate a schedule when a change is made and materialize the dates in the database so that they can be used by the NSTA data warehouse. 

## Option 1 - Recursive partial calculation method

The first option is to calculate the dates on the licence recursively from the term/phase that is being edited onwards.

### Pseudocode example (recalculating the schedule when a term duration is updated)
```java
void calculateTermDates(Term term, Duration duration) {
   saveDatesForTerm(term, duration);
   
   if (term.hasPhases) {
      calculatePhaseDates(getFirstPhaseForTerm(term)); //method would behave similarly to calculateTermDates but for phases
   }

   saveDatesForItemsAttachedToTerm(getItemsAttachedToTerm(term)) ;// Sets all items attached to the end of a term to the end date of the term and saves them.

   if (hasFollowingTerm(term)) {
     calculateTermDates(followingTerm); // call method again on the next term in the schedule
   }
}
```

### Pros
- Only recalculates dates affected by the change to the licence schedule.

### Cons
- Recursive method is harder to test and debug if issues arise
- Partial recalculation could introduce bugs where modified dates are missed

## Option 2 - Iterative complete calculation method

The second option is to calculate all the dates on the entire licence iteratively.

### Pseudocode example (recalculating the schedule when a term duration is updated)
```java
void calculateTermDates(Term term, Duration duration) {
  saveDurationForTerm(term, duration);
  calculateScheduleDates(term.getSchedule);
}

void calculateScheduleDates(Schedule schedule) {
  var terms = schedule.getTerms().sortedBytermOrder();
  
  for (Term term : terms) {
    saveDatesForTerm(term);

    if (term.hasPhases) {
      var phases = term.getPhases();
      
      for (Phase phase : phases) {
        saveDatesForPhase(phase); 
      }
    }

    saveDatesForItemsAttachedToTerm(getItemsAttachedToTerm(term));// Sets all items attached to the end of a term to the end date of the term and saves them.
  }
}
```

### Pros
- Iterative method is easier to test and debug.
- If bugs in the logic are found, the script can be rerun to fix any bad data as we recalculate the entire schedule. 

### Cons
- Recalculates the dates for the entire licence schedule even if most of the dates are unchanged.

## Other considerations

### End dates

In other services we only materialize the start dates of a period. This is to minimize bugs where start dates and end dates are mismatched and overlap.
We need to decide if LMS should materialize end dates as part of the licence schedule.

#### Pros of materializing end dates
- Centralizes date calculation logic as the NSTA data warehouse team will not need to calculate the dates themselves.
- Prevents the need to recalculate end dates every time we view the schedule as we only need to recalculate it when edited.

#### Cons of materializing end dates
- Introduces potential for bugs when aligning start/end dates

## Decision outcome

The decision is to calculate the entire licence schedule (Option 2).

We have also chosen to materialize the end dates for terms and phases. This is low risk as they are calculated entirely based on durations and cannot be affected by user entered dates.
We will not materialize end dates of rates as these can be set to user entered dates.
Extra care will need to be taken when testing the calculation logic to ensure that term and phase dates are saved correctly.

