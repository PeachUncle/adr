<!-- based on this template: https://github.com/adr/madr/blob/develop/template/adr-template-minimal.md -->

# Converter Default Case

## Context and Problem Statement
- arbitrary open-source C/C++ projects may use unconventional formats (or rather: not follow [doxygen](https://www.doxygen.nl/index.html) conventions) for inline documentation (doctrings before/after function/class/field declarations)
- [doxygen](https://www.doxygen.nl/index.html) may not handle these docstrings correctly (i.e. formatting them incorrectly in the output or missing them entirely)
- we want to do something to gain a potential to improve generated API documentation for arbitrary open-source C/C++ projects
- we want to pre-process a project's source code (only the comments/docstrings) to be better suited as doxygen input

## Considered Options

- deterministic static comment style converter (only change "comment initiation syntax" (i.e. "/*" to "/**") based on regular expression pattern matching)
- Large-Language-Model-based (LLM) comment converter

## Decision Outcome

The following compromise was chosen:
- both options are implemented to a degree:
  - static comment style converter (can change between most known C/C++ comment styles)
  - LLM converter for function docstrings, "without quality metric"
- on default, converter tool is not executed, so the user does not change a project's source files unwillingly/unknowingly
- on default, when the converter is enabled via `--converter`, the comment style converter is run and changes comment format to `/**...*/` style block/doctring comments
- LLM converter can be enabled via `--converter function_comment_llm`


### Consequences

* on default, source files remain untouched
* on default with enabled converter
  * compatibility is improved significantly (especially when `/*...*/` style block comments are used as docstrings, which are not recognized by doxygen as valid docstrings)
  * no high-power hardware or running LLM is necessary
* if desired, usage of LLM is fully supported
* however, no "easy" metric to determine the results are good or how good/true to the source they are

## Pros and Cons of the Options

### deterministic comment style converter

* (+) deterministic/reproducible results
* (+) quick execution and low required computing power
* (-) manual labour required for implementing every case
* (-) only known/"previously encountered" docstring formats can be supported

### LLM-based converter
* (+) supports every potential docstring format (theoretically)
* (+) no need for manual implementation of handling of obscure formats
* (-) higher required computing power and slow execution (based on the used LLM model)
* (-) results may vary (based on the used LLM model)
* (-) results are (likely) not reproducible
* results may require additional evaluation metric to determine "quality"/if they are usable
* if something was AI-generated, it should at least be marked as such to avoid complications

## More Information
- https://www.doxygen.nl/manual/index.html
