mod astrella;

use color_eyre::Result;
use common::types::Graph;

pub async fn airlines(graph: &mut Graph) -> Result<()> {
    astrella::astrella(graph).await?;
    Ok(())
}
