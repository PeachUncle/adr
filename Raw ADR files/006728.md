# ADR-3: Use Redis Cache With Micronaut

# Status 
Accepted

# Context
We can cache URLs that are frequently accessed. We can use any off-the-shelf solution like [Memcached](https://memcached.org/), [Redis](https://redis.io/) 
Or [Hazelcast](https://hazelcast.com/), which can store full URLs with their respective hashes. Thus, the application servers, before hitting the backend storage, 
can quickly check if the cache has the desired URL.

We can start with around 25% traffic redirect by cache.


# Decision
Based on our use case, Redis, Memcache and Hazelcast any of this work.

Redis, Memcache and Hazelcast offer highly available\scalable key\value storage. With very fast response times < 10ms.

Redis is unique in that it supports other data structures like sored sets, hash sets and a pub\sub mechanism. It's also extensible via lua scripting. It is probably the most popular and widely used of the two products.

Hazelcast is unique in that it can be embedded in a Java host process, making it great for building stateful microservices without an external database dependency. It also has some other small differences, like the ability to get a call back from a key expiration. In a sense, it does less overall but the few things it does, it does them better. Especially if you're using Java.

Overall these are similar solutions designed for similar use cases like caching external data, creating a communication backplane or shared memory state for a stateful microservice, or possibly even storing (small amounts of non-relational) business data with some degree of durability.

Both Redis and Memcached support sub-millisecond response times. By storing data in-memory they can read data more quickly than disk based databases.Both Redis and Memcached are syntactically easy to use and require a minimal amount of code to integrate into your application.
Both Redis and Memcached allow you to distribute your data among multiple nodes. This allows you to scale out to better handle more data when demand grows.
Both Redis and Memcached have many open-source clients available for developers. Supported languages include Java, Python, PHP, C, C++, C#, JavaScript, Node.js, Ruby, Go and many others.
Additionally, Redis also support Advance Datastructure, Replicaton, Snapshots, Transaction, Geospatical Support, Lua Script and Pub/Sub.

We choose Redis for our application as it most popular and used cache solution. Also, developers have experience with working on Redis Cache.

In futue, We will check [performance benchmark](https://github.com/punitpatel214/baby-url-generator/issues/13)) of all cache solution.


