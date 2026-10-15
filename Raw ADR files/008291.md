# Programming Style Decision

## Context and Problem Statement

How to create code that is uniform across multiple coders?
What style should we all agree too?

## Considered Options

* Considered typical code style practices and agreed upon one format for us all to use

## Decision Outcome
We all agreed on the following styling conventions:

Variable naming conventions:
- Multiword Delimited – Used to separate multiple words in a variable name without white space.
- Separate multiple words using _
- Try to use descriptive words instead of “convenient” names like s1, s2 for strings… etc. 
- Ensure that the code is easy to understand and always store commonly used variables before application

Class and function naming conventions
- functions and classes should also consist of descriptive titles that are delimited by using conventions, as mentioned above
make sure that the variables, functions, and classes within your code can be easily distinguished from one another

Clear and concise comments
- Use the right amount of comments to help the group members and the coder to understand the code after weeks. 
- Always include comments before functions(example listed below)
- Divide functions up to different sections and include comments for every section

> /**
> 
>   \* Returns x raised to the n-th power.
>  
>   \*
>  
>   \* @param {number} x the description of the parameter
>  
>   \* @return {number} x description of the value the function returns
>  
>   \*/
 
Indentations
- Use ideal coding formatting and indentation include correct spacing for html, css and javascript for readability

Portability
- Try to take advantage of the functions like flexbox and so on to ensure portability 

Reusability and scalability
- Reusability is essential for software engineering and it would definitely be a central part of our website. The structure of the website would be designed for reusability in order for continuous usage and potential scalability
- Reuse some of our code: for snippets of code that will be used repeatedly in our code, create functions so we can just call the functions instead of copying & pasting the code every time we need to use it
- Making our software easier to navigate so more features can be easily added to it

