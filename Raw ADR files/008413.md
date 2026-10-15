---
title: [Storage Api ADR] - [Proposing IndexDB]
status: Proposed
date: 05-10-2025
decision-makers: [Thanh-Long (T.L.) Nguyen-Trong, Aruthan Raveendra, Yilong Chen]
---

## Summary

**One-sentence overview of the decision.**
We will store card data in as JSON documents tied to user accounts in IndexDB.

---

## Context and Problem Statement

The main quesiton: How will we store files, songs, links, pictures, other information or data?

This can be broken down into two requirements: storing structured data, such as title, description, date and time posted, and unstructured elements such as pictures, videos, and music.

While we will do not need to store all examples above in the final product, we need to make sure that we _can_ store all the above in the event that we choose to include those features.

## Considered Options

- Cookies
- WebStorage
- IndexDB
- Cache API

## Decision Outcome

Chosen option: "IndexDB", because comes out best (see "Pros and Cons of the Options" below).

### Consequences

- Good, supports storage of structured and unstructured data
- Good, much higher storage capacity than other local storage APIs (since we are restricted to only local dependencies)
- Good, data isn't lost when the browser is closed

- Bad, while supported on many browsers, there are many different restrictions accross the browsers
- Bad, writing clean and maintainable code using this API can be challenging

### Confirmation

- Check project dependencies, IndexDB should appear.
- Collect experience with IndexDB in sprint reviews and retrospectives to determine if the gains pros and cons evaluation below?
- Have a trial run with other teams in charge of determining datatypes of how to store location, images, and other needs.

## Pros and Cons of the Options

### Index DB

[Homepage](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)

Example:

```js
const openRequest = indexedDB.open("InstaPostsDB", 1);

openRequest.onupgradeneeded = function (e) {
  const db = e.target.result;
  if (!db.objectStoreNames.contains("posts")) {
    const store = db.createObjectStore("posts", {
      keyPath: "id",
      autoIncrement: true,
    });
    store.createIndex("title", "title", { unique: false });
  }
};

openRequest.onsuccess = function (e) {
  const db = e.target.result;
  const fileInput = document.querySelector("#imageInput");

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    // Convert Blob to base64 for JSON storage
    const reader = new FileReader();
    reader.onload = function (event) {
      const base64String = event.target.result;

      const post = {
        title: "Beach Day",
        caption: "Sunny and chill vibes ☀️🏖️",
        imageBase64: base64String, // now fully structured
      };

      const tx = db.transaction("posts", "readwrite");
      const store = tx.objectStore("posts");
      store.add(post);

      tx.oncomplete = () => console.log("Structured JSON post added!");
      tx.onerror = () => console.error("Failed to add post.");
    };

    reader.readAsDataURL(file); // This returns a base64 string
  });
};
```

- Good, because structured data uses objectStore with key paths and indexes, enabling efficient retrieval and filtering (e.g., by title).
- Good, satisfies requirements of storing structured and unstructured elements
- Bad, because complex assertions tend to get hard to read

### Webstorage

[Homepage](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)

- Good, because Simple and Intuitive API - Easy-to-use key/value interface with setItem, getItem, and removeItem.
- Good, Built-in Browser Support - Widely supported across all modern browsers without requiring additional libraries.
- Bad, Synchronous API - Blocks the main thread—can cause performance issues with large data.
- Bad, Limited Capacity - Typically capped at 5–10 MB per origin—unsuitable for large datasets or files.

### Cookies

[Homepage](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)

Example:

```json
document.cookie = "username=joe; expires=Fri, 31 Dec 2025 23:59:59 UTC; path=/";
```

- Good: **Session Management**

  Ideal for maintaining user sessions (e.g., login state, shopping carts).

- Bad: **Small Size Limit**

  Typically limited to ~4KB per cookie and a maximum number of cookies per domain (~50–100).

- Bad: **Performance Impact**

  Sent with every request—even static resources—potentially slowing down page loads.

- Bad: **Limited Storage Use Cases**

  Poor fit for large or complex data structures (unlike `localStorage` or `IndexedDB`).

## More Information

GFor more information on each technology, refer to this website: <https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria>.
