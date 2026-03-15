use strum_macros::EnumString;

use crate::{_from_sql_for_enum, _get_column, _get_derived_vec, _get_set, node_type, util::ID};

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum RailMode {
    #[strum(serialize = "warp")]
    Warp,
    #[strum(serialize = "cart")]
    Cart,
    #[strum(serialize = "traincarts")]
    TrainCarts,
    #[strum(serialize = "vehicles")]
    Vehicles,
}
_from_sql_for_enum!(RailMode);

node_type!(RailCompany);
impl RailCompany {
    _get_column!("RailCompany", name, String);
    _get_column!("RailCompany", link, Option<String>);
    _get_derived_vec!(lines, RailLine, "SELECT i FROM RailLine WHERE company = ?");
    _get_derived_vec!(
        stations,
        RailStation,
        "SELECT i FROM RailStation WHERE company = ?"
    );
    _get_derived_vec!(
        platforms,
        RailPlatform,
        concat!(
            "SELECT DISTINCT RailPlatform.i ",
            "FROM (SELECT i FROM RailStation WHERE company = ?) A ",
            "INNER JOIN RailPlatform on A.i = RailPlatform.station"
        )
    );
}

node_type!(RailLine);
impl RailLine {
    _get_column!("RailLine", code, String);
    _get_column!("RailLine", company, RailCompany);
    _get_column!("RailLine", name, Option<String>);
    _get_column!("RailLine", colour, Option<String>);
    _get_column!("RailLine", mode, Option<RailMode>);
    _get_column!("RailLine", local, Option<bool>);

    _get_derived_vec!(
        platforms,
        RailPlatform,
        concat!(
            "SELECT DISTINCT RailPlatform.i ",
            "FROM (SELECT \"from\", \"to\" FROM RailConnection WHERE line = ?) A ",
            "LEFT JOIN RailPlatform ON A.\"from\" = RailPlatform.i OR A.\"to\" = RailPlatform.i"
        )
    );
    _get_derived_vec!(
        stations,
        RailStation,
        concat!(
            "SELECT DISTINCT RailPlatform.station ",
            "FROM (SELECT \"from\", \"to\" FROM RailConnection WHERE line = ?) A ",
            "LEFT JOIN RailPlatform ON A.\"from\" = RailPlatform.i OR A.\"to\" = RailPlatform.i"
        )
    );
}

node_type!(located RailStation);
impl RailStation {
    _get_set!("RailStationCodes", codes, "code", String);
    _get_column!("RailStation", company, RailCompany);
    _get_column!("RailStation", name, Option<String>);

    _get_derived_vec!(
        platforms,
        RailPlatform,
        "SELECT i FROM RailPlatform WHERE station = ?"
    );
    _get_derived_vec!(
        connections_from_here,
        RailConnection,
        concat!(
            "SELECT DISTINCT RailConnection.i ",
            "FROM (SELECT i FROM RailPlatform WHERE station = ?) A ",
            "INNER JOIN RailConnection ON A.i = RailConnection.\"from\""
        )
    );
    _get_derived_vec!(
        connections_to_here,
        RailConnection,
        concat!(
            "SELECT DISTINCT RailConnection.i ",
            "FROM (SELECT i FROM RailPlatform WHERE station = ?) A ",
            "INNER JOIN RailConnection ON A.i = RailConnection.\"to\""
        )
    );
    _get_derived_vec!(
        lines,
        RailLine,
        concat!(
            "SELECT DISTINCT RailConnection.line ",
            "FROM (SELECT i FROM RailPlatform WHERE station = ?) A ",
            "LEFT JOIN RailConnection ON A.i = RailConnection.\"from\" OR A.i = RailConnection.\"to\""
        )
    );
}

node_type!(RailPlatform);
impl RailPlatform {
    _get_column!("RailPlatform", code, Option<String>);
    _get_column!("RailPlatform", station, RailStation);

    _get_derived_vec!(
        connections_from_here,
        RailConnection,
        "SELECT RailConnection.i FROM RailConnection WHERE RailConnection.\"from\" = ?"
    );
    _get_derived_vec!(
        connections_to_here,
        RailConnection,
        "SELECT RailConnection.i FROM RailConnection WHERE RailConnection.\"to\" = ?"
    );
    _get_derived_vec!(
        lines,
        RailLine,
        concat!(
            "SELECT DISTINCT RailConnection.line FROM RailConnection ",
            "WHERE RailConnection.\"from\" = ? OR RailConnection.\"to\" = ?"
        )
    );
}

node_type!(RailConnection);
impl RailConnection {
    _get_column!("RailConnection", line, RailLine);
    _get_column!("RailConnection", from, RailPlatform);
    _get_column!("RailConnection", to, RailPlatform);
    _get_column!("RailConnection", direction, Option<String>);
    _get_column!("RailConnection", duration, Option<u32>);
}
