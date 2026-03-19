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
    _get_derived_vec!(lines, BusLine, "../sql/bus/company_lines.sql");
    _get_derived_vec!(stops, BusStop, "../sql/bus/company_stops.sql");
    _get_derived_vec!(berths, BusBerth, "../sql/bus/company_berths.sql");
}

node_type!(BusLine);
impl BusLine {
    _get_column!("BusLine", code, String);
    _get_column!("BusLine", company, BusCompany);
    _get_column!("BusLine", name, Option<String>);
    _get_column!("BusLine", colour, Option<String>);
    _get_column!("BusLine", mode, Option<BusMode>);
    _get_column!("BusLine", local, Option<bool>);

    _get_derived_vec!(berths, BusBerth, "../sql/bus/line_berths.sql");
    _get_derived_vec!(stops, BusStop, "../sql/bus/company_stops.sql");
}

node_type!(located BusStop);
impl BusStop {
    _get_set!("BusStopCodes", codes, "code", String);
    _get_column!("BusStop", company, BusCompany);
    _get_column!("BusStop", name, Option<String>);

    _get_derived_vec!(berths, BusBerth, "../sql/bus/stop_berths.sql");
    _get_derived_vec!(
        connections_from_here,
        BusConnection,
        "../sql/bus/stop_connections_from_here.sql"
    );
    _get_derived_vec!(
        connections_to_here,
        BusConnection,
        "../sql/bus/stop_connections_to_here.sql"
    );
    _get_derived_vec!(lines, BusLine, "../sql/bus/stop_lines.sql");
}

node_type!(BusBerth);
impl BusBerth {
    _get_column!("BusBerth", code, Option<String>);
    _get_column!("BusBerth", stop, BusStop);

    _get_derived_vec!(
        connections_from_here,
        BusConnection,
        "../sql/bus/berth_connections_from_here.sql"
    );
    _get_derived_vec!(
        connections_to_here,
        BusConnection,
        "../sql/bus/berth_connections_to_here.sql"
    );
    _get_derived_vec!(lines, BusLine, "../sql/bus/berth_lines.sql");
}

node_type!(BusConnection);
impl BusConnection {
    _get_column!("BusConnection", line, BusLine);
    _get_column!("BusConnection", from, BusBerth);
    _get_column!("BusConnection", to, BusBerth);
    _get_column!("BusConnection", direction, Option<String>);
    _get_column!("BusConnection", duration, Option<u32>);
}
