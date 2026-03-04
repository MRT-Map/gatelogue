use strum_macros::EnumString;

use crate::{from_sql_for_enum, get_column, get_derived_vec, get_set, node_type, util::ID};

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum SeaMode {
    #[strum(serialize = "cruise")]
    Cruise,
    #[strum(serialize = "warp ferry")]
    WarpFerry,
    #[strum(serialize = "traincarts ferry")]
    TrainCartsFerry,
}
from_sql_for_enum!(SeaMode);

node_type!(SeaCompany);
impl SeaCompany {
    get_column!("SeaCompany", name, String);
    get_column!("SeaCompany", link, Option<String>);
    get_derived_vec!(lines, SeaLine, "SELECT i FROM SeaLine WHERE company = ?");
    get_derived_vec!(stops, SeaStop, "SELECT i FROM SeaStop WHERE company = ?");
    get_derived_vec!(
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
    get_column!("SeaLine", code, String);
    get_column!("SeaLine", company, SeaCompany);
    get_column!("SeaLine", name, Option<String>);
    get_column!("SeaLine", colour, Option<String>);
    get_column!("SeaLine", mode, Option<SeaMode>);
    get_column!("SeaLine", local, Option<bool>);

    get_derived_vec!(
        docks,
        SeaDock,
        concat!(
            "SELECT DISTINCT SeaDock.i ",
            "FROM (SELECT \"from\", \"to\" FROM SeaConnection WHERE line = ?) A ",
            "LEFT JOIN SeaDock ON A.\"from\" = SeaDock.i OR A.\"to\" = SeaDock.i"
        )
    );
    get_derived_vec!(
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
    get_set!("SeaStopCodes", codes, "code", String);
    get_column!("SeaStop", company, SeaCompany);
    get_column!("SeaStop", name, Option<String>);

    get_derived_vec!(docks, SeaDock, "SELECT i FROM SeaDock WHERE stop = ?");
    get_derived_vec!(
        connections_from_here,
        SeaConnection,
        concat!(
            "SELECT DISTINCT SeaConnection.i ",
            "FROM (SELECT i FROM SeaDock WHERE stop = ?) A ",
            "INNER JOIN SeaConnection ON A.i = SeaConnection.\"from\""
        )
    );
    get_derived_vec!(
        connections_to_here,
        SeaConnection,
        concat!(
            "SELECT DISTINCT SeaConnection.i ",
            "FROM (SELECT i FROM SeaDock WHERE stop = ?) A ",
            "INNER JOIN SeaConnection ON A.i = SeaConnection.\"to\""
        )
    );
    get_derived_vec!(
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
    get_column!("SeaDock", code, Option<String>);
    get_column!("SeaDock", stop, SeaStop);

    get_derived_vec!(
        connections_from_here,
        SeaConnection,
        "SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection.\"from\" = ?"
    );
    get_derived_vec!(
        connections_to_here,
        SeaConnection,
        "SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection.\"to\" = ?"
    );
    get_derived_vec!(
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
    get_column!("SeaConnection", line, SeaLine);
    get_column!("SeaConnection", from, SeaDock);
    get_column!("SeaConnection", to, SeaDock);
    get_column!("SeaConnection", direction, Option<String>);
    get_column!("SeaConnection", duration, Option<u32>);
}
