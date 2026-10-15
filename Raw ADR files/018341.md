# ADR 005: Password Hashing Strategy with bcrypt

## Status

Accepted

## Context

User passwords need to be stored securely in the system to prevent unauthorized access and mitigate the risks of data breaches. Storing plaintext passwords is not an option, and even weakly hashed passwords (e.g., using MD5 or SHA1) are vulnerable to offline brute-force and rainbow table attacks.

A secure password hashing strategy must:

* Use a strong and slow hashing algorithm
* Incorporate a random salt to protect against rainbow table attacks
* Avoid storing any sensitive credentials in plaintext

## Decision

We chose to use the `bcrypt` hashing algorithm for the following reasons:

* `bcrypt` automatically generates a **unique salt** for each password
* The algorithm is **designed to be slow**, which protects against brute-force attacks
* The hashed result embeds the salt and cost parameters
* Well-supported in Go via the `golang.org/x/crypto/bcrypt` package

The application uses:

```go
bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
```

This generates a salted and hashed password that is safe to store in the database.

To compare passwords:

```go
bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(plainPassword))
```

## Consequences

* Passwords are never stored in plaintext
* Salting is automatic, so there is no need for manual salt management
* Login performance is slightly slower due to bcrypt's intentional computational cost, but this is acceptable given the security benefits

## Alternatives Considered

* **Manual salt + SHA-256**: More error-prone, less secure, and harder to maintain
* **scrypt / Argon2**: Stronger algorithms, but not supported natively by `bcrypt`, and would require additional dependency management and performance tuning

## Future Considerations

If stronger hashing is required in the future, the system can migrate to Argon2 or scrypt, as long as appropriate hash versioning and backward compatibility are maintained.

## References

* [https://pkg.go.dev/golang.org/x/crypto/bcrypt](https://pkg.go.dev/golang.org/x/crypto/bcrypt)
* [https://cheatsheetseries.owasp.org/cheatsheets/Password\_Storage\_Cheat\_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
* [https://auth0.com/blog/hashing-passwords-one-way-road-to-security/](https://auth0.com/blog/hashing-passwords-one-way-road-to-security/)

---

**Date:** 2025-08-05  
**Author:** Rodrigo Prata  
**Status:** Recorded  
