use common::types::{AirportCode, Flight, Gate};
use itertools::Itertools;
use petgraph::visit::IntoNodeReferences;
use stylist::yew::styled_component;
use yew::prelude::*;

use crate::consts::{ACC_A, ACC_C, COL_B, COL_C, GRAPH};

#[derive(Properties, Clone, PartialEq)]
pub struct SingleGateProps {
    pub gate: &'static Gate,
    pub flights: Vec<(&'static Flight, AirportCode)>,
}

#[styled_component]
pub fn SingleGate(props: &SingleGateProps) -> Html {
    let gate_code_css = css!(
        r"
        font-size: 2em;
        border-radius: 0.5em 0 0 0.5em;
        background-color: ${ACC_A};
        padding: 0.25em;
        font-weight: bold;
    ",
        ACC_A = ACC_A
    );
    let size_css = css!(
        r"
        background-color: ${bg};
        padding: 0.25em;
        font-size: 1.5em;
        font-weight: bold;
    ",
        bg = COL_C
    );
    let airline_css = css!(
        r"
        background-color: ${bg};
        padding: 0.25em;
        font-size: 1.5em;
        color: ${fg};
        ",
        bg = if props.gate.airline.is_some() {
            COL_B
        } else {
            ACC_C
        },
        fg = if props.gate.airline.is_some() {
            "#fff"
        } else {
            "#111"
        }
    );
    let closing_css = css!(
        r"
        font-size: 2em;
        border-radius: 0 0.5em 0.5em 0;
        background-color: ${bg};
        padding: 0.25em;
    ",
        bg = COL_B
    );
    let airline = props.gate.airline.as_deref().unwrap_or("No recorded owner");
    let size = props.gate.size.as_deref().unwrap_or("?");
    let flights = props.flights.iter().map(move |(f, a)| {
        let flights_css = css!(
            r"
                background-color: ${bg};
                padding: 0.25em;
                font-size: 1.5em;
            ",
            bg = COL_C
        );
        html! {
            <td class={flights_css}>
                {&f.flight_no}<br />{a}
            </td>
        }
    });
    html! {
        <tr>
            <td class={gate_code_css}>{&props.gate.gate_code}</td>
            <td class={size_css}>{size}</td>
            <td class={airline_css}>{airline}</td>
            { for flights }
            <td class={closing_css} colspan={(7usize.saturating_sub(props.flights.len())).to_string()}>{"   "}</td>
        </tr>
    }
}

#[derive(Properties, Clone, PartialEq)]
pub struct GateViewerProps {
    pub state: UseStateHandle<Option<String>>,
}

#[styled_component]
pub fn GateViewer(props: &GateViewerProps) -> Html {
    let main_css = css!(
        r"
        height: calc( 100vh - 1em );
        width: calc( 90vw - 4em );
        float: right;
        padding: 1em;
        padding-bottom: 0;
        overflow-y: auto;
        text-align: center;
    "
    );

    let Some(airport) = &*props.state else {
        return html! {
            <div class={main_css}>
                {"Select an airport to the left!"}
            </div>
        };
    };

    let header_css = css!(
        r"
        font-size: 5em;
    "
    );

    let gates = GRAPH
        .node_references()
        .filter(|(_, g)| *g.airport == *airport)
        .sorted_by(|(_, g1), (_, g2)| {
            alphanumeric_sort::compare_str(&*g1.gate_code, &*g2.gate_code)
        })
        .map(|(i, g)| {
            (
                GRAPH
                    .neighbors(i)
                    .flat_map(|a| {
                        GRAPH
                            .edges_connecting(i, a)
                            .map(move |f| (f.weight(), GRAPH.node_weight(a).unwrap().airport))
                    })
                    .collect::<Vec<_>>(),
                g,
            )
        })
        .map(|(f, g)| {
            html! {
                <SingleGate gate={g} flights={f} />
            }
        });

    html! {
        <div class={main_css}>
            <b class={header_css}>{airport}</b>
            <br /><br />
            <table class={css!("width: 100%;")}>
                { for gates }
            </table>
        </div>
    }
}
