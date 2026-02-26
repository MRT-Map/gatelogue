use rusqlite::{Connection, Params, Row};

use crate::error::Result;

pub type ID = u16;

#[macro_export]
macro_rules! get_column {
    ($table_name:literal, $column_name:ident, $ColTy:ty) => {
        pub fn $column_name(self, gd: &$crate::GD) -> $crate::error::Result<$ColTy> {
            #[allow(unused_imports)]
            use $crate::node::Node;
            gd.0.query_one(
                concat!(
                    "SELECT \"",
                    stringify!($column_name),
                    "\" FROM ",
                    $table_name,
                    " WHERE i = ?"
                ),
                (self.i(),),
                |a| a.get(0),
            )
            .map_err(|e| {
                if e == rusqlite::Error::QueryReturnedNoRows {
                    $crate::error::Error::NoNodeOfType(self.i(), self.ty())
                } else {
                    e.into()
                }
            })
        }
    };
    ($table_name:literal, $fn_name:ident, $column_name:literal, $ColTy:ty) => {
        pub fn $fn_name(self, gd: &$crate::GD) -> $crate::error::Result<$ColTy> {
            #[allow(unused_imports)]
            use $crate::node::Node;
            gd.0.query_one(
                concat!(
                    "SELECT \"",
                    $column_name,
                    "\" FROM ",
                    $table_name,
                    " WHERE i = ?"
                ),
                (self.i(),),
                |a| a.get(0),
            )
            .map_err(|e| {
                if e == rusqlite::Error::QueryReturnedNoRows {
                    $crate::error::Error::NoNodeOfType(self.i(), self.ty())
                } else {
                    e.into()
                }
            })
        }
    };
}
#[macro_export]
macro_rules! get_set {
    ($table_name:literal, $fn_name:ident, $column_name:literal, $ColTy:ty) => {
        pub fn $fn_name(self, gd: &$crate::GD) -> $crate::error::Result<Vec<$ColTy>> {
            #[allow(unused_imports)]
            use $crate::node::Node;
            match gd
                .0
                .prepare_cached(concat!(
                    "SELECT DISTINCT \"",
                    $column_name,
                    "\" FROM ",
                    $table_name,
                    " WHERE i = ?"
                ))?
                .query_and_then((self.i(),), |a| a.get(0).map_err(Into::into))
            {
                Ok(a) => Ok(a.collect::<$crate::error::Result<Vec<_>>>()?),
                Err(e) => Err(e.into()),
            }
        }
    };
}

#[macro_export]
macro_rules! get_derived_vec {
    ($fn_name:ident, $RetTy:ty, $sql:expr) => {
        pub fn $fn_name(self, gd: &$crate::GD) -> $crate::error::Result<Vec<$RetTy>> {
            use $crate::util::ConnectionExt;
            gd.0.query_and_then_get_vec($sql, (self.0,), |row| Ok(row.get(0)?))
        }
    };
}

#[macro_export]
macro_rules! from_sql_for_enum {
    ($Ty:ty) => {
        impl rusqlite::types::FromSql for $Ty {
            fn column_result(
                value: rusqlite::types::ValueRef<'_>,
            ) -> rusqlite::types::FromSqlResult<Self> {
                use std::str::FromStr;
                Self::from_str(value.as_str()?)
                    .map_err(|e| rusqlite::types::FromSqlError::Other(e.into()))
            }
        }
    };
}

pub trait ConnectionExt {
    fn query_and_then_get_vec<T, P, F>(&self, sql: &str, params: P, f: F) -> Result<Vec<T>>
    where
        P: Params,
        F: FnMut(&Row<'_>) -> Result<T>;
}
impl ConnectionExt for Connection {
    fn query_and_then_get_vec<T, P, F>(&self, sql: &str, params: P, f: F) -> Result<Vec<T>>
    where
        P: Params,
        F: FnMut(&Row<'_>) -> Result<T>,
    {
        match self.prepare(sql)?.query_and_then(params, f) {
            Ok(a) => Ok(a.collect::<Result<Vec<_>>>()?),
            Err(e) => Err(e.into()),
        }
    }
}
