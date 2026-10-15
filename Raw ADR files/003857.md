# 7. Use ConversationCollection

Date: 2024-07-03

## Status

Accepted

## Context

I have been having some problems when using this.

There are two types that sre similar:

- `ConversationModelCollectionType`
- `window.Whisper.ConversationCollection`

```ts
// ts/ConversationController.ts
export class ConversationController implements IConversationController {
  constructor(private _conversations: ConversationModelCollectionType) {}
}
```

`ConversationController` is actually initialised like this:

```ts
// ts/ConversationController.ts
export function start(): void {
  log.info("ts/ConversationController.ts start", new Error().stack);
  const conversations = new window.Whisper.ConversationCollection();

  window.ConversationController = new ConversationController(conversations);
  window.getConversations = () => conversations;
}
```

So in reality it uses `window.Whisper.ConversationCollection`.

We have been doing this:

```ts
// ts/ports/DevNullConversationController.ts
export class DevNullConversationController implements IConversationController {
  private readonly _conversations: ConversationModelCollectionType =
    new ConversationModelCollectionType();

  get conversations(): ConversationModelCollectionType {
    return this._conversations;
  }

  constructor(...conversations: Array<ConversationAttributesType>) {
    conversations.forEach(conversation =>
      this._conversations.add(this.create(conversation))
    );
  }
```

I think this may be the source of issues like:

```shell
Model caught error triggering add event: TypeError: conversation.format is not a function
    at ConversationModelCollectionType.<anonymous> (/home/ben/sauce/Signal-Desktop/preload.bundle.js:317921:56)
    at triggerEvents (/home/ben/sauce/Signal-Desktop/preload.bundle.js:320076:42)
    at ConversationModelCollectionType.trigger (/home/ben/sauce/Signal-Desktop/preload.bundle.js:320007:5)
    at ConversationModelCollectionType._onModelEvent (/home/ben/sauce/Signal-Desktop/preload.bundle.js:69325:24)
    at triggerEvents (/home/ben/sauce/Signal-Desktop/preload.bundle.js:320085:42)
    at Backbone3.Model.trigger (/home/ben/sauce/Signal-Desktop/preload.bundle.js:320009:5)
    at ConversationModelCollectionType.set (/home/ben/sauce/Signal-Desktop/preload.bundle.js:69064:21)
    at ConversationModelCollectionType.add (/home/ben/sauce/Signal-Desktop/preload.bundle.js:68959:23)
    at DevNullConversationController.getOrCreate (/home/ben/sauce/Signal-Desktop/preload.bundle.js:307766:46)
    at DevNullConversationController.maybeMergeContacts (/home/ben/sauce/Signal-Desktop/preload.bundle.js:308028:30)
```

I think possibly `ConversationModelCollectionType` does not return the expected type.

## Decision

### Have `DevNullConversationController` use `window.Whisper.ConversationCollection`, too

## Consequences

What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.
