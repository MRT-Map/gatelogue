use strum_macros::EnumString;

use crate::{_from_sql_for_enum, _get_column, _get_derived_vec, _get_set, node_type, util::ID};

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum SeaMode {
    #[strum(serialize = "cruise")]
    Cruise,
    #[strum(serialize = "warp ferry")]
    WarpFerry,
    #[strum(serialize = "traincarts ferry")]
    TrainCartsFerry,
}
_from_sql_for_enum!(SeaMode);

node_type!(SeaCompany);
impl SeaCompany {
    _get_column!("SeaCompany", name, String);
    _get_column!("SeaCompany", link, Option<String>);
    _get_derived_vec!(lines, SeaLine, "SELECT i FROM SeaLine WHERE company = ?");
    _get_derived_vec!(stops, SeaStop, "SELECT i FROM SeaStop WHERE company = ?");
    _get_derived_vec!(
        docks,
        SeaDock,
        concat!(
            "SELECT DISTINCT SeaDock.i ",
            "FROM (SELECT i FROM SeaStop WHERE company = ?) A ",
            "INNER JOIN SeaDock on A.i = SeaDock.stop"
        )
    );
}

node_type!(SeaLine);
impl SeaLine {
    _get_column!("SeaLine", code, String);
    _get_column!("SeaLine", company, SeaCompany);
    _get_column!("SeaLine", name, Option<String>);
    _get_column!("SeaLine", colour, Option<String>);
    _get_column!("SeaLine", mode, Option<SeaMode>);
    _get_column!("SeaLine", local, Option<bool>);

    _get_derived_vec!(
        docks,
        SeaDock,
        concat!(
            "SELECT DISTINCT SeaDock.i ",
            "FROM (SELECT \"from\", \"to\" FROM SeaConnection WHERE line = ?) A ",
            "LEFT JOIN SeaDock ON A.\"from\" = SeaDock.i OR A.\"to\" = SeaDock.i"
        )
    );
    _get_derived_vec!(
        stops,
        SeaStop,
        concat!(
            "SELECT DISTINCT SeaDock.stop ",
            "FROM (SELECT \"from\", \"to\" FROM SeaConnection WHERE line = ?) A ",
            "LEFT JOIN SeaDock ON A.\"from\" = SeaDock.i OR A.\"to\" = SeaDock.i"
        )
    );
}

node_type!(located SeaStop);
impl SeaStop {
    _get_set!("SeaStopCodes", codes, "code", String);
    _get_column!("SeaStop", company, SeaCompany);
    _get_column!("SeaStop", name, Option<String>);

    _get_derived_vec!(docks, SeaDock, "SELECT i FROM SeaDock WHERE stop = ?");
    _get_derived_vec!(
        connections_from_here,
        SeaConnection,
        concat!(
            "SELECT DISTINCT SeaConnection.i ",
            "FROM (SELECT i FROM SeaDock WHERE stop = ?) A ",
            "INNER JOIN SeaConnection ON A.i = SeaConnection.\"from\""
        )
    );
    _get_derived_vec!(
        connections_to_here,
        SeaConnection,
        concat!(
            "SELECT DISTINCT SeaConnection.i ",
            "FROM (SELECT i FROM SeaDock WHERE stop = ?) A ",
            "INNER JOIN SeaConnection ON A.i = SeaConnection.\"to\""
        )
    );
    _get_derived_vec!(
        lines,
        SeaLine,
        concat!(
            "SELECT DISTINCT SeaConnection.line ",
            "FROM (SELECT i FROM SeaDock WHERE stop = ?) A ",
            "LEFT JOIN SeaConnection ON A.i = SeaConnection.\"from\" OR A.i = SeaConnection.\"to\""
        )
    );
}

node_type!(SeaDock);
impl SeaDock {
    _get_column!("SeaDock", code, Option<String>);
    _get_column!("SeaDock", stop, SeaStop);

    _get_derived_vec!(
        connections_from_here,
        SeaConnection,
        "SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection.\"from\" = ?"
    );
    _get_derived_vec!(
        connections_to_here,
        SeaConnection,
        "SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection.\"to\" = ?"
    );
    _get_derived_vec!(
        lines,
        SeaLine,
        concat!(
            "SELECT DISTINCT SeaConnection.line FROM SeaConnection ",
            "WHERE SeaConnection.\"from\" = ? OR SeaConnection.\"to\" = ?"
        )
    );
}

node_type!(SeaConnection);
impl SeaConnection {
    _get_column!("SeaConnection", line, SeaLine);
    _get_column!("SeaConnection", from, SeaDock);
    _get_column!("SeaConnection", to, SeaDock);
    _get_column!("SeaConnection", direction, Option<String>);
    _get_column!("SeaConnection", duration, Option<u32>);
}
