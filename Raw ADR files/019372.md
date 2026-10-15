# Database Tooling

## Status

accepted (trial)

## Context

Which ORM or database tooling should we adopt?
Though SQL is king of the castle when it comes to dealing with raw data - good old JDBC with inline SQL statements is a
dangerous endeavour at best and a loaded foot-gun without safety in all other cases.

The most obvious option would be Hibernate. Convenient, mature, widely adopted. But there are a couple of things that
bother us with it:

1. `@Entity` as a foundation for the domain object is a recipe for disaster (you're bound to the suboptimal `java.util`
   and everything can be null,
   which means that [Jesus-driven-development](https://no-kill-switch.ghost.io/jesus-driven-development/) is your only
   option...
   eg.: `repository.findByIdJoin3LazyRelationsButNotTheOneYouNeed(123).getNullpointerExceptionAfter2Refactorings().pray()`) [^1] [^2]
2. SQL generated at runtime might be a mess [^3]
3. Too many ways of interaction to mock properly (The way of mutating an Object where everything can be null and
   calling `repository.save(entity)` is hard to test and mock. Inevitably the persistence logic bleeds into the domain
   logic. If it doesn't you loose all the benefits, the framework promised you in the first place.)

In Summary:

- This is not Hibernate specific but applies to all[^4] ORMs
- You sacrifice fine-grained control for short term convenience

Here are some other considerations:

| Tool                                             | Positive                                        | Negative                                                                                                                                                                                                                                                                                                 |
|--------------------------------------------------|-------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [QueryDsl](https://github.com/querydsl/querydsl) | no ORM                                          | hard to mock (similar to Hibernate "Too many ways of interaction to mock properly"); we experienced some deprecation issues in a previous project, where dropped support lead to a 'cannot update'-situation; [also](https://www.reddit.com/r/java/comments/iv0oxe/jooq_vs_jdbi_vs_querydsl_vs_mybatis/) |
| JDBC                                             | no ORM                                          | no typesafety, no convenience, you gotta know your db good [^5]                                                                                                                                                                                                                                          |
| [JDBI](http://jdbi.org/)                         | no ORM                                          | doesn't seem to much different from JDBC - you pretty much gotta trust in your sql strings                                                                                                                                                                                                               |
| [MyBatis](https://mybatis.org/)                  | no ORM                                          | XML [^6]                                                                                                                                                                                                                                                                                                 |
| [sql2o](https://www.sql2o.org/)                  | no ORM                                          | similar to JDBC                                                                                                                                                                                                                                                                                          |
| [jOOQ](https://www.jooq.org/)                    | no ORM; has type-safety through code generation | obviously a bit more verbose for repetitive CRUD stuff (but that to applies to everything that is not an ORM)                                                                                                                                                                                            |

## Decision

* Use jOOQ as persistence tooling.
* Use `./gradlew generateJooq` to generate typesafe db interaction boilerplate.
* Use it in repositories, while strictly separating database-layer from domain- & app-layer.
* Use flyway to enforce migration scripts - make jooq code-gen task depend on flyway-migrate. [^7]

## Consequences

| Profit/Price | Description                                                                          |
|--------------|--------------------------------------------------------------------------------------|
| PROFIT       | It becomes easier to separate domain- and persistence-layer.                         |
| PRICE        | It becomes a bit more tedious to create CRUD-mechanics for every table (needs impl). |
| PROFIT       | We have a maximum of compile checks and a minimum of runtime surprises.              |
| PRICE        | We have more build steps and a bit more complex project setup.                       |

### Footnotes

* [^1]: still some teams go for hibernate annotated domain models despite all that - shockingly even
  so-called [architectural template projects](https://github.com/citerus/dddsample-core) (
  eg. [Cargo.java](https://github.com/citerus/dddsample-core/blob/master/src/main/java/se/citerus/dddsample/domain/model/cargo/Cargo.java))
* [^2]: part of this might be possible to mitigate with strict separation of persistence layer and domain layer and
  tight db-integration tests
* [^3]: not really an issue 99.9% of the time, mostly just a reason for premature optimization and if you encounter some
  problems you can always use a better native-query to fix your performance
* [^4] all known ones at least
* [^5] possibly at every release / commit - meaning you have a shit ton of sql strings in your repositories and
  junior123 writes a new migration script that changes a little thing, but essentially everything... now you better got
  some good integration tests in place or you are up for some hot surprise in prod...
* [^6] srsly. when was it ever a good idea to bring XML into the game?? I find it amusing but would run away as far as
  possible, if I ever saw an actual team use it 🤣 - sample:
```
    <?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE mapper
      PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
      "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
    <mapper namespace="org.mybatis.example.BlogMapper">
      <select id="selectBlog" resultType="Blog">
        select * from Blog where id = #{id}
      </select>
    </mapper>
 ``` 
* [^7] the real gain of trusting our generated code only comes if we use flyway or some other migration management tooling.
There is an annoying bug with the picked flyway dependency (see bottom of /build.gradle.kts), but let's not get too side tracked at this point and just move on as long as it works.