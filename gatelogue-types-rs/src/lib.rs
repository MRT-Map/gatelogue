//! Rust utility library for using Gatelogue data in Rust projects. It will load the database for you to access via ORM or raw SQL.
//!
//! # Installation
//! Add to your `Cargo.toml`:
//! ```toml
//! gatelogue-types = { version = "3", features = [...] }
//!
//! # To import directly from the repository:
//! gatelogue-types = { git = "https://github.com/mrt-map/gatelogue", package = "gatelogue-types", features = [...] }
//! ```
//! Features as denoted by `...` include `reqwest_get`, `surf_get`, `ureq_get` (to download with `reqwest`, `surf` and `ureq` respectively) and `bundled` (to bundle SQLite).
//!
//! # Usage
//! To retrieve the data:
//! ```rust
//! use gatelogue_types::{GD, getter};
//! # #[tokio::main]
//! # async fn main() -> Result<(), Box<dyn std::error::Error>> {
//! // with pre-written getter!() functions:
//! let gd = GD::get_async_no_sources(getter!(reqwest)).await?; // retrieve data (async)
//! let gd = GD::get_no_sources(getter!(ureq))?; // retrieve data (blocking)
//!
//! // or with any HTTP client of your choice (with a callable that takes in a &str and returns an AsRef<[u8]>):
//! let gd = GD::get_async_no_sources(async |url| surf::get(url).recv_bytes().await); // retrieve data (async)
//! let gd = GD::get_no_sources(|url| ureq::get(url).call()?.into_body().read_to_vec())?; // retrieve data (blocking)
//!
//! // similar syntax can be used if you want the sources, with `get_async_with_sources` and `get_with_sources`
//! # Ok(()) }
//! ```
//! `getter!()` accepts the following inputs:
//! - `reqwest` (async) requiring `reqwest`
//! - `reqwest_blocking` (blocking) requiring `reqwest` with `blocking` feature
//! - `surf` (async) requiring `surf`
//! - `ureq` (blocking) requiring `ureq`
//! - `isahc` (blocking) requiring `isahc`
//! - `isahc_async` (async) requiring `isahc`
//! - `attohttpc` (blocking) requiring `attohttpc` (untested)
//! - `minreq` (blocking) requiring `minreq`
//! - `wreq` (async) requiring `wreq`
//!
//! Using the ORM does not require SQL and makes for generally clean code.
//! However, doing this is very inefficient as each attribute access is one SQL query.
//! ```rust
//! use gatelogue_types::AirAirport;
//! # fn main() -> Result<(), Box<dyn std::error::Error>> {
//! # let gd = gatelogue_types::GD::get_no_sources(gatelogue_types::getter!(ureq))?;
//! for airport in gd.nodes_of_type::<AirAirport>()? {
//!     for gate in airport.gates(&gd)? {
//!         println!("Airport {:?} has gate {:?}", airport.code(&gd)?, gate.code(&gd)?)
//!     }
//! }
//! # Ok(()) }
//! ```
//!
//! Querying the underlying `SQLite` database directly with `rusqlite` is generally more efficient and faster.
//! It is also the only way to access the `*Source` tables, if you retrieved the database with those.
//!
//! ```rust
//! # fn main() -> Result<(), Box<dyn std::error::Error>> {
//! # let gd = gatelogue_types::GD::get_no_sources(gatelogue_types::getter!(ureq))?;
//! gd.0.prepare("SELECT A.code, G.code FROM AirGate G INNER JOIN AirAirport A ON G.airport = A.i")?
//!     .query_map((), |row| {
//!         println!("Airport {:?} has gate {:?}", row.get::<_, String>(0)?, row.get::<_, String>(1)?);
//!         Ok(())
//!     })?;
//! # Ok(()) }
//! ```

use std::fmt::Debug;
use rusqlite::{types::FromSql, Connection};

mod error;
mod node;
mod util;

pub use error::*;
pub use node::{
    air::*, bus::*, located::*, rail::*, sea::*, spawn_warp::*, town::*, AnyNode, Node,
};
pub use util::ID;

use crate::util::ConnectionExt;

pub const URL: &str =
    "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.db";
pub const URL_NO_SOURCES: &str =
    "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data-ns.db";

#[macro_export]
macro_rules! getter {
    (reqwest) => {async |url: &'static str| -> Result<Vec<u8>, reqwest::Error> {Ok(reqwest::get(url).await?.bytes().await?.to_vec())}};
    (reqwest_blocking) => {|url: &'static str| -> Result<Vec<u8>, reqwest::Error> {Ok(reqwest::blocking::get(url)?.bytes()?.to_vec())}};
    (surf) => {async |url: &'static str| -> Result<Vec<u8>, surf::Error> {surf::get(url).recv_bytes().await}};
    (ureq) => {|url: &'static str| -> Result<Vec<u8>, ureq::Error> {ureq::get(url).call()?.into_body().read_to_vec()}};
    (isahc) => {|url: &'static str| -> Result<Vec<u8>, isahc::Error> {Ok(isahc::ReadResponseExt::bytes(&mut isahc::get(url)?)?)}};
    (isahc_async) => {async |url: &'static str| -> Result<Vec<u8>, isahc::Error> {Ok(isahc::AsyncReadResponseExt::bytes(&mut isahc::get_async(url).await?).await?)}};
    (attohttpc) => {|url: &'static str| -> Result<Vec<u8>, attohttpc::Error> {attohttpc::get(url).send()?.bytes()}};
    (minreq) => {|url: &'static str| -> Result<Vec<u8>, minreq::Error> {Ok(minreq::get(url).send()?.into_bytes())}};
    (wreq) => {async |url: &'static str| -> Result<Vec<u8>, wreq::Error> {Ok(wreq::get(url).send().await?.bytes().await?.to_vec())}};
}

pub struct GD(pub Connection);

impl GD {
    fn from_bytes(bytes: &[u8]) -> Result<Self> {
        let mut conn = Connection::open_in_memory()?;
        conn.deserialize_read_exact("main", bytes, bytes.len(), true)?;
        Ok(Self(conn))
    }
    pub async fn get_async_with_sources<F: AsyncFnOnce(&'static str) -> Result<B, E>, B: AsRef<[u8]>, E: Debug + Send + Sync + 'static>(getter: F) -> Result<Self> {
        Self::from_bytes(getter(URL).await.map_err(|e| Error::HTTPGetError(Box::new(e)))?.as_ref())
    }
    pub async fn get_async_no_sources<F: AsyncFnOnce(&'static str) -> Result<B, E>, B: AsRef<[u8]>, E: Debug + Send + Sync + 'static>(getter: F) -> Result<Self> {
        Self::from_bytes(getter(URL_NO_SOURCES).await.map_err(|e| Error::HTTPGetError(Box::new(e)))?.as_ref())
    }
    pub fn get_with_sources<F: FnOnce(&'static str) -> Result<B, E>, B: AsRef<[u8]>, E: Debug + Send + Sync + 'static>(getter: F) -> Result<Self> {
        Self::from_bytes(getter(URL).map_err(|e| Error::HTTPGetError(Box::new(e)))?.as_ref())
    }
    pub fn get_no_sources<F: FnOnce(&'static str) -> Result<B, E>, B: AsRef<[u8]>, E: Debug + Send + Sync + 'static>(getter: F) -> Result<Self> {
        Self::from_bytes(getter(URL_NO_SOURCES).map_err(|e| Error::HTTPGetError(Box::new(e)))?.as_ref())
    }

    pub fn timestamp(&self) -> Result<String> {
        self.0
            .query_one("SELECT timestamp FROM Metadata", (), |a| a.get(0))
            .map_err(Into::into)
    }
    pub fn version(&self) -> Result<u32> {
        self.0
            .query_one("SELECT version FROM Metadata", (), |a| a.get(0))
            .map_err(Into::into)
    }
    pub fn has_sources(&self) -> Result<bool> {
        self.0
            .query_one("SELECT has_sources FROM Metadata", (), |a| a.get(0))
            .map_err(Into::into)
    }

    pub fn nodes(&self) -> Result<Vec<AnyNode>> {
        self.0
            .query_and_then_get_vec("SELECT i FROM Node", (), |a| {
                AnyNode::from_id(self, a.get(0)?).map(|a| a.unwrap())
            })
    }
    pub fn located_nodes(&self) -> Result<Vec<AnyLocatedNode>> {
        self.0
            .query_and_then_get_vec("SELECT i FROM LocatedNode", (), |a| {
                AnyLocatedNode::from_id(self, a.get(0)?).map(|a| a.unwrap())
            })
    }
    pub fn nodes_of_type<T: Node + From<ID> + FromSql>(&self) -> Result<Vec<T>> {
        let ty = T::from(0).ty();
        self.0.query_and_then_get_vec(
            "SELECT i FROM Node WHERE type = ?",
            (ty,),
            |a| Ok(a.get(0)?),
        )
    }
    pub fn get_node(&self, id: ID) -> Result<Option<AnyNode>> {
        AnyNode::from_id(self, id)
    }
    pub fn get_located_node(&self, id: ID) -> Result<Option<AnyLocatedNode>> {
        AnyLocatedNode::from_id(self, id)
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn ureq_sources() {
        let gd = GD::get_with_sources(getter!(ureq)).unwrap();
        println!("{} {}", gd.version().unwrap(), gd.timestamp().unwrap());
        assert!(gd.has_sources().unwrap());
    }

    #[test]
    fn ureq_no_sources() {
        let gd = GD::get_no_sources(getter!(ureq)).unwrap();
        println!("{} {}", gd.version().unwrap(), gd.timestamp().unwrap());
        assert!(!gd.has_sources().unwrap());
    }

    #[tokio::test]
    async fn reqwest() {
        GD::get_async_no_sources(getter!(reqwest)).await.unwrap();
    }

    #[test]
    fn reqwest_blocking() {
        GD::get_no_sources(getter!(reqwest_blocking)).unwrap();
    }

    #[tokio::test]
    async fn surf() {
        GD::get_async_no_sources(getter!(surf)).await.unwrap();
    }

    #[test]
    fn isahc() {
        GD::get_no_sources(getter!(isahc)).unwrap();
    }

    #[tokio::test]
    async fn isahc_async() {
        GD::get_async_no_sources(getter!(isahc_async)).await.unwrap();
    }

    // #[test]
    // fn attohttpc() {
    //     GD::get_no_sources(getter!(attohttpc)).unwrap();
    // }

    #[test]
    fn minreq() {
        GD::get_no_sources(getter!(minreq)).unwrap();
    }

    #[tokio::test]
    async fn wreq() {
        GD::get_async_no_sources(getter!(wreq)).await.unwrap();
    }
}
