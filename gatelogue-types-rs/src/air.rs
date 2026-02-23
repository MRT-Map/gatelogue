use strum_macros::EnumString;
use crate::{get_column, get_set, node_type};
use crate::node::ID;

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum AirMode {
    #[strum(serialize = "helicopter")]
    Helicopter,
    #[strum(serialize = "seaplane")]
    Seaplane,
    #[strum(serialize = "warp plane")]
    WarpPlane,
    #[strum(serialize = "traincarts plane")]
    TrainCartsPlane,
}

node_type!(AirAirline);
impl AirAirline {
    get_column!("AirAirline", name, String);
    get_column!("AirAirline", link, Option<String>);
}

node_type!(located AirAirport);
impl AirAirport {
    get_column!("AirAirport", code, String);
    get_set!("AirAirport", names, "name", String);
    get_column!("AirAirport", link, Option<String>);
    get_set!("AirAirport", modes, "mode", AirMode);
}

node_type!(AirGate);
impl AirGate {
    get_column!("AirGate", code, Option<String>);
    get_column!("AirGate", airport, AirAirport);
    get_column!("AirGate", airline, Option<AirAirline>);
    get_column!("AirGate", size, Option<String>);
    get_column!("AirGate", mode, AirMode);
}

node_type!(AirFlight);
impl AirFlight {
    get_column!("AirFlight", airline, AirAirline);
    get_column!("AirFlight", code, String);
    get_column!("AirFlight", from, AirGate);
    get_column!("AirFlight", to, AirGate);
    get_column!("AirFlight", mode, Option<String>);
}