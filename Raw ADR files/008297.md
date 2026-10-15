# Creating and Storing posts

## Problem Statement

We need a consistent method of interfacing with some persistant storage, to keep track of users and their posts, aswell as a way to search for specific posts within that storage.

## Discussed Solutions

### Storage

- External Database
    - Not enough time to learn how to use and integrate an external database, out side the scope of this class

- Local Storage
    - Is persistant, and can store up to 10mb which should be enough for storing simple text posts.
    - It is limiting if we wanted to host multimedia posts, like images or videos.

### Creating Posts

post object should be a custom web-component similar to the recipe articles from lab

### Multiple Users

- Could assign a user variable to posts then when loading in all the posts, could simply filter out the posts that don't match the current user

- Could store each users post array seperately in local storage and only pull the current users post.
    - This is quicker as we don't need to sort anything out later

## Design Decisions

### Storage:

Local Storage : 10mb

Stores key value pairs
all keys and all values must be strings

```
let posts = [] of posts
value = JSON.stringify(posts)
key = "post_list"
window.localStorage.setItem(key, value)
window.localStorage.getItem(key) -> value

JSON.parse(value) -> original array object
```


### Multiple Users:

Store a user into the database like this:

```
createAccount(username, password)
{
    setItem(username, password)
}
```

```
login(username, password) 
{
    getItem(username) -> actual_password
    return password == actual_password
    // matches given password with stored password
}
```

### Creating Post Objects:

A Post is simply a set of data which can be attached to a custom HTMLElemnt post object (journal-post).  This set of data should be of the format:
```
data = 
{
    "id" = id
    "label" = label // custom user labels?, enumerator, custom colors for labels?
    "text" = text   // Character limit?
    "dateCreated" = MMDDYYYY 
    "dateModified" = null | MMDDYYYY
}
```


### Storing Posts:

key for a given users posts: username+"post_list"

```
posts = getItem(username+"post_list") 
// posts = list of data objects that can be used to make journal-post HTML elements
```

## Things to be decided :

### Post IDs

Currently to get a unique post ID, we have a number set in localStorage as the nextPost ID. Everytime we create a post, we pull that number and use it as our post ID, then we add 1 and put it back into storage.

This has its shortcomings as deleting posts doesn't free up their ID for use, I don't think there is enough storage space to store posts to the point we would run out of IDs however, theoretically the system could be broken by creating and deleting posts until we reach integer overflow and reset the ID to 0.  This could result in two posts having the same ID would could cause problems.

### Unique labels

How should labels be stored in the post object, right now they are just expected to be strings.  Could have a list of labels, and store their index in that list which could make it possible to add unique labels.  Mabey we have label objects instead of just like string tags, that way we could store different attributes to the labels, like we want users to customize the color of posts with specific labels.

