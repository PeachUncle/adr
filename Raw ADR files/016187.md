# 4. Architecture and Libraries

Date: 2025-05-22

## Status

Accepted

## Context

For building the application we should choose the Architecture pattern and select the 
libraries that will be used for building the core functionality. 

## Decision

- Architecture: MVVM, Unidirectional Data Flow
- Modern App Architecture recommendations:
  - A reactive and layered architecture.
  - Unidirectional Data Flow (UDF) in all layers of the app.
  - A UI layer with state holders to manage the complexity of the UI.
  - Coroutines and flows.
  - Dependency injection best practices.

### State Holder

State Holders - [ViewModel libraries](https://developer.android.com/topic/libraries/architecture/viewmodel)

Tags: #LiveData #ViewModel #Lifecycle

### Networking Library - Http Client

Retrofit - https://square.github.io/retrofit/, Retrofit turns your HTTP API into a Java (or Kotlin) interface.
OkHttp - https://github.com/square/okhttp, Http client
Moshi - https://github.com/square/moshi/, JSON parser

Alternatives:
- Ktor - https://ktor.io/

ref1: https://kashifahmad.medium.com/how-to-use-moshi-serialiizer-with-retrofit-mvvm-coroutine-in-kotlin-d3e5da6d0adb
ref2: https://bladecoder.medium.com/advanced-json-parsing-techniques-using-moshi-and-kotlin-daf56a7b963d
ref3: https://www.baeldung.com/java-json-moshi

### Images Loading Library

Coil - https://coil-kt.github.io/coil/, Coil is:

- **Fast**: Coil performs a number of optimizations including memory and disk caching, downsampling the image, automatically pausing/cancelling requests, and more.
- **Lightweight**: Coil only depends on Kotlin, Coroutines, and Okio and works seamlessly with Google's R8 code shrinker.
- **Easy to use**: Coil's API leverages Kotlin's language features for simplicity and minimal boilerplate.
- **Modern**: Coil is Kotlin-first and interoperates with modern libraries including Compose, Coroutines, Okio, OkHttp, and Ktor.

Coil is an acronym for: Coroutine Image Loader.

### Images View Library

Telephoto - https://github.com/saket/telephoto, `Drop-in` replacement for 
`Image()` composables featuring support for pan & zoom gestures and 
automatic sub‑sampling of large images that'd otherwise not fit into memory.

Alternatives:
- https://github.com/skydoves/landscapist

### Logs

Timber - https://github.com/JakeWharton/timber

### Dependency Injection

Dagger, Hilt - https://github.com/google/dagger, https://dagger.dev/hilt/
https://developer.android.com/training/dependency-injection/hilt-android#kts

Alternatives:
- Anvil - https://github.com/square/anvil
- Metro - https://github.com/ZacSweers/metro
- Kotlin-Inject-Anvil - https://github.com/amzn/kotlin-inject-anvil

ref1: https://dagger.dev/hilt/components.html
ref2: https://proandroiddev.com/integrate-kotlin-inject-anvil-to-tv-maniac-e1330c9cb566
ref3: https://slack.engineering/extending-anvil-for-fun-and-profit/
ref4: https://developer.android.com/training/dependency-injection/hilt-android#kts
ref5: https://proandroiddev.com/hilt-viewmodels-assisted-injection-aca2d6ee581d

### KSP vs KAPT

https://developer.android.com/build/migrate-to-ksp
https://github.com/google/ksp

## Consequences

Architecture dictates at least three levels of the abstractions: ui, domain and data.
The data layer that contains the business logic of your app and exposes application data.
The domain layer to simplify and reuse the interactions between the UI and data layers.

Skip features/modularization for simplifying the solution.

## References

- https://developer.android.com/topic/architecture