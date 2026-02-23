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

    #[error("rusqlite error: {0:?}")]
    Decode(#[from] rusqlite::Error),

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