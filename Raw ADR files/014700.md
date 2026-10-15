# ADR-0021: vpc configuration

## Status

Accepted

Date of decision: 2024 Q4

## Context and Problem Statement

Our VPC in AWS must be divided into subnets so that different access controls, e.g. firewall rules, can be applied to
different subnets. How
the VPC is divided into subnets determines both the number of possible additional subnets that can be added, and the
number of different IP addresses (and therefore possible resources) in that subnet.

## Considered Options

* One subnet per resource type (per AZ of that resource)
* One public, one private, and one isolated subnet (per AZ required for each type of subnet)<sup>\*

<sup>*</sup> NAT gateway and Firewall need to be in their own subnets in both options for sensible firewall rules to be
applied

## Decision Outcome

One public, one private, and one isolated subnet, because it allows us to apply the correct firewall rules to each
subnet while minimising the risk that we'll be limited by our choice of CIDR blocks later.

## Pros and Cons of the Options

### One subnet per resource type

A subnet is created for each resource type, e.g. ECS, Redis, RDS, etc

* Good because it allows the finest-grained control possible over ingress and egress to/ from the subnets.
* Neutral because it is a pattern used on other MHCLG projects, e.g. Delta.
* Bad because it requires more careful design over CIDR blocks to ensure we do not run out of IP addresses or subnets.
* Bad because it is more complex and more difficult to maintain if/ when the architecture evolves to include more
  resource types.

### One public, one private, and one isolated subnet

One subnet is created for each ingress/ egress type - i.e. public, private (internet reachable via NAT gateway) and
isolated (internet not reachable)

* Good because it is a simpler design
* Good because we can prioritise having larger address blocks in each subnet, making it less likely we'll run out of IP
  addresses in a subnet, while still having capacity for several additional subnets if required
* Neutral because it still allows granular control over access to the subnets
* Neutral because it is used in other MHCLG projects, e.g. CORE and EPB
* Bad because changing the access control to a resource means destroying it and recreating it in a new subnet, rather
  than just changing a firewall rule

