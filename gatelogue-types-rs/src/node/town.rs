use strum_macros::EnumString;

use crate::{_from_sql_for_enum, _get_column, node_type, util::ID};

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum Rank {
    Unranked,
    Councillor,
    Mayor,
    Senator,
    Governor,
    Premier,
    Community,
}
_from_sql_for_enum!(Rank);

node_type!(located Town);
impl Town {
    _get_column!("Town", name, String);
    _get_column!("Town", rank, Rank);
    _get_column!("Town", mayor, String);
    _get_column!("Town", deputy_mayor, "deputyMayor", Option<String>);
}
