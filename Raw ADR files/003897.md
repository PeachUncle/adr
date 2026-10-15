## Choosing the Web Framework:

### Context and Problem Statement:
AML require a clean user-interface to interact with the system. In order to develop that, we require a front-end
framework to contain all of this code, and render it on the website. 

#### Decision Drivers:

* Scalability - AML hopes to increase their size by 10% annualy.
* Maintainability - Simplicity.
* Reusability - Code elements should be reusable across the project. Things like forms or buttons for example.
* Clear Codebase - This falls under Maintainability, but ensuring the code is clean and readable is very important for a maintainable system. Easy to manage code is clean code, and clean code is quick to edit.
* SSR - Server-side rendering allows for less loading time and bottlenecking from the framework itself.

#### Considered Options:

* [NextJS](https://nextjs.org/) - Front-end Web Framework.
* [Nuxt](https://nuxt.com/) - Vue Framework.
* [React](https://react.dev/) - React | Too verbose and messy. 
* [Vue](https://vuejs.org/) Similar to react, verbose and not very maintainable.
* [SvelteKit](https://kit.svelte.dev/) - Component-based Framework with Global State Management.

### Decision Outcome: 

#### SvelteKit.
Chosen because:

* The majority of our team have experience inside SvelteKit. 
* The documentation and integration of other technologies is also fantastic, although the stack is new, it's very well adopted.
* The modular methodology of SvelteKit allows for easy maintenance and development.
* Global state stops the TS from getting messy and having Memory Race issues.

### Consequences:
* Components are more modular, this allows for reusable code, easier styling and less bloat.
* The code will be easier to maintain.
* The group will have an easier time picking up the framework and coding proficiently.
* Some members of the group will struggle to pick up the technology, but through on-boarding this shouldn't pose a problem.
* Compatability with external technologies is now limited to PureJS and SvelteKit integrations, no React components.
* We are now able to use more complicated external packages in conjunction with SvelteKit to remove boilerplate.

Example:
Component.svelte:
```html
  <div>
    <h1>Some component</h1>
  </div>
```
```html
  <script>
    import SomeComponent from "./Components/SomeComponent.svelte"
  </script>

  <SomeComponent />
```
