# ADR 014 - OpenTelemetry

### Status: Accepted

### Josh Holbrook

## Context

Until recently, I was using a hand-rolled class called `Tracer` to attempt to trace execution for debug purposes. It was becoming unwieldy, and I yearned for a better solution. As part of that effort, I implemented OpenTelemetry tracing in debug builds of Matanuska.

### Why Tracing?

Naively, I implemented `Tracer` for following the path of execution when errors in parsing or compiling occurred. Both the parser and the compiler have very deep call stacks making stateful changes to the called methods' respective classes. When errors occurred during development, it could be difficult to understand the path of execution that got us there.

This implies that there's a strong benefit to good visualizations for traces, something my `Tracer` class was struggling to provide. By using OpenTelemetry, we can leverage an open source platform, such as [Jaeger](https://www.jaegertracing.io/), to view traces.

In addition, tracing can be valuable for _profiling_. While my `Tracer` didn't implement it, OpenTelemetry traces are timed, and the visualizations show the relative length of time a given trace took. In a world where I don't have great profiling tools for JavaScript, this could be really valuable.

### When is Inspecting Better?

A challenge when it comes to tracing is understanding the state of the program at a particular point in time. This can be helped by setting attributes on spans. But in many of these situations, it's arguably more prudent to use Node.js's built-in [inspector support](https://nodejs.org/en/learn/getting-started/debugging).

The benefits and usage of the inspector functionality are largely out of scope for this discussion. But I bring it up to highlight that tracing is not expected to solve every issue with debugging - at least, on its own. In the future, it will likely operate as complimentary to the inspector.

### Advantages to OpenTelemetry

Before we get into some of the problems with OpenTelemetry, let's nail down the positives which motivate us to use it:

1. Better visualization and decreased clutter by using a separate GUI backend for viewing traces
2. Less maintenance of bespoke abstractions
3. Fully-featured API

### Issues with OpenTelemetry

There are, unfortunately, a few major issues with OpenTelemetry, which need to either be accepted or mitigated.

### Challenging Onboarding

First - and this is the elephant in the room - OpenTelemetry's API is sprawling and the JavaScript documentation is lacking. I think this is for a few reasons:

1. The API has historically been fast-moving. This meant that, once documentation was written down, it immediately went out of date. The OpenTelemetry developers then struggled to fix it in post, especially as the old APIs weren't deprecated - just lower level than a user might expect.
2. The developers are deep subject matter experts on observability, not user experience. This means that, when prompted, they tend to get into the weeds in ways that don't necessarily help a naive user.
3. There are generalized problems with tracing that are earnestly hard to solve in a manner conducive to facades and other abstractions. The most significant of these is [context management](https://opentelemetry.io/docs/languages/js/context/) - that is, how does a trace know which span is its parent? It's tempting to say that if React can hide the complexity of hooks, that they can hide the complexity of contexts as well. But React has the advantage of having a single entry point for execution - team Otel, in contrast, fundamentally has to deal with arbitrary entry points.

This caused significant issues when onboarding. I am, however, hopeful that with internal abstractions and the relative stability of today's OpenTelemetry libraries, that the _maintenance_ burden will be acceptable.

### Deep Stack Traces

Second - and this was a problem with the hand-rolled abstraction as well - tracing creates very deep stack traces. In the case of OpenTelemetry and `trace.startActiveSpan`, it's at least two added layers to the stack - one when calling `trace.startActiveSpan` itself, and another when that method calls `context.with` in turn. In practice, it's often more.

This can be somewhat mitigated by calling `context.with` directly. But that introduces a lot of boilerplate, in a world where `trace.startActiveSpan` is already lightweight enough to motivate a framework-specific implementation with more bells and whistles. Macros could help address the problem, though `jscc` doesn't support them as such. But even with macros or boilerplate, it would still add the overhead of `context.with`, which is non-optional when using OpenTelemetry.

Rather than going down this road, here are some other techniques to address the issue:

1. Use [span events](https://opentelemetry.io/docs/languages/js/instrumentation/#span-events). These show up as points in time within an owning span, rather than separate spans. Using span events will avoid polluting the stack trace at _all_, and are plenty sufficient when the method being called is short-lived - for example, as in most parser methods.
2. Use `jscc` to optionally include tracing calls. This can make source mapping more challenging, but will decrease the size of the call stack when tracing isn't desired or necessary.

### Sensitivity to Load Ordering

The nature of instrumentation is that it must be loaded _as early as possible_ in the lifecycle of an application. In fact, it's so sensitive that OpenTelemetry recommends [pushing the setup into a `.cjs` file and loading it with the `--require` flag from the CLI](https://opentelemetry.io/docs/languages/js/getting-started/nodejs/#run-the-instrumented-app).

In production at many companies, this is simply pulled in as one of the first imports - that was my initial approach as well. But the nature of Matanuska's Vite-based build means that load order can be tough to control.

The introduction of this `--require` flag for debug-only builds means added complexity to the entry point (ie, `./bin/matbas`), to the point where templating becomes a reality.

## On Backends

One challenge introduced by OpenTelemetry was the need for a separate backend service. Luckily, Docker is good at hiding that complexity in a container, and Terraform is good at spinning up and down stacks in a reproducible manner. Jaeger in particular has a [one-container solution](https://www.jaegertracing.io/docs/2.0/getting-started/) for firing up a backend for local use - this worked great for my purposes.

## Decision

With **all that in mind**, here are the design decisions I went with.

### Jaeger Backend

I wrote a new tool called `fireball` (it's an alcohol joke) which uses Terraform and Docker to stand up and tear down a Jaeger instance. The ergonomics are somewhat similar to Docker Compose - `fireball up`, `fireball up -d` and `fireball down` all work as expected.

This technique has worked incredibly well, beyond my dreams. It was the least challenging part of the OpenTelemetry implementation.

### Telemetry Library

The `--require` technique motivated a separate compiled entry point for the setup of the OpenTelemetry SDK. I decided to push this into a module in a workspace, which is now called via `node --require '@matanuska/telemetry' ...`. The major wrinkle, versus the standard Matanuska build, is that I needed to generate a `.cjs` build, which in turn meant I needed to use the `replace` plugin instead of the `consts` plugin (which appears to depend on the use of import syntax). Luckily, this library is simple and these differences are narrowly constrained. It was even able to leverage `grabthar`, the custom build tool for Matanuska.

### Debug Functions

The `debug.ts` module implements thin wrappers around the OpenTelemetry API. In particular, it implements a function called `startSpan`, which is somewhat similar to `tracer.startActiveSpan` but with the added behaviors of attaching exception data to the span and automatically closing it. In addition, it implements a function called `addEvent`, which will fetch the currently active span and add an event to it. These functions are _not_ hidden behind jscc blocks, as they need to work in the event that they are called in the release build.

### Jscc Patterns

As mentioned, `debug.ts` exposes its helper functions regardless of the value of `MATBAS_BUILD`. Instead, this is handled at the call sites.

First, the functions are conditionally imported:

```ts
//#if _MATBAS_BUILD == 'debug'
import { Span } from '@opentelemetry/api';
//#endif
```

```ts
//#if _MATBAS_BUILD == 'debug'
import { startSpan } from './debug';
//#endif
```

The spans are also _called_ conditionally. For instance, in the main loop of the REPL:

```ts
async function repl(executor: Executor, host: Host) {
  while (true) {
    //#if _MATBAS_BUILD == 'debug'
    await startSpan('read-eval-print', async (_: Span) => {
      //#endif
      try {
        const input = await executor.prompt();
        await executor.eval(input);
      } catch (err) {
        if (err instanceof BaseFault || err instanceof Exit) {
          throw err;
        }

        if (err instanceof BaseException) {
          host.writeException(err);
          return;
        }

        throw RuntimeFault.fromError(err, null);
      }
      //#if _MATBAS_BUILD == 'debug'
    });
    //#endif
  }
}
```

This helps avoid the performance overhead inherent in adding tracing, and additionally may help simplify stack traces for release build errors.

### Entrypoint

The entrypoint is now assembled from templates, using Terraform. This is accomplished with another module, similar in interface to `fireball` or `citree`. It is called during Matanuska's build process.

## Loose Ends

This work lays the foundations for doing some really cool things with tracing. However, it does leave some loose ends.

### Incomplete Instrumentation

First, at the time of this writing, the parser and compiler are not fully instrumented. Spans for large parts of Matanuska are in-place, but the end result is fundamentally not as fine-grained as it was previously. This is intentional, even aside from efforts to cap scope. As mentioned, it's unclear how useful traces are for fine-grained debugging as compared to inspector tools. As such, I decided to fully instrument these components on an as-needed basis. That will hopefully lead to more useful traces long term.

### Bugs

Second, there are number of small but significant bugs. One of them is that the root span for the REPL appears to log twice within Jaeger, for unknown reasons. Another is that spans for script runs are never received at all, likely due to the process exiting before spans can be flushed. OpenTelemetry was largely assumed to be running in the context of long-running applications, and those assumptions are running counter to my current usage. These weren't considered enough to stop me from shipping, but should be addressed eventually.

### Jscc Patterns for Non-Telemetry Use Cases

This ADR outlines a series of patterns for use of the `debug` module. This pattern is new - older features are given default no-op implementations in the `debug` module. This is because, historically, the problems solved by `jscc` in all files were being handled through templating in just the `debug` module. The work to migrate other uses of this module to follow the same patterns is outstanding, as is an ADR discussing how `jscc` came into the picture.

### Debug Logging

Third, there are some questions around debug logging. By default, the SDK will create a `DiagLogger` if the `OTEL_LOG_LEVEL` environment variable is set to a valid value, such as `info`. However, the output is really basic and does not spark joy.

Related is logging from Nestjs, our dependency injection framework. Prior to these changes, I was using functionality on the tracer to log debug information from Nestjs. Now that this is gone, I'm doing so with the default Nest logger.

Between these two, it's tempting to create some shared logging conventions between both Nest and `@matanuska/telemetry`. However, `@matanuska/telemetry` should not have a _dependency_ on a given logging library - the implementation should be inline as to avoid instrumentation ordering bugs. Moreover, the `OTEL_LOG_LEVEL` behavior is relatively difficult to customize and override.

### Debugging and Inspecting

Finally, I want to reiterate that the jury is still out in terms of whether or when debugging will be more useful. I deeply suspect that I'll find the debugger more useful in many of the situations I was trying to solve with my `Tracer` previously. But until I actually have those issues and attempt to use Node's debugging facilities, it will be a mystery. For now, I'm going to include telemetry as a feature, and see where it leads.
