use yew::prelude::*;
use stylist::yew::styled_component;
use crate::consts::{COL_A, COL_B, COL_C, COL_D, COL_E};

#[derive(Properties, Clone, PartialEq)]
pub struct AirportButtonProps {
    pub code: &'static str,
    pub state: UseStateHandle<Option<String>>
}

#[styled_component]
fn AirportButton(props: &AirportButtonProps) -> Html {
    let onclick = {
        let props = props.clone();
        Callback::from(move |_| props.state.set(Some(props.code.to_owned())))
    };
    let bg = if *props.state == Some(props.code.to_owned()) {
        "#f00"
    } else {
        COL_A
    };

    let css = css!(r"
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
            background-color: ${COL_D};
            color: #111;
            box-shadow: ${COL_D}8 0px 4px;
            transform: translateY(-1px);
            cursor: pointer;
        }

        &:active {
            background-color: ${COL_E} !important;
            box-shadow: ${COL_E}8 0px 0px !important;
            transform: translateY(3px);
            color: #111;
        }",
        bg = bg,
        COL_D = COL_D,
        COL_E = COL_E
    );
    html! {
        <div class={css} {onclick}>
            {props.code}
        </div>
    }
}

#[styled_component]
pub fn AirportSelector() -> Html {
    let state = use_state_eq(|| None);
    let css = css!(r"
        background-color: ${COL_B};
        height: 100%;
        width: 10%;
        float: left;
        padding: 1em;
    ", COL_B = COL_B);
    html! {
        <div class={css}>
            <AirportButton code="SEG" state={state.clone()}/>
            <AirportButton code="PCE" {state}/>
        </div>
    }
}