# ADR-0003: Open Source Licensing Model

## Status
Proposed

## Context
The deployment system has potential value to the broader technical community. Open-sourcing the project would allow others to use, contribute to, and improve the system. However, we want to prevent commercial entities from using our codebase to create competing commercial products without contributing back.

We need a licensing model that:
- Allows users to freely use the software
- Encourages contributions from the community
- Ensures modifications are shared back with the community
- Prevents commercial products from being built using our codebase

## Decision
We will adopt the GNU Affero General Public License version 3 (AGPL-3.0) with the addition of the Commons Clause.

Key aspects of this decision:
- The AGPL-3.0 is a strong copyleft license that requires any modified versions to be open-sourced, even when used to provide a service over a network
- The Commons Clause will be added to explicitly prohibit using the software commercially to sell a product or service
- All source code will be publicly available on GitHub
- External contributions will be welcome through pull requests
- All contributions must adhere to the same license terms

Note: This combination (AGPL + Commons Clause) means the project is technically "source-available" rather than "open source" as defined by the Open Source Initiative, as the Commons Clause restricts commercial use.

## Consequences
- The community can use and contribute to the project
- All improvements to the code must be shared with everyone
- Commercial companies cannot create closed-source products from our code
- Commercial companies cannot sell services based directly on our code
- We may receive reduced contributions from commercial entities
- We will need to maintain contributor agreements
- We may need to address licensing questions from potential users

## Compliance
- All code files must include appropriate license headers
- The repository must include full license text
- Contributors must sign a Contributor License Agreement
- We must periodically review the licensing model to ensure it continues to meet our needs 