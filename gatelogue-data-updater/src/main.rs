mod airlines;
mod airports;
mod utils;

use color_eyre::Result;
use common::types::Graph;

use crate::{airlines::airlines, airports::airports};

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;
    let mut graph = Graph::new_undirected();
    airports(&mut graph).await?;
    airlines(&mut graph).await?;
    println!("{graph:#?}");

    std::fs::write(
        {
            let mut path = std::env::current_dir()?;
            path.push("graph.msgpack");
            path
        },
        rmp_serde::to_vec(&graph)?,
    )?;
    Ok(())
}
