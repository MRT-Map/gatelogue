use crate::util::ID;
use crate::{from_sql_for_enum, get_column, node_type};
use strum_macros::EnumString;

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
from_sql_for_enum!(WarpType);

node_type!(located SpawnWarp);
impl SpawnWarp {
    get_column!("SpawnWarp", name, String);
    get_column!("SpawnWarp", warp_type, "warpType", WarpType);
}
