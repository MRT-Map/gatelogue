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

use rusqlite::Connection;
use rusqlite::types::FromSql;

mod error;
mod node;
mod util;

pub use error::*;
pub use node::{
    air::*, bus::*, located::*, rail::*, sea::*, spawn_warp::*, town::*, AnyNode, Node,
};
pub use util::ID;
use crate::util::ConnectionExt;

// TODO
pub const URL: &str = "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist-v3/data.db";
pub const URL_NO_SOURCES: &str =
    "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist-v3/data-ns.db";

pub struct GD(Connection);

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
        self.0.query_and_then_get_vec("SELECT i FROM Node", (), |a| AnyNode::from_id(self, a.get(0)?))
    }
    pub fn located_nodes(&self) -> Result<Vec<AnyLocatedNode>> {
        self.0.query_and_then_get_vec("SELECT i FROM LocatedNode", (), |a| AnyLocatedNode::from_id(self, a.get(0)?))
    }
    pub fn nodes_of_type<T: Node + From<ID> + FromSql>(&self) -> Result<Vec<T>> {
        let ty = T::from(0).ty();
        self.0.query_and_then_get_vec("SELECT i FROM Node WHERE type = ?", (ty,), |a| Ok(a.get(0)?))
    }
    pub fn get_node(&self, id: ID) -> Result<AnyNode> {
        AnyNode::from_id(self, id)
    }
    pub fn get_located_node(&self, id: ID) -> Result<AnyLocatedNode> {
        AnyLocatedNode::from_id(self, id)
    }
}

#[cfg(test)]
#[cfg(feature = "ureq_get")]
mod test {
    use super::*;

    #[test]
    fn ureq1() {
        let _ = GD::ureq_get_with_sources().unwrap();
    }

    #[test]
    fn ureq2() {
        let _ = GD::ureq_get_no_sources().unwrap();
    }
}
