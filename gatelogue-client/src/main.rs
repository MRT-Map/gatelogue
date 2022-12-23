mod consts;
mod airport_selector;

use yew::prelude::*;
use crate::airport_selector::AirportSelector;
use stylist::yew::styled_component;
use crate::consts::COL_A;

#[styled_component]
fn App() -> Html {
    let css = css!(r"
        background-color: ${COL_A};
        height: 100vh;
    ", COL_A = COL_A);
    html! {
        <div class={css}>
            <AirportSelector />
        </div>
    }
}

fn main() {
    yew::Renderer::<App>::new().render();
}