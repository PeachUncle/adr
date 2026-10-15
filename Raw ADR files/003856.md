# 5. Replace runtime type imports

Date: 2024-06-28

## Status

Accepted

## Context

`ts/models/conversations.ts` imports implementation functions from `window.Signal`at compile time.

We have found that this fails when we try and use the `ConversationModel` constructor because `window.Signal` is undefined due to constants being defined by diretly referencing `window.Signal`.

For example:

```ts
// ts/models/conversations.ts
const {
  deleteAttachmentData,
  doesAttachmentExist,
  getAbsoluteAttachmentPath,
  getAbsoluteTempPath,
  readStickerData,
  upgradeMessageSchema,
  writeNewAttachmentData,
} = window.Signal.Migrations;
```

This is an unusual construct.

We want to use the `ConversationModel` constructor in order to populate `DevNullConversationController` with artificial conversations.

All of these references are being resolved at compile time and so depending on `window.Signal.Migrations` cannot work.

```ts
// ts/ports/DevNullConversationController.ts
export class DevNullConversationController implements IConversationController {
  private readonly _conversations: ConversationModelCollectionType =
    new ConversationModelCollectionType();

  constructor() {
    console.log('[DevNullConversationController] started');

    // [!] Fails at runtime because of this in `ts/models/conversations.ts`
    //
    //    const { Message } = window.Signal.Types;
    //
    // Solution is to just import `hasExpiration` and `VERSION_NEEDED_FOR_DISPLAY`.
    //
    const c = new ConversationModel(
      /* ConversationAttributesType */ {
        id: 'id-1',
        type: 'private',
        version: 1,
        // addedBy: 'Ben',
        // description: 'A B C',
        // groupId: 'group-1',
        // members: ['Ben'],
      }
    );

    this._conversations.add(c);
  }
```

Solution is to inline these usages and remove those `const` assignments.

### `export class ConversationModel extends window.Backbone.Model`

This is another issue:

```ts
export class ConversationModel extends window.Backbone
  .Model<ConversationAttributesType> {
  //...
}
```

Trying this:

```ts
import { Model } from "backbone";

export class ConversationModel extends Model<ConversationAttributesType> {
  //...
}
```

### window.Whisper.ConversationCollection = window.Backbone.Collection.extend

Hmm.

## Decision

### Move `ConversationModel` to its own file

This resolves problems like:

```ts
window.Whisper.ConversationCollection = window.Backbone.Collection.extend;
```

because we can import `ConversationModel` without inluding that stuff.

### Inline `window.Signal.Migrations` usages

This means we can get rid of these types of declarations:

```ts
// ts/models/conversations.ts
const {
  deleteAttachmentData,
  doesAttachmentExist,
  getAbsoluteAttachmentPath,
  getAbsoluteTempPath,
  readStickerData,
  upgradeMessageSchema,
  writeNewAttachmentData,
} = window.Signal.Migrations;
```

## Consequences
