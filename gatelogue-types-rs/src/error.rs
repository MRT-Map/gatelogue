use std::fmt::Debug;
use thiserror::Error;

use crate::util::ID;

#[derive(Error, Debug)]
#[non_exhaustive]
pub enum Error {
    #[error("rusqlite error: {0:?}")]
    RuSQLite(#[from] rusqlite::Error),

    #[error("No node {0}")]
    NoNode(ID),
    #[error("No node {0} of type {1}")]
    NoNodeOfType(ID, &'static str),
    #[error("No aircraft {0}")]
    NoAircraft(String),
    #[error("Node {0} not Located")]
    NodeNotLocated(ID),

    #[error("HTTP GET error: {0:?}")]
    HTTPGetError(Box<dyn Debug + Send + Sync + 'static>),

    #[error("unknown error: {0:?}")]
    Unknown(#[from] anyhow::Error),
}

pub type Result<T, E = Error> = std::result::Result<T, E>;
