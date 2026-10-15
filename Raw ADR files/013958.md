# ADR4 - RSA Algorithm Requirements

Date: 22/05/2024

Status: Accepted

# Summary

While using a combination of asymmetric and symmetric encryption like RSA and AES provides better performance and more secure method for encrypting large data (i.e. large messages, files, media etc.), we decided to implement a purely asymmetrical RSA implementation would be easier to achieve. This could be considered for future works for the project where a more comprehensive implementation of a combination of asymmetric and symmetric encryption would help make the security of the pigeon application more robust.

# Context

The main influence for this decision was the time constraints, prior knowledge of team members in the subject matter, and the ease of implementation. For starters, time is the biggest bottleneck of this entire project. The scope is too vast and can be implemented in various ways which can easily lead to scope creep. This is an extremely tough line to tread because the project could easily turn into a passion project for the entire team leading unrealistic targets and expectations like the implementation of a combination of RSA and AES. 

# Decision

The decision solves a lot of problems for the team. For starters, based on the weightage of the marking criteria, we will be able to deliver on the key ASRs without compromising on our overall efficiency. While a robust implementation of the combination for RSA and AES would have been more suitable and ideal for acheiving the Security ASR of the project, a pure implementation of the asymmetric RSA encryption would help us deliver the core security functionality without any compromises to the key ASR of the project.

# Consequences

The positive consequences of the decision is that we'll be able to deliver the security ASR at a high-level. The negative consequence of the decision is that it reduces the scope of the application in terms of testing for efficiency in security with large/complex data (i.e. large messages, files, media etc).