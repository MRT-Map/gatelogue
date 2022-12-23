use common::types::Graph;
use once_cell::sync::Lazy;

pub const COL_A: &str = "#111";
pub const COL_B: &str = "#333";
pub const COL_C: &str = "#555";
pub const COL_D: &str = "#888";
pub const COL_E: &str = "#aaa";
pub const ACC_A: &str = "#f40";
pub const ACC_B: &str = "#f84";

pub static GRAPH: Lazy<Graph> =
    Lazy::new(|| rmp_serde::from_slice(include_bytes!("../../graph.msgpack")).unwrap());
