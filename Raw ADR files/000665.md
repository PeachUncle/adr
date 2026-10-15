# 002_technology for backend


## Context
If we are going to make a web app (or any app, basically) we need to choose a language and framework.

Often, you can buy a product, but as there are likely very few if any companies who need specialized attendance-trackers, and ITvitae does not have a large budget, this option seems practically impossible.

The second 'line of development' would be low-code/no-code solutions. While they could work, they tend to cost money and are not very flexible; we would also likely not be able to maintain it cheaply.

The third line would be enterprise programming languages with their frameworks. Looking at the Redmonk index of January 2023, we see 
1 JavaScript
2 Python
3 Java
4 PHP
5 C#
6 CSS
7 TypeScript
7 C++
9 Ruby
10 C
11 Swift
12 Shell
12 R
14 Go
14 Scala
16 Objective-C
17 Kotlin
18 PowerShell
19 Rust
19 Dart

From the Redmonk languages, the (many) dynamic languages are less attractive due to a higher occurrence of bugs, and even if languages are (somewhat) statically typed, like TypeScript, they may lack a rich enterprise ecosystem. Shell, CSS and PowerShell and R are not capable of creating complex programs due to not being regular programming languages, Objective-C is deprecated, TypeScript, C++, C, Rust, Go and Scala don't have many libraries for enterprise development (okay, in theory Scala could use all Java libraries, in practice, Scala is not good at it); JavaScript, Python, PHP and Ruby are dynamic, Swift is just for OSX, Dart just for mobile.

Which means only Java, C# and Kotlin remain as candidates.

Most important is the availability of libraries. The Java ecosystem (Java+Kotlin) has (many) more libraries than the .NET ecosystem, often they are also more advanced and even free. With C# you can also make lots of stuff, but if something is not available in the Microsoft ecosystem, you're in trouble, as I saw in several commercial projects in the past (no SOAP libraries for ASP.NET Core, no good mobile framework for C#, problems linking users who did not have an Azure account). This may be one of the reasons why Java seems much more popular with successful software companies than C#/the .NET ecosystem (https://appdevelopermagazine.com/The-top-programming-languages-used-by-us-unicorn-companies/)
  
Also, our current batch of students is learning Java, so finding people to help maintain the app should be easier.

So between Java and Kotlin, which to choose?

In fact one would not have to choose between Java and Kotlin, as you can mix them in the same project. But for simplicity: the differences:

- Support/documentation: far superior for Java than for Kotlin due to Java's greater age and popularity. In my experience, you can almost always if not always make Kotlin code work with Java libraries, but it can require more googling and experimenting

- Speed of feature production/maintenance: I would say that Kotlin has an edge here; Kotlin code is more concise, needing less lines (Meta measured about an 11% reduction) and generally also fewer characters; also, null-safety is built into the languages, leading to fewer bugs; as does Kotlin's more functional programming style and better support for constants.

Maintainability is however also affected by the programming languages one knows. This project may be maintained by Java developers and created by at least one person with C# experience (and, while Kotlin is also inspired by C#, Java looks more like C# than Kotlin does). For resume purposes (relevant for something done in one's free time) Java is also likely better at the moment. And if that calculus one day changes: with the tools of Jetbrains it is easy to convert Java code to Kotlin code.


## Decision
We'll use Java for now. We can switch to Kotlin when it becomes more popular and better documented, but for now: Java. There are no good reasons to do this project in C# instead.


## Status
Proposed

 [Proposed, Accepted, Deprecated, Superseded]


## Consequences
- We'll have to make use of Java libraries (of which there are a lot!)
- Execution speed and memory usage won't be optimal (but that won't be required)
- We'll have access to LOTS of documentation
- Coding may be a bit longer and produce more boilerplate than in C# or Kotlin, but we can likely live with those consequences.
- We can at least always convert to Kotlin when desired (there are no tools I know of that convert Kotlin to Java :/ )
- The code will be able to run with few if any modifications for years, as Java prizes backwards compatibility higher than C# or Kotlin.