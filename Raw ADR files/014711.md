# ADR-0032: Restricting pilot access

## Status

Accepted

Date of decision: 2025-07-03

## Context and Problem Statement

We need to restrict access to the pilot for two reasons:

- to ensure that no one can accidentally mistake the pilot for a live service,
- to manage the risk of the application being overloaded with too many users

There are different options for restricting access to the pilot, which balance cost of implementation, code that will be
thrown away after the pilot, and efficacy of the restriction.

How should we restrict access to the pilot?

## Considered Options

* Single fixed passcode for all users
* Allocate passcode for user on demand, limiting the total number of passcodes issued
* Associate unique passcodes with user account, limiting the total number of accounts created
* Provide an invitation flow for Local Authorities to invite users, allocating them unique passcodes and associating
  them with user accounts on registration

## Decision Outcome

Associate unique passcodes with user account, limiting the total number of accounts created, because it prevents users
from sharing their passcodes and allows us to limit the number of users who can access the pilot, but stops short of
implementing an invitation flow for Local Authorities to invite users, which would be more work and not reusable after
the pilot.

## Pros and Cons of the Options

### Single fixed passcode for all users

All users would use the same passcode to access the pilot, which would be communicated to them via email from the Local
Authorities when they invite users to the pilot.

* Good, because it is the simplest solution to implement.
* Good, because there is limited code that will be thrown away after the pilot.
* Good, because it is easy to communicate the passcode to users.
* Bad, because it does not limit the number of users who can access the pilot.
* Bad, because if the passcode is shared publicly, changing it would require all users to be informed of the new
  passcode,
  which would be difficult to manage and would disrupt the pilot.

### Allocate passcode for user on demand, limiting the total number of passcodes issued

This option would involve creating a page in the WebApp where a passcode can be requested. That page would only be
accessible Local Authorities (who would then need to share a unique passcode with each user). The system would limit the
total number of passcodes issued to a fixed number.

* Good, because having a personal code might dissuade users from sharing it publicly.
* Good, because if a passcode is shared publicly, it can be deactivated without disrupting the pilot.
* Neutral, because it requires some additional work to implement the passcode request page that cannot be reused, but
  not a very large amount.
* Bad, because it relies on Local Authorities to manage the distribution of passcodes, which leaves us open to errors
  such as accidentally sending all users the same passcode.
* Bad, because it does not limit the number of users who can access the pilot, only the number of passcodes issued.
* Bad, because some patterns of sharing could be hard to detect, leading to more users than intended accessing the
  pilot.

### Associate unique passcodes with user account, limiting the total number of accounts created

This option would be similar to the previous option, except that when a user completes their registration the passcode
they used to access the pilot would be associated with their user account. This would allow us to limit the total number
of accounts created, rather than just the total number of passcodes issued.

* Good, because it allows us to limit the number of users who can access the pilot.
* Good, because it eliminates the risk of users sharing their passcode, as it is associated with their account.
* Neutral, because it requires some additional work to implement the passcode request page that cannot be reused, but
  not a very large amount.
* Bad, because it requires additional work to implement the user account association, which cannot be reused after the
  pilot.
* Bad, because it relies on Local Authorities to manage the distribution of passcodes, which leaves us open to errors
  such as accidentally sending all users the same passcode (which in this case would lead to all but one user being
  unable to access the pilot).

### Provide an invitation flow for Local Authorities to invite users, allocating them unique passcodes and associating them with user accounts on registration

This option would involve creating an invitation flow in the WebApp where Local Authorities just enter the email of the
user they want to invite. The system would then generate a unique passcode for that user and email it to them. On
registration, the user would enter the passcode they received, which would be associated with their user account.

* Good, because it allows us to limit the number of users who can access the pilot.
* Good, because it eliminates the risk of users sharing their passcode, as it is associated with their account.
* Good, because it eliminates the risk of manual errors by Local Authorities e.g. accidentally sending all users the
  same passcode.
* Bad, because it requires additional work to implement the invitation flow, which cannot be reused after the pilot.
* Bad, because it requires additional work to implement the user account association, which cannot be reused after the
  pilot.
