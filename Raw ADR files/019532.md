<!-- Short descriptive title -->

# RTK Query and Supporting Decisions

<!-- Date -->

_2022-09-12_

<!-- Summary -->

Strategies were investigated for handling kbase service (jsonrpc) API calls and
caching of responses. Goal was to create a simple developer experience for
fetching data from kbase services within components and hooks. Challenges
included caching, integrating caching with the redux store, and dealing with the
particular request format of jsonrpc (v1.1). **JSONrpc 2.0 is not currently
supported, but it will be trivial to implement when needed.**

## Authors <!-- GitHub Username(s) -->

@dauglyon

## Status <!-- Status of this ADR -->

Accepted

## Alternatives Considered <!-- Short list of considered alternatives, should include the chosen path -->

- Hand-roll a fetch-based JSONRpc client, and manage requests within individual
  feature slices.
- Use [TanStack React Query](https://tanstack.com/query/v4/docs/overview) to
  handle caching and hooks, hand-roll integration with redux
- Use [RTK-query](https://redux-toolkit.js.org/rtk-query/overview) with a custom
  baseQuery

## Decision Outcome <!-- Summary of the decision -->

Used RTK-query with a custom baseQuery to manage caching, jsonrpc logic, and
both async functions and hooks for running query (get-like) and mutation
(post-like) calls.

## Consequences <!-- Summary of the decision -->

Using RTK-query in our usecase requires a few supported but not wonderfully
documented deviations from the introductory rtk-query docs. These include:

1. A custom base query, implemented in `src/common/api/utils/kbaseBaseQuery.ts`.
   This allows all the api endpoints to share jsonrpc and authentication logic,
   it also lets us automatically fetch/cache URLs for dynamic services, again
   without too much developer overhead when making individual endpoints.
2. In order to have different services' endpoints split between files, but also
   to allow the APIs for different services to share cache "tags" (so, for
   instance, changing a narrative name can invalidate caches which may reference
   that narrative from other services), a single rtk-query API is created in
   `src/common/api/index.ts`. `injectEndpoints` is then used in each
   `src/common/api/[service].ts` file to add service-specific endpoints, these
   endpoints are then export and imported from the service-specific file, but
   act on the api instance and cache defined in `.../index.ts`.
3. Because we also may want to use the endpoints _outside of react components_,
   we can instead export the endpoint objects, instead of the auto-generated
   hooks. The auto-generated hooks (and the `initiate` function to call the
   endpoint outside of a react component) are then available as properties of
   those exported endpoints. More detail below.
4. Small helper utils in `src/common/api/utils/serviceHelpers.ts` which handle
   defining the service type (static\[core\]/dynamic) and location, and returns
   a helper function that prevents that information from needing to be
   individually defined for every endpoint.

### Exporting Endpoints instead of Hooks

Instead of exporting Hooks:

```js
// common/api/userProfileApi
export const {
  useGetUserProfileQuery,
  useSetUserProfileQuery,
  useStatusQuery,
} = userProfileApi;
```

we can export Endpoints:

```js
// common/api/userProfileApi
export const { getUserProfile, setUserProfile, status } =
  userProfileApi.endpoints;
```

which means instead of directly using hooks:

```js
// features/auth/Auth.tsx
import { useGetUserProfileQuery } from '../../common/api/userProfileApi';
// ...
const profile = useGetUserProfileQuery(profileParams);
```

we use them like this:

```js
// features/auth/Auth.tsx
import { getUserProfile } from '../../common/api/userProfileApi';
// ...
const profile = getUserProfile.useQuery(profileParams);
```

Doing this is useful because `[endpoint].initiate` can be used call the endpoint
outside of a react component (without having to add more exports). Further, in
my (@dauglyon) opinion this looks way nicer than the what is in rtk-query docs,
and it's still through their documented API.

```js
// some/non-component/function.js
import { getUserProfile } from '../../common/api/userProfileApi';
import { store } from '../../../app/store';
// ...
const args = {...};

const query = getUserProfile.initiate(args, subscribe: false);
await query;
const result = getUserProfile.select(args)(store.getState());

```

## Pros and Cons of the Alternatives <!-- List Pros/Cons of each considered alternative -->

### Hand-roll a fetch-based JSONRpc client, and manage requests within individual feature slices

- `+` Fully customizable to our needs
- `-` would require us to hand-roll a cache invalidation setup if we wanted
  caching
- `-` integrating well with redux, and separation of concerns from store slices
  could be very complicated.
- `-` would require us to hand-roll our own API react hooks for data fetching,
  which would require either very complicated typescript or a lot of boilerplate
  code per service

### Use TanStack React Query to handle caching and hooks, hand-roll integration with redux

- `+/-` Very similar to hand-rolling everything but...
- `+` helps solve react-hook-based API calls (has a base hook which makes
  creating cached query hooks relatively straightforward)
- `-` Caching is done per-hook, hard to invalidate caches across endpoints
- `-` Not designed to work outside react components or hooks.

### Use RTK-query with a custom baseQuery

- `+` Plays well with redux and react hooks
- `+` comes with query caching and a "tag-based" cache invalidation setup
- `+` adds middleware which automatically refetches in-use queries which become
  invalid
- `+` well-typed and enforces the creation of request/response types per
  endpoint
- `+` de-duplicates and caches GET-like queries by default
- `+` usable outside of react components/hooks
- `-` default setup is more targeted at RESTful APIs and to use a single api
  (whereas we have one per service)
- `-` while it is extensible to our usecase, the code to do so is a bit complex
  due to typing and working with dynamic services

## References <!-- List any relevant resources about the ADR, consider using footnotes as below where useful -->

- [RTK Query comparison with other tools](https://redux-toolkit.js.org/rtk-query/comparison)
