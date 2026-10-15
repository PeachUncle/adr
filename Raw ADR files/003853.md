# 2. Identifying ports

Date: 2024-06-20

## Status

Accepted

## Context

We know that most of the work is happening in `ts/background.ts`, where `window.startApp` is.

The actual creation of the React part looks like this:

```ts
// Around line 1455
render(
  window.Signal.State.Roots.createApp(window.reduxStore),
  document.getElementById("app-container")
);
```

Notice there are no dependencies configured here, that's because dependencies (adapters) are read directly from `window`.

For example, you can see here that `refreshRemoteConfig` is failing:

```ts
VM113 preload.bundle.js:138231 Uncaught (in promise) HTTPError: promiseAjax: error response; code: 401
    at makeHTTPError (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138231:10)
    at _promiseAjax (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138165:11)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async _retryAjax (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138211:12)
    at async _ajax (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138513:16)
    at async Object.getConfig (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138627:22)
    at async refreshRemoteConfig (/home/ben/sauce/Signal-Desktop/preload.bundle.js:36371:54)
    at async Object.initRemoteConfig (/home/ben/sauce/Signal-Desktop/preload.bundle.js:36278:3)
Original stack:
Error
    at _outerAjax (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138224:19)
    at _ajax (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138513:22)
    at Object.getConfig (/home/ben/sauce/Signal-Desktop/preload.bundle.js:138627:28)
    at refreshRemoteConfig (/home/ben/sauce/Signal-Desktop/preload.bundle.js:36371:67)
    at invokeFunc (/home/ben/sauce/Signal-Desktop/preload.bundle.js:4276:28)
    at leadingEdge (/home/ben/sauce/Signal-Desktop/preload.bundle.js:4283:30)
    at debounced (/home/ben/sauce/Signal-Desktop/preload.bundle.js:4332:24)
    at Object.initRemoteConfig (/home/ben/sauce/Signal-Desktop/preload.bundle.js:36278:9)
    at /home/ben/sauce/Signal-Desktop/preload.bundle.js:316529:377
```

The application is started by the HTML page calling `startApp`, which calls:

```ts
// ts/background.ts

//...

window.Signal.RemoteConfig.initRemoteConfig(server);

//...
```

## Decision

### Things assigned to `window` that may be adapters

If we assume that all dependencies are sourced from `window`, then finding usages of `window` is a good start.

Looking in `./ts/background.ts` because that's where `startApp` is.

A good place to start is anything mentioned in `ts/background.ts` that starts with `window`:

```shell
grep -Eiro "window\.[^\.,;)(+]+" ./ts/background.ts | sort | uniq
window.addEventListener
window.ConversationController
window.dispatchEvent
window.document
window.Events
window.Events = createIPCEvents
window.flushAllWaitBatchers
window.getAccountManager
window.getAccountManager =
window.getBuildExpiration
window.getConversations
window.getEnvironment
window.getServerTrustRoot
window.getSfuUrl
window.getSocketStatus
window.getSocketStatus =
window.getSyncRequest
window.getSyncRequest =
window.getTitle
window.getVersion
window.i18n
window.initialTheme === ThemeType
window.IPC
window.isAfterVersion
window.isBeforeVersion
window.masterKey'
window.platform === 'darwin'
window.reduxActions
window.reduxActions?
window.reduxStore
window.sendChallengeRequest
window.setImmediate = window
window.Signal
window.SignalCI
window.SignalContext
window.SignalProtocolStore
window.startApp = startApp
window.storage
window.storage isn't ready yet
window.storageKey'
window.systemTheme
window.textsecure
window.waitForAllBatchers
window.waitForAllWaitBatchers
window.waitForEmptyEventQueue = waitForEmptyEventQueue
window.WebAPI
window.Whisper

```

Not all of these represent dependencies, but these ones defintely do:

- `window.ConversationController`
- `window.getAccountManager`
- `window.Signal`
- `window.storage`
- `window.WebAPI`
- `window.Whisper`

### Try to substitute `window.Signal`

One step in `startApp` is loading configuration, which is does using `window.Signal`.

```ts
// ts/background.ts
void window.Signal.RemoteConfig.initRemoteConfig(server);
```

Based on where `window.Signal` is assigned:

```ts
// ts/windows/main/phase2-dependencies.ts
window.Signal = setup({
  Attachments,
  getRegionCode: () => window.storage.get("regionCode"),
  logger: log,
  userDataPath,
});
```

`window.Signal` has type `SignalCoreType`:

```ts
// ts/window.d.ts
export type SignalCoreType = {
  AboutWindowProps?: AboutWindowPropsType;
  Crypto: typeof Crypto;
  Curve: typeof Curve;
  Data: typeof Data;
  DebugLogWindowProps?: DebugLogWindowPropsType;
  Groups: typeof Groups;
  PermissionsWindowProps?: PermissionsWindowPropsType;
  RemoteConfig: typeof RemoteConfig;
  ScreenShareWindowProps?: ScreenShareWindowPropsType;
  Services: {
    calling: CallingClass;
    backups: BackupsService;
    initializeGroupCredentialFetcher: () => Promise<void>;
    initializeNetworkObserver: (network: ReduxActions["network"]) => void;
    initializeUpdateListener: (updates: ReduxActions["updates"]) => void;
    retryPlaceholders?: RetryPlaceholders;
    lightSessionResetQueue?: PQueue;
    storage: typeof StorageService;
  };
  SettingsWindowProps?: SettingsWindowPropsType;
  Migrations: ReturnType<typeof initializeMigrations>;
  Types: {
    Message: typeof Message2;
    Address: typeof Address;
    QualifiedAddress: typeof QualifiedAddress;
  };
  Components: {
    ConfirmationDialog: typeof ConfirmationDialog;
  };
  OS: OSType;
  State: {
    Roots: {
      createApp: typeof createApp;
    };
  };
  conversationControllerStart: () => void;
  challengeHandler?: ChallengeHandler;
};
```

We can modify `ts/windows/main/phase2-dependencies.ts` to substitute an alternative version.

This can be toggled at run time.

## Consequences

Swapping dependencies will allow us to exercise the application without needing real data or real connections.

This means we can set up the UI for tests.

## Notes

### Cannot find module '/home/ben/sauce/Signal-Desktop/app/ts/sql/mainWorker.js'

```shell
npx electron app/main.js

Set Windows Application User Model ID (AUMID) { AUMID: 'org.whispersystems.signal-desktop' }
config: Using config source default.json
config: Using config source development.json
NODE_ENV development
NODE_CONFIG_DIR /home/ben/sauce/Signal-Desktop/config
NODE_CONFIG {}
ALLOW_CONFIG_MUTATIONS undefined
HOSTNAME undefined
NODE_APP_INSTANCE undefined
SUPPRESS_NO_CONFIG_WARNING undefined
SIGNAL_ENABLE_HTTP undefined
userData: /home/ben/.config/Signal-development
config/get: Successfully read user config file
config/get: Successfully read ephemeral config file
making app single instance
Unhandled Error: Error: Cannot find module '/home/ben/sauce/Signal-Desktop/app/ts/sql/mainWorker.js'
    at Module._resolveFilename (node:internal/modules/cjs/loader:1151:15)
    at Module._load (node:internal/modules/cjs/loader:992:27)
    at c._load (node:electron/js2c/node_init:2:13672)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:150:12)
    at MessagePort.<anonymous> (node:internal/main/worker_thread:186:26)
    at [nodejs.internal.kHybridDispatch] (node:internal/event_target:826:20)
    at exports.emitMessage (node:internal/per_context/messageport:23:28)
Unhandled Error: Error: Cannot find module '/home/ben/sauce/Signal-Desktop/app/ts/sql/mainWorker.js'
    at Module._resolveFilename (node:internal/modules/cjs/loader:1151:15)
    at Module._load (node:internal/modules/cjs/loader:992:27)
    at c._load (node:electron/js2c/node_init:2:13672)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:150:12)
    at MessagePort.<anonymous> (node:internal/main/worker_thread:186:26)
    at [nodejs.internal.kHybridDispatch] (node:internal/event_target:826:20)
    at exports.emitMessage (node:internal/per_context/messageport:23:28)
Unhandled Error
Error: Cannot find module '/home/ben/sauce/Signal-Desktop/app/ts/sql/mainWorker.js'
    at Module._resolveFilename (node:internal/modules/cjs/loader:1151:15)
    at Module._load (node:internal/modules/cjs/loader:992:27)
    at c._load (node:electron/js2c/node_init:2:13672)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:150:12)
    at MessagePort.<anonymous> (node:internal/main/worker_thread:186:26)
    at [nodejs.internal.kHybridDispatch] (node:internal/event_target:826:20)
    at exports.emitMessage (node:internal/per_context/messageport:23:28)

```

it seems that this command

```shell
npx electron app/main.js
```

Causes `Electron` to use `./app` as a root directory.

Only solution I can find is to change this:

```json
"main": "app/main.js",
```

to:

```json
"main": "app/main-bare.js",
```

### called ipcRenderer.sendSync() with '{name}' channel without listeners.

```json
{
  "level": 40,
  "time": "2024-06-20T00:48:02.716Z",
  "msg": "WebContents #1 called ipcRenderer.sendSync() with 'get-config' channel without listeners."
}
```

I think this is because you have to add channel handlers:

```ts
// app/main-bare.ts
ipc.on("get-config", async (event) => {
  const theme = await getResolvedThemeSetting();

  // ...
});
```

### prepareUrl: Failed to parse renderer config

```
Unhandled Promise Rejection

Error: prepareUrl: Failed to parse renderer config {"formErrors":[],"fieldErrors":{"appStartInitialSpellcheckSetting":["Required"],"reducedMotionSetting":["Required"]}}
    at IpcMainImpl.<anonymous> ([REDACTED]/app/main-bare.js:715:11)
```
