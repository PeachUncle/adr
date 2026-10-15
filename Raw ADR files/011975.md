# Cross-compile project on development machine

Date: `2024-07-02`
Status: `Accepted`

## Context and Problem Statement

Monotax is a local tool and should be conveniently available to the user. Users working on a single machine/OS won't have any inconvenience. Those who use multiple OSes or machines would prefer to deploy the tool on one of the machines.

The Raspberry Pi is a good platform for Monotax. It's usually acts as a home server available 24/7. The user can access Monotax via SSH. So the Monotax should support ARM architecture as a target.

## Decision

Monotax will be cross-compiled on the development machine. The target platform will be 64-bit Raspbian. Other compilation targets can be added later. The cross-compilation will be done using Docker and the cross tool.

## Alternatives

- Cross-compile on the dev machine
- Compile on the target machine
- Cross-compile on CI server
- Deploy on the x86_64 cloud server

### Cross-compile on the dev machine

- Good: relatively fast compilation
- Bad: cross-compilation is more complex than native compilation
- Good: native compilation is not affected
- Bad: requires manual copying to a target machine
- Bad: don't yet support running tests on the target architecture

### Compile on the target machine

- Bad: slow compilation. The compilation requires significant resources
- Good: easy to deploy
- Good: supports tests in the runtime environment
- Bad: requires manual operations to run build

### Cross-compile on CI server

- Good: offloads compilation from the dev machine
- Good: always run builds for a target platform
- Bad: the results aren't easy to retrieve. Requires a hosting for compiled artifacts
- Bad: the hosting requires project to be published. I don't want to pollute the public space with the project

### Deploy on the x86_64 cloud server

- Good: easy to deploy
- Bad: additional costs for running in cloud
- Neutral: the service is available outside of local network. Reduced security but adds a possibility to access from anywhere
- Bad: requires manual operations to run build or a complex CI setup

## Consequences

The cross-compilation requires additional setup. The cross-compilation may fail and requires some maintenance.

I will inevitably skip compilation for some builds, so I'm not 100% sure that each commit is runnable. That's not a critical issue.

## Changelog

- 2024-07-02: Initial version