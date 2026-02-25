pub mod air;
pub mod bus;
pub mod located;
pub mod rail;
pub mod sea;
pub mod spawn_warp;
pub mod town;

use enum_dispatch::enum_dispatch;
use strum_macros::{EnumIs, EnumTryAs};

use crate::{
    error::Result,
    node::{
        air::{AirAirline, AirAirport, AirFlight, AirGate},
        bus::{BusBerth, BusCompany, BusConnection, BusLine, BusStop},
        located::AnyLocatedNode,
        rail::{RailCompany, RailConnection, RailLine, RailPlatform, RailStation},
        sea::{SeaCompany, SeaConnection, SeaDock, SeaLine, SeaStop},
        spawn_warp::SpawnWarp,
        town::Town,
    },
    util::ID,
    GD,
};

#[enum_dispatch]
pub trait Node: Copy {
    fn i(self) -> ID;
    fn ty(self) -> &'static str;
}

macro_rules! any_node {
    ($($Variant:ident),+) => {
        #[enum_dispatch(Node)]
        #[derive(Clone, Copy, PartialEq, Eq, Debug, EnumIs, EnumTryAs)]
        pub enum AnyNode {
            $($Variant),+
        }

        impl AnyNode {
            pub fn from_id(gd: &GD, id: ID) -> Result<Self> {
                gd.0.query_one("SELECT type FROM Node WHERE i = ?", (id,), |row| {
                    Ok(match &*row.get::<_, String>(0)? {
                        $(stringify!($Variant) => $Variant(id).into(),)+
                        _ => unreachable!(),
                    })
                })
                .map_err(Into::into)
            }
        }
    };
}
any_node!(
    AirAirline,
    AirAirport,
    AirGate,
    AirFlight,
    BusCompany,
    BusLine,
    BusStop,
    BusBerth,
    BusConnection,
    RailCompany,
    RailLine,
    RailStation,
    RailPlatform,
    RailConnection,
    SeaCompany,
    SeaLine,
    SeaStop,
    SeaDock,
    SeaConnection,
    SpawnWarp,
    Town
);

#[macro_export]
macro_rules! node_type {
    ($Ty:ident) => {
        #[derive(Clone, Copy, PartialEq, Eq, Debug)]
        pub struct $Ty(pub(crate) ID);

        impl $crate::node::Node for $Ty {
            fn i(self) -> ID {
                self.0
            }
            fn ty(self) -> &'static str {
                stringify!($Ty)
            }
        }

        impl From<ID> for $Ty {
            fn from(value: ID) -> Self {
                Self(value)
            }
        }

        impl rusqlite::types::FromSql for $Ty {
            fn column_result(
                value: rusqlite::types::ValueRef<'_>,
            ) -> rusqlite::types::FromSqlResult<Self> {
                Ok(Self(ID::try_from(value.as_i64()?).map_err(|e| {
                    rusqlite::types::FromSqlError::Other(e.into())
                })?))
            }
        }
    };

    (located $Ty:ident) => {
        node_type!($Ty);

        impl $crate::node::located::LocatedNode for $Ty {}
    };
}
