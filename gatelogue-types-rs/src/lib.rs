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
//! ```rust,ignore
//! use gatelogue_types::GD;
//! let gd = GD::reqwest_get_with_sources().await?; // with sources, requires `reqwest_get` feature
//! let gd = GD::reqwest_get_no_sources().await?; // no sources, requires `reqwest_get` feature
//! let gd = GD::surf_get_with_sources().await?; // with sources, requires `surf_get` feature
//! let gd = GD::surf_get_no_sources().await?; // no sources, requires `surf_get` feature
//! let gd = GD::ureq_get_with_sources()?; // with sources, requires `ureq_get` feature
//! let gd = GD::ureq_get_no_sources()?; // no sources, requires `ureq_get` feature
//! ```
//!
//! Using the ORM does not require SQL and makes for generally clean code.
//! However, doing this is very inefficient as each attribute access is one SQL query.
//! ```rust
//! use gatelogue_types::AirAirport;
//! # fn main() -> gatelogue_types::Result<()> {
//! # let gd = gatelogue_types::GD::ureq_get_no_sources()?;
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
//! # fn main() -> gatelogue_types::Result<()> {
//! # let gd = gatelogue_types::GD::ureq_get_no_sources()?;
//! gd.0.prepare("SELECT A.code, G.code FROM AirGate G INNER JOIN AirAirport A ON G.airport = A.i")?
//!     .query_map((), |row| {
//!         println!("Airport {:?} has gate {:?}", row.get::<_, String>(0)?, row.get::<_, String>(1)?);
//!         Ok(())
//!     })?;
//! # Ok(()) }
//! ```

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

pub struct GD(pub Connection);

impl GD {
    fn from_bytes(bytes: &[u8]) -> Result<Self> {
        let mut conn = Connection::open_in_memory()?;
        conn.deserialize_read_exact("main", bytes, bytes.len(), true)?;
        Ok(Self(conn))
    }
    #[cfg(feature = "reqwest_get")]
    pub async fn reqwest_get_with_sources() -> Result<Self> {
        let bytes = reqwest::get(URL).await?.bytes().await?;
        Self::from_bytes(&bytes)
    }
    #[cfg(feature = "reqwest_get")]
    pub async fn reqwest_get_no_sources() -> Result<Self> {
        let bytes = reqwest::get(URL_NO_SOURCES).await?.bytes().await?;
        Self::from_bytes(&bytes)
    }
    #[cfg(feature = "surf_get")]
    pub async fn surf_get_with_sources() -> Result<Self> {
        let bytes = surf::get(URL).recv_bytes().await?;
        Self::from_bytes(&bytes)
    }
    #[cfg(feature = "surf_get")]
    pub async fn surf_get_no_sources() -> Result<Self> {
        let bytes = surf::get(URL_NO_SOURCES).recv_bytes().await?;
        Self::from_bytes(&bytes)
    }
    #[cfg(feature = "ureq_get")]
    pub fn ureq_get_with_sources() -> Result<Self> {
        let bytes = ureq::get(URL).call()?.into_body().read_to_vec()?;
        Self::from_bytes(&bytes)
    }
    #[cfg(feature = "ureq_get")]
    pub fn ureq_get_no_sources() -> Result<Self> {
        let bytes = ureq::get(URL_NO_SOURCES)
            .call()?
            .into_body()
            .read_to_vec()?;
        Self::from_bytes(&bytes)
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
#[cfg(feature = "ureq_get")]
mod test {
    use super::*;

    #[test]
    fn ureq_sources() {
        let gd = GD::ureq_get_with_sources().unwrap();
        println!("{} {}", gd.version().unwrap(), gd.timestamp().unwrap());
        assert!(gd.has_sources().unwrap());
    }

    #[test]
    fn ureq_no_sources() {
        let gd = GD::ureq_get_no_sources().unwrap();
        println!("{} {}", gd.version().unwrap(), gd.timestamp().unwrap());
        assert!(!gd.has_sources().unwrap());
    }
}
