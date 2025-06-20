//! # Usage
//! The data can be imported into your Rust project with `serde`. Add to your `Cargo.toml`:
//! ```toml
//! gatelogue-types = { version = "2", features = [...] }
//!
//! # To import directly from the repository:
//! gatelogue-types = { git = "https://github.com/mrt-map/gatelogue", package = "gatelogue-types", features = [...] }
//! ```
//! where `features` as denoted by `...` are `reqwest_get`, `surf_get` and `ureq_get`.
//!
//! To retrieve the data:
//! ```rust,ignore
//! use gatelogue_types::GatelogueData;
//! GatelogueData::reqwest_get_with_sources().await?; // with sources, requires `reqwest_get` feature
//! GatelogueData::reqwest_get_no_sources().await?; // no sources, requires `reqwest_get` feature
//! GatelogueData::surf_get_with_sources().await?; // with sources, requires `surf_get` feature
//! GatelogueData::surf_get_no_sources().await?; // no sources, requires `surf_get` feature
//! GatelogueData::ureq_get_with_sources()?; // with sources, requires `ureq_get` feature
//! GatelogueData::ureq_get_no_sources()?; // no sources, requires `ureq_get` feature
//! ```

use duplicate::duplicate_item;
use enum_as_inner::EnumAsInner;
use serde::{Deserialize, Deserializer, Serialize};
use std::collections::HashMap;
use std::ops::{Deref, DerefMut};
use thiserror::Error;

#[derive(Error, Debug)]
#[non_exhaustive]
pub enum Error {
    #[cfg(feature = "reqwest_get")]
    #[error("reqwest error: {0:?}")]
    Reqwest(#[from] reqwest::Error),
    #[cfg(feature = "surf_get")]
    #[error("surf error: {0:?}")]
    Surf(surf::Error),
    #[cfg(feature = "ureq_get")]
    #[error("ureq error: {0:?}")]
    Ureq(#[from] ureq::Error),

    #[error("decoding error: {0:?}")]
    Decode(#[from] serde_json::error::Error),

    #[error("No node {0}")]
    NoNode(ID),
    #[error("{0} not {1}")]
    IncorrectType(ID, &'static str),

    #[error("unknown error")]
    Unknown,
}

#[cfg(feature = "surf_get")]
impl From<surf::Error> for Error {
    fn from(err: surf::Error) -> Self {
        Self::Surf(err)
    }
}

pub type Result<T, E = Error> = std::result::Result<T, E>;

pub type ID = u16;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GatelogueData {
    pub timestamp: String,
    pub version: u64,
    pub nodes: HashMap<ID, Node>,
}
impl GatelogueData {
    #[cfg(feature = "reqwest_get")]
    pub async fn reqwest_get_with_sources() -> Result<Self> {
        let bytes = reqwest::get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json",
        )
        .await?
        .bytes()
        .await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "reqwest_get")]
    pub async fn reqwest_get_no_sources() -> Result<Self> {
        let bytes = reqwest::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json").await?.bytes().await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "surf_get")]
    pub async fn surf_get_with_sources() -> Result<Self> {
        let bytes = surf::get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json",
        )
        .recv_bytes()
        .await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "surf_get")]
    pub async fn surf_get_no_sources() -> Result<Self> {
        let bytes = surf::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json").recv_bytes().await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "ureq_get")]
    pub fn ureq_get_with_sources() -> Result<Self> {
        let reader = ureq::get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json",
        )
        .call()?
        .into_body()
        .into_reader();
        Ok(serde_json::from_reader(reader)?)
    }
    #[cfg(feature = "ureq_get")]
    pub fn ureq_get_no_sources() -> Result<Self> {
        let reader = ureq::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json").call()?.into_body().into_reader();
        Ok(serde_json::from_reader(reader)?)
    }

    #[duplicate_item(
        nodes_  as_node Ty;
        [air_airlines] [as_air_airline] [AirAirline];
        [air_airports] [as_air_airport] [AirAirport];
        [air_flights] [as_air_flight] [AirFlight];
        [air_gates] [as_air_gate] [AirGate];
        [bus_companies] [as_bus_company] [BusCompany];
        [bus_lines] [as_bus_line] [BusLine];
        [bus_stops] [as_bus_stop] [BusStop];
        [rail_companies] [as_rail_company] [RailCompany];
        [rail_lines] [as_rail_line] [RailLine];
        [rail_stations] [as_rail_station] [RailStation];
        [sea_companies] [as_sea_company] [SeaCompany];
        [sea_lines] [as_sea_line] [SeaLine];
        [sea_stops] [as_sea_stop] [SeaStop];
        [spawn_warps] [as_spawn_warp] [SpawnWarp];
        [towns] [as_town] [Town];
    )]
    pub fn nodes_(&self) -> impl Iterator<Item = &Ty> {
        self.nodes.values().filter_map(|a| a.as_node())
    }

    #[duplicate_item(
        nodes_mut  as_node_mut Ty;
        [air_airlines_mut] [as_air_airline_mut] [AirAirline];
        [air_airports_mut] [as_air_airport_mut] [AirAirport];
        [air_flights_mut] [as_air_flight_mut] [AirFlight];
        [air_gates_mut] [as_air_gate_mut] [AirGate];
        [bus_companies_mut] [as_bus_company_mut] [BusCompany];
        [bus_lines_mut] [as_bus_line_mut] [BusLine];
        [bus_stops_mut] [as_bus_stop_mut] [BusStop];
        [rail_companies_mut] [as_rail_company_mut] [RailCompany];
        [rail_lines_mut] [as_rail_line_mut] [RailLine];
        [rail_stations_mut] [as_rail_station_mut] [RailStation];
        [sea_companies_mut] [as_sea_company_mut] [SeaCompany];
        [sea_lines_mut] [as_sea_line_mut] [SeaLine];
        [sea_stops_mut] [as_sea_stop_mut] [SeaStop];
        [spawn_warps_mut] [as_spawn_warp_mut] [SpawnWarp];
        [towns_mut] [as_town_mut] [Town];
    )]
    pub fn nodes_mut(&mut self) -> impl Iterator<Item = &mut Ty> {
        self.nodes.values_mut().filter_map(|a| a.as_node_mut())
    }

    #[duplicate_item(
        get_node  as_node Ty;
        [get_air_airline] [as_air_airline] [AirAirline];
        [get_air_airport] [as_air_airport] [AirAirport];
        [get_air_flight] [as_air_flight] [AirFlight];
        [get_air_gate] [as_air_gate] [AirGate];
        [get_bus_company] [as_bus_company] [BusCompany];
        [get_bus_line] [as_bus_line] [BusLine];
        [get_bus_stop] [as_bus_stop] [BusStop];
        [get_rail_company] [as_rail_company] [RailCompany];
        [get_rail_line] [as_rail_line] [RailLine];
        [get_rail_station] [as_rail_station] [RailStation];
        [get_sea_company] [as_sea_company] [SeaCompany];
        [get_sea_line] [as_sea_line] [SeaLine];
        [get_sea_stop] [as_sea_stop] [SeaStop];
        [get_spawn_warp] [as_spawn_warp] [SpawnWarp];
        [get_town] [as_town] [Town];
    )]
    pub fn get_node(&self, id: ID) -> Result<&Ty> {
        self.nodes
            .get(&id)
            .ok_or(Error::NoNode(id))?
            .as_node()
            .ok_or(Error::IncorrectType(id, stringify!(Ty)))
    }

    #[duplicate_item(
        get_node_mut  as_node_mut Ty;
        [get_air_airline_mut] [as_air_airline_mut] [AirAirline];
        [get_air_airport_mut] [as_air_airport_mut] [AirAirport];
        [get_air_flight_mut] [as_air_flight_mut] [AirFlight];
        [get_air_gate_mut] [as_air_gate_mut] [AirGate];
        [get_bus_company_mut] [as_bus_company_mut] [BusCompany];
        [get_bus_line_mut] [as_bus_line_mut] [BusLine];
        [get_bus_stop_mut] [as_bus_stop_mut] [BusStop];
        [get_rail_company_mut] [as_rail_company_mut] [RailCompany];
        [get_rail_line_mut] [as_rail_line_mut] [RailLine];
        [get_rail_station_mut] [as_rail_station_mut] [RailStation];
        [get_sea_company_mut] [as_sea_company_mut] [SeaCompany];
        [get_sea_line_mut] [as_sea_line_mut] [SeaLine];
        [get_sea_stop_mut] [as_sea_stop_mut] [SeaStop];
        [get_spawn_warp_mut] [as_spawn_warp_mut] [SpawnWarp];
        [get_town_mut] [as_town_mut] [Town];
    )]
    pub fn get_node_mut(&mut self, id: ID) -> Result<&mut Ty> {
        self.nodes
            .get_mut(&id)
            .ok_or(Error::NoNode(id))?
            .as_node_mut()
            .ok_or(Error::IncorrectType(id, stringify!(Ty)))
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(untagged)]
pub enum Sourced<T> {
    Unsourced(T),
    Sourced { v: T, s: Vec<String> },
}

impl<T> Deref for Sourced<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        match self {
            Self::Unsourced(v) | Self::Sourced { v, .. } => v,
        }
    }
}
impl<T> DerefMut for Sourced<T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        match self {
            Self::Unsourced(v) | Self::Sourced { v, .. } => v,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NodeCommon {
    pub i: ID,
    pub source: Vec<String>,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug, Serialize, Deserialize)]
pub enum World {
    Old,
    New,
    Space,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Proximity {
    pub distance: Option<f64>,
    pub explicit: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LocatedNodeCommon {
    pub i: ID,
    pub source: Vec<String>,
    pub world: Option<Sourced<World>>,
    pub coordinates: Option<Sourced<(f64, f64)>>,
    #[serde(deserialize_with = "deserialise_proximity")]
    pub proximity: HashMap<ID, Sourced<Proximity>>,
    pub shared_facility: Vec<Sourced<ID>>,
}

#[derive(Clone, Debug, Serialize, Deserialize, EnumAsInner)]
#[serde(tag = "type")]
pub enum Node {
    AirAirline(AirAirline),
    AirAirport(AirAirport),
    AirFlight(AirFlight),
    AirGate(AirGate),
    BusCompany(BusCompany),
    BusLine(BusLine),
    BusStop(BusStop),
    SeaCompany(SeaCompany),
    SeaLine(SeaLine),
    SeaStop(SeaStop),
    RailCompany(RailCompany),
    RailLine(RailLine),
    RailStation(RailStation),
    SpawnWarp(SpawnWarp),
    Town(Town),
}

#[derive(Clone, Copy, PartialEq, Eq, Debug, Serialize, Deserialize)]
pub enum AirMode {
    #[serde(rename = "helicopter")]
    Helicopter,
    #[serde(rename = "seaplane")]
    Seaplane,
    #[serde(rename = "warp plane")]
    WarpPlane,
    #[serde(rename = "traincarts plane")]
    TrainCartsPlane,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AirAirline {
    pub name: String,
    pub link: Option<Sourced<String>>,
    pub flights: Vec<Sourced<ID>>,
    pub gates: Vec<Sourced<ID>>,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AirAirport {
    pub code: String,
    pub names: Option<Sourced<Vec<String>>,
    pub link: Option<Sourced<String>>,
    pub modes: Option<Sourced<Vec<AirMode>>>,
    pub gates: Vec<Sourced<ID>>,
    #[serde(flatten)]
    pub common: LocatedNodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AirFlight {
    pub codes: Vec<String>,
    pub mode: Option<Sourced<AirMode>>,
    pub airline: Sourced<ID>,
    pub gates: Vec<Sourced<ID>>,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AirGate {
    pub codes: Option<String>,
    pub size: Option<Sourced<String>>,
    pub airline: Option<Sourced<ID>>,
    pub airport: Sourced<ID>,
    pub flights: Vec<Sourced<ID>>,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BusCompany {
    pub name: String,
    pub lines: Vec<Sourced<ID>>,
    pub stops: Vec<Sourced<ID>>,
    pub local: bool,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BusLine {
    pub code: String,
    pub name: Option<Sourced<String>>,
    pub colour: Option<Sourced<String>>,
    pub company: Sourced<ID>,
    pub stops: Vec<Sourced<ID>>,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BusStop {
    pub codes: Vec<String>,
    pub name: Option<Sourced<String>>,
    pub company: Sourced<ID>,
    #[serde(deserialize_with = "deserialise_connections")]
    pub connections: HashMap<ID, Vec<Sourced<Connection>>>,
    #[serde(flatten)]
    pub common: LocatedNodeCommon,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum RailMode {
    #[serde(rename = "warp")]
    Warp,
    #[serde(rename = "cart")]
    Cart,
    #[serde(rename = "traincarts")]
    TrainCart,
    #[serde(rename = "vehicles")]
    Vehicles,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RailCompany {
    pub name: String,
    pub lines: Vec<Sourced<ID>>,
    pub stations: Vec<Sourced<ID>>,
    pub local: bool,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RailLine {
    pub code: String,
    pub name: Option<Sourced<String>>,
    pub colour: Option<Sourced<String>>,
    pub company: Sourced<ID>,
    pub stations: Vec<Sourced<ID>>,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RailStation {
    pub codes: Vec<String>,
    pub name: Option<Sourced<String>>,
    pub company: Sourced<ID>,
    #[serde(deserialize_with = "deserialise_connections")]
    pub connections: HashMap<ID, Vec<Sourced<Connection>>>,
    #[serde(flatten)]
    pub common: LocatedNodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SeaCompany {
    pub name: String,
    pub lines: Vec<Sourced<ID>>,
    pub stops: Vec<Sourced<ID>>,
    pub local: bool,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SeaLine {
    pub code: String,
    pub name: Option<Sourced<String>>,
    pub colour: Option<Sourced<String>>,
    pub company: Sourced<ID>,
    pub stops: Vec<Sourced<ID>>,
    #[serde(flatten)]
    pub common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SeaStop {
    pub codes: Vec<String>,
    pub name: Option<Sourced<String>>,
    pub company: Sourced<ID>,
    #[serde(deserialize_with = "deserialise_connections")]
    pub connections: HashMap<ID, Vec<Sourced<Connection>>>,
    #[serde(flatten)]
    pub common: LocatedNodeCommon,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SpawnWarpType {
    Premier,
    Terminus,
    Portal,
    Misc,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SpawnWarp {
    pub name: String,
    pub warp_type: SpawnWarpType,
    #[serde(flatten)]
    pub common: LocatedNodeCommon,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug, Serialize, Deserialize)]
pub enum Rank {
    Unranked,
    Councillor,
    Mayor,
    Senator,
    Governor,
    Premier,
    Community,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Town {
    pub name: String,
    pub rank: Sourced<Rank>,
    pub mayor: Sourced<String>,
    pub deputy_mayor: Sourced<Option<String>>,
    #[serde(flatten)]
    pub common: LocatedNodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Connection {
    pub line: ID,
    pub direction: Option<Direction>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Direction {
    pub direction: ID,
    pub forward_label: Option<String>,
    pub backward_label: Option<String>,
    pub one_way: Sourced<bool>,
}

fn deserialise_connections<'de, D: Deserializer<'de>>(
    de: D,
) -> Result<HashMap<ID, Vec<Sourced<Connection>>>, D::Error> {
    HashMap::<String, Vec<Sourced<Connection>>>::deserialize(de)?
        .into_iter()
        .map(|(k, v)| Ok((k.parse::<ID>().map_err(serde::de::Error::custom)?, v)))
        .collect()
}
fn deserialise_proximity<'de, D: Deserializer<'de>>(
    de: D,
) -> Result<HashMap<ID, Sourced<Proximity>>, D::Error> {
    HashMap::<String, Sourced<Proximity>>::deserialize(de)?
        .into_iter()
        .map(|(k, v)| Ok((k.parse::<ID>().map_err(serde::de::Error::custom)?, v)))
        .collect()
}

#[cfg(test)]
#[cfg(feature = "ureq_get")]
mod test {
    use super::*;

    #[test]
    fn ureq1() {
        let _ = GatelogueData::ureq_get_with_sources().unwrap();
    }

    #[test]
    fn ureq2() {
        let _ = GatelogueData::ureq_get_no_sources().unwrap();
    }
}
