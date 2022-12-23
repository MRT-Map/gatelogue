use itertools::Itertools;
use stylist::yew::styled_component;
use yew::prelude::*;

use crate::consts::{ACC_A, ACC_B, COL_A, COL_B, COL_D, COL_E, GRAPH};

#[derive(Properties, Clone, PartialEq)]
pub struct AirportButtonProps {
    pub code: &'static str,
    pub state: UseStateHandle<Option<String>>,
}

#[styled_component]
fn AirportButton(props: &AirportButtonProps) -> Html {
    let onclick = {
        let props = props.clone();
        Callback::from(move |_| props.state.set(Some(props.code.to_owned())))
    };
    let selected = *props.state == Some(props.code.to_owned());

    let css = css!(
        r"
        border-radius: 1em;
        background-color: ${bg};
        margin: 0.5em;
        padding: 0.5em;
        text-align: center;
        -webkit-touch-callout: none;
          -webkit-user-select: none;
           -khtml-user-select: none;
             -moz-user-select: none;
              -ms-user-select: none;
                  user-select: none;
        box-shadow: ${bg}8 0px 3px;
        transition: all 0.1s ease;

        &:hover {
            background-color: ${hov};
            color: #111;
            box-shadow: ${hov}8 0px 4px;
            transform: translateY(-1px);
            cursor: pointer;
        }

        &:active {
            background-color: ${COL_E} !important;
            box-shadow: ${COL_E}8 0px 0px !important;
            transform: translateY(3px);
            color: #111;
        }",
        bg = if selected { ACC_A } else { COL_A },
        hov = if selected { ACC_B } else { COL_D },
        COL_E = COL_E
    );
    html! {
        <div class={css} {onclick}>
            {props.code}
        </div>
    }
}

#[derive(Properties, Clone, PartialEq)]
pub struct AirportSelectorProps {
    pub state: UseStateHandle<Option<String>>,
}

#[styled_component]
pub fn AirportSelector(props: &AirportSelectorProps) -> Html {
    let css = css!(
        r"
        background-color: ${COL_B};
        height: calc( 100vh - 1em );
        width: 10%;
        float: left;
        padding: 1em;
        padding-bottom: 0;
        overflow-y: auto;
    ",
        COL_B = COL_B
    );
    let airports = GRAPH
        .node_weights()
        .map(|a| &a.airport)
        .sorted()
        .dedup()
        .map(|a| html! { <AirportButton code={a.as_str()} state={props.state.clone()} /> });
    html! {
        <div class={css}>
            {for airports}
        </div>
    }
}
