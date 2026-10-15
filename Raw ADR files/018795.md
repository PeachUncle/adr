# Staged rollouts for Embeddable Framework

Date: 2021-05-03

## Attendees

Emu

Copperhead

## Status

Approved

## Context

As per
the [minimum deployment guidelines](https://zendesk.atlassian.net/wiki/spaces/INFR/pages/261824454/Deployment+Best+Practices#DeploymentBestPractices-MinimumDeploymentRequirements)
we are supposed to have some kind of staged rollout for our services. However at the moment each time we deploy the
embeddable framework it goes out to all of our customers - regardless of pod, priority or risk.

Recently, we have increased our usage of arturos as a way to roll out to high priority customers last. The way we
tracked these is via this
spreadsheet [Top 20 Widget customers](https://docs.google.com/spreadsheets/d/1UDP6WHJeDrKVGI_cUzC6L33vaJLAR-YEHAT31DejTkU/edit#gid=838784427)
by active7, MRR. When rolling out the arturo we would -subdomain all of them and after we were comfortable after rolling
out to 100% of customers we would then finish rolling out to the high priority customers. We want to somewhat replicate
this intention, but for each deployment. Where we can be confident that our deploys are safe before rolling out to some
of our larger customers.

### Helpful links

- [Embed Key Registry (EKR) Network Traffic Flow Diagram](https://zendesk.atlassian.net/wiki/spaces/CE/pages/687670851/Embed+Key+Registry+EKR+Network+Traffic+Flow+Diagram)
- [Asset Composer & Embed Key Registry](https://zendesk.atlassian.net/wiki/spaces/CE/pages/296454283/Asset+Composer+Embed+Key+Registry)

### Guiding Principles

#### At a minimum the solution must first:

1. Pass through Pod 998 and Pod 999 and all staging tests must pass before it can be released to any other pod/release
   stage (TBD).
2. Our default release process will be to deploy to Canary first for at least ~30 mins
3. Our Smoke tests will run against Canary pods first. The smoke tests are required to run every 15 minutes on what’s called Staging (Pod 999), Canary (Pod 26) and Production (Pod 23)
4. Then we release to (TBD) customers

#### Hard requirements

- We must be able to rollback any stage at any time without affecting other deploys
- We must have a mechanism to rollback all stages to a particular release
- We must have a mechanism where we bypass checks and roll forward to any release at any time.     <-- controversial,
  but we sometimes need to deploy critical fixes asap too
- We must be able to monitor differences between the different stages
- It must be possible for us to include Chat Phase 4 customers in the list of VIPs if needed
- Account moves must continue to work

#### Nice to have requirements

- We can easily manage the list of customers that we deem to be VIP

#### Compromises that we’re willing to accept:

- subdomain changes may require manual fixing
- Maintaining a list of VIP customers is something that we will manage ourselves internally (Not configured via arturos)

#### Then with that in mind let’s pick one of the following options:

- Leave existing deploy process as is
- 2 stage: Canary + non-VIPs, then VIPs
- 3 stage: Canary, then non-VIPs, then VIPs
- n stages (podded): Canary, Pod 1, Pod 2, Pod 3…. Pod n
- n stages(podded) + VIPs: Canary, Pod 1, Pod 2, Pod 3…. Pod n… then VIPs

Where’s the sweet spot for reducing risk for customers vs increasing risk/maintenance for us?

#### How do things work at the moment?

A full set of diagrams can be seen
here [LucidChart](https://lucid.app/lucidchart/invitations/accept/inv_8646a28c-e477-4074-b600-b82eb61fab52)

A summary of how each moving part works

##### How the Web Widget loads on a customer's website

- Script loads in asset composer
- Asset composer calls out to EKR (via compose endpoint) to get a list of all assets to load on the customer’s website
- EKR finds all product_configs for the customer, all Web Widget customers will have a web_widget product config
- EKR looks up the data for each product the customer has, each product will have information that includes its current
  version
- EKR does a call out to S3 to get the asset_manifest.json for each product the customer has, for the Web Widget it
  looks in the versioned folder /web_widget/<version>/asset_manifest.json
- EKR sends back a list of assets for asset composer to load on the customer’s website. For the Web Widget, the assets
  it sends down will be pointing to the assets uploaded in the latest folder, e.g.
  /web_widget/latest/framework-[contenthash].js

##### Uploading Embeddable Framework to S3

In Samson we have the stages “Build staging” and “Build production”. These stages simply build the Embeddable Framework
and upload the created assets to s3 into two folders.

- /web_widget/<git revision sha>
- /web_widget/latest

##### Release Embeddable Framework

In Samson, we have the stages “Release staging” and “Release production” that calls out to EKR’s API endpoint called
/release that allows you to update the version for a specific product. All it does is update the product’s version to be
the git revision sha for the release you want to be released.

##### How the customer’s product config is created/updated

How asset composer works, is when it loads on a customer’s website, it will call out to EKR to get all of the scripts
for all of the products that the customer has.

So in order to get the Web Widget on the customer’s website, the customer needs to have a Web Widget product config.

This product config is created/updated every time the user makes a change to their Web Widget config in Support. On
save, embeddable will do a call out to EKR to update the product config.

For the Web Widget, the product config contains things like the features the customer has, this allows EKR to only send
down assets for the features that the customer uses.

## Part 1. Staged rollouts Possible approaches

### 1. Store priority versions in EKR products

Currently the last released version of the widget is stored in the EKR products table. An example of the contents for
the web_widget product looks like:

```json
{
  "version": "237df6b1e9cd197763b358613e18ffa4c84b7077",
  "use_latest": true,
  "path": null,
  "name": "web_widget",
  "use_asset_manifest": true,
  "base_url": "https://static.zdassets.com"
}
```

We can store additional versions in this record to indicate the requested version according to priority, like so:

```json
{
  "version": "237df6b1e9cd197763b358613e18ffa4c84b7077",
  "priority": {
    "vip": "abc123",
    "canary": "def456"
  }
}
```

We would then have two new stages in Samson that updates that record with the appropriate sha/version, e.g.

```bash
# Release Prod (Canary)
curl $ekr_release_url -d “{ “priority”: { “canary”: <sha> } }”

# Release Prod (VIP)
curl $ekr_release_url -d “{ “priority”: { “vip”: <sha> } }”
```

When generating the compose response, we will fetch the appropriate version for the product based on the account’s
priority. Logic would look like:

Fetch https://ekr.zdassets.com/compose/<manifest-key>

1. Find product configs for <manifest-key>

Example:

```json
{
  "manifest_key": "18b527a8-69bc-4445-a630-8b72e985d17c",
  "product": "web_widget",
  "external_id": "subdomain.zendesk.com",
  "linking_key": "subdomain.zendesk.com",
  "linking_type": "zendesk_host",
  "enabled": true,
  "features": []
}
```

2. Find all products associated with the product configs Example:

```json
{
  "version": "237df6b1e9cd197763b358613e18ffa4c84b7077",
  "use_latest": true,
  "path": null,
  "name": "web_widget",
  "use_asset_manifest": true,
  "base_url": "https://static.zdassets.com",
  "priority": {
    "vip": "abc123",
    "canary": "def456"
  }
}
```

Retrieve the priority of the product config (to be discussed in Part 2)
If priority exists, and has a match in the product.priority.<priority>, it will use that version. Otherwise it will
fallback to product.version

Embeddable Framework will be updated to support the new release stages. EKR will need to modify the release endpoint (or
create a new release endpoint) that supports accepting and updating the priority attribute in the products table. EKR
will also need to update the compose endpoint to support fetching a different version according to priority.

#### Pros

- Easy to implement.
- Low-risk. Care should be taken to implement it to be backwards compatible and should also safely fallback to current
  workflow if no compatible versions are available.
- No effect on performance. This solution does not introduce any new lookups or external dependencies so performance
  shouldn’t be affected.
- Easy to add future priorities. The solution can be extended to include any number of possible priorities, e.g. vip2,
  vip3, etc The stages/priorities in the previous examples are all arbitrary. Since EKR uses a schema-less database, we
  can add an arbitrary number of attributes to the products table without requiring a database migration.

#### Cons

- Additional overhead in tracking which versions have been deployed to which customer.

### 2. Create separate products per priority/deploy group

We could store each deploy group as a different product. For example, a canary web widget deploy group would be a
different EKR product, separate from the normal web widget group.

```json
{
  "version": "237df6b1e9cd197763b358613e18ffa4c84b7077",
  "use_latest": true,
  "path": null,
  "name": "web_widget_canary",
  "use_asset_manifest": true,
  "base_url": "https://static.zdassets.com"
}
```

EKR would treat it like a separate product, with no changes in the compose logic.

#### Pros

- No change in EKR

#### Cons

- Embeddable needs to know which product a customer is in. This means embeddable needs to store the deploy group in the
  database, so a backfill is necessary to update all the records.
- Need to add logic during migration to disable other products. E.g. when customer A is part of web_widget_canary group,
  we have to make sure they’re not part of the web_widget group, otherwise they will get 2 widgets in their page.
- Chat phase 4 accounts aren’t persisted in the database, which means they can’t be part of any deploy groups and are
  thus excluded from staged rollouts.

## Part 2. Grouping customers into canary, default and high priority

### 1. Store list of customers in a file in the embed_key_registry repo

For this solution, we can simply store the list of customers in some kind of file in the repo that would utilise the
list. The file could be txt, yml or json - whatever is easiest to read from.

A sample of what this could look like

```yaml
canary:
  - zendesk
  - z3ntest1
  - z3ntest2
vip:
  - high-priority-1
  - high-priority-2
```

When a request comes in to the compose endpoint, it can quickly check to see if the customer is listed in one of the
lists defined in the file and send the asset for the group the customer is in.

#### Pros

- Requires a PR to change the list of customers
- No network calls or database access to get list of customers
- All groups and lists are visible in the same location, making it easier to not accidentally add customers to more than
  one group

#### Cons

- List of customers isn’t _super_ visible, you have to know where to look
- Getting accounts onto canary would be a slow process, so using fresh accounts in browser tests wouldn’t be possible
- Ekr does not have information on accounts, only product_configs, which are per widget/brand. We would need to list out
  all brands of an account in the file. Also, new widgets created by vip accounts would not be covered automatically,
  and would have to be manually added each time

### Use arturos as customer groups

This solution uses multiple arturo feature flags as ways to group customers.

When a compose request comes in, we would query hardcoded arturo feature flags to see if any group is enabled for the
customer, if it is then the assets for that group would be sent done, otherwise the default assets would be returned.

Some basic pseudocode for this could look like

```
if Arturo.isEnabled(subdomain, web_widget_deploy_canary)
  return canary_assets

if Arturo.isEnabled(subdomain, web_widget_deploy_high_priority)
  return high_priority_assets

return regular_assets
```

#### Pros

- Updating list of customers is out of the PR and deploy cycle, but logs are still kept for changes
- Groups could be defined based on percentage of users as well as hard coded for specific customers
- Being out of a repo and in a location more people are familiar with - more people could make changes to the groups of
  customers not just developers
- Adding and maintaining groups of customers is still relatively easy, however would involve updating in two places (
  monitor and embed_key_registry)

#### Cons

- A network request is made for each arturo check, slowing down the entire compose request
- Work would need to be done to allow EKR to query arturos since it doesn’t currently do this
- Since lists of customers would be under separate arturos, it will be easier to accidentally add a single customer to
  two different groups

### Persisting priority groups in DB and exposing API for updating it

For this one, we could store an additional property in the product config database to indicate the customer’s deploy
group. Although the product config gets returned in a public endpoint - we could configure it to simply not show the
list of customers for the API endpoint and just use it privately internally in the compose API to avoid exposing what
customer is in what group.

The deploy group could just an additional property on the config as outlined above
in [Store priority versions in EKR products](https://docs.google.com/document/d/1ITdFq_JPgIuxRdWMV3Gz3ZWN_fbfMflCf0m3_NRO_U0/edit#heading=h.3ybkq7cz18ku)

```json
{
  "manifest_key": "keykeykey",
  "product": "web_widget",
  "external_id": "subdomain.zendesk.com",
  "deploy_group": "vip"
}
```

When it comes to updating the database, we already have an API for updating an individual product config. We could
create an additional API that accepts a list of Zendesk hostnames to do them in batches.

#### Pros

- List of customers can be updated from anywhere - allowing us to potentially build nicer tooling for managing this list
  of customers
- Can build tooling into monitor to update the database - allowing anyone to change which group a customer is in via UI

#### Cons

- Will need to build specific logic to maintain deploy group when the customer switches between Web Widget and Web SDK

## Decision

Part 1 - Solution 1 - Store priority versions in EKR products Part 2 - Solution 1 - Store list of customers in a file in
the embed_key_registry repo

The suggested combined solution is using both Solution 1s from each part.

### Implementation

At the moment we have one release stage in samson that updates the single version on the product in EKR

With this change, we will now have three Samson release stages, that each update a different version for the product

Then in the /compose endpoint, instead of using the top level version from the product, we would look to see if the subdomain of the customer existed in the text file that would look something like this

```yaml
canary:
  - support
  - z3n-browser-test-1

vip:
  - special-customer-1
  - special-customer-2
```

If the customer does exist in one of these groups, then we would use the matching version from the product.

So for the product

```json
{
  "name": "web_widget",
  "base_url": "https://static.zdassets.com",
  "versions": {
    "canary": "123",
    "regular": "456",
    "vip": "789"
  }
}
```

The customer with subdomain special-customer-1 would receive version 789 of the product.

If the customer isn’t mentioned in this file, then they would receive the regular version, which in this case is version 456.

This will be the only change required for the compose endpoint, all other functionality will remain the same.


## Consequences

- With the file being static, is it going to be hard to update? Will it be forgotten? Will it be hard to manage a large number of customers?
- Ekr does not have information on accounts, only individual widgets. We would need to list out all brands of an account in the file. Also, new widgets created by vip accounts would not be covered automatically, and would have to be manually added each time



