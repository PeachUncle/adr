# ADR-002: Use Dictionaries Instead of Conditional Statements

## Status
Accepted

## Context
CharacterCraft Lite includes multiple document-generation modules that build markdown or text content from user-selected options (e.g., communication styles, feedback styles, etc.).

Originally, the logic relied on long `if-else` or `switch` statements to check the selected value and return an appropriate response block. These blocks often included markdown templates or reusable text snippets.

As the number of options increased, this approach became harder to read, harder to test, and harder to maintain.

## Decision
We will use **dictionaries (JavaScript objects)** to store string templates instead of using verbose conditional logic.

For example:
```js
const communicationStyleDocs = {
  "Formal and Professional": `### Formal and Professional Communication\n...`,
  "Friendly and Conversational": `### Friendly and Conversational Communication\n...`,
  "Balanced": `### Balanced Communication Approach\n...`,
};
```

We retrieve the output using a simple lookup:
```js
const doc = communicationStyleDocs[data.communicationStyle] || communicationStyleDocs['Balanced'];
```

This pattern is:
- More readable
- Easier to extend with new keys
- Reduces accidental duplication
- Can easily be adapted to use functions later (e.g., templates with interpolation)

We also explicitly store default/fallback values (e.g., "Balanced") in the dictionary, avoiding branching logic.

## Consequences
✅ Improves readability and reduces branching
✅ Makes future maintenance (e.g., updating copy) easier
✅ Allows reuse and modularisation of content blocks
✅ Supports fallback/defaults without extra conditionals
⚠️ Some strings are longer, so formatting the dictionary for readability is important
⚠️ Not ideal if logic per case becomes highly dynamic (future cases may move to arrow functions or factories)

## Future Considerations
- We may migrate to arrow-function templates later:
  ```js
  const communicationStyleDocs = {
    "Formal and Professional": (orgName) => `### Communication Guidelines for ${orgName}\n...`
  };
  ```
  But for now, we favor simplicity and avoid premature abstraction.

- Dictionaries could eventually be exported as standalone data files (e.g. JSON or .md) if required for a backend or SaaS version.

---

*This supports our principle: "Start simple, scale with purpose."*

*— [Michael Nygard](https://twitter.com/mtnygard)*
