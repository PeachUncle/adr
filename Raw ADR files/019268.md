# Track organizations using the session based organization field in android v2.0

* Status: accepted
* Deciders: Zaven, Seb
* Date: 2022-03-15

Technical Story: Android v2.0 implements a bridge solution to providing per-session organizations, which relies on correct direct type-in of organization.  v2.2 will provide a more robust solution.

## Context and Problem Statement

Currently planter has a fixed planting organization, in the legacy trees table, and is dealt with in the admin panel growers module where admin users can the organization.  Android v2.0 allows for grower to be tracking for multiple organizations, and these organizations are specified in the field_data.session table.  We require a way to assign trees.planting_organization_id based off this organization string in each session record.   In the legacy system, trees.planting_organization_id overrides the planter.organization_id, so this can be used by clients of the legacy system.  

Note: direct type of organization name is error prone - this require direct operator oversight to assign the correct organiation id in both legacy and v2 system. (this will be solve by Android app v2.2)

## Decision Drivers 

* Whether or not to make temporary changes to database schema
* Complexity of final migration once Android app v2.2 and treeacker schema are fully in use
* Complexity of direct database operations

## Considered Options

1. Add a temporary organization_id column to the field_data.session table and allow an operator directly write access to this column to assign organization.
2. Create a separate table for linking sessions to organization ids
3. Just populate trees.organization_id and do not track the assignment of organization_id to session

## Decision Outcome

Chosen option: "Option 1", because this is the easiest to achieve (just add one column), and because the complexity of final migration is miminal - we just have to remember to it.

### Plan
1. Add organization_id column to field_data.session
2. Database operator updates new sessions with correct organization_id based on inspection of string organization column
3. Database operator assigns trees.organization_id to corresponding trees using the the uuid of the capture records
4. Wait for Android v2.2 to be released, which will include a primary key for each organization making organization_id assigning automatic
5. Consider if we can remove the string organization column from session table, and further considers on organization feature in Android v2.2
