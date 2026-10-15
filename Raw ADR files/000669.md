# 011 Structure of database: Teacher and Registrar tables


## Context

Preferably, you want data structures in which you can have a:

* Teacher/Schedulable (someone who can be scheduled to give a class)
* Registrar (a user who can log in and register the attendance of students)

To avoid confusion, names should be unique (likely also ignoring case).

One design is having a WorkerIdentity table, which contains the name, and a Teacher and Registrar table which refer to that table.

This is however not elegant for several reasons:

* It creates a vague class "WorkerIdentity"
* To get the name of teachers and registrars, you have to use teacher.getIdentity().getName(), which feels unnatural.

Wouldn't it be better if a teacher simply _had_ a name?

None of the choices I can see here at the moment feel very good.

1. If I create a table for Registrar and for Teacher, with their separate names, the database does not automatically enforce the constraint that names should not be shared/duplicated. Accessing the names would be natural, though.

2. If I let tables refer to the WorkerIdentity, I get a weird WorkerIdentity class, and awkward .getIdentity().getName() The constraint of unshared names is enforced, though!

3. If I try to use inheritance here, it simply won't work, since someone can be both a registrar and a teacher. It _could_ work with three classes, though (ExternalTeacher, RegisteringTeacher, and Admin). However, this would likely be more complicated with authorization (2 tables to join and poll, though I guess I could make a hierarchy like worker -> NonRegistrar | Registrar -> RegisteringTeacher, Admin). But then it is awkward again to get all teachers, as that is a join of all NonRegistrars and RegisteringTeachers.

4. Having one table with some members (only teachers!) not having a password but null as a special value gives all kinds of nasty things, like using a 'special value' (null) with a 'special meaning'.

The above listing either means that I am overlooking a smarter, more fundamental option, or that this is simply a case of Sowell's Law ('There are no solutions, only tradeoffs')


## Decision

For now, it is unclear how much value is gained (in reduced update/maintenance time) by looking for an alternative or moving from the current version (option 2) to another version (option 1 or 3). As I've now spent more than 30 minutes thinking about it, I propose to leave things as they are for now (removing some code that some people find hard to read and which may not be an improvement in the grand scheme of things), and only revisit this when we bump into fundamental problems with this approach. After all, the greater current need is to finish the class management (deletion of classes) and personnel management, and definitely the dockerization.


## Status [Proposed, Accepted, Deprecated, Superseded]

Accepted


## Consequences

Positives:
- No extra time spent on refactoring

Negatives: 
- Writing and reading code may be a bit more unnatural. 

When to change:
- Based on further developments, if we would spend say 10 more hours on the backend, and the Teacher/Registrar becomes too onerous, spend one hour or such refactoring the solution to 1, 3, or something better thought up then or later.