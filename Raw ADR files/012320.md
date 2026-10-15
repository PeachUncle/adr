[[All Docs](../index.md)]

# Maintaining web + desktop app simultaneously

More specifically how to maintain a web build (any frameowrk) and an electron build at the same time.
In this case I was open for any web app framework that would make this easy.
But if I want to use electron forge, I'm currently limited to webpack or vite.
So there seems to be no easy and direct way to use astro in combination with electron as far as I figured.
There seems to be this [astro-electron](https://github.com/Igloczek/astro-electron) tool but it's rather new.

So I tried with using
- Vite
- Typescript
- React
- Tanstack Router (see decision on [routing library](./routing_library.md)).

## Options

### Configure forge.config.ts to point to web app

When using Electron Forge with the vite + typescript template it automatically creates a forge.config.ts file. But this file does not point to a specific html or ts file for the rendering project. It only points to the vite.renderer.config.ts file. Which cannot be changed to another file outside the package apparently.

### Use @neote/web as a dependency

I tried to export the mainly relevant files from @neote/web - index.html and main.ts - from the web package and imported them in the desktop package.
All of these tries failed:

- Add a <script> that points to the @neote/web main.ts file directly
- Import the @neote/web main.ts file in the renderer.ts file
- Copy the main.ts code from @neote/web and only import App.tsx from @neote/web

All of these failed with weird dependency issues. For example that react-dom/client would not export `createRoot` (which I did not find a solution for - sometimes it worked and then not) or some other dependencies not working correctly.
I was able to fix all non react-dom issues by optimizing the vite.renderer.config.ts setting with

```
optimizeDeps: {
  // Ensure Vite pre-bundles the external package correctly.
  include: ["events", "spark-md5", "vuvuzela", "remove-accents", "react-dom"],
},
build: {
  commonjsOptions: {
    transformMixedEsModules: true,
    // This flag forces a default export to be added if the imported module is only named
    requireReturnsDefault: "auto",
  },
},
```

But then HMR would not work. This I was able to somehow fix with ...

```
server: {
  watch: {
    // Enable HMR whenever one of the other packages is updated
    ignored: ["!**/node_modules/@neote/**"],
  },
},
```

... but this was really slow - even for the small demo app.

I also had to basically copy the content of /apps/web/tsconfig.app.json into /apps/desktop/tsconfig.json to make this work.

All in all it also had weird build behaviour.


### Use vite.renderer.config.ts and point it to the web folder

This is the most simple solution. Just by adding `root: '../web'` to the vite.renderer.config.ts stuff simply worked.

For the build I also needed to update the `build: {outDir: '...'}` value to point back again to the /apps/desktop folder. Because otherwise the build output folder would be created in /apps/web and would not have been packaged correctly. In this case I changed the outDir to `"../desktop/.vite/renderer/main_window"` which includes the `name` attribute of the renderer config in forge.config.ts.

**(!) See also [the architecture doc](../architecture/web+desktop_app_architecture.md)!**

The only problem with this solution is that it would not support multiple renderers with one vite.renderer.config.ts, because the [original Forge VitePlugin code generates the output dir name based on the forge.config.ts renderer name attribute](https://github.com/electron/forge/blob/main/packages/plugin/vite/src/config/vite.renderer.config.ts#L15C15-L15C39).

I suppose a solution would be to have a separate vite.rendererX.config.ts for each window if this would become necessary in the future for some reason.

## Decision

I decided to use the last option. It's the only really working solution with only a minor shortcoming.
