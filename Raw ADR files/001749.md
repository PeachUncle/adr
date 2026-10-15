# 📄 Architecture Decision Record: Navigation Strategy

## Table of Contents

- [Summary](#summary)
- [Issue](#issue)
- [Decision](#decision)
- [Status](#status)
- [Details](#details)
  - [Assumptions](#assumptions)
  - [Constraints](#constraints)
  - [Positions: Comparative Analysis](#positions-comparative-analysis)
- [Argument](#argument)
- [Implications](#implications)
- [Related Decisions](#related-decisions)
- [Related Requirements](#related-requirements)
- [Related Artifacts](#related-artifacts)
- [Related Principles](#related-principles)
- [Notes](#notes)
- [References](#-references)

---

## Summary

We need to define a robust internal navigation strategy for **FitMind AI** that supports transitions between key sections such as login, dashboard, workouts, AI recommendations, and community features. The navigation system must be scalable, intuitive, compatible with React Native, and adaptable to mobile usage patterns.

---

## Issue

The app consists of multiple functional modules that require structured screen transitions and top-level tab access. The navigation must:

- Provide **stacked navigation** for workflow steps (e.g., Login → Dashboard → Details),
- Offer **tab navigation** for global access to core features (e.g., Workouts, AI Coach, Progress),
- Support **deep linking**, **authentication flows**, and **back-button handling** on Android,
- Work well with React Native and support modular, maintainable code.

We must choose between:

- React Navigation
- React Native Navigation (Wix)
- Custom Router

---

## Decision

✅ We will use **React Navigation** with a **hybrid approach** combining:

- **Stack Navigation**: for transitions within a workflow
- **Bottom Tab Navigation**: for primary app sections

---

## Status

**Decided (Final)**

---

## Details

### Assumptions

- App is built using React Native.
- We expect 6+ main screens (login, register, workouts, dashboard, settings, community).
- The app will evolve, so nested navigators and dynamic routing must be supported.
- The team prefers a declarative navigation pattern compatible with component-based UI.

---

### Constraints

- Bootstrap offers no built-in mobile navigation features.
- Navigation complexity must be minimized due to project timeline (10 weeks).
- Support for Android back navigation and dynamic routes is necessary.

---

## Positions: Comparative Analysis

| Navigation Library                | Pros                                                                                                                                                                         | Cons                                                                                                                                    |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **React Navigation**              | - Official React Native library <br> - Highly modular (Stack, Tab, Drawer) <br> - Strong community and documentation <br> - Supports nested navigation, guards, deep linking | - Pure JavaScript navigation (not native-level transitions) <br> - May require linking with native dependencies (e.g., gesture handler) |
| **React Native Navigation (Wix)** | - Native performance and transitions <br> - Better for animations <br> - Good support for native modules                                                                     | - More complex to configure and integrate <br> - Higher learning curve <br> - Slower iteration for new devs                             |
| **Custom State Router**           | - Fully customizable <br> - Lightweight and decoupled                                                                                                                        | - Time-consuming to build <br> - High maintenance <br> - No ecosystem support                                                           |

---

## Argument

React Navigation is the most balanced choice for **FitMind AI**. It supports:

- Modular architecture via navigators (stack, tab, drawer),
- Easy setup with Expo or React Native CLI,
- Smooth learning curve for a student team with limited setup time,
- Excellent compatibility with other React Native libraries.

While **React Native Navigation (Wix)** is excellent for animations and native transitions, it introduces **added complexity** for integration, which may slow down the team’s development in a time-limited academic project.

A **custom solution** would take too much time to build, test, and maintain without bringing significant benefits.

---

## Implications

- Simple, maintainable routing using a widely adopted library
- Easily extensible with drawer navigation or modal flows in future versions
- Consistent user experience across Android (and future iOS)
- Easier testing and code modularization

---

## Related Decisions

- Development Framework: React Native
- CSS Framework: Bootstrap
- Project Timeline: 10 weeks, limited resources

---

## Related Requirements

- Authentication and onboarding flow
- Tabbed UI for accessing workouts, dashboard, settings
- Screen transitions and user session tracking

---

## Related Artifacts

- `Navigation.js`, `routes/index.js`
- Screens: `LoginScreen.js`, `Dashboard.js`, `WorkoutScreen.js`
- Navigators: `TabNavigator.js`, `StackNavigator.js`

---

## Related Principles

- **Simplicity**: Declarative and well-documented
- **Scalability**: Easily extendable for future needs
- **Usability**: Familiar mobile patterns like bottom tabs and stacks

---

## Notes

- In Phase 2, we will add:
  - Custom transition animations (React Native Reanimated)
  - Persistent user sessions (with AsyncStorage)
  - Dynamic routes for personalized user content

---

## 📚 References

- [React Navigation Documentation](https://reactnavigation.org/)
- [React Navigation vs React Native Navigation – LogRocket](https://blog.logrocket.com/react-navigation-vs-react-native-navigation/)
- [React Navigation Performance Overview – Expo](https://reactnative.dev/docs/next/performance#ui-frame-rate-main-thread)
