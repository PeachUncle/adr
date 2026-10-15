# Tenancy V2 to V3 migration

## Status

Draft

## Context

Version 2 of `Marain.TenantManagement` is aligned with version 2 of `Corvus.Tenancy` and associated libraries. Version 3 `Marain.TenantManagement` moves to version 2 of `Corvus.Tenancy`, and this entails some significant changes, notably:

* Use of `Azure.Core` family Azure client libraries, with support for AAD authentication
* Application-defined container names
* Containers creation by applications during tenant onboarding (and [not automatically on demand as used to happen](https://github.com/corvus-dotnet/Corvus.Tenancy/blob/main/docs/adr/0003-no-automatic-storage-container-creation.md))

One upshot of these changes is that storage configuration stored in tenant properties is different—we needed to add new properties to support new client capabilities, but since the usage model wasn't backwards compatible, we also fixed some long-standing problems with the older format (e.g., some weird conventions in which properties didn't always do what their names suggested).

For example, storage configuration for `Marain.Operations` in the V2 model looks like this:


```json
"StorageConfiguration__operations": {
    "accountName": "maridgoperationsy3qxmrir",
    "container": "operations",
    "keyVaultName": "maridgoperationsy3qxmrir",
    "accountKeySecretName": "OperationsStorageAccountKey",
    "disableTenantIdPrefix": false
},
```

but in the V3 world, an exact equivalent might look like this:

```json
"Marain:Operations:BlobContainerConfiguration:Operations": {
    "accountName": "maridgoperationsy3qxmrir",
    "container": "513162c27e77e52411ececa40f1e615455b01fc5",
    "accessKeyInKeyVault": {
        "vaultName": "maridgoperationsy3qxmrir",
        "secretName": "OperationsStorageAccountKey",
    }
}
```

The key vault secret handling may look like some unnecessary arbitrary moving around of things, but it is part of adopting a uniform approach to Azure Key Vault and service identities across all sources, and it adds the ability to specify the identity with which to connect to key vault. (It defaults to the service identity, but you can configure alternatives.) These same changes also make it possible to authenticate to storage using a service identity instead of a key (by specifying `clientIdentity` instead of `accessKeyInKeyVault`).

The most substantial change, though, is that the `container` no longer contains a logical container name that the Corvus tenanted storage libraries rewrite as a tenanted name. Instead, that name choice happens during tenant onboarding, and the configuration in the tenant properties records the chosen container name. The v3 tenanted storage libraries require this container already to exist (whereas the v2 ones created it on first use automatically).

[Corvus.Tenancy ADR 0004](https://github.com/corvus-dotnet/Corvus.Tenancy/blob/main/docs/adr/0004-v2-to-v3-transition.md) describes the V2 to V3 transition from the perspective of a single service, but `Marain.TenantManagement` necessarily takes a broader view.


What do we do if there are systems out there that require V2-style config? E.g., someone is using Marain.Operations but hasn't yet deployed an update to the version that is aware of V3-style config? One response to this might be: "Tough! If that's your situation, use V2 of `Marain.TenantManagement`. However, a problem with that is that it means that until every Marain service in the deployment has been upgraded to be V3-capable, nothing can start using the V3 approach. We want it to be possible to upgrade individual services piecemeal.

Prior to `Marain.Tenancy` V3, a ServiceManifest's `requiredConfigurationEntries` contains only V2-style entries.
A newly-implemented version would want to live in a V3-only world, so it would have only V3-style required configuration. But what about a formerly V2-style service that has been upgraded to support V3 configuration? Existing tenants may well have V2 configuration, and that needs to continue to work. More subtly, we need to be able to enrol tenants, and that needs to work when V2-style enrolment configuration items are supplied. This is especially important for automated onboarding scenarios—we don't want these to break when services start to get upgraded.

So we can't just pretend that V3 is the only thing. The following combinations of supplied configuration vs what the service actually requires are conceivable:

| Supplied | Req: V2 only | Req: V3 only | Req: V3 with V2 fallback |
|---|---|---|---|
| V2 | V2 only | Fail, or generated V3? | Just V2, generated V3, or both? |
| V3 | Fail | V3 | V3 |

In the case where a service only has V2-style requirements, and only V2-style config items have been supplied, it's straightforward. Likewise when it's V3 all the way. In cases where a service supports only V2, but V3 configuration is supplied, that's also clearly not acceptable because V3 configuration cannot in general be converted to V2.

So the interesting cases are where V2 has been supplied but the service is either V3 with V2 migration support, or V3 only. All V2-style storage configuration can be migrated to V3, because `Corvus.Tenancy` provides support for V2-to-V3 migration for all storage types,


Matthew suggests that in the "Need V3, was given V2", fail, but as part of the failure message, show what the V3 config looks like.

In the case where the service works with either V2 or V3, and is given V2, there are three options

* just store the V2 data
* convert to V3 and store
* fail (reporting what the V3 should look like)

```
TenantManagementCli --allow-v2tov3migration
```

Might need three modes in cases where automatic V2 to V3 conversion is possible but might not be desired:

1. It's fine
2. Do it but issue a warning
3. Fail

The current plan for all the Marain services we have implemented is that as we upgrade to tenancy V3, we support both V2 and V3 configuration, so the "V3 only" case in the table above won't arise.

## Decision

For now, we are simply accepting and storing V2 setting if that's what's supplied during enrollment, if the service manifest says it's acceptable. This works because all our services accept V2 configuration.

However, this ADR is in draft status because this is probably not the final word in this. We want to get V3 released, and this is the quickest path to release. But we will revisit this and might decide to build V2 to V3 conversion into the command line tool.