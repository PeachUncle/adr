# Support "Save as you go" editing

## Status

Accepted

## Context

"Save as you go" in this context means leaning into a pattern whereby the data entered by users is saved during data entry and not necessarily at the end of the process with a manual "Save" action invoked by the user. This would allow a user to leave the application partway through some data entry and return to the point they left off, without having to leave the application running to persist their data in memory.

If information is saved in this manner, it also allows users to jump around the system and return to data, or view data, in different parts aside from where they initially begun the entry.

Take the scenario where a litter is created - clicking "Add litter" on a buck could at that point in time save the new litter and relate it to the buck. It would have very little information stored at that point (Sire ID and litter ID) but it would be persisted and easier to return to, especially through a disconnected litter list which could allow for a flow where a user returns to the litter simply by searching the sire's name in the litter list, not having to navigate via the rat in the same way they created it.

The rat community has not been polled at large for this but Morgan has assisted in discussions around the user experience in adding a litter, leading to this decision.

## Decision

We will support "Save as you go editing" for the creation of new records insofar as stubbing them out in the database at the point of creation with an ID and anything strictly necessary (like related IDs).

We will support "Save as you go editing" for any non-trivial or related data, supporting processes whereby a user can add a litter to a rat, add another new parent rat to that and return to it, then add offspring to that litter.

We will not support "Save as you go editing" for simple properties of entities in the system, such as date of birth or notes. Users will be expected to click "Save" to persist these changes.

## Consequences

- Users can still lose work if the application crashes or is closed if they are amending specific details on a simple record, like rat notes (which is a freetext field and could theoretically be paragraphs).
- Stateless navigability becomes a bit easier - we don't need to persist lots of data in the view state to traverse around theoretical records - we can just redirect users to pages that load directly from the db.
- Models become somewhat more complicated to support pushing information into repositories as they go.
- Models become somewhat more looser as "minimum information required to construct" is quite small (e.g. rats currently require name, dob, sex. This change would unrestrict all that).
- It is potentially not obvious to a user when information is saved or unsaved, and will require some patterns in place to warn them of navigating away from unsaved information.
- Mobile platforms become less susceptible to data loss as task managers are quite eager to close unused applications unexpectedly.
- Potentially produces a lot of litter, it might not be clear that clicking "Create new rat" immediately saves a new blank rat - maybe work is needed to support automatic deletion of blank stubs when the user navigates away.
- Allows for quick-stubbing as a feature, for such a scenario as "A breeder's litter is born and they want to record that 10 new rats are in the litter, but they are not going to sit down and enter in all ten rats individually and manually at this point in time - they will want to come back and edit them later"
