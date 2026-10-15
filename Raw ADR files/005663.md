# 14. Cache CERC API responses using postgres

Date: 2024-10-29

## Status

Accepted

## Context

The airTEXT service we're building obtains forecasts from [CERC's API][]. These
forecasts are available for a particular day, from 50 areas or "zones". The
forecasts are updated occasionally during the day (we're not clear as to the
exact schedule of updates). A single request to the CERC API can be for:

- a particular zone or for all zones

- either 1, 2 or 3 days

Clearly we don't need to make an external API call to CERC every time a user
requests a forecast for a zone.

## Decision

We will implement a simple "cache" using Postgres:

### We will get forecasts for all zones in a single request

A request to the CERC API endpoint `/getforecast/all` without a zone param
returns forecasts for all zones (currently 50).

### We will request 3 days' worth of forecasts

We'll get forecasts for 3 days: today, tomorrow and the day after. This is how
the UI works currently. (However, our caching strategy won't be tied to this
number of forecasts being returned per zone.)

### We will use Postgres for our cache

This is simple in terms of infrastructure. It also will allow us to retain
cached forecasts to build an archive of historical forecasts. Research is
underway to properly understand users' needs for historical data.

### We will cache 3 days' worth of forecasts for each zone

Each entry in our cache will include these properties:

##### `obtained_at`

The timestamp of when the forecast was fetched. We will use this to expire our
cache after `CERC_FORECAST_API_CACHE_LIMIT_MINS` with the
`CachedForecast.stale?` test.

##### `zone`

The zone to which it relates

##### `data`

A serialised dump of the 3 forecasts which are received for the zone. Note that
we can handle any quantity of forecasts if for example we added a feature
showing a 7 day view.

Note that we won't cache CERC's JSON response. We will cache our "built" domain
`Forecast` entities, like this:

```
#<Forecast
  @obtained_at=2024-10-29 11:59:00 UTC
  @date=2024-10-29
  @zone=
    #<ForecastZone
      @id=9
      @name=Ealing
      @type=1>
  @air_pollution=
    #<AirPollutionPrediction
      @forecasted_at=2024-10-29 10:09:00 UTC
      @nitrogen_dioxide=2
      @particulate_matter_10=2
      @particulate_matter_2_5=2
      @ozone=1
      @value=2
      @label=LOW>
  @uv=
    #<UvPrediction
      @value=2>
  @pollen=
    #<PollenPrediction
      @value=-999>
  @temperature=
    #<TemperaturePrediction
      @min=10.3
      @max=16.4>
>
```

### We will use a naive cache expiration strategy

We will expire the cache based purely on age, for example every 60 mins.

We could in theory get smarter as each forecast in an individual cache record
for a zone contains two "version" numbers, one for the air pollution prediction
and another for the other predictions (pollen, temp, uv etc):

```json
"forecasts": [
  {
    "forecast_date": "2024-10-30",
    "non_pollution_version": null,
    "pollution_version": 202410300809
    ...
  },
  {
    "forecast_date": "2024-10-31",
    "non_pollution_version": null,
    "pollution_version": 202410300349
    ...
  },
  {
    "forecast_date": "2024-11-01",
    "non_pollution_version": null,
    "pollution_version": 202410300349,
    ...
  }
],
```

However:

- `non_pollution_version` is not being supplied by CERC

- the logic/mechanism for recording and comparing the 6 different version
  numbers would be quite a bit more complex

## Consequences

Going forward we'll need to verify that the time limit for expiring the cache is
appropriate.

In the future we might want to refresh the cache in the background before it
expires to avoid having a couple of seconds of slow performance whilst the cache
is being refreshed.

[CERC's API]: https://www.airtext.info/API/#/default/get-forecast
