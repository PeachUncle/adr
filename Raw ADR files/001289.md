# Database communication encriptation

* Status: accepted
* Deciders: Alejandro Garcia Prada
* Date: 2025-11-06

## Context and Problem Statement

The system handles sensitive client information, including personal and potentially confidential data. To comply with security best practices and data protection regulations, TCP/IP communication between the application and the database must be encrypted to prevent data leaks, unauthorized interception, or man-in-the-middle attacks.

## Decision Drivers

* RF-02 Autenticación básica (login/register)
* RF-11 Validar datos personales

## Considered Options

* 0009-1-TLS
* 0009-2-Client-side-encriptation

## Decision Outcome

Chosen option: "0009-1-TLS", because the communication between the business logic layer and the database provides a reliable, connection-oriented channel that ensures ordered data delivery, integrity, and broad compatibility across most database systems. Since the data we will store is not highly sensitive, encrypting the communication channel with TLS is sufficient to maintain security. The additional complexity and overhead of implementing full client-side or database-level encryption are not justified in this context.


### Positive Consequences

* Provides encryption, keeping data private and secure during transmission.
* Ensures data integrity, preventing tampering or corruption while in transit.
* Authenticates the server (and optionally the client), helping to establish trust between components.
* Can be seamlessly integrated with existing TCP-based communication without major architectural changes.

### Negative Consequences

* Introduces additional processing overhead due to encryption and decryption operations.
* Increases connection setup time because of the TLS handshake phase.
* Makes debugging and traffic inspection more complex, as encrypted data cannot be easily analyzed.


## Pros and Cons of the Options

## 0009-1-TLS

TLS (Transport Layer Security) is a protocol that works on top of TCP (Transmission Control Protocol) to make internet communication safe. TCP makes sure that data is sent and received correctly, while TLS adds security by encrypting the information and checking that it hasn’t been changed. This helps protect the data from hackers and keeps private information safe when you visit websites, send emails, or use other online services.

More info: https://dev-aditya.medium.com/tls-over-tcp-protocols-how-secure-internet-connections-really-work-4c4addc30801

* Good, because it provides encryption, keeping data private and secure during transmission.
* Good, because it ensures data integrity, preventing information from being changed or corrupted.
* Good, because it authenticates the server, helping confirm identities and build trust.
* Bad, because it adds extra processing overhead, which can slightly reduce performance.
* Bad, because it can make troubleshooting and monitoring network traffic more difficult due to encryption.
* Bad, because it increases the connection setup time due to the TLS handshake process.

## 0009-2-Client-side-encriptation

Client-side encryption means that data is encrypted on the user’s device before it is sent to the server or database, and only the client can decrypt it. This way, even if someone accesses the database or intercepts the data, they cannot read it without the encryption keys. Unlike TLS, which only protects data in transit, client-side encryption protects data at rest and in transit, since the server never sees the plain information.

More info: https://multilogin.com/glossary/client-side-encryption/

* Good, because it protects sensitive data even if the server or database is hacked.
* Good, because only the client can decrypt the data, giving full control over privacy.
* Good, because it provides end-to-end security, not just protection during transmission.
* Bad, because it makes searching, filtering, or indexing encrypted data in the database much harder.
* Bad, because key management becomes more complex and must be handled securely on the client side.
* Bad, because debugging and logging become more difficult when the server can't see the decrypted data.



