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
    _get_derived_vec!(lines, SeaLine, "../sql/sea/company_lines.sql");
    _get_derived_vec!(stops, SeaStop, "../sql/sea/company_stops.sql");
    _get_derived_vec!(
        docks,
        SeaDock,
         "../sql/sea/company_docks.sql"
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
        "../sql/sea/line_docks.sql"
    );
    _get_derived_vec!(
        stops,
        SeaStop,
        "../sql/sea/company_stops.sql"
    );
}

node_type!(located SeaStop);
impl SeaStop {
    _get_set!("SeaStopCodes", codes, "code", String);
    _get_column!("SeaStop", company, SeaCompany);
    _get_column!("SeaStop", name, Option<String>);

    _get_derived_vec!(docks, SeaDock, "../sql/sea/stop_docks.sql");
    _get_derived_vec!(
        connections_from_here,
        SeaConnection,
        "../sql/sea/stop_connections_from_here.sql"
    );
    _get_derived_vec!(
        connections_to_here,
        SeaConnection,
        "../sql/sea/stop_connections_to_here.sql"
    );
    _get_derived_vec!(
        lines,
        SeaLine,
        "../sql/sea/stop_lines.sql"
    );
}

node_type!(SeaDock);
impl SeaDock {
    _get_column!("SeaDock", code, Option<String>);
    _get_column!("SeaDock", stop, SeaStop);

    _get_derived_vec!(
        connections_from_here,
        SeaConnection,
        "../sql/sea/dock_connections_from_here.sql"
    );
    _get_derived_vec!(
        connections_to_here,
        SeaConnection,
        "../sql/sea/dock_connections_to_here.sql"
    );
    _get_derived_vec!(
        lines,
        SeaLine,
        "../sql/sea/dock_lines.sql"
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
