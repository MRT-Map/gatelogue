use std::collections::HashMap;
use std::ops::{Deref, DerefMut};
use serde::{Deserialize, Deserializer, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GatelogueData {
    timestamp: String,
    version: u64,
    nodes: HashMap<ID, Node>
}
impl GatelogueData {
    #[cfg(feature = "reqwest_get")]
    pub async fn reqwest_get_with_sources() -> Result<Self, Box<dyn std::error::Error>> {
        let bytes = reqwest::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json").await?.bytes().await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "reqwest_get")]
    pub async fn reqwest_get_no_sources() -> Result<Self, Box<dyn std::error::Error>> {
        let bytes = reqwest::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json").await?.bytes().await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "surf_get")]
    pub async fn surf_get_with_sources() -> Result<Self, Box<dyn std::error::Error>> {
        let bytes = surf::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json").recv_bytes().await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "surf_get")]
    pub async fn surf_get_no_sources() -> Result<Self, Box<dyn std::error::Error>> {
        let bytes = surf::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json").recv_bytes().await?;
        Ok(serde_json::from_slice(&bytes)?)
    }
    #[cfg(feature = "ureq_get")]
    pub fn ureq_get_with_sources() -> Result<Self, Box<dyn std::error::Error>> {
        let reader = ureq::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json").call()?.into_reader();
        Ok(serde_json::from_reader(reader)?)
    }
    #[cfg(feature = "ureq_get")]
    pub fn ureq_get_no_sources() -> Result<Self, Box<dyn std::error::Error>> {
        let reader = ureq::get("https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json").call()?.into_reader();
        Ok(serde_json::from_reader(reader)?)
    }
}

pub type ID = u16;

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
            Self::Sourced {v, ..} => v,
            Self::Unsourced(v) => v,
        }
    }
}
impl<T> DerefMut for Sourced<T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        match self {
            Self::Sourced {v, ..} => v,
            Self::Unsourced(v) => v,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NodeCommon {
    i: ID,
    source: Vec<String>,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum World {
    Old,
    New,
    Space,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Proximity {
    distance: Option<f64>, // TODO remove distance
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LocatedNodeCommon {
    i: ID,
    source: Vec<String>,
    world: Option<Sourced<World>>,
    coordinates: Option<Sourced<(f64, f64)>>,
    #[serde(deserialize_with = "deserialise_proximity")]
    proximity: HashMap<ID, Sourced<Proximity>>,
    shared_facility: Vec<Sourced<ID>>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
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

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
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
    name: String,
    link: Option<Sourced<String>>,
    flights: Vec<Sourced<ID>>,
    gates: Vec<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AirAirport {
    code: String,
    name: Option<Sourced<String>>,
    link: Option<Sourced<String>>,
    modes: Option<Sourced<Vec<AirMode>>>,
    gates: Vec<Sourced<ID>>,
    #[serde(flatten)]
    common: LocatedNodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AirFlight {
    codes: Vec<String>,
    mode: Option<Sourced<AirMode>>,
    airline: Sourced<ID>,
    gates: Vec<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AirGate {
    codes: Option<String>,
    size: Option<Sourced<String>>,
    airline: Option<Sourced<ID>>,
    airport: Sourced<ID>,
    flights: Vec<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BusCompany {
    name: String,
    lines: Vec<Sourced<ID>>,
    stops: Vec<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BusLine {
    code: String,
    name: Option<Sourced<String>>,
    colour: Option<Sourced<String>>,
    company: Sourced<ID>,
    ref_stop: Option<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BusStop {
    codes: Vec<String>,
    name: Option<Sourced<String>>,
    company: Sourced<ID>,
    #[serde(deserialize_with = "deserialise_connections")]
    connections: HashMap<ID, Vec<Sourced<Connection>>>,
    #[serde(flatten)]
    common: LocatedNodeCommon,
}


#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum RailMode {
    #[serde(rename = "warp")]
    Warp,
    #[serde(rename = "cart")]
    Cart,
    #[serde(rename = "traincart")]
    TrainCart,
    #[serde(rename = "vehicles")]
    Vehicles,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RailCompany {
    name: String,
    lines: Vec<Sourced<ID>>,
    stations: Vec<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RailLine {
    code: String,
    name: Option<Sourced<String>>,
    colour: Option<Sourced<String>>,
    company: Sourced<ID>,
    ref_stop: Option<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RailStation {
    codes: Vec<String>,
    name: Option<Sourced<String>>,
    company: Sourced<ID>,
    #[serde(deserialize_with = "deserialise_connections")]
    connections: HashMap<ID, Vec<Sourced<Connection>>>,
    #[serde(flatten)]
    common: LocatedNodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SeaCompany {
    name: String,
    lines: Vec<Sourced<ID>>,
    stops: Vec<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SeaLine {
    code: String,
    name: Option<Sourced<String>>,
    colour: Option<Sourced<String>>,
    company: Sourced<ID>,
    ref_stop: Option<Sourced<ID>>,
    #[serde(flatten)]
    common: NodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SeaStop {
    codes: Vec<String>,
    name: Option<Sourced<String>>,
    company: Sourced<ID>,
    #[serde(deserialize_with = "deserialise_connections")]
    connections: HashMap<ID, Vec<Sourced<Connection>>>,
    #[serde(flatten)]
    common: LocatedNodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SpawnWarpType {
    Premier,
    Terminus,
    Portal,
    Misc
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SpawnWarp {
    name: String,
    warp_type: SpawnWarpType,
    #[serde(flatten)]
    common: LocatedNodeCommon,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum Rank {
    Unranked,
    Councillor,
    Mayor,
    Senator,
    Governor,
    Premier,
    Community
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Town {
    name: String,
    rank: Sourced<Rank>,
    mayor: Sourced<String>,
    deputy_mayor: Sourced<Option<String>>,
    #[serde(flatten)]
    common: LocatedNodeCommon,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Connection {
    line: ID,
    direction: Option<Direction>
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Direction {
    direction: ID,
    forward_label: Option<String>,
    backward_label: Option<String>,
    one_way: Sourced<bool>
}

fn deserialise_connections<'de, D: Deserializer<'de>>(de: D) -> Result<HashMap<ID, Vec<Sourced<Connection>>>, D::Error> {
    HashMap::<String, Vec<Sourced<Connection>>>::deserialize(de)?.into_iter()
        .map(|(k, v)| Ok((k.parse::<ID>().map_err(serde::de::Error::custom)?, v))).collect()
}fn deserialise_proximity<'de, D: Deserializer<'de>>(de: D) -> Result<HashMap<ID, Sourced<Proximity>>, D::Error> {
    HashMap::<String, Sourced<Proximity>>::deserialize(de)?.into_iter()
        .map(|(k, v)| Ok((k.parse::<ID>().map_err(serde::de::Error::custom)?, v))).collect()
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