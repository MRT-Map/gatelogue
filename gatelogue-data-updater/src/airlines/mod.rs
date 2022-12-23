mod extractors;

use color_eyre::Result;
use common::types::{Flight, Gate, Graph};
use petgraph::visit::IntoNodeReferences;
use regex::Regex;

use crate::utils::wikitext;

async fn extract(airline_name: &str, regex: Regex) -> Result<Vec<(Gate, Gate, String)>> {
    let wikitext = wikitext(airline_name).await?;
    Ok(regex
        .captures_iter(&wikitext)
        .filter_map(|a| {
            Some((
                Gate {
                    airport: a.name("a1")?.as_str().try_into().ok()?,
                    gate_code: a.name("g1")?.as_str().into(),
                    airline: Some(airline_name.into()),
                    size: Some(a.name("s")?.as_str().into()),
                },
                Gate {
                    airport: a.name("a2")?.as_str().try_into().ok()?,
                    gate_code: a.name("g2")?.as_str().into(),
                    airline: Some(airline_name.into()),
                    size: Some(a.name("s")?.as_str().into()),
                },
                a.name("code")?.as_str().into(),
            ))
        })
        .collect())
}

pub async fn airlines(graph: &mut Graph) -> Result<()> {
    let handles = vec![extractors::astrella()]
        .into_iter()
        .map(|a| tokio::spawn(a));
    let mut flights = Vec::<(Gate, Gate, String)>::new();
    for handle in handles {
        flights.extend(handle.await??)
    }

    for (gate1, gate2, flight) in flights {
        let index1 = if let Some((index1, _)) = graph.node_references().find(|(_, g)| **g == gate1)
        {
            graph[index1].size = gate1.size.to_owned();
            graph[index1].airline = gate1.airline.to_owned();
            index1
        } else {
            graph.add_node(gate1)
        };
        let index2 = if let Some((index2, _)) = graph.node_references().find(|(_, g)| **g == gate2)
        {
            graph[index2].size = gate2.size.to_owned();
            graph[index2].airline = gate2.airline.to_owned();
            index2
        } else {
            graph.add_node(gate2)
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
