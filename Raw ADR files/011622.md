# ADR-002: Tech Decision – React Native

**Date:** 2025-10-27
**Related ADRs:** [ADR-001: Offline-First Architecture](./adr-001-offline-first-decision.md)

---

## 1. Context

Following our decision to adopt an **Offline-First** architecture, we need to select a technology stack that enables:

- Reliable **offline data storage and synchronization**.  
- A **shared codebase** for multiple platforms (iOS and Android).  
- Integration with a **centralized backend server** and potential future **cloud hosting**.  
- Strong developer productivity and community support.  
- Long-term maintainability and ecosystem maturity.

We considered several options, including **React Native**, **Flutter**, **Web (PWA + Capacitor)**, **Kotlin Multiplatform**, and **native development**.

---

## 2. Options Considered

### ⚛️ React Native
- Language: **TypeScript / JavaScript**
- Platforms: iOS, Android (optionally Web via React Native Web)
- Offline Data: **WatermelonDB**, **Realm**, or **SQLite**
- Sync Options: Custom API sync, **CouchDB**, **Supabase**, **AWS Amplify DataStore**
- Pros:
  - Shared code between mobile platforms  
  - Mature ecosystem and large community  
  - Easy integration with existing web tech (React, Node.js, etc.)  
  - Cloud-ready with popular services like Supabase, Firebase, or AWS  
  - Strong developer tooling and hot reload
- Cons:
  - Occasional native module maintenance  
  - Slight performance gap vs fully native apps

---

### 🎯 Flutter
- Language: **Dart**
- Platforms: iOS, Android, Web, Desktop
- Offline Data: Drift / Hive / Isar
- Pros:
  - Single codebase for all major platforms  
  - Excellent performance and UI consistency  
- Cons:
  - Heavier build size and larger runtime  
  - Less direct code sharing with web or Node.js ecosystems  
  - Smaller enterprise adoption for backend-integrated workflows

---

### 🌐 React (PWA) + Capacitor / Tauri
- Pros:
  - Reuse existing web stack  
  - Good for desktop or web-first direction  
- Cons:
  - Limited offline background sync on iOS  
  - Weaker native UX for mobile users

---

### 🧩 Kotlin Multiplatform / Native
- Pros:
  - Best native integration and control  
- Cons:
  - Separate UI layers per platform  
  - Higher complexity, slower iteration speed

---

## 3. Decision

We will use **React Native** as the primary framework for the mobile application.

---

## 4. Rationale

- **Cross-platform development:**  
  React Native provides a **single codebase** for iOS and Android while maintaining native-level UI responsiveness.  

- **Offline-first compatibility:**  
  Mature solutions like **WatermelonDB**, **Realm**, and **SQLite** enable **local persistence** and **synchronization** with a central backend.

- **Cloud readiness:**  
  The JavaScript/TypeScript ecosystem integrates well with cloud services such as **Supabase**, **Firebase**, or **AWS Amplify**, ensuring the app can evolve toward cloud deployment.

- **Team familiarity:**  
  The React and JavaScript ecosystem aligns with our existing skills and tooling, improving productivity and onboarding speed.

- **Community and longevity:**  
  React Native has a strong open-source ecosystem, active contributors (Meta, Microsoft, Expo), and proven production use cases.