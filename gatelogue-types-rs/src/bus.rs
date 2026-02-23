use strum_macros::EnumString;
use crate::{get_column, get_set, node_type};
use crate::node::ID;

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum BusMode {
    #[strum(serialize = "warp")]
    Warp,
    #[strum(serialize = "traincarts")]
    Seaplane,
}

node_type!(BusCompany);
impl BusCompany {
    get_column!("BusCompany", name, String);
}

node_type!(BusLine);
impl BusLine {
    get_column!("BusLine", code, String);
    get_column!("BusLine", company, BusCompany);
    get_column!("BusLine", name, Option<String>);
    get_column!("BusLine", colour, Option<String>);
    get_column!("BusLine", mode, Option<BusMode>);
    get_column!("BusLine", local, Option<bool>);
}

node_type!(located BusStop);
impl BusStop {
    get_set!("BusStop", codes, "code", String);
    get_column!("BusStop", company, BusCompany);
    get_column!("BusStop", name, Option<String>);
}

node_type!(BusBerth);
impl BusBerth {
    get_column!("BusBerth", code, Option<String>);
    get_column!("BusBerth", stop, BusStop);
}

node_type!(BusConnection);
impl BusConnection {
    get_column!("BusConnection", line, BusLine);
    get_column!("BusConnection", from, BusBerth);
    get_column!("BusConnection", to, BusBerth);
    get_column!("BusConnection", direction, Option<String>);
}