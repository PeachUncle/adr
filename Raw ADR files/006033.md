# Resource and IIIF API

## Date
2025-06-01

## Status
`Accepted`

## Context
Apotheca does not provide a user-facing discovery layer for the content contained within it. Because of this we depend on other applications to serve up the content. This means that consumer applications, like Colenda, must provide endpoints that allow users to download files.

There's a few problematic things with this set up:
- The consumer applications need to know AWS S3 credentials in order to serve up files.
- The JSON payload sent to Colenda can be fairly large because it includes all the assets. For each asset, we include the file location for derivatives, file location for preservation files, size, filename, etc.
- In order to create the IIIF manifest, Apotheca needs to know about Colenda's download links.
- Any consumer application would have to implement it's own logic to support access controls.

The purpose of separating Apotheca from the discovery layer was to insulate each system from each other, but the systems ended up having to know about each other more than expected. As is, it would be challenging to support additional discovery layers without duplicating code and adding even more complex configuration to Apotheca.

Because of these issues we explored different options for better supporting Apotheca's "consumer" applications. When thinking about these solutions we considered other features that our digital repository ecosystem has been asked to support, like access controls and display of transcriptions.

## Decision
1. We propose to add two public APIs to Apotheca to help serve data and files. These two public APIs will help "consumer" applications (discovery layers) make the content available while only having to know the structure of the publicly available Apotheca API. The two APIs are:
    1. The [Resource API](https://upennlibrary.atlassian.net/wiki/spaces/COL/pages/1672151056/Resource+API): A publicly accessible endpoint meant for applications that are displaying the content in Apotheca. This API is *not* meant to be used by the staff facing part of the application. As such, not every detail of a resource is exposed here, only the information needed to build out a discovery interface. This API exposes JSON endpoints that allow consumer applications to fetch information about resources and exposes download endpoints for original files and derivatives.
    2. The [IIIF API](https://upennlibrary.atlassian.net/wiki/spaces/COL/pages/1673363463/IIIF+API): A publicly accessible endpoint that serves up IIIF JSON-LD objects as required by the [IIIF Presentation API](https://iiif.io/api/presentation/3.0/) (i.e., manifests, annotations) to represent our resources. Initially this endpoint will only expose the IIIF V3 Presentation Manifest for an Item, but in the future it will be expanded to provide endpoints for IIIF annotations.
2. These two public endpoints will be served up a from a seperate container than the rest of the application. This will protect the staff facing side of the application from the increased traffic of the public endpoints.
3. Add a new domain for these endpoints so that we do not bake the `apotheca` host name into publicly available URLs.

## Consequences
#### PROs
1. The consumer application's interactions with Apotheca would be explicitly documented by APIs. Making it easier to create new interfaces if needed.
2. The consumer application wouldn't need to have access to the S3 bucket and know the location of the file to provide file downloads. It can now depend on Apotheca for all file downloads.
3. IIIF manifests would be able to use download links from Apotheca's IIIF API and would therefore only need to know what the URL for the item at the consumer site is (for the "Available Online" links). This greatly simplifies the logic in the IIIF manifest generation code.
4. IIIF manifest can be shared among different consumer applications because they will use generic Apotheca API links.
5. We could use this API to index sample content into our development environments for Digital Collections and Apotheca.

#### CONs
1. Part of Apotheca's infrastructure would be publicly available, whereas before this change the entire Apotheca application was behind VPN.
2. Apotheca would be connected to the consumer applications and thus any Apotheca downtime would effect the consumer applications.

