use color_eyre::Result;
use common::types::{Flight, Gate, Graph};
use petgraph::visit::IntoNodeReferences;
use regex::Regex;

use crate::utils::wikitext;

pub async fn astrella(graph: &mut Graph) -> Result<()> {
    let wikitext = wikitext("Astrella").await?;
    println!("{wikitext}");
    let flights = Regex::new(r"\{\{AstrellaFlight\|code = ([^$]*?)\|airport1 = (.*?)\|gate1 = (.*?)\|airport2 = (.*?)\|gate2 = (.*?)\|size = (.*?)\|status = active}}")?
        .captures_iter(&wikitext)
        .filter_map(|a| Some((
            Gate {
                airport: a.get(2)?.as_str().try_into().ok()?,
                gate_code: a.get(3)?.as_str().into(),
                recorded_airline: Some("Astrella".into()),
                size: Some(a.get(6)?.as_str().into()),
            },
            Gate {
                airport: a.get(4)?.as_str().try_into().ok()?,
                gate_code: a.get(5)?.as_str().into(),
                recorded_airline: Some("Astrella".into()),
                size: Some(a.get(6)?.as_str().into()),
            },
            a.get(1)?.as_str()
            )))
        .collect::<Vec<_>>();
    for (gate1, gate2, flight) in flights {
        let index1 = if let Some((index1, _)) = graph.node_references().find(|(_, g)| **g == gate1)
        {
            graph[index1].size = gate1.size.to_owned();
            graph[index1].recorded_airline = gate1.recorded_airline.to_owned();
            index1
        } else {
            graph.add_node(gate1)
        };
        let index2 = if let Some((index2, _)) = graph.node_references().find(|(_, g)| **g == gate2)
        {
            graph[index2].size = gate2.size.to_owned();
            graph[index2].recorded_airline = gate2.recorded_airline.to_owned();
            index2
        } else {
            graph.add_node(gate2)
        };
        graph.add_edge(
            index1,
            index2,
            Flight {
                flight_no: flight.into(),
                airline: "Astrella".into(),
            },
        );
    }
    Ok(())
}
