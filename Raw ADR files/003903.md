---
scope: Jobberknoll
date: 2025-01-14
deciders: "@tchojnacki, @mlodybercik"
informed: "@jakubzehner, @piterek130"
---

# Password hashing and storage requirements for Jobberknoll

## Context and Problem Statement

Passwords need to be securely stored in Jobberknoll's database. To achieve this, we need to define password hashing and storage requirements. According to [OWASP recommendations](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), passwords should be stored after hashing with **Argon2id** (with other alternatives provided). The stored data should include the salt and information about the hashing algorithm used. Unfortunately, due to Argon2id's computational load, it has no supported implementations in JavaScript or TypeScript. This means, that we have to use FFI to call native libraries or use a less secure alternative.

## Considered Options

- Using Argon2id with static FFI (`@node-rs/argon2`)
- Using Argon2id with dynamic FFI (`libargon2`)
- Using a less secure key derivation function (e.g. bcrypt)

## Decision Outcome

Chosen option: **Using Argon2id with dynamic FFI (`libargon2`)**, because it is the most secure and audited option.

The backend must use Argon2id implemented in a native language (e.g. Rust, C, C++) and accessed via FFI. The reference implementation of Argon2id was selected, which is available under the `libargon2.so.1` dynamic library. The OWASP recommendations for algorithm parameters should be followed.

The password must be stored using the [modular PHC string format](https://github.com/P-H-C/phc-string-format/blob/master/phc-sf-spec.md), to retain the ability to change the hashing algorithm in the future. Passwords should be rehashed on first login after the change of the hashing algorithm. This is currently unimplemented, since only Argon2id is supported.

## Consequences

- Good, because we use the algorithm recommended by OWASP.
- Good, because the hashing and validation of passwords can be offloaded to an external library.
- Good, because the modular PHC string format allows smooth algorithm changes in the future.
- Bad, because we require all service runners to have the `libargon2.so.1` library installed.
