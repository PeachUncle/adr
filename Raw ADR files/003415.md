# Minimal dataset ILIAD Registry
* Status:  accepted (v01, 2021-11-04)
* Deciders: ILIAD registry project
* Date: 23 June 2021

## Context

Make it possible to add patient, gene anomaly and chromosomal anomaly information in the ILIAD registry. The framework to add new patient information with linked gene or chromosomal anomalies is called the data model, in this model fields are defined, descriptions of questions are added, drop_down or radio button chosen. The data model is made in EMX_1, a newer version is available but not yet compatible with wishes of ERN ITHACA. The ILIAD data model needs the newest version of MOLGENIS(9.xx), since there are some dependencies(expressions) on what you see in edit-mode.

- EMX 1
- Expressions (`validationExpression`, `visible`)
- Default values (`defaultValue`)
- Range values (`rangeMin`, `rangeMax`)
- Compounds (`partOfAttribute`)
- Date now (automatic adding creation date (`auto`))

## Decision

 Information from patients with linked anomalies are separated, this means that there are potentially three tables to be filled with information regarding one case. When adding patient information manually it depends on how many anomalies should be linked to that patient, more then one form needs to be saved. A patient with a biologically confirmed rare disease can have a molecular diagnosis or a chromosomal diagnosis or both. Codebooks and option list(list extends to templateOptionlist) are stored in a separate package. This package can be used by all users (view-permissions).

Datamodel:
* [/data/ILIAD_datamodel.xlsx](/ERN_implementation/ERN_ITHACA/data/ILIAD_datamodel_v01_2021-11-04.xlsx)
* [/data/Overview_codebooks.xlsx](/ERN_implementation/ERN_ITHACA/data/Overview_codebooks_v01_2021-11-04.xlsx)

## Consequences

Adding linked information; patient linked to gene and/or chromosomal anomaly, can be confusing. When manually adding patients, you need to fill in more than one screen. And using the bulk upload, linked items need to have corresponding ids. 

## External links
- [data](/ERN_implementation/ERN_ITHACA/data/)
