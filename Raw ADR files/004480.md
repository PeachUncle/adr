# Architecture Decision Record #001

## Title: ERD Enhancement for Facial Recognition Management System

## Status: 
- ❌ Superseded by ADR #003
## Reason:
- ERD v.3 introduced refinements, such as renaming "Course" to "Program," enhancing attendance tracking, and improving user-role relationships. ADR #002 now reflects the latest architecture.

## Metadata

- **Created By:** Lady Joy Borja 
- **Created On:** February 22, 2025
- **Approved By:** Iryl Jean Cadalin [Project Manager]
- **Approved On:** February 22, 2025

## Context

The original Entity-Relationship Diagram (ERD) for the Facial Recognition Management System managed students, courses, events, and attendance. However, it lacked flexibility in role management, user identity tracking, and detailed attendance logs. The new ERD introduces several enhancements to improve system scalability, security, and usability.

## Decision

We decided to update the ERD with the following changes:

1. **Introduction of `User Roles` Table**

   - A many-to-many relationship between `User` and `Role` allows users to hold multiple roles (ex. a user can be both a Student and an Organizer).

2. **Addition of `Face Entity` Table**

   - Introduced for facial recognition purposes, linking unique facial data to the `User` table.

3. **Enhanced `Attendance` Table**

   - Added fields like `Check_In_Time`, `Check_Out_Time`, `Checkpoint`, and `Status` to capture more granular attendance data.

4. **Normalization of `User` Entities**

   - `Event Organizer`, `SSG Officer`, and `Student` tables now include a foreign key reference to the `User` table (`UserID`) to unify user management.

5. **Refined Role Management**

   - The `Role Name` table now works with the `Role` and `User Roles` tables to streamline role assignment.

6. **Improved `Officer_Event` Bridge Table**

   - Maintains many-to-one relationships between `SSG Officer` and `Event`, ensuring efficient mapping. The table remains structurally the same but now explicitly includes the `SSG Officer` for more comprehensive event-officer associations.

## Consequences

### Positive

- **Scalability:** The system can now handle complex user-role scenarios.
- **Security:** The unified user structure and facial recognition enhance identity verification.
- **Usability:** Detailed attendance tracking improves event management.

### Negative

- **Complexity:** Additional tables and relationships increase the system's complexity.
- **Performance:** More joins in queries could impact database performance, necessitating optimization.



## ERD Version 2 - Enhanced ERD
(https://github.com/KHRISTMAE/VALID8/blob/main/ERD/ERD%20v.2.jpg)
## Conclusion

The updated ERD provides a robust and flexible architecture that supports advanced features like multi-role management and facial recognition, ensuring the system meets current and future needs despite the added complexity.


