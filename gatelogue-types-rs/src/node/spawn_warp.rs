use strum_macros::EnumString;

use crate::{_from_sql_for_enum, _get_column, node_type, util::ID};

#[derive(Clone, Copy, PartialEq, Eq, Debug, EnumString)]
pub enum WarpType {
    #[strum(serialize = "premier")]
    Premier,
    #[strum(serialize = "terminus")]
    Terminus,
    #[strum(serialize = "traincarts")]
    TrainCarts,
    #[strum(serialize = "portal")]
    Portal,
    #[strum(serialize = "misc")]
    Misc,
}
_from_sql_for_enum!(WarpType);

node_type!(located SpawnWarp);
impl SpawnWarp {
    _get_column!("SpawnWarp", name, String);
    _get_column!("SpawnWarp", warp_type, "warpType", WarpType);
}
