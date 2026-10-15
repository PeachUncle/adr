# ADR 001 - Encoding Language

### Status: Accepted

### Josh Holbrook

## Context

In the language of `Writing Interactive Compilers and Interpreters` (WIC&I), the _encoding language_ is the language in which the interpreter is written. This is in contrast to the _source language_, which is the language being implemented by the interpreter.

Practically speaking, there are two categories of choices when it comes to choosing the encoding language:

1. A high level interpreted language - for example, Python, Java, or Typescript
2. A lower level compiled language - for example, C, C++, or Rust

### Trade-Offs

The advantages of a compiled language largely come down to performance. It can be difficult to get the same speed out of an interpreted language as you can from C. On the other hand, the higher level languages may be easier to work with.

As to my own skillsets: my strongest language is Typescript, followed by Python. I'm very weak in C, have little experience with C++, and am still learning Rust.

Writing an interpreter is a challenging problem - or collection of problems. Therefore, it pays to work in a language the author is comfortable with, so they may focus on the core problems.

### On Rust

In fact, the first attempts at implementing a BASIC were in Rust. Rust is a modern, high level language as compared to C. But I found myself having a number of struggles:

1. Polymorphism in Rust can be challenging. While it supports generic traits, there are many limitations. For example, until recently Rust had poor support for async methods in traits. It also has some idiosyncratic requirements around known sizes of properties, and requires many hoops to have multiple dynamic types within a single collection.
2. The parser library I was using, `nom`, had some challenges, particularly around writing parsers over types other than `str` and `&[u8]`. They aren't intractible to a Rust expert, but definitely require some skill.
3. Rust is particularly pedantic around text encodings. This even shows up in how it treats paths.
4. Errors are non-generic, and must be converted or wrapped into reified types. The `thiserror` and `anyhow` crates can help get started, but I found it difficult to prototype errors when I didn't know what I was looking for.
5. Many of the techniques used by a bytecode compiler require "unsafe" features of Rust, an intermediate/advanced topic.

While Rust is a compelling target for an interpreter in general, I found it challenging to both learn how to implement an interpreter _and_ level up in Rust.

### Extension & Plugins

Another consideration is extensions. A scripting language is likely the most straightforward mechanism for extension. The alternative is generating dynlibs. This strategy is possible, but not as seamless. Moreover, it would require expertise in lower level mechanics on the part of extension developers.

## Decision

The first version of Matanuska BASIC will be implemented in TypeScript and Node.JS. This will allow me to focus on learning how an interpreter works. It will also ensure I have the expertise in the encoding language to effectively prototype concepts.

## Future

In the future, as Matanuska BASIC matures, it is likely that I will consider rewriting it, in part or in whole, in a compiled language. The decision is out of scope of this ADR. However, I would still like to outline some of the considerations.

Chances are high that I will want to do this incrementally by leveraging Node's native addons. The standard addon language is C++. However, there are [toolkits](https://neon-bindings.com/docs/introduction) for Rust as well.

Between the two, Rust has some advantages:

1. Many baked-in high level abstractions and data structures, including automatically resizing `Vec`s and `Map`s
2. Great build and test tooling
3. A fantastic library ecosystem
4. Memory safety, unsafe features notwithstanding
5. Unsafe features where necessary

On the other hand, C++ has its pros as well:

1. It's the [official extension mechanism](https://github.com/nodejs/node-addon-api), and therefore has the best support
2. Supports builds with [cmake.js](https://github.com/cmake-js/cmake-js), which I have some experience with and feel positively about
3. Supports unsafe operations more easily or naturally than Rust
4. Due to its similarity to C, it would be easier to reimplement abstractions from `Crafting Interpreters`

Testing is worth elaborating on. Rust has a built-in test framework. C++, does not have a de facto standard test framework, though it does have [some options](https://stackoverflow.com/questions/242926/comparison-of-c-unit-test-frameworks).

The most common option for Node.js addon tests is exporting the addons to Node, and writing the tests in JavaScript. My Node.js [test framework](https://node-tap.org/) is nice to work with, and using it would offer some consistency. However, this would limit me to writing tests for only the API exposed to Node.

A final note: it's possible to mix and match. I could, for example, build a rust library and then link it in a C++ library. The build would be more complex, but it may allow me to leverage the respective advantages of the languages accordingly.
