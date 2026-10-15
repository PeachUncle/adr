# Adding initial consent date to PWA

## Context and Problem Statement

In Section 29, there is a table that is included in the letter templates which lists out the pipelines with their respective PWA reference
and the date that the PWA was consented. We already have the information from EPA to retrieve the pipeline number and the linked PWA reference, but we
do not have the initial consent date.

The PWA data is retrieved by hitting the PWA API, so there will need to be a change to both PWA and EPA in order to support this requirement.

Currently in FOX, the data for this mail merge field is queried from `api_vw_current_pipeline_data` which in turn gets the `initial_pwa_consent_date` from the
`api_vw_primary_pwas` view within PWA.

```sql
CREATE OR REPLACE VIEW ${datasource.user}.api_vw_primary_pwas AS
SELECT
  pwad.reference primary_pwa_reference
, pwad.pwa_id primary_pwa_id
, pc.reference initial_pwa_consent_reference
, CAST(pc.consent_timestamp AS DATE) initial_pwa_consent_date
, pc.id initial_pwa_consent_id
FROM ${datasource.user}.pwa_details pwad
LEFT JOIN ${datasource.user}.pwa_consents pc ON pwad.pwa_id = pc.pwa_id
WHERE pwad.end_timestamp IS NULL
AND pwad.pwa_status = 'CONSENTED'
-- below condition should remove cardinality as only ever 1 initial consent per PWA.
AND pc.consent_type = 'INITIAL_PWA';
```

The PWA details that are being fetched as part of the PWA API are retrieved from `PwaDtoRepository.searchPwas`, which currently only
gets the information from the `MasterPwaDetail` which is the same as the `pwa_details` table that is used in the `api_vw_primary_pwas` view.

Note that there can be multiple consents linked to a PWA, as demonstrated with the inline comment on the view above.

### Option 1: Adding initialConsentDate to PWA type

#### PWA changes

Below is the purposed change to the existing query, where the `PwaConsent` object will be included in a LEFT JOIN, so that we can still retrieve PWAs that have not yet been
consented. The WHERE conditions that were included in the `api_vw_primary_pwas` view are included as part of the LEFT JOIN conditions, except for the `pwad.end_timestamp IS NULL`
which is already part of the existing query.

The `initialConsentDate` will be added to the PwaDto object with a datatype of Instant.

```
@Query("SELECT new uk.co.ogauthority.pwa.externalapi.PwaDto(mpd.masterPwa.id, mpd.reference, mpd.masterPwaDetailStatus, initial_pc.consentInstant) " +
      "FROM MasterPwaDetail mpd " +
      "LEFT JOIN PwaConsent initial_pc ON initial_pc.pwa_id = mpd.masterPwa.id" +
      "AND initial_pc.consent_type = 'INITIAL_PWA' AND mpd.masterPwaDetailStatus = 'CONSENTED'"
      "WHERE mpd.endInstant IS NULL " +
      "AND (mpd.masterPwa.id in (:ids) or COALESCE(:ids, null) is null) " +
      "AND (LOWER(mpd.reference) like LOWER('%'||:reference||'%') or :reference is null) " +
      "AND (mpd.masterPwaDetailStatus = :status or :status is null)"
```

#### EPA changes

There will only be a change to the PWA schema type as part of this change:

```
type Pwa {
    id: Int,
    reference: String,
    pipelines: [Pipeline],
    status: PwaStatus, 
    initialConsentDate: Date
}
```


### Option 2: Adding PwaConsent type 

In this option, all the linked PWA consents for the filtered PWAs, which will allow the consuming services to decide which consent is required rather than being 
limited to the initial consent. 

#### PWA changes

```
@Query("SELECT new uk.co.ogauthority.pwa.externalapi.PwaConsentDto(mpd.masterPwa.id, pc.id, pc.reference pc.consentType, pc.consentInstant, pc.createdInstant) " +
      "FROM MasterPwaDetail mpd " +
      "JOIN PwaConsent pc ON pc.pwa_id = mpd.masterPwa.id" +
      "WHERE mpd.endInstant IS NULL " +
      "AND (mpd.masterPwa.id in (:ids) or COALESCE(:ids, null) is null) " +
```

There will be a new PwaConsentsDto which will then be added as a List to the PwaDto. This will be achieved by doing the following: 
- Search PWAs, then if there are results found search for consents using a set of the masterPwaIds returned from the PWA search
- Pass a set of PWA ids into the PwaConsent repository query above 
- Map the PWA consents to the relevant PWA so that it can be added as a list on the Pwa type

This approach will also require careful use of the `OracleParitionUtil`, in both when querying the PwaConsents and when mapping the PwaConsents to the PWAs. 

#### EPA changes

In EPA, I purpose that we make the following schema changes and that we don't need to add a query param to the existing APIs. 

```
type Pwa {
    id: Int,
    reference: String,
    pipelines: [Pipeline],
    status: PwaStatus, 
    consents: [PwaConsent]
}

type PwaConsent {
    id: Int,
    pwa: Pwa, 
    reference: String, 
    consentType: PwaConsentType, 
    consentDate: Date, 
    createdDate: Date 
}

enum PwaConsentType {
    INITIAL_PWA, 
    VARIATION, 
    DEPOSIT_CONSENT 
}
```

Within Section 29, the required data for the initial consent data for a PWA can be retrieved by filtering on the pwaJson.pwaStatus for 'CONSENTED' and then filtering the consents list for consentType = INITIAL_PWA.

## Decision outcome 

I think it would be best to go with Option 2 as it provides not only the data that Section 29 requires but also provides more flexibility in case we need to get more information from not the initial consent. 

