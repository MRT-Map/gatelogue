use crate::util::ID;
use crate::{from_sql_for_enum, get_column, get_derived_vec, get_set, node_type};
use strum_macros::EnumString;

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
from_sql_for_enum!(AirMode);

node_type!(AirAirline);
impl AirAirline {
    get_column!("AirAirline", name, String);
    get_column!("AirAirline", link, Option<String>);

    get_derived_vec!(
        flights,
        AirFlight,
        "SELECT i FROM AirFlight WHERE airline = ?"
    );
    get_derived_vec!(
        gates,
        AirGate,
        concat!(
            "SELECT i FROM AirGate WHERE airline = ? ",
            "UNION SELECT \"from\" AS i FROM AirFlight WHERE airline = ? ",
            "UNION SELECT \"to\" AS i FROM AirFlight WHERE airline = ?"
        )
    );
    get_derived_vec!(airports, AirAirport, concat!("SELECT DISTINCT airport FROM AirGate WHERE airline = ? ",
                "UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = \"from\" WHERE AirFlight.airline = ? ",
                "UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = \"to\" WHERE AirFlight.airline = ?"));
}

node_type!(located AirAirport);
impl AirAirport {
    get_column!("AirAirport", code, String);
    get_set!("AirAirport", names, "name", String);
    get_column!("AirAirport", link, Option<String>);
    get_set!("AirAirport", modes, "mode", AirMode);
    get_derived_vec!(gates, AirGate, "SELECT i FROM AirGate WHERE airport = ?");
}

node_type!(AirGate);
impl AirGate {
    get_column!("AirGate", code, Option<String>);
    get_column!("AirGate", airport, AirAirport);
    get_column!("AirGate", airline, Option<AirAirline>);
    get_column!("AirGate", size, Option<String>);
    get_column!("AirGate", mode, AirMode);
    get_derived_vec!(
        flights_from_here,
        AirFlight,
        "SELECT i FROM AirFlight WHERE \"from\" = ?"
    );
    get_derived_vec!(
        flights_to_here,
        AirFlight,
        "SELECT i FROM AirFlight WHERE \"to\" = ?"
    );
}

node_type!(AirFlight);
impl AirFlight {
    get_column!("AirFlight", airline, AirAirline);
    get_column!("AirFlight", code, String);
    get_column!("AirFlight", from, AirGate);
    get_column!("AirFlight", to, AirGate);
    get_column!("AirFlight", mode, Option<String>);
}
