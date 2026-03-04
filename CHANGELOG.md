# Changelog

## Planned
* `RailConnection`, `SeaConnection`, `BusConnection` as nodes instead of edges
* add rail, sea and bus to client/data viewer

## v3.0.0+12 (20260304)
* `gatelogue-aggregator`
  * rework line builder for `BusBerth`, `RailPlatform` and `SeaDock`
  * one-way data, berth/platform/dock code, 
  * remove graph (it took too long)
  * integrate source-dropping into CLI
  * `Source` rework
    * priority is now based on its order in the final `SOURCES` list, instead of relative to other `Source`s
    * air node updating moved to `GatelogueData`
    * `SOURCES` list now broken down by `Air`, `Bus`, `Rail`, `Sea` and miscellaneous
    * wiki `AirAirline`s and `AirAirport`s separated into individual sources
  * download Dynmap markers and warps only once
* `gatelogue-client`
  * show aircraft/gate width instead of size
  * show arrow between `AirFlight` from and to
* `gatelogue-types`: rework API to account for new data format
* **Data v12**
  * data format moved from `rustworkx`/JSON to SQLite
  * new `BusBerth`, `RailPlatform` and `SeaDock` nodes
  * `RailConnection`, `SeaConnection`, `BusConnection` are now nodes instead of edges
  * `AirFlight`, `RailConnection`, `SeaConnection`, `BusConnection` are now for only one direction and can no longer be for both
    * `AirFlight` `code` is no longer unique. Two `AirFlight`s may have the same code, especially for return trips
  * `AirGate` `size` replaced with `mode`
  * two `AirGate` of the same `AirAirport` now not equivalent if codes are `None`
  * `AirFlight` `mode` replaced with new `Aircraft` class
  * `BusCompany`, `RailCompany`, `SeaCompany` `local` attribute moved to `BusLine`, `RailLine`, `SeaLine`
  * added `duration` attribute to `RailConnection`, `SeaConnection`, `BusConnection`
  * added `link` to `BusCompany`, `RailCompany`, `SeaCompany`

## v2.0.9+11 (20260105)
* **Data v11**
  * `SpawnWarp` new type: `traincarts`

## v2.0.8+10 (20260103)
* `gatelogue-types` (ts): fix even more `Sourced` types
* 
## v2.0.7+10 (20260102)
* `gatelogue-types` (ts): fix more `Sourced` types
* 
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
