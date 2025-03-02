# Changelog

<!-- insertion marker -->
## [v0.6.0b0](https://github.com/sleiner/oocone/releases/tag/0.6.0b0) (2025-03-02)

### Features & Improvements

- oocone can now fetch data for the quarter's solar panels. ([#35](https://github.com/sleiner/oocone/issues/35))
- oocone can now discover multiple areas if present in your Enocoo account. ([#41](https://github.com/sleiner/oocone/issues/41))

### Bug Fixes

- `oocone.Enocoo.get_individual_consumption()` with `interval == "year"` used to return `Consumption` objects where the start was a [datetime.date](https://docs.python.org/3/library/datetime.html#date-objects).
  Now, it returns [datetime.datetime](https://docs.python.org/3/library/datetime.html#datetime-objects), as promised by the type hints. ([#40](https://github.com/sleiner/oocone/issues/40))

### Removals and Deprecations

- All [dataclasses](https://docs.python.org/3/library/dataclasses.html) in the public API are now [frozen](https://docs.python.org/3/library/dataclasses.html#frozen-instances). ([#31](https://github.com/sleiner/oocone/issues/31))
- Dropped support for Python 3.11. ([#36](https://github.com/sleiner/oocone/issues/36))
- `enocoo.types` was renamed to `enocoo.model`. ([#37](https://github.com/sleiner/oocone/issues/37))
- `oocone.Enocoo.get_area_ids()` was removed in favor of `oocone.Enocoo.get_areas()`. ([#41](https://github.com/sleiner/oocone/issues/41))

### Miscellaneous

- oocone is now tested with Python 3.13. ([#36](https://github.com/sleiner/oocone/issues/36))
- oocone is now type-checked using [mypy](https://mypy.readthedocs.io/). ([#40](https://github.com/sleiner/oocone/issues/40))


## [v0.5.1](https://github.com/sleiner/oocone/releases/tag/0.5.1) (2024-09-25)

### Bug Fixes

- Consumption data in the enocoo dashboard used to be off by one unit of time (usually 15 minutes).
  We are now compensating for this. ([#30](https://github.com/sleiner/oocone/issues/30))


## [v0.5.0](https://github.com/sleiner/oocone/releases/tag/0.5.0) (2024-09-22)

### Removals and Deprecations

- `MeterStatus.value` and `TrafficLightStatus.current_energy_price` are not a `float` anymore.
  Instead, they now have the new type `Quantity`, which contains not only the numeric value, but also a unit.
  Consequently, `MeterStatus.unit` has been removed. ([#28](https://github.com/sleiner/oocone/issues/28))


## [v0.4.0](https://github.com/sleiner/oocone/releases/tag/0.4.0) (2024-09-18)

### Features & Improvements

- We made `Enocoo.get_meter_table` more flexible:

  -   You can now pass in a date for which the latest meter table shall be returned.
  -   If no data is available yet for the meter table page of the given day, we try looking at the meter table page for the previous day.
      If that contains data for the given day at 00:00, we return that data.
      Additionally, you may set a time until which data from the previous day are still acceptable.
      This is helpful, because data from the Enocoo website may lag behind up until 30 minutes in regular operation.
      So, shortly after midnight, the newest data available might be from 23:45.
      If you set the `allow_previous_day_until` parameter to `datetime.time(23, 45)`, you will get those data shortly after midnight.

  ([#26](https://github.com/sleiner/oocone/issues/26))

### Bug Fixes

- We now ignore the false-positive `MarkupResemblesLocatorWarning` from `beautifulsoup4`. ([#19](https://github.com/sleiner/oocone/issues/19))
- Adapt to new data returned on change from summer to winter time:
  We don't throw an error anymore if we get more than four data points per hour. ([#25](https://github.com/sleiner/oocone/issues/25))

### Miscellaneous

- More debug logging has been added. ([#26](https://github.com/sleiner/oocone/issues/26))


## [v0.3.1](https://github.com/sleiner/oocone/releases/tag/0.3.1) (2024-07-29)


### Bug Fixes

- Removed broken LRU cache for `Enocoo.get_area_ids()` ([#16](https://github.com/sleiner/oocone/issues/16))


## [v0.3.0](https://github.com/sleiner/oocone/releases/tag/0.3.0) (2024-07-28)

### Features & Improvements


- Added access to historic consumption data via ` Enocoo.get_individual_consumption()` [#15](https://github.com/sleiner/oocone/issues/15)

## [v0.2.1](https://github.com/sleiner/oocone/releases/tag/0.2.1) (2024-06-30)

### Bug Fixes


- Fix issues in automated release script. [#12](https://github.com/sleiner/oocone/issues/12)

## [v0.2](https://github.com/sleiner/oocone/releases/tag/0.2) (2024-06-30)

### Features & Improvements


- Introduce new API `Enocoo.get_meter_table()` for getting the current meter readings. [#10](https://github.com/sleiner/oocone/issues/10)

## [v0.1](https://github.com/sleiner/oocone/releases/tag/0.1) (2024-06-19)

Initial release
