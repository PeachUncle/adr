<!-- based on this template: https://github.com/adr/madr/blob/develop/template/adr-template-minimal.md -->

# Documentation Generator Choice

## Context and Problem Statement

- we want to use an existing tool for generating usable, well-structured API documentation in HTML format from existing (inline-documented) source files
- the "industry standard" for generating API documentation from C/C++ source code is [doxygen](https://www.doxygen.nl/index.html)
- [sphinx](https://www.sphinx-doc.org/en/master/) is a newer, more customizable tool for this purpose, but is mainly known for working with Python
- the sphinx extension [breathe](https://breathe.readthedocs.io/en/latest/) provides directives for parsing [doxygen](https://www.doxygen.nl/index.html)'s HTML output
- the sphinx extension [exhale](https://exhale.readthedocs.io/en/latest/index.html) can automatically parse [doxygen](https://www.doxygen.nl/index.html)'s XML output to properly organized HTML API documentation

## Considered Options

* sphinx-based ([sphinx](https://www.sphinx-doc.org/en/master/) + [breathe](https://breathe.readthedocs.io/en/latest/) + [exhale](https://exhale.readthedocs.io/en/latest/index.html) + [doxygen](https://www.doxygen.nl/index.html))
* sphinx-based ([sphinx](https://www.sphinx-doc.org/en/master/) + [breathe](https://breathe.readthedocs.io/en/latest/) + [doxygen](https://www.doxygen.nl/index.html))
* doxygen-only

## Decision Outcome

After careful evaluation, the doxygen-only approach was chosen despite initial shortcomings, because the "shortcomings" could be circumvented with rather easy workarounds.  
Sphinx-based, on the other hand, ended up calling for workaround after workaround and, at its current state, was considered not worth it.  
However, this could potentially change in the future, at least when new versions of [breathe](https://breathe.readthedocs.io/en/latest/)/[exhale](https://exhale.readthedocs.io/en/latest/index.html) with better graphviz-support are released. 

### Consequences
- customizability is limited from here on out
- inserting something custom into the API-documentation (i.e. linking to the test coverage reports) could be slightly more troublesome


## Pros and Cons of the Options

### sphinx-based
- (+) highly customizable (themes, output based on reStructured text, ...)
- (+) more polished "modern" look and feel
- (+) [breathe](https://breathe.readthedocs.io/en/latest/) directives can parse [graphviz](https://graphviz.org/) dot tool calls (to a certain degree)
- (-) [breathe](https://breathe.readthedocs.io/en/latest/) directives parse some dot tool calls imperfectly and generate corrupted graphics or do not work at all
- (-) output structure of [exhale](https://exhale.readthedocs.io/en/latest/index.html) rather limiting for use with arbitrary projects
- (-) [exhale](https://exhale.readthedocs.io/en/latest/index.html) output potentially more hierarchical than desired
- (-) [exhale](https://exhale.readthedocs.io/en/latest/index.html) output does not include [breathe](https://breathe.readthedocs.io/en/latest/) directives

### sphinx-based (without exhale)
- (+) highly customizable (themes, output based on reStructured text, ...)
- (+) more polished "modern" look and feel
- (+) [breathe](https://breathe.readthedocs.io/en/latest/) directives can parse [graphviz](https://graphviz.org/) dot tool calls (to a certain degree)
- (+) breathe apidocs command uses [breathe](https://breathe.readthedocs.io/en/latest/) directives
- (-) [breathe](https://breathe.readthedocs.io/en/latest/) directives parse some dot tool calls imperfectly and generate corrupted graphics or do not work at all
- (-) output of breathe apicdocs command has no proper hierarchy
- (-) re-implementing something "[exhale](https://exhale.readthedocs.io/en/latest/index.html)-like" would require a lot of work/time

### doxygen-only
- (+) full support of generating various graphics (include/caller graphs etc.) with the [graphviz](https://graphviz.org/) dot tool
- (-) may look somewhat dated by default
- (-) content/layout/hierarchy are not freely configurable 
- custom themes exist (see more information at the bottom) but are not "the standard" / an integrated option
- inserting custom content is possible (by editing the HTML output afterward), but can be somewhat "hacky" and complicated

## More Information
- https://www.sphinx-doc.org/en/master/
- https://breathe.readthedocs.io/en/latest/
- https://exhale.readthedocs.io/en/latest/index.html
- https://www.doxygen.nl/index.html
- https://graphviz.org/
- https://jothepro.github.io/doxygen-awesome-css/
- https://mcss.mosra.cz/documentation/doxygen/