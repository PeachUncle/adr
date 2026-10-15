# ADR.2 E-mail Processing

This ADR describes the approach to E-mail polling and processing which are crucial processes for collecting
travel-related events such as itinerary receipts, hotel bookings, etc.

## Status `APPROVED`

## Rationale

The E-mail processing consists of **polling**, **filtering**, and **transforming** sub-processes.

### Polling

In order to read e-mails, the Road Warrior should be provided with read-only access to the user's mailbox. However,
we should not require users to give their credential to the Road Warrior directly. That would be considered by majority
of users as a privacy violation and a big security threat. Besides, there are mail servers protected by 2FA, private
mail servers that require VPN connection, hence the credentials alone would not work. Beyond credentials (username and
password) a connection to a mail server also requires a few technical things to be provided, such as server address,
protocol (POP/IMAP), various ports, TLS parameters. This is often information that an end-user is not aware of and
therefore users will not use the app due to the inability to correctly configure the app.

There are ways however to provide access to mailbox indirectly:

1. **Connect Mailbox** (server-side): Works with mail platforms allowing token-based access for 3<sup>rd</sup> party
   applications after owner's approval; particularly, Gmail. From the user's point of view this looks like a button
   that redirects to service provider's page allowing to grant or deny the access.

2. **System Mailbox** (client-side): The mobile app acts as an E-mail client, accessing mailbox configuration and
   credentials from the system (iOS, Android) Internet Accounts registry. User just needs to select a mailbox to use
   in the app settings or initial set-up wizard.

The second approach looks more beneficial since the e-mails processed locally on device, and only those related to
travel will be sent to the backend; local device network settings are used (including VPN) so private mail servers
can be accessed.

### Filtering

Filtering is intended to select travel-relevant E-mails. For the first iteration the filtering process can rely on the
whitelist of sender domains. Whenever our app sees an E-mail message whose sender address's domain matches an entry from
the whitelist, that message considered relevant and passed to the transformation process. Otherwise, the E-mail is
skipped.

Filtering is done either on server or client side depending on where the polling process is running. For the client
side filtering the whitelist updates are downloaded from the backend and cached locally.

### Transforming

Transformation process extracts travel-relevant data from E-mails based on set of pre-compiled rules defined for
particular senders. It can be considered a state machine having raw E-mail message as an input and zero or more
travel events as the output.

Transformation process is server-side only and it can be accessed via API endpoint.

## Decision

Combine both approaches of **polling** for maximum coverage of possible mail server configurations and **user behavioral patterns**.

## Consequences

Positive:

* Security and privacy is respected since users grant access to the app without compromising credentials.

Negative:

* Processing of large number of mailboxes on server side may inflict additional infrastructural costs.