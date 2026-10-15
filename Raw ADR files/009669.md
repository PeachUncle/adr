# Selection of Hashing Algorithm Architectural Decision Record

* Status: accepted
* Date: 2024-11-17
* Decision-Makers: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz
* Consulted: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz
* Informed: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz

## Context and Problem Statement

AML requires a secure mechanism to handle sensitive user data, such as passwords. Hashing is essential to ensure password confidentiality, even if the database is compromised. Laravel's built-in hashing mechanism provides support for secure password storage and validation. To determine the most suitable hashing algorithm for this project, we must evaluate Laravel's default option (Bcrypt) and potential alternatives.

## Decision Drivers

* Security: Protection against brute force, rainbow table, and dictionary attacks.
* Performance: Efficient hashing for a high number of user accounts and concurrent logins.
* Ease of Use: Compatibility with Laravel's authentication ecosystem.
* Future Proofing: Flexibility to adapt to evolving cryptographic standards.

## Considered Options

### 1. Bcrypt (Laravel Default)
* Key derivation function designed for password hashing.
* Incorporates a computational cost factor, adjustable for future security needs.
* Supported natively in Laravel.

### 2. Argon2
* Winner of the Password Hashing Competition (PHC).
* Provides memory-hard hashing to prevent brute-force attacks with hardware like GPUs.
* Supported in Laravel as an alternative to Bcrypt.

### 3. SHA-256/512 with Salt
* General-purpose cryptographic hash functions.
* Requires additional implementation to incorporate salt and ensure password security.
* Less ideal for password hashing compared to dedicated algorithms like Bcrypt or Argon2.

## Decision Outcome

Chosen option: Bcrypt (Laravel Default)

Justification:
Bcrypt is an industry-standard hashing algorithm for passwords, providing strong protection against brute-force attacks. Its computational cost factor ensures that hashing can remain secure as computing power increases. Since Bcrypt is natively supported in Laravel's hashing facade, it minimizes development effort and integrates seamlessly with our authentication system.

Although Argon2 offers advanced features, Bcrypt's established security record and compatibility make it a better fit for AML at this stage.

## Consequences

Good:
* Strong protection against brute force and dictionary attacks.
* Ease of integration with Laravel's built-in authentication system.
* Adjustable cost factor to ensure long-term security.

Bad:
* Memory-hard protections are less robust compared to Argon2.
* Potential future migration if Argon2 or other algorithms become industry standards.

## Confirmation

The implementation will be validated through:
* Password Security Audits: Ensuring compliance with best practices.
* Performance Testing: Evaluating hashing performance under peak loads.
* Developer Feedback: Ensuring ease of use within the Laravel ecosystem.
* Monitoring and Updates: Staying informed on cryptographic advancements.

## Pros and Cons of Options

### Bcrypt
* Good: Secure, well-established, and natively supported in Laravel.
* Neutral: Higher computational cost than SHA-based solutions.
* Bad: Less memory-hard than Argon2.

### Argon2
* Good: Advanced security with memory-hard protections.
* Neutral: Slightly more complex to configure in Laravel.
* Bad: Less widespread adoption compared to Bcrypt.

### SHA-256/512 with Salt
* Good: Fast hashing and widely supported.
* Neutral: Requires custom implementation for salting.
* Bad: Not recommended for password hashing due to lack of computational cost factor.

## More Information

References:
1. [https://laravel.com/docs/11.x/hashing#:~:text=By%20default%2C%20Laravel%20uses%20the%20bcrypt%20hashing%20driver%20when%20hashing%20data](https://laravel.com/docs/11.x/hashing#:~:text=By%20default%2C%20Laravel%20uses%20the%20bcrypt%20hashing%20driver%20when%20hashing%20data)
2. [https://www.password-hashing.net/#:~:text=We%20recommend%20that%20you%20use,and%20reference%20code%20just%20below](https://www.password-hashing.net/#:~:text=We%20recommend%20that%20you%20use,and%20reference%20code%20just%20below)
3. [https://www.blackduck.com/blog/cryptography-best-practices.html](https://www.blackduck.com/blog/cryptography-best-practices.html)

Review:
This choice will be revisited if:
* Cryptographic vulnerabilities in Bcrypt are discovered.
* Argon2 adoption increases significantly.
* Project requirements demand stronger memory-hard protections.