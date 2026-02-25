use enum_dispatch::enum_dispatch;
use strum_macros::EnumString;

use crate::{
    error::Error,
    from_sql_for_enum,
    node::{
        air::AirAirport, bus::BusStop, rail::RailStation, sea::SeaStop, spawn_warp::SpawnWarp,
        town::Town, AnyNode, Node,
    },
    util::{ConnectionExt, ID},
    Result, GD,
};

#[enum_dispatch]
pub trait LocatedNode: Node + Copy {
    fn world(self, gd: &GD) -> Result<Option<World>> {
        gd.0.query_one(
            "SELECT world FROM LocatedNode WHERE i = ?",
            (self.i(),),
            |a| a.get(0),
        )
        .map_err(Into::into)
    }

    fn coordinates(self, gd: &GD) -> Result<Option<(f64, f64)>> {
        gd.0.query_one(
            "SELECT x, y FROM LocatedNode WHERE i = ?",
            (self.i(),),
            |a| {
                let Some(x) = a.get::<_, Option<f64>>(0)? else {
                    return Ok(None);
                };
                let Some(y) = a.get::<_, Option<f64>>(1)? else {
                    return Ok(None);
                };
                Ok(Some((x, y)))
            },
        )
        .map_err(Into::into)
    }

    fn nodes_in_proximity(self, gd: &GD) -> Result<Vec<(AnyLocatedNode, Proximity)>> {
        gd.0.query_and_then_get_vec(
            "SELECT node1, node2 FROM Proximity WHERE node1 = ?1 OR node2 = ?1",
            (self.i(),),
            |row| {
                let node1 = row.get(0)?;
                let node2 = row.get(1)?;
                Ok((
                    AnyLocatedNode::from_id(gd, if node1 == self.i() { node2 } else { node1 })?,
                    Proximity(node1, node2),
                ))
            },
        )
    }

    fn shared_facilities(self, gd: &GD) -> Result<Vec<AnyLocatedNode>> {
        gd.0.query_and_then_get_vec(
            "SELECT node1, node2 FROM SharedFacility WHERE node1 = ?1 OR node2 = ?1",
            (self.i(),),
            |row| {
                let node1 = row.get(0)?;
                let node2 = row.get(1)?;
                AnyLocatedNode::from_id(gd, if node1 == self.i() { node2 } else { node1 })
            },
        )
    }
}

macro_rules! any_located_node {
    ($($Variant:ident),+) => {
        #[enum_dispatch(Node, LocatedNode)]
        #[derive(Clone, Copy, PartialEq, Eq, Debug)]
        pub enum AnyLocatedNode {
            $($Variant),+
        }

        impl TryFrom<AnyNode> for AnyLocatedNode {
            type Error = Error;

            fn try_from(value: AnyNode) -> std::result::Result<Self, Self::Error> {
                match value {
                    $(AnyNode::$Variant(a) => Ok(Self::$Variant(a)),)+
                    _ => Err(Error::NodeNotLocated(value.i())),
                }
            }
        }

        impl From<AnyLocatedNode> for AnyNode {
            fn from(value: AnyLocatedNode) -> Self {
                match value {
                    $(AnyLocatedNode::$Variant(a) => Self::$Variant(a),)+
                }
            }
        }
    };
}
any_located_node!(AirAirport, BusStop, RailStation, SeaStop, SpawnWarp, Town);

impl AnyLocatedNode {
    pub fn from_id(gd: &GD, id: ID) -> Result<Self> {
        AnyNode::from_id(gd, id)?.try_into()
    }
}

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum World {
    Old,
    New,
    Space,
}
from_sql_for_enum!(World);

pub struct Proximity(pub ID, pub ID);

impl Proximity {
    pub fn distance(self, gd: &GD) -> Result<f64> {
        gd.0.query_one(
            "SELECT distance FROM Proximity WHERE node1 = ? AND node2 = ?",
            (self.0, self.1),
            |a| a.get(0),
        )
        .map_err(Into::into)
    }
    pub fn explicit(self, gd: &GD) -> Result<bool> {
        gd.0.query_one(
            "SELECT explicit FROM Proximity WHERE node1 = ? AND node2 = ?",
            (self.0, self.1),
            |a| a.get(0),
        )
        .map_err(Into::into)
    }
}
