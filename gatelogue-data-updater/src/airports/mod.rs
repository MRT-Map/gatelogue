mod pce;

use color_eyre::Result;
use common::types::Graph;

pub async fn airports(graph: &mut Graph) -> Result<()> {
    pce::pce(graph).await?;
    Ok(())
}
