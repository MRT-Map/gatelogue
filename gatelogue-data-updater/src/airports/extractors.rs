use color_eyre::Result;
use common::types::Gate;
use regex::Regex;

use crate::airports::extractor;

pub async fn pce() -> Result<Vec<Gate>> {
    extractor(
        "Peacopolis International Airport",
        "PCE",
        Regex::new(
            r"\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?P<airline>.*?)(?:\|.*?)?]].*?|)\|\|.*Service",
        )?,
    )
    .await
}
