# ADR 3. Validator selection off-chain specification

Date: 2023-08-13

## Status

Proposed

## Context

As a consequence of [ADR 0002 Validator selector](./0002-validator-selector.md) an off-chain script will automatically publish validator statistics to an oracle.  These statistics are used by the [`validator_selector`](../../contracts/validator_selector/) contract for an optimal validator selection.

## Decision

Next to relevant performance KPIs, a list of recently slashed validators is also needed for [ADR 0002 Validator selector](./0002-validator-selector.md).

Two different off-chain scripts will be developed to perform the necessary operations:
- **List of candidates:** querying of archiving node and select list of validators, publish to oracle
- **Validator blacklist:** listen to slashing events and publish to oracle

The reason two different scripts are used is for reasons of transparancy.

### List of candidates

| Tunable Parameter | Comment | Value |
| --- | --- | --- |
| historical_eras | Number of most recently past eras from which statistics are gathered   | 25 |
| max_commission | Maximum commission value a validator can apply for it to be selected | 5% |
| published_validators | Number of validators published to oracle | 250 |

This list is obtained as follows:

#### 1. Active validators

Obtain a list of all validators active in the last *historical_eras.* This list can be through *api.query.staking.erasRewardPoints*. 

#### 2. Apply commission limits

From the list of active validators, only select those with *max_commission* or less. Can be obtained through *api.query.staking.validators<ValidatorPrefs>*

#### 3. Calculate EMA

For the list of validators with acceptable commission rate, calculate the EMA of earned **Era points** over the last *historical_eras* period. An example implementation is available in *proof-of-concepts/validator-statistics/src/[parse-era-points.py](http://parse-era-points.py/)* 

#### 4. Publish to oracle

Publish the *published_validators* with the best EMA values to the Oracle.

#### Other parameters

The following parameters were considered, but are not used at this point. They could be included in a future version:

- **Oversubscribed validators:** Over-subscription of a validator, as this will no longer be an issue in the future.
- **Uptime:** The actual recent uptime of a validator. An offline node will already be listed in the slashed blacklist or have a lower erapoint EMA.
- **Self staking:** The self staked amount of a validator.
- **Verified:** The verified status of a validator.

### Validator blacklist 

| Tunable Parameter | Comment | Value |
| --- | --- | --- |
| slashing_blacklist_days | Number of days in the past scanned for slashing events | 250 |

The validator black list consists of validators that have been the target of a slashing event in the past *slashing_blacklist_days*. This info can be obtained through the *staking.SlashReported* event.

## Consequences

Per selected validator, the following data is published to the oracle:

| Parameter | Comment |
| --- | --- |
| address | The account address of the validator |
| ema | The calculated EMA over the past historical_eras  |
| total_bond | The total amount of bonded tokens for this validator. A lower total_bond gives a higher reward. |

Per recently slashed validator the following data is published to the oracle:

| Parameter | Comment |
| --- | --- |
| address | The account address of the validator |
