mod extractors;

use color_eyre::Result;
use common::types::{Gate, Graph};
use regex::Regex;

use crate::utils::wikitext;

async fn extractor(page: &str, code: &str, regex: Regex) -> Result<Vec<Gate>> {
    let wikitext = wikitext(page).await?;
    Ok(regex
        .captures_iter(&wikitext)
        .filter_map(|a| {
            Some(Gate {
                airport: code.try_into().ok()?,
                gate_code: a.name("code")?.as_str().into(),
                airline: a.name("airline").map(|a| a.as_str().into()),
                size: None,
            })
        })
        .collect())
}

pub async fn airports(graph: &mut Graph) -> Result<()> {
    let gates = extractors::pce().await?;

    for gate in gates {
        graph.add_node(gate);
    }
    Ok(())
}
