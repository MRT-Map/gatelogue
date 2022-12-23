mod extractors;

use color_eyre::Result;
use common::types::{Gate, Graph};
use indicatif::ProgressIterator;
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
                airline: a
                    .name("airline")
                    .or_else(|| a.name("airline2"))
                    .map(|a| a.as_str().into()),
                size: a.name("size").map(|a| a.as_str().into()),
            })
        })
        .collect())
}

pub async fn airports(graph: &mut Graph) -> Result<()> {
    let handles = vec![
        tokio::spawn(extractors::pce()),
        tokio::spawn(extractors::mwt()),
        tokio::spawn(extractors::kek()),
        tokio::spawn(extractors::lar()),
        tokio::spawn(extractors::abg()),
        tokio::spawn(extractors::opa()),
        tokio::spawn(extractors::chb()),
        tokio::spawn(extractors::cbz()),
        tokio::spawn(extractors::cbi()),
        tokio::spawn(extractors::dfm()),
        tokio::spawn(extractors::vda()),
        tokio::spawn(extractors::dje()),
        tokio::spawn(extractors::wmi()),
        tokio::spawn(extractors::gsm()),
        tokio::spawn(extractors::vfw()),
        tokio::spawn(extractors::sdz()),
    ];
    let mut gates = Vec::<Gate>::new();
    for handle in handles.into_iter().progress() {
        gates.extend(handle.await??)
    }

    for gate in gates {
        graph.add_node(gate);
    }
    Ok(())
}
