use std::str::FromStr;
use rusqlite::OptionalExtension;
use rusqlite::types::{FromSql, FromSqlError, FromSqlResult, ValueRef};
use strum_macros::EnumString;
use crate::error::Result;
use crate::GD;

pub type ID = u16;

#[macro_export]
macro_rules! get_column {
    ($table_name:literal, $column_name:ident, $ColTy:ty) => {
        fn $column_name(self, gd: GD) -> crate::error::Result<$ColTy> {
            gd.0.query_one(concat!("SELECT ", stringify!($column_name), " FROM ", $table_name, " WHERE i = ?"), (self.i(),), |a| a.get(0)).map_err(Into::into)
        }
    };
    ($table_name:literal, $fn_name:ident, $column_name:literal, $ColTy:ty) => {
        fn $fn_name(self, gd: GD) -> crate::error::Result<$ColTy> {
            gd.0.query_one(concat!("SELECT ", $column_name, " FROM ", $table_name, " WHERE i = ?"), (self.i(),), |a| a.get(0)).map_err(Into::into)
        }
    };
}
#[macro_export]
macro_rules! get_set {
    ($table_name:literal, $fn_name:ident, $column_name:literal, $ColTy:ty) => {
        fn $fn_name(self, gd: GD) -> crate::error::Result<Vec<$ColTy>> {
            gd.0.prepare_cached(concat!("SELECT DISTINCT ", $column_name, " FROM ", $table_name, " WHERE i = ?"))?.query_map(, (self.i(),), |a| a.get(0)).map(|a| a.collect()).map_err(Into::into)
        }
    };
}

pub trait Node: Copy {
    fn i(self) -> ID;
    get_column!("Node", ty, "type", World);
}

#[macro_export]
macro_rules! node_type {
    ($Ty:ident) => {
        #[derive(CLone, Copy, PartialEq, Eq, Debug)]
        pub struct $Ty(pub ID);

        impl crate::node::Node for $Ty {
            fn i(self) -> ID {
                self.0
            }
        }
    };

    (located $Ty:ident) => {
        node_type!($Ty)

        impl LocatedNode for $Ty {

        }
    };
}

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum World {
    Old,
    New,
    Space,
}
impl FromSql for World {
    fn column_result(value: ValueRef<'_>) -> FromSqlResult<Self> {
        World::from_str(value.as_str()?).map_err(FromSqlError::Other)
    }
}

pub trait LocatedNode: Node {
    get_column!("LocatedNode", world, Option<World>);
    fn coordinates(self, gd: GD) -> Result<Option<(f64, f64)>> {
        gd.0.query_one("SELECT x, y FROM LocatedNode WHERE i = ?", (self.i(),), |a| {
            let Some(x) = a.get::<_, Option<f64>>(0) else {
                return Ok(None);
            };
            let Some(y) = a.get::<_, Option<f64>>(1) else {
                return Ok(None);
            };
            Ok(Some((x, y)))
        }).map_err(Into::into)
    }
}