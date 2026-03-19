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
    _get_derived_vec!(lines, RailLine, "../sql/rail/company_lines.sql");
    _get_derived_vec!(stations, RailStation, "../sql/rail/company_stations.sql");
    _get_derived_vec!(platforms, RailPlatform, "../sql/rail/company_platforms.sql");
}

node_type!(RailLine);
impl RailLine {
    _get_column!("RailLine", code, String);
    _get_column!("RailLine", company, RailCompany);
    _get_column!("RailLine", name, Option<String>);
    _get_column!("RailLine", colour, Option<String>);
    _get_column!("RailLine", mode, Option<RailMode>);
    _get_column!("RailLine", local, Option<bool>);

    _get_derived_vec!(platforms, RailPlatform, "../sql/rail/line_platforms.sql");
    _get_derived_vec!(stations, RailStation, "../sql/rail/company_stations.sql");
}

node_type!(located RailStation);
impl RailStation {
    _get_set!("RailStationCodes", codes, "code", String);
    _get_column!("RailStation", company, RailCompany);
    _get_column!("RailStation", name, Option<String>);

    _get_derived_vec!(platforms, RailPlatform, "../sql/rail/station_platforms.sql");
    _get_derived_vec!(
        connections_from_here,
        RailConnection,
        "../sql/rail/station_connections_from_here.sql"
    );
    _get_derived_vec!(
        connections_to_here,
        RailConnection,
        "../sql/rail/station_connections_to_here.sql"
    );
    _get_derived_vec!(lines, RailLine, "../sql/rail/station_lines.sql");
}

node_type!(RailPlatform);
impl RailPlatform {
    _get_column!("RailPlatform", code, Option<String>);
    _get_column!("RailPlatform", station, RailStation);

    _get_derived_vec!(
        connections_from_here,
        RailConnection,
        "../sql/rail/platform_connections_from_here.sql"
    );
    _get_derived_vec!(
        connections_to_here,
        RailConnection,
        "../sql/rail/platform_connections_to_here.sql"
    );
    _get_derived_vec!(lines, RailLine, "../sql/rail/platform_lines.sql");
}

node_type!(RailConnection);
impl RailConnection {
    _get_column!("RailConnection", line, RailLine);
    _get_column!("RailConnection", from, RailPlatform);
    _get_column!("RailConnection", to, RailPlatform);
    _get_column!("RailConnection", direction, Option<String>);
    _get_column!("RailConnection", duration, Option<u32>);
}
