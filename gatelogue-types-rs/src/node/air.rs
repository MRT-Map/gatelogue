use rusqlite::types::{FromSql, FromSqlResult, ValueRef};
use strum_macros::EnumString;

use crate::{_from_sql_for_enum, _get_column, _get_derived_vec, _get_set, node_type, util::ID};

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
_from_sql_for_enum!(AirMode);

node_type!(AirAirline);
impl AirAirline {
    _get_column!("AirAirline", name, String);
    _get_column!("AirAirline", link, Option<String>);

    _get_derived_vec!(
        flights,
        AirFlight,
        "SELECT i FROM AirFlight WHERE airline = ?"
    );
    _get_derived_vec!(
        gates,
        AirGate,
        concat!(
            "SELECT i FROM AirGate WHERE airline = ? ",
            "UNION SELECT \"from\" AS i FROM AirFlight WHERE airline = ? ",
            "UNION SELECT \"to\" AS i FROM AirFlight WHERE airline = ?"
        )
    );
    _get_derived_vec!(airports, AirAirport, concat!("SELECT DISTINCT airport FROM AirGate WHERE airline = ? ",
                "UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = \"from\" WHERE AirFlight.airline = ? ",
                "UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = \"to\" WHERE AirFlight.airline = ?"));
}

node_type!(located AirAirport);
impl AirAirport {
    _get_column!("AirAirport", code, String);
    _get_set!("AirAirportNames", names, "name", String);
    _get_column!("AirAirport", link, Option<String>);
    _get_set!("AirAirportModes", modes, "mode", AirMode);
    _get_derived_vec!(gates, AirGate, "SELECT i FROM AirGate WHERE airport = ?");
}

node_type!(AirGate);
impl AirGate {
    _get_column!("AirGate", code, Option<String>);
    _get_column!("AirGate", airport, AirAirport);
    _get_column!("AirGate", airline, Option<AirAirline>);
    _get_column!("AirGate", width, Option<u32>);
    _get_column!("AirGate", mode, AirMode);
    _get_derived_vec!(
        flights_from_here,
        AirFlight,
        "SELECT i FROM AirFlight WHERE \"from\" = ?"
    );
    _get_derived_vec!(
        flights_to_here,
        AirFlight,
        "SELECT i FROM AirFlight WHERE \"to\" = ?"
    );
}

node_type!(AirFlight);
impl AirFlight {
    _get_column!("AirFlight", airline, AirAirline);
    _get_column!("AirFlight", code, String);
    _get_column!("AirFlight", from, AirGate);
    _get_column!("AirFlight", to, AirGate);
    _get_column!("AirFlight", aircraft, Option<Aircraft>);
}

#[macro_export]
macro_rules! get_aircraft_column {
    ($column_name:ident, $ColTy:ty) => {
        pub fn $column_name(self, gd: &$crate::GD) -> $crate::error::Result<$ColTy> {
            gd.0.query_one(
                concat!(
                    "SELECT \"",
                    stringify!($column_name),
                    "\" FROM Aircraft WHERE name = ?"
                ),
                (&self.name(),),
                |a| a.get(0),
            )
            .map_err(|e| {
                if e == rusqlite::Error::QueryReturnedNoRows {
                    $crate::error::Error::NoAircraft(self.name().clone())
                } else {
                    e.into()
                }
            })
        }
    };
}

#[derive(Clone, PartialEq, Eq, Debug)]
pub struct Aircraft(pub(crate) String);
impl FromSql for Aircraft {
    fn column_result(value: ValueRef<'_>) -> FromSqlResult<Self> {
        Ok(Self(value.as_str()?.into()))
    }
}

impl Aircraft {
    #[must_use]
    pub const fn name(&self) -> &String {
        &self.0
    }
    get_aircraft_column!(manufacturer, String);
    get_aircraft_column!(width, u32);
    get_aircraft_column!(height, u32);
    get_aircraft_column!(length, u32);
    get_aircraft_column!(mode, AirMode);
}
