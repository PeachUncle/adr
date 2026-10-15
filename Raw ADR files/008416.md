---
title: [Displaying Cards] - [Card Creation to Display Pipeline]
status: Purposed
date: 06-01-2025
decision-makers: [Myat Thiha, Eric, Thanh-Long Nguyen-Trong]
---

- Store Memory created in IndexDB by users through Memory Creation Form

- Every memory stored in the IndexDB will display on Memories Page

- Every memory stored in the IndexDB will marked on Memories Map

## Summary

This proposal outlines the workflow for creating and displaying memory entries using IndexedDB. When a user submits the Memory Creation Form, the data is stored in IndexedDB. Each stored memory is then dynamically displayed on the Memories Page and visually represented as a marker on the Memories Map.

**One-sentence overview of the decision.**

Enable real-time creation, display, and deletion of memory cards with visual representation on my memories page using a dynamic IndexedDB-driven UI pipeline.

## Context and Problem Statement

Currently we have stored memories card filled out through the form in IndexDB and have dataDisplay.js handling to inject the innerHTML to memories.html using the cardTemplate.js. Our goal is to be able to dynamically create, display and delete the memories cards. We have implemented the backend functions of retreiving and deleting specific cards associated with their card ids. What changes to has to be make in cardTemplate.js for better UI in My Memories page?

## Considered Options

- refactor the current cardTemplate.js to align with our UI goal for My Memories Page
- reflect cardTemplate.js with change attributes in MemoryCard (cards.js)

## Decision Outcome

We decided to use MemoryCard and reference to make changes to reflect new template in cardTemplate.js. We will then use those reflected new template in dataDisplay.js.

### Consequences

- May still need to address any other UI issues that arise from My Memories page

### Confirmation

reflect cardTemplate.js with change attributes in MemoryCard (cards.js)

## Pros and Cons of the Options

Pros:

- Centralizes template definition through MemoryCard, improving maintainability.
- Ensures consistency across different displays (e.g., card view and map view).
- Easier to support dynamic behavior (delete/edit) via component-based architecture.

Cons:

- Requires coordination between data structure and template rendering.
- May introduce more complexity upfront compared to a simple refactor.

## More Information
