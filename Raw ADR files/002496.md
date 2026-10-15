---
date: { 2024-11-18 }
written-by: { Ahmed Sulaimon, Ayman Sammo, Nayan Stanley }
decision-makers: { Ahmed Sulaimon, Ayman Sammo, Nayan Stanley }
---

# Hosting Platform

## Context and Problem Statement

- How should authentication to the system be handled?

## Considered Options

- [Email and Password](#email-and-password)
- [OAuth](#oauth)
- [Passwordless Login](#passwordless)

## Decision Outcome

**Chosen option:** Email and Password
**Rationale:** This option allows for full control over authentication. [See below for pros and cons](#pros-cons).

### Consequences

- **Positive:** Could ask user to add more fields upon sign up when required.
- **Positive:** Own the data on your own database instead of 3rd party.
- **Negative:** Need to ensure that passwords are handled securely and in accordance with regulations.

### Confirmation

Users should be able log in to the system to access their own data and no one else is able to log into their account.

<a name="pros-cons"></a>

## Pros and Cons of the Options

<a name="email-and-password"></a>

### Email and Password

- **Pros:**
  - Does not require integration with external systems.
  - Could ask user to add more fields upon sign up when required.
  - Own the data on your own database instead of 3rd party.
- **Cons:**
  - Need to ensure that passwords are handled securely and in accordance with regulations.

<a name="oauth"></a>

### OAuth

- **Pros:**
  - Saves time building authentication.
  - Allows users sign in easily without typing in credentials
- **Cons:**
  - Requires integration with external systems.
  - Not customizable.

<a name="passwordless"></a>

### Passwordless Login

- **Pros:**
  - User does not need to remember their password, it auto generate when needed.
  - Can be more secure, as the password changes with every attempt or every 5 mintues.
  - Own the data on our on database.
- **Cons:**
  - Have to send an email for single time password.
  - If user mistype it, it will reset again which could confuse the user who never used it before.

## More Information

<!-- How did the team come up with the decision -->
