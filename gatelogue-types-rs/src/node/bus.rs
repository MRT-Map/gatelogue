use strum_macros::EnumString;

use crate::{from_sql_for_enum, get_column, get_derived_vec, get_set, node_type, util::ID};

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum BusMode {
    #[strum(serialize = "warp")]
    Warp,
    #[strum(serialize = "traincarts")]
    TrainCarts,
}
from_sql_for_enum!(BusMode);

node_type!(BusCompany);
impl BusCompany {
    get_column!("BusCompany", name, String);
    get_derived_vec!(lines, BusLine, "SELECT i FROM BusLine WHERE company = ?");
    get_derived_vec!(stops, BusStop, "SELECT i FROM BusStop WHERE company = ?");
    get_derived_vec!(
        berths,
        BusBerth,
        concat!(
            "SELECT DISTINCT BusBerth.i ",
            "FROM (SELECT i FROM BusStop WHERE company = ?) A ",
            "INNER JOIN BusBerth on A.i = BusBerth.stop"
        )
    );
}

node_type!(BusLine);
impl BusLine {
    get_column!("BusLine", code, String);
    get_column!("BusLine", company, BusCompany);
    get_column!("BusLine", name, Option<String>);
    get_column!("BusLine", colour, Option<String>);
    get_column!("BusLine", mode, Option<BusMode>);
    get_column!("BusLine", local, Option<bool>);

    get_derived_vec!(
        berths,
        BusBerth,
        concat!(
            "SELECT DISTINCT BusBerth.i ",
            "FROM (SELECT \"from\", \"to\" FROM BusConnection WHERE line = ?) A ",
            "LEFT JOIN BusBerth ON A.\"from\" = BusBerth.i OR A.\"to\" = BusBerth.i"
        )
    );
    get_derived_vec!(
        stops,
        BusStop,
        concat!(
            "SELECT DISTINCT BusBerth.stop ",
            "FROM (SELECT \"from\", \"to\" FROM BusConnection WHERE line = ?) A ",
            "LEFT JOIN BusBerth ON A.\"from\" = BusBerth.i OR A.\"to\" = BusBerth.i"
        )
    );
}

node_type!(located BusStop);
impl BusStop {
    get_set!("BusStopCodes", codes, "code", String);
    get_column!("BusStop", company, BusCompany);
    get_column!("BusStop", name, Option<String>);

    get_derived_vec!(berths, BusBerth, "SELECT i FROM BusBerth WHERE stop = ?");
    get_derived_vec!(
        connections_from_here,
        BusConnection,
        concat!(
            "SELECT DISTINCT BusConnection.i ",
            "FROM (SELECT i FROM BusBerth WHERE stop = ?) A ",
            "INNER JOIN BusConnection ON A.i = BusConnection.\"from\""
        )
    );
    get_derived_vec!(
        connections_to_here,
        BusConnection,
        concat!(
            "SELECT DISTINCT BusConnection.i ",
            "FROM (SELECT i FROM BusBerth WHERE stop = ?) A ",
            "INNER JOIN BusConnection ON A.i = BusConnection.\"to\""
        )
    );
    get_derived_vec!(
        lines,
        BusLine,
        concat!(
            "SELECT DISTINCT BusConnection.line ",
            "FROM (SELECT i FROM BusBerth WHERE stop = ?) A ",
            "LEFT JOIN BusConnection ON A.i = BusConnection.\"from\" OR A.i = BusConnection.\"to\""
        )
    );
}

node_type!(BusBerth);
impl BusBerth {
    get_column!("BusBerth", code, Option<String>);
    get_column!("BusBerth", stop, BusStop);

    get_derived_vec!(
        connections_from_here,
        BusConnection,
        "SELECT BusConnection.i FROM BusConnection WHERE BusConnection.\"from\" = ?"
    );
    get_derived_vec!(
        connections_to_here,
        BusConnection,
        "SELECT BusConnection.i FROM BusConnection WHERE BusConnection.\"to\" = ?"
    );
    get_derived_vec!(
        lines,
        BusLine,
        concat!(
            "SELECT DISTINCT BusConnection.line FROM BusConnection ",
            "WHERE BusConnection.\"from\" = ? OR BusConnection.\"to\" = ?"
        )
    );
}

node_type!(BusConnection);
impl BusConnection {
    get_column!("BusConnection", line, BusLine);
    get_column!("BusConnection", from, BusBerth);
    get_column!("BusConnection", to, BusBerth);
    get_column!("BusConnection", direction, Option<String>);
}
