use strum_macros::EnumString;

use crate::{_from_sql_for_enum, _get_column, _get_derived_vec, _get_set, node_type, util::ID};

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum BusMode {
    #[strum(serialize = "warp")]
    Warp,
    #[strum(serialize = "traincarts")]
    TrainCarts,
}
_from_sql_for_enum!(BusMode);

node_type!(BusCompany);
impl BusCompany {
    _get_column!("BusCompany", name, String);
    _get_column!("BusCompany", link, Option<String>);
    _get_derived_vec!(lines, BusLine, "SELECT i FROM BusLine WHERE company = ?");
    _get_derived_vec!(stops, BusStop, "SELECT i FROM BusStop WHERE company = ?");
    _get_derived_vec!(
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
    _get_column!("BusLine", code, String);
    _get_column!("BusLine", company, BusCompany);
    _get_column!("BusLine", name, Option<String>);
    _get_column!("BusLine", colour, Option<String>);
    _get_column!("BusLine", mode, Option<BusMode>);
    _get_column!("BusLine", local, Option<bool>);

    _get_derived_vec!(
        berths,
        BusBerth,
        concat!(
            "SELECT DISTINCT BusBerth.i ",
            "FROM (SELECT \"from\", \"to\" FROM BusConnection WHERE line = ?) A ",
            "LEFT JOIN BusBerth ON A.\"from\" = BusBerth.i OR A.\"to\" = BusBerth.i"
        )
    );
    _get_derived_vec!(
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
    _get_set!("BusStopCodes", codes, "code", String);
    _get_column!("BusStop", company, BusCompany);
    _get_column!("BusStop", name, Option<String>);

    _get_derived_vec!(berths, BusBerth, "SELECT i FROM BusBerth WHERE stop = ?");
    _get_derived_vec!(
        connections_from_here,
        BusConnection,
        concat!(
            "SELECT DISTINCT BusConnection.i ",
            "FROM (SELECT i FROM BusBerth WHERE stop = ?) A ",
            "INNER JOIN BusConnection ON A.i = BusConnection.\"from\""
        )
    );
    _get_derived_vec!(
        connections_to_here,
        BusConnection,
        concat!(
            "SELECT DISTINCT BusConnection.i ",
            "FROM (SELECT i FROM BusBerth WHERE stop = ?) A ",
            "INNER JOIN BusConnection ON A.i = BusConnection.\"to\""
        )
    );
    _get_derived_vec!(
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
    _get_column!("BusBerth", code, Option<String>);
    _get_column!("BusBerth", stop, BusStop);

    _get_derived_vec!(
        connections_from_here,
        BusConnection,
        "SELECT BusConnection.i FROM BusConnection WHERE BusConnection.\"from\" = ?"
    );
    _get_derived_vec!(
        connections_to_here,
        BusConnection,
        "SELECT BusConnection.i FROM BusConnection WHERE BusConnection.\"to\" = ?"
    );
    _get_derived_vec!(
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
    _get_column!("BusConnection", line, BusLine);
    _get_column!("BusConnection", from, BusBerth);
    _get_column!("BusConnection", to, BusBerth);
    _get_column!("BusConnection", direction, Option<String>);
    _get_column!("BusConnection", duration, Option<u32>);
}
