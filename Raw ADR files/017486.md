# 3. Create modules from directories

Date: 2023-02-25

## Status

Accepted

## Context

While content has to be stored in the output JSON formats, the source can be worked on with multiple formats (markdown, text, images, etc).

To facilitate the creation of modules by developers, using multiple files is preferred. This way, developers can create their content with their preferred tools, then use another process to "compile" the source material into a valid module file.

To support this process, however, there must be a balance between the multiple approaches for this compilation, allowing for maximum flexibility without creating needless complexity.

For example, when writing the contents of a specific piece of content, multiple fields of similar nature could be stored in a single file, instead of one per field. However, some complex formats (images, files, etc) are probably best stored in separate files.

Another concern is the structure of the files that allows for a somewhat organized placement of related contents. Elements that are related could be grouped inside other directories.

## Decision

To try to achieve the most ergonomic design, without compromising on the flexibility, the following rules will be implemented:

### Types

Each type should be defined within their own directory, named as the type identifier, inside a `types` directory.

Inside this directory, another `rendering` directory can exist. Each file inside the rendering directory should be named as the format in question, with the contents of the file being the template to be used.

> For example, the file `./types/spell/rendering/txt.hjs`, when compiled would be mapped as the json object with the following shape:
> ```json
> {
>   types: {
>     spell: {
>       rendering: {
>         txt: "file contents here"
>       }
>     }
>   }
> }
> ```


### Contents

Each content piece should be inside a `contents` directory.

Inside this directory, there can be other directories and files.

Directories are interpreted as "groupings" unless there is a file named `_` inside of it.

This "underscore file" is a special file that signifies that other files inside the directory should be mapped as fields, not as separate content pieces. The contents of the underscore file will be expanded into the output object.

## Consequences

A new tool should be created to enable this compilation process to be used.

Supporting end-user documentation needs to be created to explain to module developers how to use the created tools and how to structure contents in directories.