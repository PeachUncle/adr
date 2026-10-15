---
parent: Decisions
nav_order: 2
title: ADR 0002 - Choosing the Journal Page design
status: proposed
date: 2024-05-16
deciders: Project Team
consulted: N/A
informed: Entire Team
---

# Choosing Our Content for the Journal Page

## Context and Problem Statement

In our recent sprint meeting, we started talking about what components we want on the journal page. The team brought up multiple ideas, and we evaluated all choices as a team. We would like to implement a journal page that provides a good user experience with the features that are given without overwhelming the user with too many confusing components.

## Decision Drivers

- **Simplicity**: The page should not have too many components
- **Features**: The page should contain all features we want a journal page to have
- **Performance**: The page should have a good user experience

## Proposed ideas

- widget for creating journals
  - direct to new page on click
- create journal pop up on same page
  - clicking on the newly created widget will direct to new page
- have a side folder of all the available journals (kind of like VS code files)
  - user can click into side journal options and go to journal
- add a search bar to the journal
  - can search up journals

## Decision Outcome

We decided the following system for the page

1. The page will take the form of google docs
   1. load first 25 available journals and display
   2. create journal option in top left corner
2. On create journal click, a menu bar will pop up to specify details for the journal
   1. user can edit and confirm to create journal
3. On clicking existing journals, we will be able to edit the journal
   1. we also have the option to delete the journal
4. We will implement a search bar to be able to search through journals by title
   1. when user types out the string, we only display the journals that match the results

### Consequences

- Good, because we support all the simple features of a journal page: add, edit, and delete
- Good, because we are supporting search functions so it's easier for the user to find docs
- Bad, because we are not supporting many other features so what the user can add to journal is very limited

## Reach features

If the team has more time, we will work on additional features listed below

1. Support uploading images to journal
2. Support search content for searchbar. not just search title

## More Information

This decision will be revisited if project requirements change significantly.
