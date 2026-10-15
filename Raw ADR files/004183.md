# ADR 0001: QML-Code-Model-False-Positives-in-Qt-Creator

- **Status**: Accepted
- **Date**: 2025-09-06
- **Owners**: Tasqly Team
- **Related**: Phase0 — Slice3 (Navigation, Loader & Fallback)
- **Tags**: qml, ide, qtcreator, code-model

---

## Context
During the implementation of **Slice 3 (Navigation, Loader & Fallback)**, a critical observation was made while working with **SmartFallback.qml** and **SmartPageLoader.qml**.  
Qt Creator (and QML Code Model) was showing **false-positive errors** like:

Invalid property name "onRetry". (M16)

yaml
Copy code

Even though:
- The `signal retry()` was correctly defined in `SmartFallback.qml`.
- The usage `onRetry: { ... }` was valid in `SmartPageLoader.qml`.

After restarting **Qt Creator**, the error disappeared.  
This proves the issue is not in our code but in the **QML code model cache** inside Qt Creator.

---

## Problem
- Qt Creator sometimes **caches QML type information incorrectly** after adding/modifying signals or properties.  
- This leads to **false red underlines** and warnings/errors in the IDE, even though the project compiles and runs fine.  
- Developers may waste time debugging non-existent issues.

---

## Decision
We will document this behavior officially and adopt the following **policy** when such errors occur:

1. ✅ **Verify runtime first**: If the app compiles and runs without error, treat IDE errors as potential false-positives.  
2. 🔄 **Reset QML code model**: Use menu `Tools → QML/JS → Reset Code Model` in Qt Creator to clear cache.  
3. 🚪 **Restart IDE**: If the issue persists, restart Qt Creator (forces full reindex of QML).  
4. 🧹 **Clean build**: If restarting doesn't help, delete the `build/` folder and reconfigure with CMake presets.  
5. 📝 **Document recurrence**: If repeatedly reproducible, log it under ADRs for tracking.  

---

## Consequences
- Developers will know that not all IDE errors are actual code issues.  
- Saves time by preventing unnecessary debugging of false errors.  
- Ensures we distinguish between **editor warnings** vs **runtime/compiler errors**.

---

## References
- Qt Creator Docs: [Reset QML/JS Code Model](https://doc.qt.io/qtcreator/creator-how-to-rescan-qml.html)  
- Internal Observation: Slice3 / SmartFallback integration (2025-09-06)