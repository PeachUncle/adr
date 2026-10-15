---
parent: Decisions
nav_order: 100
title: ADR Template
status: accepted
date: 2025-05-08
decision-makers: Daniel, Sanggeon, Yangyang, Aaron, Yilin, Kelsie
consulted: Full team
informed: CSE 110 instructors, project mentors
---

# Feature-Based Team Structure Over Functional Split

## Context and Problem Statement

At the start of the project, we needed to decide how to divide development responsibilities among team members. The two main options were: (a) splitting the team by frontend and backend roles, or (b) organizing around full-stack feature groups. Our team wanted everyone to gain experience on both frontend and backend tasks while minimizing communication overhead and delays.

## Decision Drivers

* Desire for balanced frontend/backend exposure across the team
* Minimizing delays caused by waiting on another part of the stack
* Encouragement of shared ownership of complete features
* Aligning with course advice on modular development

## Considered Options

* Split team by frontend and backend
* Split team by feature groups

## Decision Outcome

Chosen option: "Split team by feature groups", because it enables better clarity of responsibilities, improves development speed, and allows all members to engage with both frontend and backend development.

### Consequences

* Good, because teams understand end-to-end requirements and can implement complete features independently
* Good, because it reduces bottlenecks and miscommunication across frontend/backend
* Bad, because it may require individual members to quickly ramp up on unfamiliar tech (e.g., frontend styling or backend APIs)

### Confirmation

We’ve implemented this split by assigning team members to specific features such as job swipe UI, filtering, and auto-apply logic. GitHub branches and issues reflect this structure. Merge reviews confirm ownership and implementation of each feature set.

## Pros and Cons of the Options

### Split by frontend/backend

* Good, because members can specialize
* Neutral, because responsibilities are clearly divided
* Bad, because dependencies between front and back may cause blockers
* Bad, because it limits exposure to full-stack thinking

### Split by features

* Good, because members understand both frontend and backend aspects of a feature
* Good, because it fosters better modular ownership
* Bad, because members must learn unfamiliar tech faster

## More Information

This decision was discussed in detail during the May 8 meeting. Meeting notes captured concerns about communication overhead and conflicting schedules. Following the split, task assignments were clarified by GitHub issues per feature.
