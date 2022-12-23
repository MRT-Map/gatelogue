mod extractors;

use color_eyre::Result;
use common::types::{Flight, Gate, Graph};
use indicatif::ProgressIterator;
use petgraph::visit::IntoNodeReferences;
use regex::Regex;

use crate::utils::wikitext;

async fn extract(
    airline_name: &str,
    page: &str,
    code_prefix: &str,
    regex: Regex,
) -> Result<Vec<(Gate, Gate, String)>> {
    let wikitext = wikitext(page).await?;
    Ok(regex
        .captures_iter(&wikitext)
        .filter_map(|a| {
            Some((
                Gate {
                    airport: a.name("a1")?.as_str().try_into().ok()?,
                    gate_code: a.name("g1").map(|a| a.as_str()).unwrap_or("?").into(),
                    airline: Some(airline_name.into()),
                    size: a.name("s").map(|a| a.as_str().into()),
                },
                Gate {
                    airport: a.name("a2")?.as_str().try_into().ok()?,
                    gate_code: a.name("g2").map(|a| a.as_str()).unwrap_or("?").into(),
                    airline: Some(airline_name.into()),
                    size: a.name("s").map(|a| a.as_str().into()),
                },
                format!("{code_prefix}{}", a.name("code")?.as_str()).into(),
            ))
        })
        .collect())
}

pub async fn airlines(graph: &mut Graph) -> Result<()> {
    let handles = vec![
        tokio::spawn(extractors::astrella()),
        tokio::spawn(extractors::turbula()),
        tokio::spawn(extractors::intra_air()),
        tokio::spawn(extractors::blu_air()),
        tokio::spawn(extractors::fli_high()),
        tokio::spawn(extractors::ola()),
    ];
    let mut flights = Vec::<(Gate, Gate, String)>::new();
    for handle in handles.into_iter().progress() {
        flights.extend(handle.await??)
    }

    for (gate1, gate2, flight) in flights {
        let index1 = if let Some((index1, _)) = graph.node_references().find(|(_, g)| **g == gate1)
        {
            graph[index1].size = gate1.size.to_owned();
            graph[index1].airline = gate1.airline.to_owned();
            index1
        } else if gate1.gate_code != "?" {
            graph.add_node(gate1)
        } else {
            let mut owned_airlines = graph
                .node_references()
                .filter(|(_, g)| g.airport == gate1.airport && g.airline == gate1.airline);
            if let Some((index1, _)) = owned_airlines.next() {
                if owned_airlines.next().is_none() {
                    graph[index1].size = gate1.size.to_owned();
                    graph[index1].airline = gate1.airline.to_owned();
                    index1
                } else {
                    graph.add_node(gate1)
                }
            } else {
                graph.add_node(gate1)
            }
        };
        let index2 = if let Some((index2, _)) = graph.node_references().find(|(_, g)| **g == gate2)
        {
            graph[index2].size = gate2.size.to_owned();
            graph[index2].airline = gate2.airline.to_owned();
            index2
        } else if gate2.gate_code != "?" {
            graph.add_node(gate2)
        } else {
            let mut owned_airlines = graph
                .node_references()
                .filter(|(_, g)| g.airport == gate2.airport && g.airline == gate2.airline);
            if let Some((index2, _)) = owned_airlines.next() {
                if owned_airlines.next().is_none() {
                    graph[index2].size = gate2.size.to_owned();
                    graph[index2].airline = gate2.airline.to_owned();
                    index2
                } else {
                    graph.add_node(gate2)
                }
            } else {
                graph.add_node(gate2)
            }
        };
        graph.add_edge(
            index1,
            index2,
            Flight {
                flight_no: flight.into(),
            },
        );
    }
    Ok(())
}
