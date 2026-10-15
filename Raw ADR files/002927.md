# 5. Use arrays as named arguments

Date: 2019-10-29

## Status

Accepted

## Context

This application was designed as a very flexible system and
provides dynamic validation of content using modular constraints. Those constraints are defined in the data itself and change often.

In order to support this modular system, some objects have to be
instantiated from semi-structured information. In those scenarios,
and only in them, we might have methods that would look like this:

    public function __construct(
        ?int $min = null,
        ?int $max = null,
        string $type,
        ?int $step = null,
        ?string $separator = null,
        ?bool $round = false,
    )

Supporting the instantiation of this object would be very verbose and
a lot of effort would be made during parsing/evaluation of the
provided semi-structured data. A good solution for this would be to
use named arguments combined with argument unpacking.

Unfortunately, PHP has no support for named arguments in method
calls. In order to achieve this feature, libraries and frameworks
from the PHP ecosystem use the Reflection API to match the method
signature based on name instead of order. The Reflection API is
verbose and can affect runtime performance if caching is not
done properly.

## Decision

In order to reduce complexity and leverage the advantages of PHP being
a dynamic language, we decided to use arrays as named arguments.

For example:

    public function __construct(array $options)
    {
        $limit = $options['limit'] ?? 20;
        $offset = $options['offset'] ?? 0;
    }

    new Foo(['limit' => 10, 'offset' => 5]);

This is not a substitute for normal argument passing. Use this only
in scenarios where you would consider using named arguments.

## Consequences

The free-form nature of the array data structure makes typing and data
checking more difficult. However, this can be easily circumvented by
having stricter unit tests and performing assertions on access.

Autocompletion is also affected by this decision.

We believe that the maintainability cost of using the array data
structure is very low, compared to the cost of using Reflection API.
