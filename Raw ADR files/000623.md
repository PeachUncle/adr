---
status: "accepted"
date: 2024-11-06
decision-makers: Regnar110
---

# Should I implement single or separated web socket gateways to handle chat and friendList user socket connections

## Context and Problem Statement

Chat and friendList are different entites as socket conenctions in terms of user application usage. Is a good way to handle such socket connections via single gateway keeping in mind that chat connection can be pretty much heavier for server, more resource-hungry and more frequently used than friend list connection. Does single gateway be easy to maintain when handling multiple connection entities?

## Considered Options

* single gateway
* separated gateway

## Decision Outcome

Chosen option: "single gateway", because one gateway keep thing simplier which makes easier to maintain socket related modules in such low user count application. It is also possible to allow servers to scale with single gatewaye in such way:
                                                     +----------+  
                                              +------| App:Chat |  
+--------+                   +---------+      |      +----------+  
| Client |-----internet------| gateway |------+      (port 8081)  
+--------+                   +---------+      |        
                               (port80)       |      +----------+  
                                              +------| App:App2 |  
                                                     +----------+  
                                                     (port 8082)  
													 
Chat module and friend list module can later be moved to dedicated socket applications, and gateway would fulfill the role of proxy which redirects us to different socket apps on different ports (port-share)

<!-- This is an optional element. Feel free to remove. -->
### Consequences

* Good, because this solution is easier to maintain in temrs of small portfolio application
* Good, beacuse it can scale up later if needed
* Good, because single gateway allow us to centralize authentication process for multiple user connection types
* Good, possible lower latency for smaller applications
* Good, no need for gateways redirection or no need to specify a certain gateway on server or client. 
* Bad, because event if it's possible to scale up with single gateway it can be better to create
separated gateways for resource-hungry socket connections
* Bad, because it may require more work in terms of keeping chat and friend list socket modules properly        separated from each other  
* Bad, because latency can be higher when application get larger where gateway also would be used more frequently (by both socket modules)

<!-- This is an optional element. Feel free to remove. -->
### Confirmation

Client can use both Chat and FriendList socket connections through one Gateway.
