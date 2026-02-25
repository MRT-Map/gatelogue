use crate::util::ID;
use crate::{from_sql_for_enum, get_column, node_type};
use strum_macros::EnumString;

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
from_sql_for_enum!(Rank);

node_type!(located Town);
impl Town {
    get_column!("Town", name, String);
    get_column!("Town", rank, Rank);
    get_column!("Town", mayor, String);
    get_column!("Town", deputy_mayor, "deputyMayor", Option<String>);
}
