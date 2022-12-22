use color_eyre::Result;
use common::types::{Gate, Graph};
use regex::Regex;

use crate::utils::wikitext;

pub async fn pce(graph: &mut Graph) -> Result<()> {
    let wikitext = wikitext("Peacopolis_International_Airport").await?;
    let gates = Regex::new(r"\n\|([^|]*?)(?:\|\|\[\[(.*?)(?:\|.*?)?]].*?|)\|\|.*Service")?
        .captures_iter(&wikitext)
        .filter_map(|a| {
            Some(Gate {
                airport: "PCE".try_into().ok()?,
                gate_code: a.get(1)?.as_str().into(),
                recorded_airline: a.get(2).map(|a| a.as_str().into()),
                size: None,
            })
        })
        .collect::<Vec<_>>();
    for gate in gates {
        graph.add_node(gate);
    }
    Ok(())
}
