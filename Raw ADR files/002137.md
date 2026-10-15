# ADR 001: Playback State Management via Web Workers

* **Status:** Accepted
* **Date:** 2025-12-26

## Context
The core functionality of HyperReps is the ability to play specific segments (millisecond-accurate "cuts") of Spotify tracks in a sequence. A significant portion of the user base will access the application via mobile browsers. Mobile operating systems (iOS and Android) aggressively throttle JavaScript execution on the main thread when the browser tab is backgrounded or the screen is locked to save battery.

However, the **Spotify Web Playback SDK** requires access to the DOM (`window`, `document`) for Encrypted Media Extensions (DRM) and therefore *must* run on the main UI thread.

If we run the playback logic (timers, skip checks) on the main thread, the timer will drift or stop completely when the phone is locked, causing the mix to hang or fail to skip to the next track.

## Decision
We will implement a **"Conductor Pattern"** using a dedicated **Web Worker**.

1.  **The Worker (Conductor):** Runs the "Mix Clock." It holds the state machine, calculates the current position in the mix, and determines when a transition is needed. It runs on a separate thread which is not throttled as aggressively by mobile OSs as long as audio is playing.
2.  **The Main Thread (Musician):** Acts strictly as a dumb terminal for the Spotify SDK. It receives commands from the Worker (e.g., `PLAY_TRACK_URI`, `SEEK_TO`) and executes them. It sends status updates (e.g., `AUDIO_STARTED`) back to the Worker for drift correction.

## Consequences
* **Positive:** Playback timing remains accurate and functional even when the device is locked or the user switches tabs.
* **Positive:** "Separation of Concerns" ensures the complex state logic is decoupled from the UI rendering logic.
* **Negative:** Increases complexity of the codebase due to asynchronous message passing.
* **Negative:** Debugging Web Workers is slightly more difficult than debugging main-thread code.
* **Negative:** We must implement "Drift Correction" logic to account for the latency between the Worker sending a command and the audio actually starting.