mod airport_selector;
mod consts;
mod gate_viewer;

use stylist::yew::styled_component;
use yew::prelude::*;

use crate::{airport_selector::AirportSelector, consts::COL_A, gate_viewer::GateViewer};

#[styled_component]
fn App() -> Html {
    let css = css!(
        r"
        background-color: ${COL_A};
        height: 100vh;
        font-family: sans-serif;
    ",
        COL_A = COL_A
    );
    let state = use_state_eq(|| None);
    html! {
        <div class={css}>
            <AirportSelector state={state.clone()} />
            <GateViewer state={state.clone()}/>
        </div>
    }
}

fn main() {
    yew::Renderer::<App>::new().render();
}
