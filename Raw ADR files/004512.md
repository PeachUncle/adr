---
status: "accepted"
date: {2024-01-06}
deciders: {Sushain Garg}
---
# Hashing and Salting for Password Security in Visa Application System

## Context and Problem Statement

* The Visa Application System (VAS) stores sensitive user passwords, requiring robust protection against unauthorized access, breaches, and credential-based attacks.
* Storing passwords in plaintext or using reversible encryption is unacceptable due to security risks.
* Unsalted hashing is vulnerable to precomputed attacks, necessitating additional security measures.

## Decision Drivers

* Protect Sensitive Data: Prevent unauthorized access to password data in case of breaches.
* Mitigate Attack Risks: Thwart password cracking and credential stuffing attacks.
* Comply with Best Practices: Adhere to industry standards for password security.

## Considered Options

* Hashing with unique, randomly generated salts
* Plaintext password storage (rejected due to security risks)
* Reversible encryption (not recommended for password security)
* Unsalted hashing (vulnerable to rainbow table attacks)

## Decision Outcome

Chosen option: "Hashing with unique, randomly generated salts"
Specific Algorithm: bcrypt with a work factor of 12
Salt Length: 16 bytes
Rationale: Provides strong protection against password attacks while balancing security with performance.   

## Consequences

### Good 

* Enhanced password security and reduced attack risks.
* Compliance with industry best practices.

### Challenges

* Careful implementation of hashing algorithms required.
* Secure salt generation and storage essential.
* Password resets needed for future algorithm or salting strategy changes.

## Implementation Details

#### Hashing Implementation

* Use a reputable bcrypt library for the chosen programming language.
* Implement password hashing during account creation and login processes.
* Generate unique, randomly generated 16-byte salts for each password.
* Store hashed passwords and salts securely in the database.

#### Secure Coding Practices

* Mitigate vulnerabilities like SQL injection and buffer overflows.

#### Regular Review

* Stay updated with evolving password security best practices.
* Re-evaluate hashing strategies periodically.

#### Implementation Example

1. Library Selection and Installation

Use the bcrypt npm library for Node.js environments

 ```bash
 npm install bcrypt
 ```
2. Account Creation Process

Generate a unique, random 16-byte salt using a cryptographically secure random number generator (CSPRNG)

```javascript
const salt = crypto.randomBytes(16).toString('hex');
```
Hash the user's password with bcrypt, including the salt and work factor:

```javascript
const hashedPassword = await bcrypt.hash(password, saltRounds = 12);
```
Store hashedPassword and salt securely in the database, preferably in separate fields.

3. Login Process

Retrieve the hashed password and salt from the database for the user attempting to log in.

Hash the provided password using bcrypt with the retrieved salt
```javascript
const isMatch = await bcrypt.compare(providedPassword, hashedPassword);
```
If isMatch is true, the password is valid. Deny access if false

## Key Considerations

* Secure Key Storage (if applicable): Protect any keys used for password hashing with appropriate encryption and access controls.
* Regular Security Audits: Conduct regular security audits to ensure hashing implementation remains secure and up-to-date.
* Password Strength Requirements: Enforce strong password policies to complement hashing and salting measures.
* Dependency Updates: Stay updated with the latest bcrypt library version to address potential vulnerabilities.


## Confirmation

### Compliance will be confirmed through:

* Successful implementation of bcrypt with correct work factor and salting.
* Secure storage of hashed passwords and salts.
* Evidence of secure coding practices.
* Regular reviews of password security measures.

## Additional Considerations

### Password Strength Requirements

Enforce strong password policies (e.g., length, complexity, rotation).

### Secure Key Storage

Protect any keys used for password hashing (if applicable) with encryption and access controls.

### Integration with Authentication Systems

Ensure compatibility with OAuth 2.0 authentication flow for password management.
