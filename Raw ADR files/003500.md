# ADR-1: Overall Tech Stack

**Status:** Accepted

## Context

The calculation works and is implemented in python. It would not long to recreate it in any other given language though. Now I want to 
settle on an initial tech stack for wrapping this in to an app. 

Requirements:

* quick development
* works in all app stores
* well known frameworks, such that I can get good AI support
* it should be cross-platform, as I want to maintain only one codebase
* I don't have a lot of logic overall and will not need a backend at all.


## Considered Options

* Kotlin Multiplatform
  * comes with Kotlin, which is a nice language that I already know due do my Java experience
  * comes with native UIs -> I would have to maintain two UIs for ios and android
  * perfect intellij support
  * would come with SwiftUI + Jetpack compose
* Flutter
  * relatively new framework, developed by google
  * comes with Dart, a language that I don't know at all yet
    * seems like a solid language, although not as popular as e.g. TypeScript/Kotlin
  * hot reload for fast development
  * intellij support
  * paints every pixel itself with Skia (skips the UIKit / Android View System)
* React Native
  * Can come in different forms: 
    * electron-react native
    * Capacitor
      * write pure web-react
      * more for web-teams
  * world-wide actually less popular than Flutter
  * -> I don't like that it's overly pushed and overpromotes itself
  * -> seems to me like it will stagnate over the next years
  * -> I will not use it

Overall it seems to me like
* react native is overhyped and in reality many of the apps that the framework claims to be used by don't use it
* modern apps tend to go without cross-platform frameworks overall and directly use Swift UI and Jetpack Compose
* ios has UIKit (phones, tables), AppKit (MacOS) at the bottom and android has Android View System / Android UI Toolkit
  * both are imperative
  * SwiftUI and Jetpack Compose are declarative toolkits
  * they use UIKit/ViewKit by translating to them at runtime and "drive" these legacy engines


## Decision

The decision came down to (Kotlin Multiplatform + SwiftUI + Jetpack Compose) vs Flutter. I decided to go with Flutter because
* perfect native feeling isn't that important to me
* less code to maintain
* hopefully higher development speed
* the UI makes up almost the entire application, as the app-logic is very small

## Consequences
I will have to learn Dart.
