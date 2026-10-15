# TSDR-1006 Documentation  

## Status

Accepted, Proposed, Deprecated or Superseded (list DR)

## Context

Choose how and what to document.

what ever it is that go has baked in for pulling out comments into documention

look into docusaurus
	documentation tool. others? use from goa/open api?

- OpenAPI 3?
- https://passo.uno/seven-action-model/
- code docs??
- C4Model
  - db chart structurizr spelling
  - https://www.reddit.com/r/dataengineering/comments/1iy3z19/can_anyone_tell_me_what_tool_was_used_to_produced/
- Hype for documentation?
  - https://github.com/gopherguides/hype?tab=readme-ov-file
  - is there a book about? or they used it to write books?
- https://github.com/cyberagiinc/DevDocs
------------

Uses C4 Modeling to document system. 


https://doxygen.nl/

https://www.reddit.com/r/golang/comments/1khhgyt/show_go_i_made_a_tool_that_automatically/
https://www.johnnolan.dev/hcta/articles/ams-tools-architecture/
https://icepanel.medium.com/top-7-diagrams-as-code-tools-for-software-architecture-1a9dd0df1815
https://www.reddit.com/r/softwarearchitecture/comments/1i8wa5f/i_am_writing_some_documentation_for_a_system/
https://www.reddit.com/r/golang/comments/1ktcneg/how_do_you_guys_document_your_apis/

Diagrams
- [Structurizr](https://structurizr.com/)
  - Source: Structrurizr DSL
  - Generates: 
    - Schema
    - Documentation
    - Links to Decision Records
  - C4 Modeling
  - https://github.com/structurizr/lite
  - https://github.com/krzysztofreczek/go-structurizr
    - generates c4models from go code
    - https://threedots.tech/post/auto-generated-c4-architecture-diagrams-in-go/
- [goa model](https://github.com/goadesign/model)
- [Liam ERD](https://liambx.com/)
	- auto diagram from schema
	- db modeling
- [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
    - based on PlantUML
	  - C4 Modeling
- [Mermaid]()
  simpler than plantuml. but then hit constraints fast?

https://www.reddit.com/r/ExperiencedDevs/comments/1k7ki6k/plantuml_vs_mermaid/
https://news.ycombinator.com/item?id=43560736

## Decision

- Will use wiki on redmine as a catch all for what doesn't get documented in the above.
- code comments should answer **why** "foo manages foo" is worthless.
- when documenting CLIs include full flags in examples. Single letter cli flags are not descriptive enough.

## Why / Notes



## Consequences



## Other Options

Possibilities:

Not an option:

