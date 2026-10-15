# ADR 0001: Voice Input Interaction and Architecture

## Context
The Voice Input (STT) functionality initially suffered from complex state management dentro of the UI widget, leading to issues with session restarts, text duplication, and hardware stalls.

## Decision
We decided to rebuild the Voice Input feature from scratch using a **Controller-based Architecture** to decouple the speech engine logic from the UI.

### Architectural Rules
1.  **Independent Controller**: All Speech-to-Text logic is encapsulated in `SpeechRecognitionController.dart`.
2.  **State Management**: The controller extends `ChangeNotifier`, allowing widgets to listen for updates in a standard Flutter way.
3.  **Buffer Isolation**: We use `_committedText` and `_currentSessionText` within the controller to prevent overlaps and duplication.
4.  **Session Tracking**: Unique `sessionId` tracking ensures that late results from previous asynchronous sessions are ignored.
5.  **Hybrid Restart & Stall Detection**: 
    - **Stall Detection (Auto-Off)**: Automatically toggles **Off** if no speech was heard during a session, providing a graceful exit.
    - **Grace Period (1s)**: Before restarting or stopping, the controller waits 1 second to ensure all trailing words (final results) are captured from the engine.
    - This provides the best of both worlds: long-form dictation support through natural pauses, and a graceful exit when finished or when the system hangs.
6.  **UI Decoupling**: `VoiceTextField.dart` is strictly a UI component that listens to the controller and updates the `TextEditingController`.

### UX Decisions
1.  **Toggle Interaction**: A single tap on the mic icon starts/stops the process.
2.  **Interactive Selection**: Default system text interactions (long-press, copy-paste) are fully supported during dictation.
3.  **Visual Feedback**: A pulse-animated "Listening" hint and auto-scroll ensure the user feels "heard" by the system.
4.  **Deferred Permissions**: Microphone permissions are requested only when the user first taps the microphone button.

## Consequence
This architecture significantly improves robustness, eliminates duplication bugs, and makes the voice input feature extensible for future additions like multi-language support or sound-based UI feedback.
