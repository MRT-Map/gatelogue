# Changelog

## Planned
* `RailConnection`, `SeaConnection`, `BusConnection` as nodes instead of edges
* add rail, sea and bus to client/data viewer

## v2.0.6+10 (20260102)
* `gatelogue-types` (ts): fix connection types
* `gatelogue-types` (ts): accept `number` ID in parameters

## v2.0.5+10 (20251115)
* `gatelogue-types` (py): redo classing to fix inheritance lints
* `gatelogue-aggregator`: improved downloader detects incomplete/empty files

## v2.0.4+10 (20250621)
* `gatelogue-aggregator`: temporary blank `code` field for `AirAirport`s
* **Data v10**
  * `AirAirport` `name` field changed to `names` so that multiple names can be attached to one code

## v2.0.3+9 (20250601)
* various refactors inside `gatelogue-aggregator`
* `gatelogue-types` (ts): fix `stops` field inside `RailCompany`
* **Data v9**
  * `ref_stop`, `ref_station` removed from `BusLine`, `RailLine`, `SeaLine`
  * they have been replaced with `stops` and `stations` which are all the stops/stations the line stops at

## v2.0.2+8 (20250505)
* `gatelogue-types` (rs): fix `local` field missing in `SeaCompany` and extra in `AirAirline`

## v2.0.1+8 (20250501)
* update documentation
* various other fixes

## v2.0.0+8 (20250501)
* `gatelogue-aggregator` can be reasonably called stable
* type format can be reasonably called stable
* `gateloge-types` for ts, rs, py are stable
