# ADR1 - P2P to Client-Server

Date: 24/04/2024

Status: Accepted

# Summary

We decided to change from a peer-to-peer architecture that was initially proposed in the original proposal of Pigeon to a client-server architecture. This would be simpler to implement and thus allow us to meet our deadlines and focus on the documentation.

# Context

Given the time constraints associated with the project, our team collectively concluded that implementing a peer-to-peer architecture would be time-consuming to implement. The reasons are as follows -

- The decentralised nature of a P2P network can cause a lot of hindrances in the implementation of security features which is one of Pigeon's main ASRs.

- Additionally, in a P2P architecture, there is no central server that could enforce security principles that are important to the Pigeon project.

- Scaling a P2P architecture is another hassle as complex implementations for aspects like resource replication, load balancing, and fault tolerance would take up too much time.

The criteria emphasises good documentation, testing and other deliverables over the complexity of the code.

# Decision

Using a client-server architecture, we get to have a central server that can enforce security aspects of the project. Given that it is relatively simple to design and implement, we can achieve the deadline of the project. Reducing the scope of the project will allow us allow us to focus on the documentation, testing and other deliverables which the criteria awards more than just the code.

# Consequences

Some of the consequences of using a client-server architecture over a P2P architecture are that it will make the implementation of the instant messaging service a lot easier and provide centralized control through the central server which can in some ways help enforce security policies. It will also make scaling of server resources less complex. 

However, one drawback of using a client-server architecture would be that our server becomes a single point of failure. Additionally, this workaround isn't cost-effective as on a large scale deploying and maintaining the server's infrastructure can become more expensive than a P2P architecture. Additionally, the P2P architecture makes the program more decentralised which benefits the security of the system as no server admin can read or pull encrypted messages.
