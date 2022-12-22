use cached::proc_macro::cached;
use color_eyre::Result;
use common::types::Graph;

#[cached(result = true, time = 1800, sync_writes = true)]
pub async fn get_graph() -> Result<Graph> {
    let bytes = if cfg!(debug_assertions) {
        std::fs::read("graph.msgpack")?
    } else {
        reqwest::get("https://github.com/iiiii7d/gatelogue/raw/main/graph.msgpack")
            .await?
            .bytes()
            .await?
            .to_vec()
    };
    Ok(rmp_serde::from_slice(&bytes)?)
}
