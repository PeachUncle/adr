# 4. Generating unique IDs

Date: 2023-03-16

Edited: 2024-10-10

## Status

Superceded

## Context

When users start an LPA either online or via the paper route, their data will be sent to and stored in this service. We need to create a unique identifier/reference to store alongside the user's data, which case workers can then use to find LPA's by when actioning any future enquiries or objections.

We must define the format and method of generating this unique identification. This can change for private beta, but should preferably be something we don’t need to change until then.

Human-readable reference numbers are a better description rather than an IDs, as users may need to read them aloud over the phone or manually enter their reference number on the Use an LPA service. Therefore I will refer to them as reference numbers within this document. However they are not to be confused with the current LPA reference numbers in the format of 7000-0000-0000

The reference numbers generated must:

- Only use alphanumeric characters for readability purposes
- Be unique to allow us to identify 1 LPA per reference number
- Have a clear prefix to differentiate them from existing IDs. The Use an LPA service provides users with activation keys prefixed with a C- and allows users to create organisations codes to view their LPA prefixed with a V-. So this M- prefix is not only necessary to allow us to differentiate them from current LPAs, but also allow the user to differentiate their reference number(s) from Use an LPA activation keys/codes.


For private beta (but not necessarily now) they also must:

- Not be calculable (e.g. not a sequence) to avoid iteration based attacks.
- Use the safe alphabet identified by Use an LPA `346789QWERTYUPADFGHJKLXCVBNM`. This is to avoid typographically similar letters such as i, l , and 1, making them more readable/usable for end users and avoid confusion.

A problem that Use an LPA have experienced is words (particularly "bad" words) appearing within a reference number, ideally we would like a solution that prevents this.

## Decision

- The code will be 12 digits long to keep them consistent with current LPA UIDs & UAL activation key format and number of possible combinations. 
- They will have an M- prefix to differentiate from existing reference numbers and Use an LPA activation keys (M for "Modernising"), e.g. `M-3QT4-F65X-A7EJ`. Previously, we intended to use an MTEST- prefix to differentiate test codes from live ones. However, as noted in VEGA-1828, having two different prefixes caused problems with cross-service implementation; consequently, we modified both live and test codes to use the M- prefix.

- To prevent users from being able to calculate/predict the reference numbers we will incorporate a random number generator such as the [crypto/rand Golang package](https://pkg.go.dev/crypto/rand) into the reference number generator. This package provides an advantage over the [math/rand Golang package](https://pkg.go.dev/math/rand), as in crypto/rand we will not have to worry about seeding the generator ourselves eg `index, _ := rand.Int(rand.Reader, big.NewInt(13))`. This solution will prevent prediction or calculation of reference numbers.

- We will only permit upto 2 letters maximum in sequence to prevent words within reference numbers, without enforcing a sequence of 2 letters, 2 numbers as this would again reduce the total possible combinations. We should include logic to count the number of letters in sequence and force a number to be picked as the 3rd character.
- We will query the DB for the generated reference number and regenerate upto a max number of attempts if it has been found to already exist. This is to ensure that references are unique.
- We will generate a checksum for the last character of the reference number to increase security by ensuring that it has not been modified. A checksum will also prevent human error when being transcribed over the phone or scanned in, as we will be able to validate the checksum before storing data or sending requests which will reduce unnecessary API calls.

See PR for [example code generator](https://github.com/ministryofjustice/opg-data-lpa-id/pull/10) - NB: this solution was created prior discussion with my peers around the proposed solution, in which it was advised that we should not seed the generator ourselves.

## Consequences

Only permitting upto 2 letters maximum in sequence will slightly reduce the number of possible reference number combinations, however this will still be an incredibly high limit that we will not reach for a *long* time. 
